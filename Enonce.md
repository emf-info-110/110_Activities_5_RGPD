# RGPD - Anonymisation des données personnelles

## Objectifs

- Préparer des données personnelles anonymisées en vue de leur traitement.
- Connaître des procédures d'anonymisation des données.
- Distinguer pseudonymisation et anonymisation.
- Comprendre l'importance de l'anonymisation sous l'angle de la protection des données.

---

## Contexte

Vous travaillez dans une entreprise SaaS. On vous demande de préparer un export de la table `customers` pour un prestataire d'analyse externe. Ce fichier contient des données personnelles (PII) : vous devez le transformer avant tout partage.

---

## Vocabulaire essentiel

| Terme | Définition |
|---|---|
| **PII** (données personnelles) | Toute information permettant d'identifier une personne directement ou indirectement. |
| **Identifiant direct** | Email, nom, prénom, téléphone, adresse postale. |
| **Quasi-identifiant** | Age précis, code postal complet, date de naissance, IP complète : chacun est "innocent" seul, mais dangereux combiné. |
| **Pseudonymisation** | On remplace un identifiant par un pseudonyme **déterministe** (même entrée → même sortie). La ré-identification reste possible si on a la clé. **Reste souvent de la donnée personnelle au sens RGPD.** |
| **Anonymisation** | On rend la ré-identification **difficile ou impossible**, pas juste "hash + basta". Cela implique de réduire la précision, de supprimer les cas rares, de limiter les quasi-identifiants. |

> **Point clé :** un hash SHA-256 de l'email n'est **pas** de l'anonymisation : c'est de la pseudonymisation. Si l'email est connu ou devinable, on peut recalculer le hash et retrouver la personne.

---

## Données

Fichier source : `data/customers_raw.csv`

Colonnes :

| Colonne | Type | Exemple |
|---|---|---|
| `customer_id` | ID technique | `c0001` |
| `created_at` | Timestamp | `2026-03-01T08:10:12Z` |
| `last_login_at` | Timestamp | `2026-04-18T21:02:51Z` |
| `first_name` | PII | `Alice` |
| `last_name` | PII | `Martin` |
| `email` | PII | `alice.martin@example.com` |
| `phone` | PII | `+41 79 111 22 33` |
| `birthdate` | Quasi-ID | `1998-07-14` |
| `street_address` | PII | `12 Rue des Fleurs` |
| `city` | Quasi-ID | `Lausanne` |
| `postal_code` | Quasi-ID | `1003` |
| `ip_last_seen` | Quasi-ID | `10.0.1.12` |
| `plan` | Métadonnée | `free` / `pro` / `business` |
| `marketing_opt_in` | Métadonnée | `true` / `false` |

---

## Environnement

```bash
# Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Linux / Mac
.venv\Scripts\Activate.ps1      # Windows PowerShell

# Lancer le pipeline
python python/pipeline_exercice.py

# Vérifier un export
python python/check_export.py out/customers_anonymized.csv
```

Ce chapitre utilise uniquement la librairie standard Python : `csv`, `datetime`, `hashlib`, `hmac`.

---

## Exercice

Complétez le fichier `python/pipeline_exercice.py`. Chaque fonction correspond à une étape. Vous produirez 4 fichiers dans `out/`.

### Etape 0 — Définir l'objectif d'analyse

