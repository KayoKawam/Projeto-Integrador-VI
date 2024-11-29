import os
from llama_parse import LlamaParse
import pandas as pd
from io import StringIO
import re

import streamlit as st

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-26PEqrjdIHy5qULSYYkJP5OEm18faAvgZvihdqyxhG6xDI1r"

# Funções auxiliares
def extrair_tabelas_pdf(caminho_pdf):
    """
    Extrai tabelas de um PDF usando LlamaParse e salva como arquivos markdown na pasta 'meu_pdf'.
    """
    documentos = LlamaParse(result_type="markdown",
        language="pt",
        parsing_instruction="this file contains text and tables, I would like to get only the tables from the text."
    ).load_data(caminho_pdf)

    if not os.path.exists("meu_pdf"):
        os.makedirs("meu_pdf")

    for i, pagina in enumerate(documentos):
        with open(f"meu_pdf/pagina{i + 1}.md", "w", encoding="utf-8") as arquivo:
            arquivo.write(pagina.text)

def transformar_markdown_excel(texto, num_pagina):
    """
    Converte tabelas em markdown para arquivos Excel e salva na pasta 'saida_pdf'.
    """
    def tratar_tabelas_texto(texto):
        regra_busca_regex = re.compile(r"((?:\|.+\|(?:\n|\r))+)", re.MULTILINE)
        return regra_busca_regex.findall(texto)

    lista_texto_tabelas = tratar_tabelas_texto(texto)
    if not os.path.exists("saida_pdf"):
        os.makedirs("saida_pdf")

    for i, texto_tabela in enumerate(lista_texto_tabelas):
        tabela = pd.read_csv(StringIO(texto_tabela), sep="|", encoding="utf-8", engine="python")
        tabela = tabela.dropna(how="all", axis=1).dropna(how="all", axis=0)
        tabela.to_excel(f"saida_pdf/Pagina{num_pagina}Tabela{i + 1}.xlsx", index=False)

def processar_pdfs(pasta_pdf=None, arquivo_pdf=None):
    """
    Processa PDFs de uma pasta ou de um arquivo específico.
    """
    if arquivo_pdf:
        caminho_pdf = arquivo_pdf.name
        extrair_tabelas_pdf(caminho_pdf)
    elif pasta_pdf:
        arquivos_pdf = [f for f in os.listdir(pasta_pdf) if f.endswith('.pdf')]
        for arquivo in arquivos_pdf:
            extrair_tabelas_pdf(os.path.join(pasta_pdf, arquivo))

    # Converter markdown gerado em Excel
    pasta_markdown = "meu_pdf"
    if os.path.exists(pasta_markdown):
        for arquivo_md in os.listdir(pasta_markdown):
            if arquivo_md.endswith('.md'):
                with open(os.path.join(pasta_markdown, arquivo_md), "r", encoding="utf-8") as f:
                    texto = f.read()
                num_pagina = int(re.search(r"pagina(\d+)", arquivo_md).group(1))
                transformar_markdown_excel(texto, num_pagina)

def carregar_arquivos_excel(pasta: str):
    """
    Lista e carrega os arquivos Excel de uma pasta específica.
    """
    arquivos_excel = [f for f in os.listdir(pasta) if f.endswith('.xlsx')]
    dados = {}
    for arquivo in arquivos_excel:
        caminho_arquivo = os.path.join(pasta, arquivo)
        try:
            dados[arquivo] = pd.read_excel(caminho_arquivo, engine='openpyxl')
        except Exception as e:
            st.error(f"Erro ao carregar {arquivo}: {e}")
    return dados

# Interface Streamlit
st.title("Transformador de Tabelas PDF em Tabelas Excel")

# Opção 1: Upload de arquivo PDF
uploaded_file = st.file_uploader("Faça upload de um arquivo PDF", type=["pdf"])

# Botão para processar PDFs
if st.button("Processar Arquivo PDF"):
    if uploaded_file:
        with st.spinner("Processando arquivo PDF carregado..."):
            processar_pdfs(arquivo_pdf=uploaded_file)
            st.success("Processamento concluído!")
    else:
        st.warning("Por favor, faça upload ou selecione um arquivo PDF.")

# Exibição de tabelas Excel
st.subheader("Visualização de Tabelas Excel Extraídas")
pasta_saida = "saida_pdf"
if os.path.exists(pasta_saida):
    tabelas = carregar_arquivos_excel(pasta_saida)
    if tabelas:
        st.success(f"Encontrados {len(tabelas)} arquivos Excel na pasta '{pasta_saida}'.")
        arquivo_excel = st.selectbox("Escolha um arquivo para visualizar:", list(tabelas.keys()))
        if arquivo_excel:
            st.write(f"Exibindo o conteúdo do arquivo: **{arquivo_excel}**")
            st.dataframe(tabelas[arquivo_excel])
    else:
        st.warning("Nenhum arquivo Excel foi encontrado na pasta 'saida_pdf'.")
else:
    st.error(f"A pasta '{pasta_saida}' não foi encontrada.")