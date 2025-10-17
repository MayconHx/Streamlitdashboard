import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Sensibilidade de Jogadores Profissionais de Overwatch",
        layout="wide"
)

@st.cache_data
def load_data():
    try:
        players = pd.read_csv("player_settings.csv")
        mouses = pd.read_csv("mouse_data.csv")
        roster = pd.read_csv("owl_roster.csv")
        return players, mouses, roster
    except FileNotFoundError as e:
        st.error(f"Erro ao carregar os dados: O arquivo {e.filename} não foi encontrado.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

players, mouses, roster = load_data()


st.title("Sensibilidade Overwatch Pro Players Dashboard")
st.markdown("### Análise de configurações e equipamentos de jogadores profissionais de Overwatch")


if not players.empty:

    players.columns = players.columns.str.strip().str.lower()

    st.header("📊 Estatísticas Gerais")
    st.markdown("Uma visão geral das configurações médias dos jogadores profissionais.")

    col1, col2, col3 = st.columns(3)

    with col1:
        avg_sens = players["sensitivity"].mean()
        st.metric("Média de Sensibilidade", f"{avg_sens:.2f}")

    with col2:

        avg_dpi = players["dpi"].mean()
        st.metric("Média de DPI", f"{avg_dpi:.0f}")

    with col3:
        if "cmper360" in players.columns:
            avg_cm360 = players["cmper360"].mean()
            st.metric("Média de cm/360", f"{avg_cm360:.2f} cm")
        else:
            st.metric("Média de cm/360", "N/A")

    st.markdown("---") 


    graph_col1, graph_col2 = st.columns(2)

    with graph_col1:
        st.subheader("📈 Distribuição da Sensibilidade")

        fig_hist = px.histogram(
            players,
            x="sensitivity",
            nbins=30,
            title="Distribuição da Sensibilidade dos Jogadores",
            labels={"sensitivity": "Sensibilidade", "count": "Quantidade de Jogadores"}
        )
        fig_hist.update_layout(bargap=0.1) 
        st.plotly_chart(fig_hist, use_container_width=True)

    with graph_col2:

        st.subheader("🖱️ Mouses Mais Usados")

        if "mousemodel" in players.columns:
            mouse_count = players["mousemodel"].value_counts().head(10).reset_index()
            mouse_count.columns = ["Modelo", "Quantidade"] 

            fig_bar = px.bar(
                mouse_count,
                x="Quantidade",
                y="Modelo",
                orientation='h',
                title="Top 10 Mouses Mais Usados",
                labels={"Quantidade": "Nº de Jogadores", "Modelo": "Modelo do Mouse"}
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("A coluna 'mousemodel' não foi encontrada no arquivo player_settings.csv.")

    st.markdown("---")

    new_graph_col1, new_graph_col2 = st.columns(2)

    with new_graph_col1:

        st.subheader("Sensibilidade Média por Função (Role)")
        if 'role' in players.columns and 'sensitivity' in players.columns:
            sensitivity_by_role = players.groupby('role')['sensitivity'].mean().reset_index()
            fig_role_sens = px.bar(
                sensitivity_by_role,
                x='role',
                y='sensitivity',
                title="Sensibilidade Média por Função",
                labels={'role': 'Função', 'sensitivity': 'Sensibilidade Média'},
                color='role',
                text_auto='.2f'
            )
            fig_role_sens.update_traces(textposition='outside')
            st.plotly_chart(fig_role_sens, use_container_width=True)
        else:
            st.warning("Colunas 'role' ou 'sensitivity' não encontradas.")

    with new_graph_col2:

        st.subheader(" Distribuição da Sensibilidade por Peso do Mouse")
        if 'mouseweight' in players.columns and 'sensitivity' in players.columns:

            box_data = players.dropna(subset=['mouseweight', 'sensitivity'])


            bins = [0, 70, 90, 110, float('inf')]
            labels = ['Super Leve (<70g)', 'Leve (70-89g)', 'Médio (90-109g)', 'Pesado (>=110g)']
            box_data['weight_category'] = pd.cut(box_data['mouseweight'], bins=bins, labels=labels, right=False)


            fig_box = px.box(
                box_data.sort_values('weight_category'),
                x="weight_category",
                y="sensitivity",
                title="Sensibilidade por Categoria de Peso do Mouse",
                labels={"weight_category": "Categoria de Peso do Mouse", "sensitivity": "Sensibilidade"},
                color="weight_category"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("Colunas 'mouseweight' ou 'sensitivity' não encontradas.")


    st.markdown("---")

    st.header("Filtro por Jogador")
    if "player" in players.columns:

        sorted_players = sorted(players["player"].unique())
        selected_player = st.selectbox("Selecione um jogador para ver seus detalhes:", sorted_players)


        player_info = players[players["player"] == selected_player]


        st.dataframe(player_info.style.hide(axis="index"))


    st.markdown("---")
    st.caption("Dados: Kaggle (Overwatch Pro Player Settings)")
else:
    st.warning("Não foi possível carregar os dados dos jogadores. Verifique se os arquivos CSV estão no lugar correto.")

