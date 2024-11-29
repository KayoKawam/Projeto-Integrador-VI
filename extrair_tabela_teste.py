import os

os.environ["LLAMA_CLOUD_API_KEY"] = "llx-26PEqrjdIHy5qULSYYkJP5OEm18faAvgZvihdqyxhG6xDI1r"

from llama_parse import LlamaParse

documentos = LlamaParse(result_type="markdown", 
                        language= "pt",
                        parsing_instruction="this file contains text and tables, I would like to get only the tables from the text.").load_data("resultado.pdf")

print(len(documentos))

if not os.path.exists("./saida_pdf"):
    os.makedirs("./saida_pdf")

for i, pagina in enumerate(documentos):
    with open(f"meu_pdf/pagina{i+1}.md", "w", encoding="utf-8") as arquivo:
        arquivo.write(pagina.text)
    