<!--
  Fichier généré automatiquement à partir de `Plan_Appli.md`.
  Contenu conservé; seule la structure Markdown a été améliorée.
-->

# Plan de l'application

## Thème

- Vert Castleton : prestige universitaire, rappelle le vert des lauriers, l’espoir envers les nouvelles générations
- Blanc : classe, léger
- Si bordures : pas d’arrondis pour le côté strict et ferme des universités

---

## Table des matières

- [KPI](#kpi)
- [Visualisations — Vue pays](#visualisations--vue-pays)
- [Université](#universit%C3%A9)
- [Statistiques](#statistiques)

---

## KPI

### KPI — Pays

- Nombre total de pays représentés
- Valeur moyenne du PIB / habitant
- Valeur moyenne du taux d’alphabétisation
- Valeur moyenne du taux de migration
- Pays avec le plus d’universités (peut être trop spécifique ?)
- Région avec le plus d’universités

### KPI — Universités

- Nombre total d’universités
- Score global THE moyen
- Score moyen d'enseignement
- Score moyen de recherche
- Ratio moyen H/F
- Pourcentage moyen d’étudiants internationaux

---

## Visualisations — Vue pays

### Top pays et recherche

- **Graphique en barres — Top 5 pays par score d’enseignement**
  - Question : quels pays possèdent les meilleurs systèmes d’enseignement universitaire ?
- **Graphique en barres — Top 5 pays par score de recherche**
  - Question : les pays leaders en enseignement sont-ils également leaders en recherche ?

### Répartition et classement

- **Diagramme circulaire** : répartition des universités par région
- **Tableau** : 10 meilleures universités
  - Colonnes : rang, nom_univ, pays, région, indic_enseig, indic_qualite_rech, score_global
  - Bouton “Détails” → `/universite/<id>`
    - Contenu de la page détaillée : tous les indicateurs socio-économiques du pays et les indicateurs propres à l’université
    - Graphique en ligne : évolution des scores (enseignement, recherche, global) par années + storytelling

---

## Université

### Comparatifs

- 4 graphiques en barres :
  - Top 5 universités en enseignement
  - Bottom 5 universités en enseignement
  - Top 5 universités en recherche
  - Bottom 5 universités en recherche

### Recherche et filtrage

- Formulaire de recherche / filtrage simple
  - Champs : Région (liste déroulante), Pays (liste déroulante), Année (liste déroulante)
  - Filtres optionnels : score minimal d’enseignement, score minimal de recherche
- Résultat : tableau filtré
  - Colonnes : rang, nom_univ, pays, région, indic_enseig, indic_qualite_rech, score_global
  - Bouton “Détails” → `/universite/<id>`

---

## Statistiques

### Internationalisation et performance en recherche

- **Graphique en barres** : lien entre pourcentage d’étudiants internationaux et qualité de la recherche
  - Regroupement par classes de pourcentage : [0–10%[, [10–20%[, [20–30%[, [30%+]
  - Pour chaque classe : moyenne de `indic_qualite_rech`
  - Storytelling associé

### Richesse des pays et qualité de l’enseignement

- **Graphique en barres groupées** : lien entre PIB / habitant et performances universitaires
  - Catégories de PIB / habitant :
    - Faible revenu : ≤ 1 135 USD
    - Revenu intermédiaire : 1 136–4 495 USD
    - Haut revenu : ≥ 4 496 USD
  - Pour chaque catégorie : moyenne de `indic_enseig` et `indic_qualite_rech` (sur les universités du pays)
  - Storytelling associé

### Alphabétisation et score global

- **Diagramme circulaire** : rôle du taux d’alphabétisation des pays sur le score global des universités
  - Classes d’alphabétisation : < 80%, [80–90%], > 90%
  - Exemple : part du top 100 par classe

### Ratio femmes / hommes et score d’enseignement

- **Graphique en barres groupées** : influence du ratio femmes/hommes sur indic_enseig et indic_qualite_rech
  - Catégories : < 40%, 40–60%, > 60% (pour pourcentage de femmes ou d’hommes)
  - Pour chaque catégorie : moyenne `indic_enseig` et moyenne `indic_qualite_rech`
  - Storytelling associé

### Scores par région

- **Graphique en barres groupées** : comparaison des différents scores des universités par région
