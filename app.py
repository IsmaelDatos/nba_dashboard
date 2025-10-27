import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NBA Dashboard", layout="wide")

# -------------------------------
# Cargar datos
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/nba_all_elo.csv")
    df = df.rename(columns={
        "year_id": "season",
        "team_id": "team",
        "date_game": "game_date"
    })
    # Convertir fecha
    df["game_date"] = pd.to_datetime(df["game_date"])
    # Columna tipo de juego
    df["type"] = df["is_playoffs"].apply(lambda x: "Playoffs" if x == 1 else "Temporada regular")
    return df

df = load_data()

# -------------------------------
# Barra lateral
# -------------------------------
st.sidebar.header("⚙️ Filtros")

years = sorted(df["season"].unique())
selected_year = st.sidebar.selectbox("Selecciona un año:", years, index=len(years)-1)

teams = sorted(df["team"].unique())
selected_team = st.sidebar.selectbox("Selecciona un equipo:", teams)

game_type = st.sidebar.pills(
    "Selecciona tipo de juego:",
    options=["Temporada regular", "Playoffs", "Ambos"],
    default="Ambos"
)

# -------------------------------
# Filtrar datos
# -------------------------------
df_filtered = df[df["season"] == selected_year]
if game_type != "Ambos":
    df_filtered = df_filtered[df_filtered["type"] == game_type]
df_filtered = df_filtered[df_filtered["team"] == selected_team].sort_values("game_date")

# -------------------------------
# Gráficas
# -------------------------------
st.title("🏀 Dashboard NBA")

if df_filtered.empty:
    st.warning("No hay datos para los filtros seleccionados.")
else:
    df_filtered["Ganados"] = (df_filtered["game_result"] == "W").cumsum()
    df_filtered["Perdidos"] = (df_filtered["game_result"] == "L").cumsum()

    # --- Gráfica de líneas ---
    fig_lineas = px.line(
        df_filtered,
        x="game_date",
        y=["Ganados", "Perdidos"],
        labels={"value": "Acumulado", "game_date": "Fecha"},
        title=f"Evolución de juegos ganados y perdidos ({selected_team}, {selected_year})"
    )
    st.plotly_chart(fig_lineas, use_container_width=True)

    # --- Gráfica de pastel ---
    total_ganados = (df_filtered["game_result"] == "W").sum()
    total_perdidos = (df_filtered["game_result"] == "L").sum()

    fig_pie = px.pie(
        names=["Ganados", "Perdidos"],
        values=[total_ganados, total_perdidos],
        title="Porcentaje de juegos ganados y perdidos"
    )
    st.plotly_chart(fig_pie, use_container_width=True)