Avant de coder, réfléchissez à quel indicateur vous souhaitez calculer sur le fichier final (exemple : *nombre de clients par plan et par tranche d'âge*). Cet objectif guidera vos choix de minimisation.

**Objectif défini :** produire des statistiques sur la base clients à destination d'un prestataire marketing externe :
- Répartition des clients par plan (`free` / `pro` / `business`)
- Taux d'abonnement aux communications marketing (`marketing_opt_in`)
- Distribution par tranche d'âge
- Croisements : ex. tranche d'âge × plan, région × plan

**Colonnes nécessaires pour cet objectif :** `plan`, `marketing_opt_in`, `age_bucket` (calculé depuis `birthdate`), `postal_prefix` (calculé depuis `postal_code`).
Toutes les autres colonnes sont superflues et doivent être supprimées dès l'étape 1.

---

### Etape 1 — Minimiser (`customers_minimized.csv`)

**But :** supprimer toutes les colonnes inutiles à votre objectif d'analyse.

**Pourquoi ?**
Le RGPD impose le principe de **minimisation** (art. 5) : on ne doit collecter et traiter que ce qui est strictement nécessaire à la finalité déclarée. Moins il y a de données, moins le risque est grand en cas de fuite ou d'usage détourné. Conserver des colonnes superflues (ex: numéro de téléphone pour une analyse de taux de conversion) est à la fois inutile et risqué — c'est une violation du principe même si les données ne sont jamais divulguées.

- Listez les colonnes utiles.
- Supprimez les identifiants directs (`first_name`, `last_name`, `email`, `phone`, `street_address`).
- Conservez `customer_id` uniquement si vous en avez besoin pour relier des données (il sera pseudonymisé plus tard).

---

### Etape 2 — Généraliser (`customers_generalized.csv`)

**But :** réduire la précision des quasi-identifiants.

**Pourquoi ?**
Un quasi-identifiant semble anodin seul, mais devient dangereux en combinaison. Une étude célèbre (Latanya Sweeney, 2000) a montré que **87 % des Américains sont identifiables uniquement avec leur code postal, leur sexe et leur date de naissance**. La généralisation réduit ce pouvoir discriminant : on remplace une valeur précise par une plage (ex: `1998-07-14` → `25-34 ans`) pour que de nombreuses personnes partagent la même valeur — et qu'on ne puisse plus isoler un individu.

Exemples de transformations :

| Colonne | Transformation suggérée |
|---|---|
| `birthdate` | → `age_bucket` : tranches `0-17`, `18-24`, `25-34`, `35-44`, `45-54`, `55+` |
| `postal_code` | → `postal_prefix` : garder les 2 premiers chiffres |
| `created_at` / `last_login_at` | → date seule (supprimer l'heure) |
| `ip_last_seen` | → `/24` (ex: `10.0.1.x`) ou supprimer |

---

### Etape 3 — Pseudonymiser (`customers_pseudonymized.csv`)

**But :** remplacer `customer_id` par un pseudonyme déterministe (pour garder la possibilité de faire des stats "par utilisateur" sans révéler l'identité).

**Pourquoi ?**
Parfois on a besoin de suivre un utilisateur dans le temps (ex: compter ses connexions sur un mois) ou de relier deux tables — sans pour autant connaître son identité. La pseudonymisation le permet : on remplace l'ID réel par un code opaque, calculé de façon déterministe avec une clé secrète. Même résultat que l'ID pour les jointures, mais sans révéler qui est la personne.

Attention : **la pseudonymisation n'est pas de l'anonymisation**. Si quelqu'un obtient la clé secrète, ou s'il connaît déjà l'ID réel d'un utilisateur, il peut recalculer le pseudonyme et retrouver la personne. Le RGPD (considérant 26) considère les données pseudonymisées comme des **données personnelles**.

Règles :
- Fonction déterministe : même entrée → même sortie (HMAC-SHA256 avec une clé secrète).
- Le secret **ne doit pas** apparaître dans le CSV.
- Garder 12-20 caractères hexadécimaux.

La clé est passée via `--secret-key` (voir le script).

---

### Etape 4 — Suppression des cas rares (`customers_anonymized.csv`)

**But :** produire un dataset difficile à ré-identifier.

**Pourquoi ?**
Même après généralisation, certaines combinaisons de quasi-identifiants restent uniques : s'il n'y a qu'une seule personne dans la tranche `55+`, code postal `10`, plan `business`, cette ligne *est* cette personne. On l'appelle un **cas rare** — et un cas rare est identifiable par définition.

Le principe du **k-anonymat** répond à ce problème : toute combinaison de quasi-identifiants doit apparaître au moins *k* fois dans le dataset. Si k=3, chaque individu se "fond" dans un groupe d'au moins 3 personnes qui lui ressemblent, et on ne peut plus l'isoler. Les lignes qui ne respectent pas ce seuil sont supprimées. C'est une technique standard, utilisée par exemple par les offices statistiques nationaux pour publier des données de recensement.

Règle à appliquer (**k-anonymat simplifié**) :
1. Choisissez 3 quasi-identifiants (ex: `age_bucket`, `postal_prefix`, `plan`).
2. Supprimez les lignes dont la combinaison de ces 3 champs apparaît **moins de k=3 fois**.
3. Supprimez `customer_pseudo` si vous ne l'utilisez plus.

Vérifiez ensuite avec `check_export.py`.

---

## Questions (à rendre)

**1.** Quelles colonnes avez-vous supprimées à l'étape de minimisation ? Pourquoi ?

    (réponse)

**2.** Quelles colonnes avez-vous généralisées ? Comment ?

    (réponse)

**3.** Pourquoi un hash de l'email n'est-il **pas** de l'anonymisation ? Dans quel cas pourrait-on ré-identifier quelqu'un ?

    (réponse)

**4.** Quelle règle de k-anonymat avez-vous appliquée (quels 3 champs, quelle valeur de k) ? Combien de lignes avez-vous supprimées ?

    (réponse)

**5.** Donnez un exemple concret de risque si ce fichier était partagé sans anonymisation.

    (réponse)
