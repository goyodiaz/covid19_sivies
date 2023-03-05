import pandas as pd
import streamlit as st


def main():
    st.set_page_config(
        page_title="COVID-19 - Datos SiViES",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )
    st.title("COVID-19 - Datos SiViES")
    st.header("Población mayor de 60 años")
    data = get_data()
    start, end = data["fecha"].iloc[[0, -1]].dt.date

    variable = st.sidebar.selectbox(
        label="Variable", options=["num_casos", "num_hosp", "num_uci", "num_def"]
    )

    break_down = st.sidebar.checkbox(label="Desglosar por")
    break_down_by = st.sidebar.radio(
        label="Desglosar por",
        options=["sexo", "grupo_edad"],
        horizontal=True,
        disabled=not break_down,
        label_visibility="collapsed",
    )
    chart_type = st.sidebar.selectbox(
        label="Tipo de gráfico", options=["Línea", "Área", "Barra"]
    )

    start, end = st.slider(
        label="Intervalo",
        min_value=start,
        max_value=end,
        value=(start, end),
        label_visibility="collapsed",
    )

    if break_down:
        data = (
            data.groupby(["fecha", break_down_by])[variable]
            .sum(numeric_only=False)
            .reset_index()
            .pivot(index="fecha", columns=break_down_by, values=variable)
            .loc[start:end]
        )
    else:
        data = data.groupby(["fecha"])[variable].sum(numeric_only=False).loc[start:end]

    chart_types = {"Línea": st.line_chart, "Área": st.area_chart, "Barra": st.bar_chart}
    chart_types[chart_type](data)
    st.dataframe(data)


@st.cache_resource
def get_data():
    path = "https://cnecovid.isciii.es/covid19/resources/casos_hosp_uci_def_sexo_edad_provres_60_mas.csv"
    data = pd.read_csv(path)
    data["fecha"] = pd.to_datetime(data["fecha"], format="%Y-%m-%d")
    data["provincia_iso"] = data["provincia_iso"].astype("category")
    data["sexo"] = data["sexo"].astype("category")
    data["grupo_edad"] = data["grupo_edad"].astype("category")
    return data


if __name__ == "__main__":
    main()
