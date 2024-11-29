import streamlit as st 
import pandas as pd
import os

# criar funções de carregamento de dados
    # docs em xlsx da pasta saida.pdf 
def carregar_arquivos_excel(pasta: str):
    """
    Lista e carrega os arquivos Excel de uma pasta específica.

    Args:
        pasta (str): Caminho da pasta onde os arquivos Excel estão localizados.

    Returns:
        dict: Um dicionário com o nome dos arquivos como chaves e DataFrames como valores.
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

# criar a interface do streamlit
st.write("""
# Tabelas Geradas        
""") # markdown

# Configuração da pasta de saída
pasta_saida = "saida_pdf"

# Verificar se a pasta existe
if not os.path.exists(pasta_saida):
    st.error(f"A pasta '{pasta_saida}' não foi encontrada. Certifique-se de que ela existe e contém arquivos Excel.")
else:
    # Carregar os arquivos Excel
    tabelas = carregar_arquivos_excel(pasta_saida)
    
    if tabelas:
        st.success(f"Encontrados {len(tabelas)} arquivos Excel na pasta '{pasta_saida}'.")
        
        # Selecionar um arquivo para exibir
        arquivo_selecionado = st.selectbox("Escolha um arquivo para visualizar:", list(tabelas.keys()))
        
        if arquivo_selecionado:
            # Exibir o conteúdo do arquivo selecionado
            st.write(f"Exibindo o conteúdo do arquivo: **{arquivo_selecionado}**")
            st.dataframe(tabelas[arquivo_selecionado])

    else:
        st.warning(f"Nenhum arquivo Excel foi encontrado na pasta '{pasta_saida}'.")