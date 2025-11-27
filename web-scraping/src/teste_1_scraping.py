import os
import requests
from bs4 import BeautifulSoup
from zipfile import ZipFile
import urllib3

# Desabilita avisos de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIGURAÇÕES
TARGET_URL = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
INPUT_DIR = "inputs"
OUTPUT_DIR = "outputs"
ZIP_FILE = os.path.join(OUTPUT_DIR, "Anexos_Baixados.zip")

# Headers para fingir ser um navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def setup_directories():
    """Cria as pastas de input e output se não existirem."""
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def get_download_links():
    """Acessa o site e busca os links dos PDFs."""
    print(f"📡 Acessando o site: {TARGET_URL}")
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        found_links = {}

        print("\n🔎 PROCURANDO LINKS NA PÁGINA...")
        
        # Itera sobre todos os links
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip()
            href = link['href']
            
            # LOG DE LINKS VISTOS
            if "Anexo" in text:
                print(f"Visto: '{text}' -> {href}")

            # LÓGICA DE PARSEAMENTO DOS ANEXOS
            # .lower() para transformar tudo em minúsculo e facilitar a comparação
            if "anexo i" in text.lower() and "anexo ii" not in text.lower(): 
                if href.endswith('.pdf') or "download" in href:
                    found_links["Anexo_I.pdf"] = href
                    print(f"   ✅ ANEXO I ENCONTRADO: {text}")
            
            elif "anexo ii" in text.lower():
                if href.endswith('.pdf') or "download" in href:
                    found_links["Anexo_II.pdf"] = href
                    print(f"   ✅ ANEXO II ENCONTRADO: {text}")

        return found_links

    except Exception as e:
        print(f"❌ Erro ao acessar o site: {e}")
        return {}

def download_file(url, filename):
    """Baixa o arquivo e salva no diretório de input."""
    full_path = os.path.join(INPUT_DIR, filename)
    print(f"⬇️  Baixando: {filename}...")
    
    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        with open(full_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Salvo em: {full_path}")
        return full_path
    except Exception as e:
        print(f"❌ Erro ao baixar {filename}: {e}")
        return None

def create_zip(file_list):
    """Compacta os arquivos baixados em um arquivo ZIP."""
    if not file_list:
        print("⚠️  Nenhum arquivo para zipar.")
        return

    print(f"📦 Criando arquivo ZIP em: {ZIP_FILE}")
    try:
        with ZipFile(ZIP_FILE, 'w') as zipf:
            for file in file_list:
                # Adiciona ao zip apenas com o nome do arquivo
                zipf.write(file, arcname=os.path.basename(file))
        print("🚀 Sucesso! Arquivo ZIP criado.")
    except Exception as e:
        print(f"❌ Erro ao criar ZIP: {e}")

def run_scraper():
    setup_directories()
    links = get_download_links()
    
    if not links:
        print("\n⚠️  Nenhum link encontrado. Verifique as mensagens de 'Visto' acima para ajustar o filtro.")
        return

    downloaded_files = []
    for name, url in links.items():
        file_path = download_file(url, name)
        if file_path:
            downloaded_files.append(file_path)
            
    create_zip(downloaded_files)

if __name__ == "__main__":
    run_scraper()