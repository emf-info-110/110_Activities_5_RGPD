# =============================================================================
# pipeline_exercice.py — Pipeline RGPD (à compléter)
#
# Ce script lit un fichier CSV de données clients et produit 4 fichiers de
# sortie en appliquant successivement : minimisation, généralisation,
# pseudonymisation, puis suppression des cas rares.
#
# Librairies utilisées (toutes incluses dans Python, pas d'installation) :
#   csv      — lire et écrire des fichiers CSV
#   datetime — manipuler des dates (calculer un âge, tronquer un timestamp)
#   hashlib  — fonctions de hachage (SHA-256)
#   hmac     — hachage avec clé secrète (HMAC)
#   argparse — gérer les arguments de la ligne de commande
#   pathlib  — manipuler des chemins de fichiers (plus pratique que os.path)
# =============================================================================

import argparse
import csv
import datetime
import hashlib
import hmac
from pathlib import Path


# -----------------------------------------------------------------------------
# Etape 1 — Minimisation
# -----------------------------------------------------------------------------
def minimize(in_path: Path, out_path: Path) -> None:
    # """Supprime les colonnes non nécessaires pour l'analyse, en ne gardant que les
    # quasi-identifiants et les variables d'intérêt."""
    # Par exemple, on peut garder les colonnes "date_of_birth", "postal_code", "purchase_amount",
    # et supprimer les autres (nom, prénom, email, etc.)
    " TODO : implémenter la fonction minimize() "
    raise NotImplementedError("La fonction minimize() n'est pas encore implémentée.")


# -----------------------------------------------------------------------------
# Etape 2 — Généralisation
# -----------------------------------------------------------------------------
def generalize(in_path: Path, out_path: Path) -> None:
    # """Applique des transformations de généralisation sur les données."""
    # Par exemple, convertir une date de naissance en une tranche d'âge (age_bucket),
    # ou tronquer un code postal à ses 2 premiers chiffres (postal_prefix).
    " TODO : implémenter la fonction generalize() "
    raise NotImplementedError("La fonction generalize() n'est pas encore implémentée.")

# -----------------------------------------------------------------------------
# Etape 3 — Pseudonymisation
# -----------------------------------------------------------------------------
def pseudonymize(in_path: Path, out_path: Path, secret_key: str) -> None:
    # """Remplace les identifiants directs par des pseudonymes générés à partir
    # d'une clé secrète et d'une fonction de hachage."""
    " TODO : implémenter la fonction pseudonymize() "
    raise NotImplementedError("La fonction pseudonymize() n'est pas encore implémentée.")

# -----------------------------------------------------------------------------
# Etape 4 — Suppression des cas rares (k-anonymat simplifié)
# -----------------------------------------------------------------------------
def anonymize(in_path: Path, out_path: Path, k: int = 3) -> None:
    # """Supprime les lignes correspondant à des combinaisons de valeurs rares, c'est-à-dire
    # celles qui apparaissent moins de k fois dans le dataset."""
    # Par exemple, si on considère les colonnes "age_bucket" et "postal_prefix
    # comme des quasi-identifiants, on peut supprimer les lignes où la combinaison
    # de ces deux valeurs apparaît moins de k fois.
    " TODO : implémenter la fonction anonymize() "
    raise NotImplementedError("La fonction anonymize() n'est pas encore implémentée.")  


# -----------------------------------------------------------------------------
# Point d'entrée du script
# -----------------------------------------------------------------------------
def main() -> int:
    # argparse permet de passer des options depuis le terminal.
    # Exemple : python pipeline_exercice.py --secret-key monsecret
    p = argparse.ArgumentParser(description="Pipeline RGPD - exercice")
    p.add_argument(
        "--in-csv",
        type=Path,
        default=Path("data/customers_raw.csv"),
        help="Fichier CSV source (défaut : data/customers_raw.csv)",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("out"),
        help="Dossier de sortie pour les exports (défaut : out/)",
    )
    p.add_argument(
        "--secret-key",
        type=str,
        default="CHANGE_ME",
        help="Clé secrète pour la pseudonymisation (ne pas commiter en dur !)",
    )
    p.add_argument(
        "--k",
        type=int,
        default=3,
        help="Seuil k pour le k-anonymat (défaut : 3)",
    )
    args = p.parse_args()

    # Créer le dossier de sortie s'il n'existe pas encore.
    # parents=True crée aussi les dossiers parents si nécessaire.
    # exist_ok=True ne plante pas si le dossier existe déjà.
    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Définir les chemins des 4 fichiers de sortie
    minimized     = args.out_dir / "customers_minimized.csv"
    generalized   = args.out_dir / "customers_generalized.csv"
    pseudonymized = args.out_dir / "customers_pseudonymized.csv"
    anonymized    = args.out_dir / "customers_anonymized.csv"

    # Exécuter les 4 étapes dans l'ordre.
    # Chaque étape prend en entrée le résultat de l'étape précédente.
    print("Etape 1 — Minimisation...")
    minimize(args.in_csv, minimized)

    print("Etape 2 — Généralisation...")
    generalize(minimized, generalized)

    print("Etape 3 — Pseudonymisation...")
    pseudonymize(generalized, pseudonymized, secret_key=args.secret_key)

    print("Etape 4 — Suppression des cas rares...")
    anonymize(pseudonymized, anonymized, k=args.k)

    print("\nExports générés :")
    for f in [minimized, generalized, pseudonymized, anonymized]:
        print(f"  {f}")
    return 0


# Ce bloc s'exécute uniquement si on lance le fichier directement
# (pas si on l'importe depuis un autre script).
if __name__ == "__main__":
    raise SystemExit(main())
