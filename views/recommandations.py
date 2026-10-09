import streamlit as st

from utils.components import render_header, section_title


def show_recommandations():
    render_header()
    section_title("Pistes d’action pour une mobilité plus sûre")

    recommendations = [
        ("1. Renforcer la formation des conducteurs de motos", "Mettre en place des modules de sensibilisation sur la vitesse, le port du casque, la conduite de nuit et le respect du code de la route."),
        ("2. Prioriser les zones les moins desservies", "Investir dans la réhabilitation des axes de l’Intérieur, notamment dans les régions où la proportion de routes en mauvais état est la plus forte."),
        ("3. Développer la couverture de l’auto-école", "Soutenir l’ouverture d’auto-écoles dans les préfectures à faible densité pour mieux répartir la formation."),
        ("4. Renforcer la signalisation routière", "Améliorer les panneaux, marquage, feux et entretiens sur les tronçons à forte circulation."),
        ("5. Mettre en place une stratégie de données territoriales", "Suivre les accidents, les permis et l’état du réseau à l’échelle régionale pour piloter l’action publique."),
    ]

    for title, text in recommendations:
        st.markdown(f"### {title}")
        st.write(text)
