# Diagramme de Classes Python (SQLAlchemy ORM)

## Vue d'ensemble

Ce diagramme represente les classes Python utilisees pour mapper les tables de la base de donnees via **SQLAlchemy ORM**. Chaque classe correspond a une table et definit les attributs, methodes et relations.

## Diagramme de classes UML

```plantuml
@startuml
skinparam linetype ortho
skinparam class {
    BackgroundColor WhiteSmoke
    BorderColor Black
}

class Region {
    +Integer id_region <<PK>>
    +String nom_region
    --
    +List~Pays~ pays
    --
    +__repr__() : str
    +to_dict() : dict
}

class Pays {
    +Integer id_pays <<PK>>
    +String nom_pays
    +Integer population
    +Float superf_m2
    +Float pib_hab
    +Float migration_nette
    +Float industrie_part
    +Float services_part
    +Float alphabetisation_pct
    +Float tel_1000hab
    +Integer id_region <<FK>>
    --
    +Region region
    +List~Universite~ universites
    --
    +__repr__() : str
    +to_dict() : dict
    +get_nb_universites(annee) : int
    +get_score_moyen(annee, indicateur) : float
}

class Universite {
    +Integer id_universite <<PK>>
    +String nom_univ
    +Integer id_pays <<FK>>
    --
    +Pays pays
    +List~Classement~ classements
    --
    +__repr__() : str
    +to_dict() : dict
    +get_evolution() : List
}

class Classement {
    +Integer id_classement <<PK>>
    +Integer annee
    +Float rang
    +Float pop_etud
    +Float ratio_etud_pers
    +Float etud_internationaux_pct
    +String ratio_fem_hom
    +Float ratio_fem
    +Float ratio_hom
    +Float score_global
    +Float indic_enseig
    +Float indic_env_rech
    +Float indic_qualite_rech
    +Float indic_impact_industrie
    +Float indic_rel_intern
    +Integer id_univ <<FK>>
    --
    +Universite universite
    --
    +__repr__() : str
    +to_dict() : dict
    +{static} get_top_n(db, n, annee, critere) : List
    +{static} get_bottom_n(db, n, annee, critere) : List
}

' Relations de composition (Losange plein du côté du contenant)
Region "1" *-- "0..*" Pays : contient
Pays "1" *-- "0..*" Universite : localise

' Association simple (Flèche) pour Université et Classement
Universite "1" --> "0..*" Classement : possède

```

## Description des classes

### Region

Represente une region geographique (ex: Western Europe, North America).

| Attribut    | Type    | Description                     |
|-------------|---------|---------------------------------|
| id_region   | Integer | Cle primaire                    |
| nom_region  | String  | Nom de la region (unique)       |
| pays        | List    | Relation vers les pays          |

### Pays

Represente un pays avec ses statistiques socio-economiques.

| Attribut           | Type    | Description                     |
|--------------------|---------|---------------------------------|
| id_pays            | Integer | Cle primaire                    |
| nom_pays           | String  | Nom du pays (unique)            |
| population         | Integer | Population totale               |
| superf_m2          | Float   | Superficie                      |
| pib_hab            | Float   | PIB par habitant                |
| migration_nette    | Float   | Solde migratoire                |
| industrie_part     | Float   | Part industrie                  |
| services_part      | Float   | Part services                   |
| alphabetisation_pct| Float   | Taux alphabetisation            |
| tel_1000hab        | Float   | Telephones/1000 hab             |
| id_region          | Integer | Cle etrangere vers Region       |
| region             | Region  | Relation vers Region            |
| universites        | List    | Relation vers Universite        |

### Universite

Represente une universite (entite stable).

| Attribut       | Type    | Description                     |
|----------------|---------|---------------------------------|
| id_universite  | Integer | Cle primaire                    |
| nom_univ       | String  | Nom de l'universite             |
| id_pays        | Integer | Cle etrangere vers Pays         |
| pays           | Pays    | Relation vers Pays              |
| classements    | List    | Relation vers Classement        |

### Classement

Represente le classement annuel d'une universite (donnees variables par annee).

| Attribut              | Type    | Description                     |
|-----------------------|---------|---------------------------------|
| id_classement         | Integer | Cle primaire                    |
| annee                 | Integer | Annee du classement             |
| rang                  | Float   | Rang dans le classement         |
| pop_etud              | Float   | Population etudiante            |
| ratio_etud_pers       | Float   | Ratio etudiants/personnel       |
| etud_internationaux_pct| Float  | % etudiants internationaux      |
| ratio_fem_hom         | String  | Ratio F/H (texte)               |
| ratio_fem             | Float   | Ratio femmes                    |
| ratio_hom             | Float   | Ratio hommes                    |
| score_global          | Float   | Score global THE                |
| indic_enseig          | Float   | Indicateur enseignement         |
| indic_env_rech        | Float   | Indicateur env. recherche       |
| indic_qualite_rech    | Float   | Indicateur qualite recherche    |
| indic_impact_industrie| Float   | Indicateur impact industrie     |
| indic_rel_intern      | Float   | Indicateur relations intern.    |
| id_univ               | Integer | Cle etrangere vers Universite   |
| universite            | Universite | Relation vers Universite     |

## Relations ORM

| Relation                 | Type | Symbole_UML |                                         Description                                      |
|--------------------------|------|-------------|------------------------------------------------------------------------------------------|
| Region -> Pays           | 1-n  |     *--     | Une région est composée de plusieurs pays. La suppression de la région impacte les pays. |
| Pays -> Universite       | 1-n  |     *--     | Un pays contient plusieurs universités de manière structurelle.                          |
| Universite -> Classement | 1-n  |     -->     | Une université possède plusieurs relevés de classements annuels historiques.             |



## Methodes metier

### Region

- `to_dict()` : Serialisation en dictionnaire

### Pays

- `to_dict()` : Serialisation en dictionnaire
- `get_nb_universites(annee)` : Nombre d'universites classees pour une annee
- `get_score_moyen(annee, indicateur)` : Score moyen d'un indicateur

### Universite

- `to_dict()` : Serialisation en dictionnaire
- `get_evolution()` : Evolution des scores au fil des annees

### Classement

- `to_dict()` : Serialisation en dictionnaire
- `get_top_n(db, n, annee, critere)` : Top N universites selon un critere
- `get_bottom_n(db, n, annee, critere)` : Bottom N universites selon un critere
