from flask import Flask, render_template, request, redirect, url_for
from config import config 
from models import db, Region, Pays, Universite, Classement 
import os
import binascii
from sqlalchemy import and_, func, case
from math import ceil 

# --- Imports nécessaires pour la recherche (Flask-WTF) ---
from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField
from wtforms.validators import Optional, NumberRange
# --------------------------------------------------------

# --- DÉFINITION DU FORMULAIRE DE RECHERCHE ---
class SearchForm(FlaskForm):
    pays = SelectField('Pays', choices=[], validators=[Optional()])
    annee = SelectField('Année', choices=[], validators=[Optional()])
    score_enseig_min = FloatField('Score Enseignement Min', validators=[Optional(), NumberRange(min=0, max=100)])
    score_rech_min = FloatField('Score Recherche Min', validators=[Optional(), NumberRange(min=0, max=100)])
    submit = SubmitField('Filtrer')
# ---------------------------------------------


# --- Classe utilitaire de Pagination Manuelle (utilisée pour simuler le comportement) ---
class Pagination:
    def __init__(self, page, per_page, total_count, items):
        self.page = page
        self.per_page = per_page
        self.total = total_count
        self.items = items
        self.pages = int(ceil(self.total / self.per_page))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def prev_num(self):
        return self.page - 1

    def next_num(self):
        return self.page + 1

    def iter_pages(self, left_edge=2, right_edge=2, left_current=2, right_current=2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
# ------------------------------------------------------------------------------------------

# --- Fonctions d'aide pour le template ---

def format_ratio_fh_pourcentage(ratio_str):
    """
    Formate le ratio F/H. Supposons que le format est "F:H:XX".
    """
    if ratio_str is None:
        return None
    
    ratio_str = str(ratio_str).strip()
    parts = ratio_str.split(':')
    
    if len(parts) >= 2:
        try:
            pct_f = int(parts[0])
            pct_h = int(parts[1])
            
            if 95 <= pct_f + pct_h <= 105:
                return f"{pct_f}% F / {pct_h}% H"
            else:
                 return f"Ratio brut: {parts[0]}:{parts[1]}"

        except ValueError:
            return None
    
    return None


def create_app(config_name=None):
    """
    Factory function pour creer l'application Flask.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get(
            'SECRET_KEY', 
            binascii.hexlify(os.urandom(24)).decode() 
        )

    db.init_app(app)

    with app.app_context():
        db.create_all() 


    # Utilisation du ratio dans le fichier dérails universités
    @app.template_filter('format_ratio_pct')
    def format_ratio_pct_filter(classement):
        """Utilise directement les colonnes ratio_fem et ratio_hom."""
        if not classement or classement.ratio_fem is None or classement.ratio_hom is None:
            return '-'
        return f"{int(round(classement.ratio_fem))}% F / {int(round(classement.ratio_hom))}% H"

    @app.template_filter('format_pib')
    def format_pib(value):
        if value is None: return "-"
        return f"{int(value):,}".replace(",", " ") + " $"

    register_routes(app)
    return app


def register_routes(app):
        """
        Enregistre les routes de l'application.
        """
        @app.route("/")
        def index():
            """Page d'accueil avec KPI et graphiques."""
            # Récupération de l'annee la plus recente ou celle selectionnee
            annee_max = db.session.query(db.func.max(Classement.annee)).scalar() or 2025
            annee_recente = request.args.get('annee', annee_max, type=int)
            
            # Liste des annees disponibles
            annees = [a[0] for a in db.session.query(
                db.distinct(Classement.annee)
            ).order_by(Classement.annee.desc()).all()]

            # ========== KPI PAYS ==========
            nb_pays = db.session.query(db.func.count(db.distinct(Pays.id_pays))).join(
                Universite
            ).join(Classement).filter(Classement.annee == annee_recente).scalar() or 0
            
            # PIB moyen
            pib_moyen = db.session.query(db.func.avg(Pays.pib_hab)).scalar()
            pib_moyen = round(pib_moyen, 0) if pib_moyen else 0
            
            # Alphabetisation moyenne
            alpha_moyen = db.session.query(db.func.avg(Pays.alphabetisation_pct)).scalar()
            alpha_moyen = round(alpha_moyen, 1) if alpha_moyen else 0
            
            # Migration moyenne
            migration_moy = db.session.query(db.func.avg(Pays.migration_nette)).scalar()
            migration_moy = round(migration_moy, 2) if migration_moy else 0
            
            # Pays avec le plus d'universites
            pays_top_univ_query = db.session.query(
                Pays.nom_pays,
                db.func.count(Classement.id_classement).label('nb')
            ).select_from(Pays).join(
                Universite, Pays.id_pays == Universite.id_pays
            ).join(
                Classement, Universite.id_universite == Classement.id_univ
            ).filter(
                Classement.annee == annee_recente
            ).group_by(Pays.nom_pays).order_by(db.desc('nb')).first()
            
            pays_top_univ = pays_top_univ_query[0] if pays_top_univ_query else "N/A"
            pays_top_univ_nb = pays_top_univ_query[1] if pays_top_univ_query else 0
            
            # Region avec le plus d'universites
            region_top_univ_query = db.session.query(
                Region.nom_region,
                db.func.count(Classement.id_classement).label('nb')
            ).select_from(Region).join(
                Pays, Region.id_region == Pays.id_region
            ).join(
                Universite, Pays.id_pays == Universite.id_pays
            ).join(
                Classement, Universite.id_universite == Classement.id_univ
            ).filter(
                Classement.annee == annee_recente
            ).group_by(Region.nom_region).order_by(db.desc('nb')).first()
            
            region_top_univ = region_top_univ_query[0] if region_top_univ_query else "N/A"
            region_top_univ_nb = region_top_univ_query[1] if region_top_univ_query else 0

            # ========== KPI UNIVERSITES ==========
            nb_universites = Classement.query.filter_by(annee=annee_recente).count()
            nb_regions = Region.query.count()
            
            # Scores moyens
            score_moyen = db.session.query(
                db.func.avg(Classement.score_global)
            ).filter(Classement.annee == annee_recente).scalar()
            score_moyen = round(score_moyen, 2) if score_moyen else 0

            enseig_moyen = db.session.query(
                db.func.avg(Classement.indic_enseig)
            ).filter(Classement.annee == annee_recente).scalar()
            enseig_moyen = round(enseig_moyen, 2) if enseig_moyen else 0

            rech_moyen = db.session.query(
                db.func.avg(Classement.indic_qualite_rech)
            ).filter(Classement.annee == annee_recente).scalar()
            rech_moyen = round(rech_moyen, 2) if rech_moyen else 0
            
            # Ratio moyen F/H
            ratio_fh_moyen = db.session.query(
                db.func.avg(Classement.ratio_fem_hom)
            ).filter(Classement.annee == annee_recente).scalar()
            ratio_fh_moyen = round(ratio_fh_moyen, 2) if ratio_fh_moyen else 0
            
            # Pourcentage moyen etudiants internationaux
            etud_inter_moyen = db.session.query(
                db.func.avg(Classement.etud_internationaux_pct)
            ).filter(Classement.annee == annee_recente).scalar()
            etud_inter_moyen = round(etud_inter_moyen, 1) if etud_inter_moyen else 0

            # ========== TOP 5 PAYS PAR ENSEIGNEMENT ==========
            top_pays_enseig = db.session.query(
                Pays.nom_pays,
                db.func.avg(Classement.indic_enseig).label('score')
            ).select_from(Pays).join(
                Universite, Pays.id_pays == Universite.id_pays
            ).join(
                Classement, Universite.id_universite == Classement.id_univ
            ).filter(
                Classement.annee == annee_recente
            ).group_by(Pays.nom_pays).order_by(db.desc('score')).limit(5).all()

            #plus simple de renvoyer les données ce format pour éviter des erreurs d'index ou pour mieux comprendre le code ultérieurment

            data_top_pays_enseig = {"labels": [r[0] for r in top_pays_enseig],
                                    "data": [float(r[1]) if r[1] is not None else 0 for r in top_pays_enseig]
                                   }
            
            # ========== TOP 5 PAYS PAR RECHERCHE ==========
            top_pays_rech = db.session.query(
                Pays.nom_pays,
                db.func.avg(Classement.indic_qualite_rech).label('score')
            ).select_from(Pays).join(
                Universite, Pays.id_pays == Universite.id_pays
            ).join(
                Classement, Universite.id_universite == Classement.id_univ
            ).filter(
                Classement.annee == annee_recente
            ).group_by(Pays.nom_pays).order_by(db.desc('score')).limit(5).all()

            #plus simple de renvoyer les données ce format pour éviter des erreurs d'index ou pour mieux comprendre le code ultérieurment

            data_top_pays_rech = {  "labels": [r[0] for r in top_pays_rech],
                                    "data": [float(r[1]) if r[1] is not None else 0 for r in top_pays_rech]
                                }

            # ========== TOP 10 UNIVERSITES ==========
            top_10 = Classement.query.filter_by(annee=annee_recente).order_by(
                Classement.rang
            ).limit(10).all()



            # ========== REPARTITION PAR REGION ==========
            repartition_region = db.session.query(
                Region.nom_region,
                db.func.count(Classement.id_classement)
            ).select_from(Region).join(
                Pays, Region.id_region == Pays.id_region
            ).join(
                Universite, Pays.id_pays == Universite.id_pays
            ).join(
                Classement, Universite.id_universite == Classement.id_univ
            ).filter(
                Classement.annee == annee_recente
            ).group_by(Region.nom_region).all()

            #plus simple de renvoyer les données ce format pour éviter des erreurs d'index ou pour mieux comprendre le code ultérieurment


            data_repartition_region = { "labels": [r[0] for r in repartition_region],
                                        "data": [int(r[1]) if r[1] is not None else 0 for r in repartition_region]
                                    }

            # ========== TOP 5 PAYS PAR NOMBRE D'UNIVERSITES ==========
            top_pays_nb_univ = db.session.query(
                Pays.nom_pays,
                db.func.count(Classement.id_classement).label('nb')
            ).select_from(Pays).join(
                Universite, Pays.id_pays == Universite.id_pays
            ).join(
                Classement, Universite.id_universite == Classement.id_univ
            ).filter(
                Classement.annee == annee_recente
            ).group_by(Pays.nom_pays).order_by(db.desc('nb')).limit(5).all()

            return render_template(
                'index.html',
                annee_recente=annee_recente,
                annees=annees,
                # KPI Pays
                nb_pays=nb_pays, pib_moyen=pib_moyen, alpha_moyen=alpha_moyen,
                migration_moy=migration_moy, pays_top_univ=pays_top_univ,
                pays_top_univ_nb=pays_top_univ_nb,
                region_top_univ=region_top_univ, region_top_univ_nb=region_top_univ_nb,
                # KPI Universites
                nb_universites=nb_universites, nb_regions=nb_regions,
                score_moyen=score_moyen, enseig_moyen=enseig_moyen,
                rech_moyen=rech_moyen, ratio_fh_moyen=ratio_fh_moyen,
                etud_inter_moyen=etud_inter_moyen,
                # Graphiques
                top_pays_enseig=top_pays_enseig, top_pays_rech=top_pays_rech,
                top_10=top_10, repartition_region=repartition_region,
                top_pays_nb_univ=top_pays_nb_univ,

                # Graphs versions antho
                data_top_pays_enseig=data_top_pays_enseig,
                data_top_pays_rech=data_top_pays_rech,
                data_repartition_region=data_repartition_region
                
            )

        @app.route("/universites", methods=['GET', 'POST'])
        def universites():
            """Page des universités avec comparaisons graphiques et formulaire de recherche."""
            
            annee_max = db.session.query(db.func.max(Classement.annee)).scalar() or 2025
            
            # --- Préparation des listes de choix pour le formulaire ---
            
            # Années disponibles
            annees_query = db.session.query(
                db.distinct(Classement.annee)
            ).order_by(Classement.annee.desc()).all()
            annee_choices = [('', 'Toutes les années')] + [(str(a[0]), str(a[0])) for a in annees_query]

            # Pays disponibles (ceux ayant au moins un classement)
            pays_query = db.session.query(
                db.distinct(Pays.nom_pays)
            ).join(Universite).join(Classement).order_by(Pays.nom_pays).all()
            pays_choices = [('', 'Tous les pays')] + [(p[0], p[0]) for p in pays_query]

            # Initialisation du formulaire
            form = SearchForm(request.form)
            form.pays.choices = pays_choices
            form.annee.choices = annee_choices
            
            # --- 1. Récupération des données graphiques (Top/Bottom 5) ---
            annee_graph = annee_max # Année max pour les graphiques
            
            # 1. Top 5 Enseignement
            top5_enseig_query = db.session.query(
                Universite.nom_univ, Classement.indic_enseig
            ).select_from(Classement).join(Universite).filter(
                Classement.annee == annee_graph, Classement.indic_enseig.isnot(None) 
            ).order_by(db.desc(Classement.indic_enseig)).limit(5).all()
            
            data_top5_teaching = {'labels': [res[0] for res in top5_enseig_query], 'data': [res[1] for res in top5_enseig_query]}

            # 2. Bottom 5 Enseignement
            bottom5_enseig_query = db.session.query(
                Universite.nom_univ, Classement.indic_enseig
            ).select_from(Classement).join(Universite).filter(
                Classement.annee == annee_graph, Classement.indic_enseig.isnot(None)
            ).order_by(Classement.indic_enseig.asc()).limit(5).all()

            data_bottom5_teaching = {'labels': [res[0] for res in bottom5_enseig_query], 'data': [res[1] for res in bottom5_enseig_query]}

            # 3. Top 5 Recherche
            top5_rech_query = db.session.query(
                Universite.nom_univ, Classement.indic_qualite_rech
            ).select_from(Classement).join(Universite).filter(
                Classement.annee == annee_graph, Classement.indic_qualite_rech.isnot(None)
            ).order_by(db.desc(Classement.indic_qualite_rech)).limit(5).all()

            data_top5_research = {'labels': [res[0] for res in top5_rech_query], 'data': [res[1] for res in top5_rech_query]}

            # 4. Bottom 5 Recherche
            bottom5_rech_query = db.session.query(
                Universite.nom_univ, Classement.indic_qualite_rech
            ).select_from(Classement).join(Universite).filter(
                Classement.annee == annee_graph, Classement.indic_qualite_rech.isnot(None)
            ).order_by(Classement.indic_qualite_rech.asc()).limit(5).all()

            data_bottom5_research = {'labels': [res[0] for res in bottom5_rech_query], 'data': [res[1] for res in bottom5_rech_query]}
            
            
            # --- 2. CLASSEMENT INITIAL : TOP 100 UNIVERSITÉS ---
            top_100_universites_initial = db.session.query(
                Classement.id_classement, Classement.rang, Universite.nom_univ, Pays.nom_pays, 
                Region.nom_region, Classement.indic_enseig, Classement.indic_qualite_rech, Classement.score_global
            ).select_from(Classement).join(
                Universite, Classement.id_univ == Universite.id_universite
            ).join(
                Pays, Universite.id_pays == Pays.id_pays
            ).join(
                Region, Pays.id_region == Region.id_region
            ).filter(
                # IMPORTANT : Le TOP 100 par défaut utilise toujours l'année max
                Classement.annee == annee_max
            ).order_by(Classement.rang.asc()).limit(100).all()
            
            # Initialise la liste à afficher avec le TOP 100 par défaut
            universites_a_afficher = top_100_universites_initial
            
            # Détermine l'année à afficher dans le titre du tableau (par défaut l'année max)
            annee_affichée = annee_max
            
            # --- 3. Construction de la requête de base pour la liste et le comptage ---
            
            base_query = db.session.query(
                Classement.id_classement, Classement.rang, Universite.nom_univ, Pays.nom_pays, 
                Region.nom_region, Classement.indic_enseig, Classement.indic_qualite_rech, Classement.score_global
            ).select_from(Classement).join(
                Universite, Classement.id_univ == Universite.id_universite
            ).join(
                Pays, Universite.id_pays == Pays.id_pays
            ).join(
                Region, Pays.id_region == Region.id_region
            ).filter(
                Classement.score_global.isnot(None)
            ).order_by(Classement.rang.asc())

            # --- 4. Détermination des filtres et de l'état de la recherche ---
            
            is_search_request = request.method == 'POST' or any(
                request.args.get(field.name) not in ('', None)
                for field in [form.pays, form.annee, form.score_enseig_min, form.score_rech_min]
            )
            
            current_query = base_query
            annee_filtree = int(form.annee.data) if form.annee.data else None
            
            if not is_search_request:
                annee_affichée = annee_max
                current_query = current_query.filter(Classement.annee == annee_max)
            else:
                annee_affichée = annee_filtree if annee_filtree else annee_max
                
                filters = []
                
                if form.annee.data: 
                     filters.append(Classement.annee == int(form.annee.data))
                
                if form.pays.data and form.pays.data != '': 
                    filters.append(Pays.nom_pays == form.pays.data)
                    
                if form.score_enseig_min.data is not None: 
                    filters.append(Classement.indic_enseig >= form.score_enseig_min.data)
                    
                if form.score_rech_min.data is not None: 
                    filters.append(Classement.indic_qualite_rech >= form.score_rech_min.data)

                if filters:
                    current_query = current_query.filter(and_(*filters))
            
            # --- 5. Exécution de la requête avec Pagination ---
            
            page = request.args.get('page', 1, type=int)
            per_page = 100
            
            total_count = current_query.with_entities(func.count(Classement.id_classement)).scalar() or 0

            offset = (page - 1) * per_page
            resultats_page = current_query.limit(per_page).offset(offset).all()

            pagination = Pagination(page, per_page, total_count, resultats_page)

            universites_a_afficher = pagination.items


            # --- Rendu du template ---
            return render_template(
                'universités.html',
                form=form,
                data_top5_teaching=data_top5_teaching,
                data_bottom5_teaching=data_bottom5_teaching,
                data_top5_research=data_top5_research,
                data_bottom5_research=data_bottom5_research,
                universites_a_afficher=universites_a_afficher, 
                is_search_request=is_search_request, 
                annee_affichée=annee_affichée, 
                pagination=pagination,             
                total_count=total_count            
            )

        @app.route('/universite/<int:id>')
        def fiche_universite(id):
            """Affiche la fiche détaillée d'une université avec un storytelling amélioré."""
            
            # 1. Récupérer l'entrée de classement et les jointures
            classement = db.session.query(
                Classement, Universite, Pays, Region
            ).select_from(Classement).join(
                Universite, Classement.id_univ == Universite.id_universite
            ).join(
                Pays, Universite.id_pays == Pays.id_pays
            ).join(
                Region, Pays.id_region == Region.id_region 
            ).filter(Classement.id_classement == id).first()
            
            if not classement:
                return render_template('404.html'), 404

            classement_obj, universite_obj, pays_obj, region_obj = classement
            
            # 2. Récupérer l'historique pour le graphique
            historique_query = db.session.query(
                Classement.annee,
                Classement.indic_enseig,
                Classement.indic_qualite_rech,
                Classement.score_global
            ).filter(
                Classement.id_univ == universite_obj.id_universite
            ).order_by(Classement.annee.asc()).all()
            
            historique_data = {
                'labels': [h[0] for h in historique_query],
                'data_enseig': [h[1] for h in historique_query],
                'data_rech': [h[2] for h in historique_query],
                'data_global': [h[3] for h in historique_query],
            }

            # 3. Storytelling Amélioré (Utilisation directe des balises HTML)
            story = "Aucune donnée de classement historique disponible pour cette université."

            if historique_query:
                scores_global = [s for s in historique_data['data_global'] if s is not None]
                scores_enseig = [s for s in historique_data['data_enseig'] if s is not None]
                scores_rech = [s for s in historique_data['data_rech'] if s is not None]

                if len(scores_global) >= 2:
                    
                    premier_score_global = scores_global[0]
                    dernier_score_global = scores_global[-1]
                    diff_global = dernier_score_global - premier_score_global
                    
                    diff_enseig = scores_enseig[-1] - scores_enseig[0] if len(scores_enseig) >= 2 else 0
                    diff_rech = scores_rech[-1] - scores_rech[0] if len(scores_rech) >= 2 else 0

                    story_parts = []
                    
                    # Progression Globale
                    if diff_global > 2:
                        story_parts.append(f"L'Université <strong>{universite_obj.nom_univ}</strong> a démontré une <strong>progression constante</strong> de son score global, passant de {premier_score_global:.1f} à <strong>{dernier_score_global:.1f}</strong> sur la période observée.")
                    elif diff_global < -2:
                        story_parts.append(f"L'Université <strong>{universite_obj.nom_univ}</strong> a connu un <strong>léger déclin</strong> de son score global, perdant {abs(diff_global):.1f} points. Cela signale un besoin potentiel de réinvestissement dans certains domaines.")
                    else:
                        story_parts.append(f"L'Université <strong>{universite_obj.nom_univ}</strong> maintient une <strong>performance stable</strong> et de haut niveau, son score global fluctuant autour de <strong>{dernier_score_global:.1f}</strong>.")
                    
                    # Analyse des facteurs
                    if diff_enseig > 2 and diff_rech > 2:
                        story_parts.append(f"Cette performance est tirée par une <strong>amélioration notable</strong> dans ses deux piliers : l'Enseignement (gain de {diff_enseig:.1f} points) et la Recherche (gain de {diff_rech:.1f} points).")
                    elif diff_enseig > 2:
                        story_parts.append(f"L'<strong>excellence en Enseignement</strong> est son principal moteur de croissance, augmentant de {diff_enseig:.1f} points. L'indicateur de Recherche est resté stable ou a légèrement évolué.")
                    elif diff_rech > 2:
                        story_parts.append(f"Le <strong>renforcement de la Recherche</strong> est la source principale de sa progression, avec un gain de {diff_rech:.1f} points. Cela indique un impact croissant de ses travaux scientifiques.")
                    elif diff_enseig < -2 or diff_rech < -2:
                         if diff_enseig < diff_rech:
                            story_parts.append(f"Malgré une stabilité globale, l'indicateur d'Enseignement ({diff_enseig:.1f}) montre une légère faiblesse qui pourrait nécessiter une attention particulière.")
                         else:
                            story_parts.append(f"Malgré une stabilité globale, l'indicateur de Recherche ({diff_rech:.1f}) montre une légère faiblesse qui pourrait nécessiter une attention particulière.")
                    
                    # Conclusion et classement actuel
                    story_parts.append(f"Avec un rang actuel de <strong>#{classement_obj.rang}</strong>, l'université se positionne comme un leader mondial, reflet de la qualité de l'enseignement supérieur aux {pays_obj.nom_pays}.")
                    
                    story = " ".join(story_parts)
                
                else:
                    story = f"Seulement un ou zéro point de données historique trouvé. Le score global actuel est de <strong>{classement_obj.score_global:.1f}</strong> pour l'année {classement_obj.annee}."


            return render_template(
                'fiche_universite.html',
                classement=classement_obj,
                universite=universite_obj, 
                pays=pays_obj, 
                region=region_obj,
                historique_data=historique_data,
                story=story
            )
            
        @app.route("/statistiques")
        def statistiques():
            """Page des statistiques."""

            # Internationalisation et performance en recherche
            intern_categorie = case(
                (Classement.etud_internationaux_pct < 10, '[0–10%['),
                (Classement.etud_internationaux_pct < 20, '[10–20%['),
                (Classement.etud_internationaux_pct < 30, '[20–30%['),
                (Classement.etud_internationaux_pct >= 30, '[30%+]'),
                else_='Inconnu'
            ).label('pct_etud_intern')
            
            intern_perf_recherche_raw = db.session.query(
                intern_categorie,
                func.avg(Classement.indic_env_rech).label('moyenne_qualite_rech')
            ).group_by(intern_categorie).all()
            
            data_intern = [
                {'classe': row.pct_etud_intern, 'score': float(row.moyenne_qualite_rech) if row.moyenne_qualite_rech else 0}
                for row in intern_perf_recherche_raw
            ]


            # Richesse des pays et qualité de l'enseignement
            pib_categorie = case(
                (Pays.pib_hab <= 1135, 'Faible revenu'),
                (Pays.pib_hab.between(1136, 4495), 'Revenu intermédiaire'),
                (Pays.pib_hab >= 4496, 'Haut revenu'),
                else_='Inconnu'
            ).label('pib_hab')
            
            pib_qual_ens_raw = db.session.query(
                pib_categorie,
                func.avg(Classement.indic_enseig).label('moyenne_score_enseignement'),
                func.avg(Classement.indic_qualite_rech).label('moyenne_score_qualite_recherche')
            ).select_from(Pays).join(
                Universite, Universite.id_pays == Pays.id_pays
            ).join(
                Classement, Classement.id_univ == Universite.id_universite
            ).group_by(pib_categorie).all()
            
            # Ordre personnalisé pour les catégories
            ordre_pib = {'Inconnu': 0, 'Faible revenu': 1, 'Revenu intermédiaire': 2, 'Haut revenu': 3}
            
            data_pib = sorted([
                {
                    'classe': row.pib_hab,
                    'enseignement': float(row.moyenne_score_enseignement) if row.moyenne_score_enseignement else 0,
                    'recherche': float(row.moyenne_score_qualite_recherche) if row.moyenne_score_qualite_recherche else 0
                }
                for row in pib_qual_ens_raw
            ], key=lambda x: ordre_pib.get(x['classe'], 999))

            
            # Alphabétisation et score global
            alpha_categorie = case(
                (Pays.alphabetisation_pct < 80, '<80%'),
                (Pays.alphabetisation_pct.between(80, 90), '[80–90%]'),
                (Pays.alphabetisation_pct > 90, '>90%'),
                else_='Inconnu'
            ).label('pct_alphabetisation')
            
            alpha_score_glob_raw = db.session.query(
                alpha_categorie,
                func.avg(Classement.score_global).label('moyenne_score_global')
            ).select_from(Pays).join(
                Universite, Universite.id_pays == Pays.id_pays
            ).join(
                Classement, Classement.id_univ == Universite.id_universite
            ).group_by(alpha_categorie).all()
            
            data_alpha = [
                {
                    'classe': row.pct_alphabetisation,
                    'count': float(row.moyenne_score_global) if row.moyenne_score_global else 0
                }
                for row in alpha_score_glob_raw
            ]


            # Ratio femmes / hommes et score d'enseignement
            ratio_categorie = case(
                (Classement.ratio_fem_hom < 40, '< 40%'),
                (Classement.ratio_fem_hom.between(40, 60), '[40–60%]'),
                (Classement.ratio_fem_hom > 60, '>60%'),
                else_='Inconnu'
            ).label('pct_ratio')
            
            ratio_hf_score_raw = db.session.query(
                ratio_categorie,
                func.avg(Classement.indic_enseig).label('moyenne_score_enseignement'),
                func.avg(Classement.indic_qualite_rech).label('moyenne_score_qualite_recherche')
            ).group_by(ratio_categorie).all()
            
            # Ordre personnalisé pour les catégories de ratio F/H
            ordre_ratio = {'Inconnu': 0, '< 40%': 1, '[40–60%]': 2, '>60%': 3}
            
            data_ratio = sorted([
                {
                    'classe': row.pct_ratio,
                    'enseignement': float(row.moyenne_score_enseignement) if row.moyenne_score_enseignement else 0,
                    'recherche': float(row.moyenne_score_qualite_recherche) if row.moyenne_score_qualite_recherche else 0
                }
                for row in ratio_hf_score_raw
            ], key=lambda x: ordre_ratio.get(x['classe'], 999))


            # Scores par région
            scores_region_raw = db.session.query(
                Region.nom_region.label('region'),
                func.avg(Classement.indic_enseig).label('moyenne_score_enseignement'),
                func.avg(Classement.indic_qualite_rech).label('moyenne_score_qualite_recherche')
            ).select_from(Region).join(
                Pays, Region.id_region == Pays.id_region
            ).join(
                Universite, Pays.id_pays == Universite.id_pays
            ).join(
                Classement, Universite.id_universite == Classement.id_univ
            ).group_by(Region.nom_region).all()
            
            data_region = [
                {
                    'region': row.region,
                    'enseignement': float(row.moyenne_score_enseignement) if row.moyenne_score_enseignement else 0,
                    'recherche': float(row.moyenne_score_qualite_recherche) if row.moyenne_score_qualite_recherche else 0,
                    'global': (float(row.moyenne_score_enseignement) if row.moyenne_score_enseignement else 0 + float(row.moyenne_score_qualite_recherche) if row.moyenne_score_qualite_recherche else 0) / 2
                }
                for row in scores_region_raw
            ]


            return render_template('statistiques.html',
                                data_intern=data_intern,
                                data_pib=data_pib,
                                data_alpha=data_alpha,
                                data_ratio=data_ratio,
                                data_region=data_region)
    
        @app.route('/test-500')
        def test_500():
            """Route de test pour afficher la page d'erreur 500 (simulation)."""
            # En mode debug, on simule l'affichage de la page 500
            # En production, une vraie erreur afficherait cette page
            return render_template('500.html'), 500
            
        @app.errorhandler(404)
        def not_found(error):
            """Gestion des erreurs 404."""
            return render_template('404.html'), 404
            
# Point d'entree
app = create_app()

if __name__ == '__main__':
    # Pour le débogage et le fonctionnement local
    app.run(debug=True, host='0.0.0.0', port=5000)
