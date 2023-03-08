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

    st.sidebar.write("Población")
    population = st.sidebar.radio(
        label="Source",
        options=["Todos", "> 60 años"],
        horizontal=True,
        label_visibility="collapsed",
    )
    if population == "Todos":
        data = get_data_all()
    elif population == "> 60 años":
        data = get_data_60plus()
    else:
        raise ValueError(f"Unknown population {population}.")

    start, end = data["fecha"].iloc[[0, -1]].dt.date

    start, end = st.slider(
        label="Intervalo",
        min_value=start,
        max_value=end,
        value=(start, end),
        label_visibility="collapsed",
    )

    break_down = st.sidebar.checkbox(label="Desglosar por")
    break_down_by = st.sidebar.radio(
        label="Desglosar por",
        options=["sexo", "grupo_edad"],
        horizontal=True,
        disabled=not break_down,
        label_visibility="collapsed",
    )

    if break_down:
        variable = st.sidebar.selectbox(
            label="Variable", options=["num_casos", "num_hosp", "num_uci", "num_def"]
        )
        data = (
            data.groupby(["fecha", break_down_by])[variable]
            .sum(numeric_only=False)
            .reset_index()
            .pivot(index="fecha", columns=break_down_by, values=variable)
            .loc[start:end]
        )
    else:
        variables = st.sidebar.multiselect(
            label="Variables", options=["num_casos", "num_hosp", "num_uci", "num_def"]
        )
        if not variables:
            st.error("Selecciona una o varias variables.")
            st.stop()
        data = data.groupby(["fecha"])[variables].sum(numeric_only=False).loc[start:end]

    chart_type = st.sidebar.radio(
        label="Tipo de gráfico", options=["Líneas", "Área", "Barras"], horizontal=True
    )

    chart_types = {
        "Líneas": st.line_chart,
        "Área": st.area_chart,
        "Barras": st.bar_chart,
    }
    chart_types[chart_type](data)
    st.dataframe(data)


@st.cache_resource
def get_data_60plus():
    path = "https://cnecovid.isciii.es/covid19/resources/casos_hosp_uci_def_sexo_edad_provres_60_mas.csv"
    data = pd.read_csv(path)
    data["fecha"] = pd.to_datetime(data["fecha"], format="%Y-%m-%d")
    data["provincia_iso"] = data["provincia_iso"].astype("category")
    data["sexo"] = data["sexo"].astype("category")
    data["grupo_edad"] = data["grupo_edad"].astype("category")
    return data


@st.cache_resource
def get_data_all():
    path1 = "https://cnecovid.isciii.es/covid19/resources/casos_hosp_uci_def_sexo_edad_provres.csv"
    path2 = "https://cnecovid.isciii.es/covid19/resources/hosp_uci_def_sexo_edad_provres_todas_edades.csv"
    data1 = data = pd.read_csv(path1)
    data2 = data = pd.read_csv(path2)
    data = pd.concat([data1, data2])
    data["fecha"] = pd.to_datetime(data["fecha"], format="%Y-%m-%d")
    data["provincia_iso"] = data["provincia_iso"].astype("category")
    data["sexo"] = data["sexo"].astype("category")
    data["grupo_edad"] = data["grupo_edad"].astype("category")
    return data


if __name__ == "__main__":
    main()
