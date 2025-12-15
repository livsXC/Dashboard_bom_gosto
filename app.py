import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard Financeiro da Quitanda",
    page_icon="💰",
    layout="wide",
)

# --- Carregamento dos dados ---
df = pd.read_csv("dados_quitanda.csv")

# --- Conversão das colunas numéricas ---
# Remove possíveis símbolos de moeda e vírgulas, depois converte para float
df['receita'] = (
    df['receita']
    .astype(str)
    .str.replace("R\$", "", regex=True)
    .str.replace(",", ".")
    .str.strip()
)
df['despesa'] = (
    df['despesa']
    .astype(str)
    .str.replace("R\$", "", regex=True)
    .str.replace(",", ".")
    .str.strip()
)

# Converte para numérico (float), valores inválidos viram NaN
df['receita'] = pd.to_numeric(df['receita'], errors='coerce')
df['despesa'] = pd.to_numeric(df['despesa'], errors='coerce')

# --- Ajuste da ordem dos meses ---
ordem_meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]
df['mes'] = pd.Categorical(df['mes'], categories=ordem_meses, ordered=True)

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

meses_disponiveis = ordem_meses
meses_selecionados = st.sidebar.multiselect("Mês", meses_disponiveis, default=meses_disponiveis)

semanas_disponiveis = sorted(df['semana'].unique())
semanas_selecionadas = st.sidebar.multiselect("Semana", semanas_disponiveis, default=semanas_disponiveis)

produtos_disponiveis = sorted(df['produto'].unique())
produtos_selecionados = st.sidebar.multiselect("Produto", produtos_disponiveis, default=produtos_disponiveis)

formas_pagamento = sorted(
    [fp for fp in df['forma_pagamento'].astype(str).unique() if fp.strip() != "" and fp.lower() != "nan"]
)
formas_selecionadas = st.sidebar.multiselect("Forma de Pagamento", formas_pagamento, default=formas_pagamento )

# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['mes'].isin(meses_selecionados)) &
    (df['semana'].isin(semanas_selecionadas)) &
    (df['produto'].isin(produtos_selecionados)) &
    (df['forma_pagamento'].isin(formas_selecionadas))
]

# --- Conteúdo Principal ---
st.image("logo_quitanda.png", width=150)
st.title("Dashboard Bom Gosto")
st.markdown("Acompanhe receitas, despesas e lucros semanais e mensais. Use os filtros à esquerda.")

# --- KPIs ---
st.subheader("Métricas Gerais")

if not df_filtrado.empty:
    receita_total = df_filtrado['receita'].sum()
    despesa_total = df_filtrado['despesa'].sum()
    lucro_liquido = receita_total - despesa_total
    ticket_medio = df_filtrado['receita'].mean()
else:
    receita_total, despesa_total, lucro_liquido, ticket_medio, produto_mais_vendido = 0, 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Receita Total", f"R${receita_total:,.2f}")
col2.metric("Despesa Total", f"R${despesa_total:,.2f}")
col3.metric("Lucro Líquido", f"R${lucro_liquido:,.2f}")
col4.metric("Produto mais vendido", produto_mais_vendido)

st.markdown("---")


