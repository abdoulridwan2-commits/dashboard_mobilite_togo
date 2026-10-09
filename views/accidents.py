import plotly.express as px
import streamlit as st

from utils.components import render_header, section_title
from utils.data import get_data


def show_accidents():
    data = get_data()
    accidents = data["accidents"]

    render_header()
    section_title("Évolution des accidents, blessés et morts")
    st.caption("Données nationales uniquement; aucun découpage régional ou préfectoral des accidents n’est disponible.")

    year_range = st.slider(
        "Période affichée",
        min_value=int(accidents["annee"].min()),
        max_value=int(accidents["annee"].max()),
        value=(int(accidents["annee"].min()), int(accidents["annee"].max())),
        key="accidents_year_range",
    )
    selected = accidents[accidents["annee"].between(*year_range)]
    absolute = selected.melt(
        id_vars="annee",
        value_vars=["accidents", "blesses", "morts"],
        var_name="indicateur",
        value_name="nombre",
    )
    labels = {"accidents": "Accidents", "blesses": "Blessés", "morts": "Morts"}
    absolute["indicateur"] = absolute["indicateur"].map(labels)

    fig = px.line(
        absolute,
        x="annee",
        y="nombre",
        facet_row="indicateur",
        markers=True,
        title="Nombres annuels (axes distincts par indicateur)",
        labels={"nombre": "Nombre enregistré", "annee": "Année", "indicateur": ""},
        category_orders={"indicateur": ["Accidents", "Blessés", "Morts"]},
    )
    fig.update_yaxes(matches=None, title=None)
    fig.update_layout(template="plotly_white", height=660, showlegend=False)
    st.plotly_chart(fig, width="stretch")

    st.markdown("### Indicateurs avec dénominateur vérifiable")
    col1, col2, col3, col4 = st.columns(4)
    accident_2022 = accidents.loc[accidents["annee"] == 2022].iloc[0]

    with col1:
        st.metric("Morts en 2022", f"{int(accident_2022['morts']):,}")
    with col2:
        st.metric("Morts / 100 000 habitants (2022)", f"{accident_2022['morts_pour_100k_hab']:.2f}")
    with col3:
        st.metric("Blessés / 100 000 habitants (2022)", f"{accident_2022['blesses_pour_100k_hab']:.2f}")

    with col4:
        st.metric(
            "Morts pour 100 accidents (2022)",
            f"{accident_2022['deces_pour_100_accidents']:.2f}",
        )
    st.caption(
        "Formules 2022 : morts ou blessés ÷ population recensée 8 095 498 × 100 000; "
        "morts pour 100 accidents = morts ÷ accidents × 100. Ce dernier est un ratio brut, "
        "pas un taux de mortalité des personnes accidentées."
    )

    st.info(
        "Aucun taux par véhicule n’est affiché : le fichier disponible mesure les immatriculations "
        "annuelles, pas le parc roulant. La population n’est recensée qu’en 2022; les taux par habitant "
        "des années antérieures ne sont donc pas calculés."
    )
    with st.expander("Ruptures et qualité des séries"):
        variations = accidents.set_index("annee")["accidents"].pct_change()
        ruptures = variations[variations.abs() > 0.5]
        if ruptures.empty:
            st.write("Aucune variation annuelle supérieure à 50 % dans la série préparée.")
        else:
            st.write(
                "Variations absolues supérieures à 50 % à vérifier dans la source : "
                + ", ".join(f"{int(year)} ({value:+.0%})" for year, value in ruptures.items())
                + ". Elles peuvent refléter une évolution réelle ou un changement de couverture; "
                "la série seule ne permet pas de trancher."
            )
        st.write(
            "Le fichier source contient aussi un indicateur libellé « Accidents mortels /100.000 hab »; "
            "sa valeur 2022 correspond au nombre total d’accidents rapporté à la population, et non "
            "au nombre de décès. Il est conservé séparément comme taux source et n’est pas utilisé "
            "pour reconstruire les populations historiques."
        )
