from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"


def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def get_data() -> dict:
    return {
        "vehicules": load_csv("parc_vehicules.csv"),
        "permis": load_csv("permis.csv"),
        "accidents": load_csv("accidents_national.csv"),
        "regions": load_csv("indicateurs_regions.csv"),
        "prefectures": load_csv("indicateurs_prefectures.csv"),
        "routes": load_csv("routes_classees.csv"),
        "auto_ecoles": load_csv("auto_ecoles.csv"),
        "etat_routes": load_csv("etat_routes.csv"),
    }
