import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
import urllib3

# Desabilita avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIGURAÇÕES
URL_CONTABIL = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
URL_OPERADORAS = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"
INPUT_DIR = os.path.join("inputs", "teste_3")
ACCOUNTING_DIR = os.path.join(INPUT_DIR, "demonstracoes_contabeis")

# Anos alvo
TARGET_YEARS = ["2023", "2024"]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def setup_directories():
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
    if not os.path.exists(ACCOUNTING_DIR):
        os.makedirs(ACCOUNTING_DIR)

def sanitize_csv(filepath):
    """
    Lê o CSV baixado, troca vírgula por ponto nas colunas de valor
    e salva novamente em UTF-8 para o Banco aceitar.
    """
    print(f"   🔧 Corrigindo vírgulas em: {os.path.basename(filepath)}...")
    try:
        # Lê como Latin1 (padrão da ANS)
        with open(filepath, 'r', encoding='latin1') as f:
            lines = f.readlines()
        
        if not lines: return

        new_lines = []
        # Mantém o cabeçalho
        new_lines.append(lines[0].strip())
        
        # Processa linha a linha
        for line in lines[1:]:
            line = line.strip()
            if not line: continue
            
            parts = line.split(';')
            
            # Se a linha tiver dados (geralmente 6 colunas)
            # As colunas de valor são as duas últimas (Saldo Inicial e Final)
            if len(parts) >= 3:
                # Remove aspas e troca vírgula por ponto
                parts[-1] = parts[-1].replace('"', '').replace(',', '.')
                parts[-2] = parts[-2].replace('"', '').replace(',', '.')
            
            new_lines.append(';'.join(parts))
            
        # Salva de volta como UTF-8 (Padrão do Banco)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
            
    except Exception as e:
        print(f"   ❌ Erro ao corrigir arquivo: {e}")

def get_file_links_recursive(url, filters, current_depth=0):
    """
    Busca recursiva: Se achar arquivo, guarda. Se achar pasta do ano, entra nela.
    """
    if current_depth > 1: # Evita loop infinito
        return [] 

    print(f"🔎 Vasculhando: {url}")
    found_links = []
    
    # Tenta acessar a URL
    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text()
            
             # Ignora link de "voltar" 
            if "Parent Directory" in text: 
                continue
            
            # Constrói URL completa se for relativa
            full_link = url + href if not href.startswith('http') else href

            # arquivo zip ou csv com o ano alvo
            if href.lower().endswith(('.zip', '.csv')):
                for term in filters:
                    if term in href:
                        found_links.append(full_link)
                        print(f"   ✅ Encontrado arquivo: {href}")
                        break
            
            # pasta (termina com /)
            elif href.endswith('/'):
                for term in filters:
                    if term in href.replace('/', ''): # Remove a barra para checar "2023"
                        print(f"   📂 Entrando na pasta: {href}")
                        # Chama a função nela mesma recursivamente
                        found_links.extend(get_file_links_recursive(full_link, filters, current_depth + 1))
                        break
                        
        return found_links

    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")
        return []

def download_and_extract(url, extract_to=None):
    filename = url.split('/')[-1]
    save_path = os.path.join(INPUT_DIR, filename)
    final_extract_path = extract_to if extract_to else INPUT_DIR

    print(f"⬇️  Baixando: {filename}...")
    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        if filename.lower().endswith('.zip'):
            print(f"📦 Extraindo {filename}...")
            with ZipFile(save_path, 'r') as zip_ref:
                zip_ref.extractall(final_extract_path)
                
                # Limpa os CSVs extraídos imediatamente
                for extracted_file in zip_ref.namelist():
                    if extracted_file.lower().endswith('.csv'):
                        full_path = os.path.join(final_extract_path, extracted_file)
                        sanitize_csv(full_path)

            os.remove(save_path)
            print(f"✅ Extraído e limpo.")
        else:
            print(f"✅ Salvo com sucesso.")
            
    except Exception as e:
        print(f"❌ Erro ao processar {filename}: {e}")

def run_preparation():
    setup_directories()
    
    # Operadoras
    print("\n DADOS DAS OPERADORAS")
    ops_links = get_file_links_recursive(URL_OPERADORAS, ["Relatorio", "Cadop"])
    if ops_links:
        # Pega o último link mais recente
        download_and_extract(ops_links[-1])
    else:
        print("⚠️  CSV de Operadoras não encontrado.")

    print("\n DADOS CONTÁBEIS (2023-2024)")
    acc_links = get_file_links_recursive(URL_CONTABIL, TARGET_YEARS)
    
    if not acc_links:
        print("⚠️  Nenhum arquivo contábil encontrado. Verifique os logs acima.")
    else:
        print(f"\n🚀 Baixando {len(acc_links)} arquivos encontrados...")
        for link in acc_links:
            download_and_extract(link, extract_to=ACCOUNTING_DIR)

if __name__ == "__main__":
    run_preparation()