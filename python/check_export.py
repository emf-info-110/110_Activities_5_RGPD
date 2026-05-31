import argparse
import csv
import re
import sys
from pathlib import Path

# Require international format (+XX...) to avoid false positives on dates or postal codes
EMAIL_RE = re.compile(r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b")
PHONE_RE = re.compile(r"\+\d[\d\s().-]{8,}\d")
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

# Column names that should not appear in an anonymized export
FORBIDDEN_COLUMNS = {
    "first_name", "last_name", "email", "phone",
    "street_address", "birthdate", "customer_id",
    "ip_last_seen", "ip_address",
    # Common aliases
    "name", "nom", "prenom", "tel", "telephone", "mobile",
    "address", "adresse", "date_of_birth", "dob", "user_id",
}

MAX_EXAMPLES = 3


def check_column_names(headers: list[str]) -> list[str]:
    return [col for col in headers if col.lower().strip() in FORBIDDEN_COLUMNS]


def scan_values(path: Path) -> dict[str, list[tuple[int, str, str]]]:
    """Return {pattern_name: [(row_num, col_name, matched_value), ...]}."""
    hits: dict[str, list] = {"email": [], "phone": [], "ipv4": []}
    with path.open("r", newline="", encoding="utf-8") as f:
        for row_num, row in enumerate(csv.DictReader(f), start=2):
            for col, val in row.items():
                if m := EMAIL_RE.search(val or ""):
                    hits["email"].append((row_num, col, m.group()))
                if m := PHONE_RE.search(val or ""):
                    hits["phone"].append((row_num, col, m.group()))
                if m := IPV4_RE.search(val or ""):
                    hits["ipv4"].append((row_num, col, m.group()))
    return hits


def report_hits(label: str, rows: list[tuple[int, str, str]]) -> bool:
    if not rows:
        print(f"  [OK]     {label} : aucune détectée")
        return False
    print(f"  [ALERTE] {label} : {len(rows)} occurrence(s)")
    for row_num, col, val in rows[:MAX_EXAMPLES]:
        print(f"           ligne {row_num}, colonne '{col}' → {val!r}")
    if len(rows) > MAX_EXAMPLES:
        print(f"           ... et {len(rows) - MAX_EXAMPLES} autre(s)")
    return True


def main() -> int:
    p = argparse.ArgumentParser(
        description="Scan d'export CSV — détecte les PII résiduelles évidentes."
    )
    p.add_argument("csv_path", type=Path, help="Fichier CSV à analyser")
    args = p.parse_args()

    if not args.csv_path.exists():
        print(f"Erreur : fichier introuvable : {args.csv_path}", file=sys.stderr)
        return 2

    with args.csv_path.open("r", newline="", encoding="utf-8") as f:
        headers = next(csv.reader(f))

    print(f"\nFichier  : {args.csv_path}")
    print(f"Colonnes : {', '.join(headers)}")
    print(f"{'─' * 60}")

    issues_found = False

    # 1. Check column names
    bad_cols = check_column_names(headers)
    if bad_cols:
        issues_found = True
        print(f"  [ALERTE] Colonnes interdites dans les en-têtes :")
        for col in bad_cols:
            print(f"           '{col}' est un identifiant direct — à supprimer ou renommer")
    else:
        print(f"  [OK]     En-têtes : aucune colonne PII directe détectée")

    print()

    # 2. Scan values for PII patterns
    hits = scan_values(args.csv_path)
    issues_found |= report_hits("Adresses email", hits["email"])
    issues_found |= report_hits("Numéros de téléphone", hits["phone"])
    issues_found |= report_hits("Adresses IP complètes (ex: 10.0.1.12)", hits["ipv4"])

    print(f"{'─' * 60}")
    if issues_found:
        print("RÉSULTAT : ÉCHEC — des PII résiduelles ont été détectées.")
        print("           Corrigez les points signalés et relancez le scan.")
        return 1
    else:
        print("RÉSULTAT : OK — aucune PII évidente détectée.")
        print("           Ce scan ne prouve pas l'anonymisation complète.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
