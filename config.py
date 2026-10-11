"""Configuration globale du tableau de bord de mobilité et sécurité routière au Togo."""

APP_TITLE = "Mobilité et sécurité routière au Togo"
APP_SUBTITLE = "Data Challenges | Administration territoriale et mobilité – Défi 1"

# Palette de couleurs harmonieuse : Vert, Jaune/Or, Bleu, Violet, Fond clair
COLORS = {
    "primary": "#0f8f73",         # Vert Togo / institutionnel
    "primary_dark": "#0a614e",    # Vert sombre
    "primary_light": "#e8f5f0",   # Vert clair pastel
    "accent": "#f4c542",          # Jaune / Or Togo
    "accent_dark": "#d4a409",     # Jaune sombre
    "blue": "#2b6cb0",            # Bleu
    "blue_light": "#ebf4ff",      # Bleu clair
    "purple": "#7b2cbf",          # Violet
    "purple_light": "#f3e8ff",    # Violet clair
    "text": "#1a2728",            # Texte sombre
    "muted": "#5f6f73",           # Texte estompé
    "card": "#ffffff",            # Fond de carte blanc
    "bg": "#f8faf9",              # Fond d'application clair
    "border": "#dfe7e2",          # Bordure douce
    "danger": "#d05454",          # Rouge alerte / mauvais état
    "warning": "#e8ab39",         # Ambre / état moyen
    "success": "#2f9e76",         # Vert succès / bon état
    "info": "#2b6cb0",            # Bleu information
}

# Ordre exact des 8 pages selon le cahier des charges
NAV_ITEMS = [
    "Objectifs",
    "Vue d'ensemble",
    "Véhicules & Permis",
    "Accidents & Sécurité",
    "Réseau routier",
    "Cartographie",
    "Auto-écoles",
    "Recommandations",
]

# Séquence de couleurs pour les graphiques Plotly
PLOTLY_COLOR_DISCRETE = [
    COLORS["primary"],
    COLORS["accent"],
    COLORS["blue"],
    COLORS["purple"],
    "#e28743",
    "#17a2b8",
    "#6c757d",
]

