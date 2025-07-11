import streamlit as st
import pandas as pd
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Relatório de Taxa Rede", layout="wide")
st.title("📊 Visualização de Taxa Rede - Pix ")

# --- NOVOS CAMPOS INTERATIVOS ---
st.subheader("📝 Parâmetros da Saída")
col1, col2 = st.columns(2)

with col1:
    # Campo de data com calendário
    previsao_entrega_input = st.date_input(
        "1️⃣ Selecione a Previsão de Entrega",
        value=datetime.today() # Sugere a data de hoje como padrão
    )

with col2:
    # Campo de texto para observação
    obs_input = st.text_input(
        "2️⃣ Digite a Observação para o arquivo final",
        value="Taxas Rede PIX referente ao período" # Sugestão de texto padrão
    )
# --- FIM DA NOVA SEÇÃO ---


# Upload dos arquivos
st.subheader("📂 Envie os arquivos necessários")
col1_upload, col2_upload = st.columns(2)

with col1_upload:
    uploaded_dim = st.file_uploader("1️⃣ Base de Centros de Custo (.xlsx)", type=["xlsx"], key="dim")

with col2_upload:
    uploaded_dados = st.file_uploader("2️⃣ Relatorio REDE (.xlsx)", type=["xlsx"], key="dados")


if uploaded_dim and uploaded_dados:
    # Leitura dos arquivos
    dim_centro = pd.read_excel(uploaded_dim)
    dfato_rede = pd.read_excel(uploaded_dados)

    # Ajustar colunas e dados
    dfato_rede.columns = dfato_rede.iloc[0]
    dfato_rede = dfato_rede[1:].reset_index(drop=True)

    # --- CORREÇÃO DA SOMA DA TAXA ---
    # Garante que a coluna 'taxa' seja numérica antes de qualquer operação
    # Esta é a correção para o problema da soma
    if 'taxa' in dfato_rede.columns:
        # Converte para texto, remove pontos (milhar) e troca vírgula (decimal) por ponto
        dfato_rede['taxa'] = dfato_rede['taxa'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        # Converte a coluna limpa para o tipo numérico (float)
        dfato_rede['taxa'] = pd.to_numeric(dfato_rede['taxa'], errors='coerce').fillna(0)
    # --- FIM DA CORREÇÃO ---


    # Merge com base no CNPJ
    df_merged = dfato_rede.merge(dim_centro, on='CNPJ', how='left')

    # Agrupamento por centro e estabelecimento
    # Agora a soma funcionará corretamente
    df_merged = df_merged.groupby(['CENTRO DE CUSTO (NOVO)', 'Estabelecimento']).agg({'taxa': 'sum'}).reset_index()

    # Adicionar colunas fixas e as variáveis dos novos campos
    df_merged['TipoCompra'] = '04'
    df_merged['Agregador'] = '001'
    df_merged['CNPJFornecedor'] = '33264655000126'
    df_merged['CodProduto'] = '06000004'
    df_merged['Quantidade'] = '1'
    df_merged['PrevisaoEntrega'] = previsao_entrega_input.strftime('%d/%m/%Y') # Usa a data selecionada
    df_merged['ItemConta'] = '103'
    df_merged['ClasseValor'] = '81000'
    df_merged['Obs'] = obs_input # Usa a observação digitada
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
    st.metric("💰 Total Geral de Taxas", f"R$ {total_taxa:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')) # Formatação para o padrão brasileiro

    # Botão para download em CSV
    csv = df_merged.to_csv(index=False, sep=';', encoding='utf-8-sig', decimal=',') # Adicionado decimal=',' para o Excel entender corretamente
    st.download_button(
        label="⬇️ Baixar CSV",
        data=csv,
        file_name='taxa_rede.csv',
        mime='text/csv'
    )

else:
    st.info("⚠️ Envie os dois arquivos acima para processar os dados.")