# --- Gráficos ---
st.subheader("Gráficos Financeiros")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        receita_por_produto = df_filtrado.groupby('produto')['receita'].sum().reset_index()
        grafico_receita = px.bar(
            receita_por_produto,
            x='produto',
            y='receita',
            title="Receita por Produto",
            labels={'receita': 'Receita (R$)', 'produto': 'Produto'},
            color_discrete_sequence=["#2ecc71", "#27ae60", "#1abc9c", "#16a085"]
        )
        st.plotly_chart(grafico_receita, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de receita por produto.")

with col_graf2:
    if not df_filtrado.empty:
        lucro_mensal = df_filtrado.groupby('mes').apply(lambda x: x['receita'].sum() - x['despesa'].sum()).reset_index()
        lucro_mensal.columns = ['mes', 'lucro']
        grafico_lucro = px.line(
            lucro_mensal.sort_values('mes'),
            x='mes',
            y='lucro',
            title="Lucro Mensal",
            labels={'lucro': 'Lucro (R$)', 'mes': 'Mês'},
            color_discrete_sequence=["#2ecc71"]
        )
        st.plotly_chart(grafico_lucro, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de lucro mensal.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        grafico_pagamento = px.pie(
            df_filtrado,
            names='forma_pagamento',
            values='receita',
            title='Proporção das Formas de Pagamento',
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.Greens
        )
        grafico_pagamento.update_traces(textinfo='percent+label')
        st.plotly_chart(grafico_pagamento, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de formas de pagamento.")

with col_graf4:
    if not df_filtrado.empty:
        receita_semanal = df_filtrado.groupby('semana')['receita'].sum().reset_index()
        receita_semanal = receita_semanal.sort_values('semana')
        grafico_semana = px.bar(
            receita_semanal,
            x='semana',
            y='receita',
            title="Receita Semanal",
            labels={'receita': 'Receita (R$)', 'semana': 'Semana'},
            color_discrete_sequence=["#2ecc71", "#27ae60", "#1abc9c", "#16a085"]
        )
        st.plotly_chart(grafico_semana, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico semanal.")

# --- Gráfico por Categoria ---
st.subheader("Comparativo por Categoria")

if not df_filtrado.empty:
    receita_por_categoria = df_filtrado.groupby('categoria')['receita'].sum().reset_index()
    grafico_categoria = px.bar(
        receita_por_categoria,
        x='categoria',
        y='receita',
        title="Receita por Categoria",
        labels={'receita': 'Receita (R$)', 'categoria': 'Categoria'},
        color='categoria',
        color_discrete_sequence=["#2ecc71", "#27ae60", "#1abc9c", "#16a085"]
    )
    st.plotly_chart(grafico_categoria, use_container_width=True)
else:
    st.warning("Nenhum dado para exibir no gráfico por categoria.")

# --- Sugestão 3: Gráfico de tendência acumulada ---
st.subheader("📈 Tendência Acumulada de Receita")

if not df_filtrado.empty:
    receita_acumulada = df_filtrado.groupby('mes')['receita'].sum().cumsum().reset_index()
    receita_acumulada.columns = ['mes', 'receita_acumulada']

    grafico_tendencia = px.line(
        receita_acumulada,
        x='mes',
        y='receita_acumulada',
        title="Receita Acumulada ao Longo do Ano",
        labels={'receita_acumulada': 'Receita Acumulada (R$)', 'mes': 'Mês'},
        markers=True,
        color_discrete_sequence=["#2ecc71"]
    )
    st.plotly_chart(grafico_tendencia, use_container_width=True)
else:
    st.markdown(
        """
        <div style="background-color:#4CAF50; padding:10px; border-radius:8px; color:white;">
            Nenhum dado para exibir na tendência acumulada.
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Tabela de Dados Detalhados ---
st.markdown("---")
st.subheader("📦 Produtos por Categoria")

# Lista de categorias válidas (exclui despesas)
categorias = df_filtrado['categoria'].dropna().unique()
categorias = [cat for cat in categorias if cat != 'Despesa']

# Exibe duas tabelas por linha
for i in range(0, len(categorias), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j < len(categorias):
            categoria = categorias[i + j]
            df_cat = df_filtrado[df_filtrado['categoria'] == categoria][['produto', 'quantidade', 'receita', 'forma_pagamento']]
            df_cat = df_cat.dropna(subset=['produto'])
            with cols[j]:
                st.markdown(f"#### {categoria}")
                st.dataframe(df_cat, use_container_width=True, height=250)

# --- Sugestão 4: Exportação de dados filtrados ---
st.subheader("📥 Exportar Dados")
if not df_filtrado.empty:
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Baixar dados filtrados em CSV",
        data=csv,
        file_name="dados_filtrados.csv",
        mime="text/csv",
    )
else:
    st.markdown(
        """
        <div style="background-color:#4CAF50; padding:10px; border-radius:8px; color:white;">
            Nenhum dado disponível para exportação.
        </div>
        """,
        unsafe_allow_html=True
    )

