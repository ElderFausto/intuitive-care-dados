import pdfplumber
import pandas as pd
import os
from zipfile import ZipFile, ZIP_DEFLATED

# CONFIGURAÇÕES
INPUT_FILE = os.path.join("inputs", "teste_1", "Anexo_I.pdf")
OUTPUT_DIR = os.path.join("outputs", "teste_2")
CSV_FILENAME = "Rol_Procedimentos.csv"
ZIP_FILENAME = "Teste_Elder_Fausto.zip"

# Legendas do rodape completa
REPLACES = {
    "OD": "Seg. Odontológica",
    "AMB": "Seg. Ambulatorial"
}

# Cria pasta de output se não existir
def setup_output():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
# Extrai tabela do PDF
def extract_table_from_pdf(pdf_path):
    print(f"📄 Lendo PDF: {pdf_path}")
    all_data = []
    
    # Itera sobre todas as páginas do PDF
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                print(f"   - Processando página {i + 1}/{total_pages}...", end="\r")
                table = page.extract_table()
                
                if table:
                    # remove linhas que sejam totalmente vazias ou nulas
                    clean_table = [row for row in table if any(row)]
                    
                    if not clean_table:
                        continue

                    if not all_data:
                        all_data.extend(clean_table)
                    else:
                        # Se o cabeçalho se repetir, pula
                        if clean_table[0] == all_data[0]:
                            all_data.extend(clean_table[1:])
                        else:
                            all_data.extend(clean_table)
                            
        print(f"\n✅ Extração concluída! Total de linhas: {len(all_data)}")
        return all_data
    except Exception as e:
        print(f"\n❌ Erro ao ler PDF: {e}")
        return []

# Transforma dados brutos em DataFrame limpo
def transform_data(raw_data):
    if not raw_data:
        return None

    print("🔄 Transformando dados...")
    
    # DataFrame inicial com o cabeçalho
    header = raw_data[0]
    # remove quebras de linha e espaços)
    header = [str(h).replace('\n', ' ').strip() if h else f"col_{i}" for i, h in enumerate(header)]
    
    data = raw_data[1:]
    df = pd.DataFrame(data, columns=header)
    
    # Normaliza todo o texto do DF (Upper case e trim) para garantir o match
    print("   - Limpando textos e aplicando legenda...")
    
    for col in df.columns:
        # Converte para string para poder usar métodos de string
        df[col] = df[col].astype(str).str.strip()
        
        
        for sigla, descricao in REPLACES.items():
            # Substitui valores exatos
            df[col] = df[col].replace(f"^{sigla}$", descricao, regex=True)

    return df
  
# Salva DataFrame em CSV e compacta em ZIP
def save_to_csv_and_zip(df):
    if df is None: return

    csv_path = os.path.join(OUTPUT_DIR, CSV_FILENAME)
    zip_path = os.path.join(OUTPUT_DIR, ZIP_FILENAME)
    
    try:
        print(f"💾 Salvando CSV...")
        df.to_csv(csv_path, index=False, sep=';', encoding='utf-8-sig')
        
        print(f"📦 Compactando ZIP...")
        with ZipFile(zip_path, 'w', ZIP_DEFLATED) as zf:
            zf.write(csv_path, arcname=CSV_FILENAME)
        print("🚀 Sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")

def main():
    setup_output()
    raw_data = extract_table_from_pdf(INPUT_FILE)
    df_clean = transform_data(raw_data)
    save_to_csv_and_zip(df_clean)

if __name__ == "__main__":
    main()