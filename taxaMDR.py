import streamlit as st
import pandas as pd
import warnings
from datetime import datetime
import re

warnings.filterwarnings('ignore')

# --- FUNÇÃO DE LIMPEZA DE VALORES (sem alterações) ---
def limpar_e_converter_valor(valor):
    if isinstance(valor, (int, float)):
        return float(valor)
    if not isinstance(valor, str):
        return 0.0
    s = valor.strip()
    if not s:
        return 0.0
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Relatório de Taxa Rede", layout="wide")
st.title("📊 Visualização de Taxa Rede - Pix ")

# --- CAMPOS INTERATIVOS ---
st.subheader("📝 Parâmetros da Saída")
col1, col2 = st.columns(2)
with col1:
    previsao_entrega_input = st.date_input("1️⃣ Selecione a Previsão de Entrega", value=datetime.today())
with col2:
    obs_input = st.text_input("2️⃣ Digite a Observação para o arquivo final", value="Taxas Rede PIX referente ao período")

# --- UPLOAD DOS ARQUIVOS ---
st.subheader("📂 Envie os arquivos necessários")
col1_upload, col2_upload = st.columns(2)
with col1_upload:
    uploaded_dim = st.file_uploader("1️⃣ Base de Centros de Custo (.xlsx)", type=["xlsx"], key="dim")
with col2_upload:
    uploaded_dados = st.file_uploader("2️⃣ Relatorio REDE (.xlsx)", type=["xlsx"], key="dados")


if uploaded_dim and uploaded_dados:
    # --- LEITURA E PROCESSAMENTO ---
    dim_centro = pd.read_excel(uploaded_dim)
    dfato_rede = pd.read_excel(uploaded_dados)

    dfato_rede.columns = dfato_rede.iloc[0]
    dfato_rede = dfato_rede[1:].reset_index(drop=True)

    if 'VlrUnitario' in dfato_rede.columns:
        dfato_rede['VlrUnitario'] = dfato_rede['VlrUnitario'].apply(limpar_e_converter_valor)

    df_merged = dfato_rede.merge(dim_centro, on='CNPJ', how='left')
    
    df_merged = df_merged.groupby(['CENTRO DE CUSTO (NOVO)', 'Estabelecimento']).agg({'VlrUnitario': 'sum'}).reset_index()

    # <<< ALTERAÇÃO 1: RENOMEANDO A COLUNA >>>
    df_merged.rename(columns={'CENTRO DE CUSTO (NOVO)': 'CodCentroCustos'}, inplace=True)

    # Adicionar colunas
    df_merged['TipoCompra'] = '04'
    df_merged['Agregador'] = '001'
    df_merged['CNPJFornecedor'] = '33264655000126'
    df_merged['CodProduto'] = '06000004'
    df_merged['Quantidade'] = '1'
    df_merged['PrevisaoEntrega'] = previsao_entrega_input.strftime('%d/%m/%Y')
    df_merged['ItemConta'] = '103'
    df_merged['ClasseValor'] = '81000'
    df_merged['Obs'] = obs_input
    df_merged['VlrFrete'] = '0'
    df_merged['GrupoAprovacao'] = 'PC0012'
    df_merged['CNPJNotaFiscal'] = '08845676000198'

    # Reordenar colunas, agora com o novo nome 'CodCentroCustos'
    colunas_ordenadas = [
        'CNPJNotaFiscal', 'TipoCompra', 'Agregador', 'CNPJFornecedor', 'CodProduto', 'Quantidade',
        'VlrUnitario', 'PrevisaoEntrega', 'CodCentroCustos', 'ItemConta', # <<< Nome da coluna atualizado aqui
        'ClasseValor', 'Obs', 'VlrFrete', 'GrupoAprovacao'
    ]
    df_merged = df_merged[colunas_ordenadas]

    # --- EXIBIÇÃO E DOWNLOAD ---
    st.subheader("📋 Resultado Final")
    
    df_para_exibicao = df_merged.copy()
    df_para_exibicao['VlrUnitario'] = df_para_exibicao['VlrUnitario'].apply(
        lambda x: f"{x:_.2f}".replace('.', ',').replace('_', '.')
    )
    st.dataframe(df_para_exibicao, use_container_width=True)

    total_vlr_unitario = df_merged['VlrUnitario'].sum()
    total_formatado = f"R$ {total_vlr_unitario:_.2f}".replace('.', ',').replace('_', '.')
    st.metric("💰 Total Geral (Vlr. Unitário)", total_formatado)

    # <<< ALTERAÇÃO 2: OPÇÕES DE DOWNLOAD XML E CSV >>>
    st.subheader("⬇️ Download")
    col_download1, col_download2 = st.columns(2)

    with col_download1:
        # --- GERAÇÃO DO XML ---
        df_para_xml = df_merged.copy()
        df_para_xml.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', col) for col in df_para_xml.columns]
        xml_string = df_para_xml.to_xml(
            index=False,
            root_name='PedidosDeCompra',
            row_name='Pedido',
            encoding='utf-8'
        )
        st.download_button(
            label="Baixar XML de Pedidos",
            data=xml_string,
            file_name='pedidos_de_compra.xml',
            mime='application/xml'
        )

    with col_download2:
        # --- GERAÇÃO DO CSV ---
        # Usamos o df_para_exibicao para manter a formatação de número brasileira
        csv = df_para_exibicao.to_csv(index=False, sep=';', encoding='utf-8-sig')
        st.download_button(
            label="Baixar CSV de Pedidos",
            data=csv,
            file_name='pedidos_de_compra.csv',
            mime='text/csv'
        )

else:
    st.info("⚠️ Envie os dois arquivos acima para processar os dados.")
