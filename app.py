import streamlit as st
import pandas as pd

# --- FUNCIONES DE LAS PÁGINAS ---

def pagina_explorar():
    st.title("Explorar los datos")

    # R1: Cargar datos
    archivo = st.file_uploader("Selecciona bicicletas_listas.csv", type=["csv"])
    if st.button("Cargar datos") and archivo is not None:
        df = pd.read_csv(archivo, encoding="utf-8-sig", parse_dates=["fecha"])
        st.session_state["datos"] = df
        st.success(f"{len(df):,} registros cargados.")

    if "datos" not in st.session_state:
        st.info("Sube el archivo CSV y presiona 'Cargar datos' para comenzar.")
        return

    df_filtrado = aplicar_filtros()

    # R4: Dos indicadores
    c1, c2 = st.columns(2)
    c1.metric("Total de alquileres", f"{df_filtrado['alquileres'].sum():,}".replace(",", "."))
    c2.metric("Promedio por hora observada", f"{df_filtrado['alquileres'].mean():.1f}".replace(".", ","))

    # R2: Dos pestañas
    tab1, tab2 = st.tabs(["Gráfico diario", "Datos"])

    with tab1:
        diario = df_filtrado.groupby("fecha")["alquileres"].sum()
        st.line_chart(diario, x_label="Fecha", y_label="Alquileres por día")

    with tab2:
        # R5: Tabla, descarga y enlace
        st.dataframe(df_filtrado)
        csv = df_filtrado.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Descargar datos filtrados", csv, "datos_filtrados.csv", "text/csv")
        st.write("Fanaee-T, H. (2013). Bike Sharing. UCI. DOI 10.24432/C5W894. CC BY 4.0.")
        st.link_button("Consultar la fuente en UCI", "https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset")


def pagina_comparar():
    st.title("Comparar horarios")

    if "datos" not in st.session_state:
        st.info("Primero carga los datos en la página 'Explorar los datos'.")
        return

    df_filtrado = aplicar_filtros()

    # R6: Gráfico de barras, color y tabla
    color = st.color_picker("Color de las barras", "#197A8D")
    promedios = df_filtrado.groupby("hora")["alquileres"].mean()
    st.bar_chart(promedios, color=color, x_label="Hora del día", y_label="Alquileres por hora observada")

    if st.checkbox("Mostrar tabla de promedios"):
        st.dataframe(promedios.reset_index())

    # R7: Límite numérico
    limite = st.number_input("Límite de alquileres por hora", value=250)
    superan = promedios[promedios > limite]

    st.metric("Horarios con promedio mayor que el límite", f"{len(superan)}/{len(promedios)}")
    lista_horas = ", ".join([f"{h:02d}:00" for h in superan.index])
    st.write(f"Horarios: {lista_horas}.")


def aplicar_filtros():
    df = st.session_state["datos"].copy()

    if dia != "Todos":
        df = df[df["tipo_dia"] == dia]

    df = df[(df["hora"] >= horas[0]) & (df["hora"] <= horas[1])]

    if usuario == "Todos":
        df["alquileres"] = df["alquileres_total"]
    elif usuario == "Ocasionales":
        df["alquileres"] = df["alquileres_ocasionales"]
    else:
        df["alquileres"] = df["alquileres_registrados"]

    return df


# --- ESTRUCTURA PRINCIPAL Y BARRA LATERAL ---

st.sidebar.title("BiciDatos")

# R2: Navegación usando funciones en vez de archivos
nav = st.navigation([
    st.Page(pagina_explorar, title="Explorar los datos", default=True),
    st.Page(pagina_comparar, title="Comparar horarios")
])

# R3: Tres filtros compartidos
usuario = st.sidebar.selectbox("Tipo de usuario", ["Todos", "Ocasionales", "Registrados"])
dia = st.sidebar.radio("Tipo de día", ["Todos", "Laborable", "No laborable"])
horas = st.sidebar.slider("Horas del día", 0, 23, (0, 23))

nav.run()
