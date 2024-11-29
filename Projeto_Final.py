import os
from llama_parse import LlamaParse
import pandas as pd
from io import StringIO
import re
import streamlit as st

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-26PEqrjdIHy5qULSYYkJP5OEm18faAvgZvihdqyxhG6xDI1r"

# Função de Extração
def extrair_tabelas_pdf(caminho_pdf):
    documentos = LlamaParse(result_type="markdown",
        language="pt",
        parsing_instruction="this file contains text and tables, I would like to get only the tables from the text."
    ).load_data(caminho_pdf)

    if not os.path.exists("meu_pdf"):
        os.makedirs("meu_pdf")

    for i, pagina in enumerate(documentos):
        with open(f"meu_pdf/pagina{i + 1}.md", "w", encoding="utf-8") as arquivo:
            arquivo.write(pagina.text)

# Função de Transformação
def transformar_markdown_excel(texto, num_pagina):
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

# Função de Processamento de Dados com Nome Dinâmico
def processar_pdfs(pasta_pdf=None, arquivo_pdf=None):
    if arquivo_pdf:  # Caso tenha sido passado um único arquivo PDF
        caminho_pdf = os.path.join(pasta_pdf, arquivo_pdf)  # Caminho completo do arquivo
        extrair_tabelas_pdf(caminho_pdf)
    elif pasta_pdf:  # Caso uma pasta inteira tenha sido fornecida
        arquivos_pdf = [f for f in os.listdir(pasta_pdf) if f.endswith('.pdf')]
        for arquivo in arquivos_pdf:
            caminho_pdf = os.path.join(pasta_pdf, arquivo)  # Caminho dinâmico para cada arquivo
            extrair_tabelas_pdf(caminho_pdf)

    # Converter markdown gerado em Excel
    pasta_markdown = "meu_pdf"
    if os.path.exists(pasta_markdown):
        for arquivo_md in os.listdir(pasta_markdown):
            if arquivo_md.endswith('.md'):
                with open(os.path.join(pasta_markdown, arquivo_md), "r", encoding="utf-8") as f:
                    texto = f.read()
                num_pagina = int(re.search(r"pagina(\d+)", arquivo_md).group(1))
                transformar_markdown_excel(texto, num_pagina)

# Função de Carregamento de Dados
def carregar_arquivos_excel(pasta: str):
    arquivos_excel = [f for f in os.listdir(pasta) if f.endswith('.xlsx')]
    dados = {}
    for arquivo in arquivos_excel:
        caminho_arquivo = os.path.join(pasta, arquivo)
        try:
            dados[arquivo] = pd.read_excel(caminho_arquivo, engine='openpyxl')
        except Exception as e:
            st.error(f"Erro ao carregar {arquivo}: {e}")
    return dados

# Função de Descarregamento de Dados
def limpar_pastas(*pastas):
    for pasta in pastas:
        if os.path.exists(pasta):
            for arquivo in os.listdir(pasta):
                caminho_arquivo = os.path.join(pasta, arquivo)
                try:
                    if os.path.isfile(caminho_arquivo):
                        os.remove(caminho_arquivo)
                except Exception as e:
                    st.error(f"Erro ao remover {arquivo} na pasta {pasta}: {e}")

# Interface Streamlit
st.sidebar.write("""
# Transforme suas Tabelas PDF em Tabelas Excel!  
""") # markdown

# Seleção de arquivos PDF em uma pasta local
pasta_pdf = st.sidebar.text_input("Caminho da pasta com arquivos PDF", value=os.getcwd())
if os.path.exists(pasta_pdf):
    arquivos_pdf = [f for f in os.listdir(pasta_pdf) if f.endswith('.pdf')]
    arquivo_selecionado = st.sidebar.selectbox("Selecione um arquivo PDF da pasta", arquivos_pdf)

# Botão para processar PDFs
if st.sidebar.button("Processar Arquivo PDF"):
    if arquivo_selecionado:  # Se o usuário selecionou um arquivo
        with st.spinner(f"Processando arquivo PDF: {arquivo_selecionado}..."):
            processar_pdfs(pasta_pdf=pasta_pdf, arquivo_pdf=arquivo_selecionado)  # Nome dinâmico
            st.sidebar.success(f"Processamento concluído para o arquivo: {arquivo_selecionado}")
    else:
        st.sidebar.warning("Por favor, faça upload ou selecione um arquivo PDF.")


# Exibição de tabelas Excel
st.write("""
# Llamma Convert - PDF to XLSX
""") # markdown
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

# Botão para limpar pastas
st.subheader("Excluir Tabelas Extraídas")
if st.button("Limpar Dados Processados"):
    limpar_pastas("meu_pdf", "saida_pdf")
    st.success("As pastas 'meu_pdf' e 'saida_pdf' foram limpas com sucesso!")
