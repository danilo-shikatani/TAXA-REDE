import streamlit as st
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Relatório de Taxa Rede", layout="wide")
st.title("📊 Visualização de Taxa Rede - Pix Maio / Faturamento Junho 2025")

# Upload dos arquivos
st.subheader("📂 Envie os arquivos necessários")

uploaded_dim = st.file_uploader("1️⃣ Base de Centros de Custo (.xlsx)", type=["xlsx"], key="dim")
uploaded_dados = st.file_uploader("2️⃣  Relatorio REDE (.xlsx)", type=["xlsx"], key="dados")

if uploaded_dim and uploaded_dados:
    # Leitura dos arquivos
    dim_centro = pd.read_excel(uploaded_dim)
    dfato_rede = pd.read_excel(uploaded_dados)

    # Ajustar colunas e dados
    dfato_rede.columns = dfato_rede.iloc[0]
    dfato_rede = dfato_rede[1:].reset_index(drop=True)

    # Merge com base no CNPJ
    df_merged = dfato_rede.merge(dim_centro, on='CNPJ', how='left')

    # Agrupamento por centro e estabelecimento
    df_merged = df_merged.groupby(['CENTRO DE CUSTO (NOVO)', 'Estabelecimento']).agg({'taxa': 'sum'}).reset_index()

    # Adicionar colunas fixas
    df_merged['TipoCompra'] = '4'
    df_merged['Agregador'] = '001'
    df_merged['CNPJFornecedor'] = '33264655000126'
    df_merged['CodProduto'] = '06000004'
    df_merged['Quantidade'] = '1'
    df_merged['PrevisaoEntrega'] = 'inserir data'
    df_merged['ItemConta'] = '103'
    df_merged['ClasseValor'] = '81000'
    df_merged['Obs'] = 'Observação padrão'  # <- Ajuste aqui se quiser outra coisa
    df_merged['VlrFrete'] = '0'
    df_merged['GrupoAprovacao'] = 'PC0012'
    df_merged['CNPJ'] = '08845676000198'

    # Reordenar colunas
    colunas_ordenadas = [
        'CNPJ', 'TipoCompra', 'Agregador', 'CNPJFornecedor', 'CodProduto', 'Quantidade',
        'taxa', 'PrevisaoEntrega', 'CENTRO DE CUSTO (NOVO)', 'ItemConta',
        'ClasseValor', 'Obs', 'VlrFrete', 'GrupoAprovacao'
    ]

    df_merged = df_merged[colunas_ordenadas]

    # Exibir resultado
    st.subheader("📋 Resultado Final")
    st.dataframe(df_merged, use_container_width=True)

    # Totais
    total_taxa = df_merged['taxa'].sum()
    st.metric("💰 Total Geral de Taxas", f"R$ {total_taxa:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','))

else:
    st.info("⚠️ Envie os dois arquivos acima para processar os dados.")
