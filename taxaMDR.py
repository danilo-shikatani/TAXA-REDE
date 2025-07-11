import streamlit as st
import pandas as pd
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# --- NOVA FUNÇÃO DE LIMPEZA INTELIGENTE ---
def limpar_e_converter_valor(valor):
    """
    Converte um valor para float de forma segura, lidando com números
    que já são numéricos ou textos formatados no padrão brasileiro.
    """
    # Se já for um número (int ou float), retorna ele mesmo.
    if isinstance(valor, (int, float)):
        return valor
    
    # Se for um texto, tenta limpar e converter.
    if isinstance(valor, str):
        try:
            # Remove pontos de milhar, depois troca a vírgula decimal por ponto
            valor_limpo = valor.replace('.', '').replace(',', '.')
            return float(valor_limpo)
        except (ValueError, TypeError):
            # Se a conversão falhar, retorna 0
            return 0.0
            
    # Se não for nem número nem texto, retorna 0
    return 0.0
# --- FIM DA FUNÇÃO ---


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
    dim_centro = pd.read_excel(uploaded_dim)
    dfato_rede = pd.read_excel(uploaded_dados)

    dfato_rede.columns = dfato_rede.iloc[0]
    dfato_rede = dfato_rede[1:].reset_index(drop=True)

    # --- CORREÇÃO PRINCIPAL APLICADA AQUI ---
    # Usamos a nova função inteligente para limpar e converter a coluna 'taxa'
    if 'taxa' in dfato_rede.columns:
        dfato_rede['taxa'] = dfato_rede['taxa'].apply(limpar_e_converter_valor)
    # --- FIM DA CORREÇÃO ---

    df_merged = dfato_rede.merge(dim_centro, on='CNPJ', how='left')
    df_merged = df_merged.groupby(['CENTRO DE CUSTO (NOVO)', 'Estabelecimento']).agg({'taxa': 'sum'}).reset_index()

    # Adicionar colunas fixas e as variáveis dos novos campos
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
    df_merged['CNPJ'] = '08845676000198'

    colunas_ordenadas = [
        'CNPJ', 'TipoCompra', 'Agregador', 'CNPJFornecedor', 'CodProduto', 'Quantidade',
        'taxa', 'PrevisaoEntrega', 'CENTRO DE CUSTO (NOVO)', 'ItemConta',
        'ClasseValor', 'Obs', 'VlrFrete', 'GrupoAprovacao'
    ]
    df_merged = df_merged[colunas_ordenadas]

    # --- EXIBIÇÃO E DOWNLOAD (com formatação brasileira) ---
    st.subheader("📋 Resultado Final")
    df_para_exibicao = df_merged.copy()
    df_para_exibicao['taxa'] = df_para_exibicao['taxa'].apply(lambda x: f"{x:_.2f}".replace('.', ',').replace('_', '.'))
    st.dataframe(df_para_exibicao, use_container_width=True)

    total_taxa = df_merged['taxa'].sum()
    total_formatado = f"R$ {total_taxa:_.2f}".replace('.', ',').replace('_', '.')
    st.metric("💰 Total Geral de Taxas", total_formatado)

    csv = df_para_exibicao.to_csv(index=False, sep=';', encoding='utf-8-sig')
    st.download_button("⬇️ Baixar CSV", data=csv, file_name='taxa_rede.csv', mime='text/csv')

else:
    st.info("⚠️ Envie os dois arquivos acima para processar os dados.")
