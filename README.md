# 📊 Intuitive Care - Teste de Dados

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker)

> Desafio para extração, transformação e análise de dados públicos da Agência Nacional de Saúde Suplementar (ANS).

---

## 🚀 Sobre o Projeto

Este repositório contém a solução para os desafios de dados (Testes 1, 2 e 3) do processo seletivo da Intuitive Care.
### 🛠️ Funcionalidades Implementadas

* **Teste 1 - Web Scraping:**
    * Robô (`requests` + `BeautifulSoup`) que acessa o portal da ANS.
    * Identifica dinamicamente os links para os Anexos I e II.
    * Baixa os PDFs e compacta em um arquivo `.zip`.

* **Teste 2 - Transformação de Dados:**
    * Extração de tabelas complexas de PDF utilizando `pdfplumber`.
    * Limpeza e normalização de dados com `pandas`.
    * Substituição de abreviações ("OD", "AMB") pelas descrições completas conforme legenda.
    * Exportação para CSV e compactação ZIP.

* **Teste 3 - Data de Banco de dados:**
    * Download automático dos dados contábeis (2023-2024) e cadastrais das operadoras.
    * **Sanitização Automática:** Conversão de arquivos do padrão brasileiro (vírgula decimal, Latin1) para o padrão internacional (ponto decimal, UTF-8).
    * Banco de Dados **PostgreSQL** containerizado.
    * Queries SQL analíticas para identificar as operadoras com maiores despesas em eventos assistenciais.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Banco de Dados:** PostgreSQL 15 (Docker)
* **Infraestrutura:** Docker e Docker Compose
* **Bibliotecas Principais:**
    * `requests` / `urllib3`: Para requisições HTTP e download de arquivos.
    * `beautifulsoup4`: Para parsing de HTML e navegação no site da ANS.
    * `pdfplumber`: Para extração precisa de tabelas em PDFs.
    * `pandas`: Para manipulação, limpeza e transformação de dados (DataFrames).
    * `zipfile` / `shutil`: Para manipulação de arquivos e compactação.

---

## ⚙️ Pré-requisitos

Para rodar este projeto, você precisa ter instalado na sua máquina:

* **Git**
* **Docker** e **Docker Compose** (Altamente Recomendado)

*Caso opte por rodar sem Docker:*
* Python 3.10+
* PostgreSQL instalado e configurado localmente.

---

## 📦 Como Rodar (Docker - Recomendado)

O projeto está 100% dockerizado. Você **não precisa** instalar Python ou configurar o Postgres na sua máquina local.

### 1. Preparação

Clone o repositório e entre na pasta do projeto:

```bash
git clone [https://github.com/elderfausto/intuitive-care-dados.git](https://github.com/elderfausto/intuitive-care-dados.git)
cd intuitive-care-dados/web-scraping

Suba o ambiente (Python + Banco de Dados):
docker compose up -d --build

(Aguarde o download das imagens e a inicialização dos serviços)

```

### 2. Executar os Testes
Todos os comandos abaixo devem ser rodados no seu terminal, dentro da pasta web-scraping.

▶️ Teste 1: Web Scraping (Baixar PDFs)
Este comando acessa o site da ANS, baixa os anexos e cria o ZIP.

```bash
docker compose exec app python3 src/teste_1_scraping.py

Saída: Verifique a pasta inputs/teste_1 (PDFs) e outputs/teste_1 (ZIP).
```

▶️ Teste 2: Transformação (PDF -> CSV)
Este comando lê o PDF baixado, extrai a tabela, substitui as siglas e gera o CSV final.

```bash
docker compose exec app python3 src/teste_2_transformacao.py

Saída: Verifique a pasta outputs/teste_2 (CSV e ZIP).
```

▶️ Teste 3: Banco de Dados e Análise
Etapa A: Baixar e Preparar Dados O script baixa os dados contábeis e de operadoras e corrige automaticamente a formatação (vírgula para ponto, encoding).
```bash
docker compose exec app python3 src/teste_3_banco_de_dados.py

cat src/teste_3_queries.sql | docker compose exec -T db psql -U user -d intuitive_db

Saída: O terminal exibirá logs de criação de tabelas (CREATE TABLE), importação (COPY) e, ao final, duas tabelas com o ranking das operadoras.
```

## 📂 Estrutura do Projeto
<img width="722" height="252" alt="image" src="https://github.com/user-attachments/assets/ba2eceee-05eb-4fac-97ae-0074126116af" />

> Encoding: Os arquivos da ANS utilizam originalmente Latin-1 (ISO-8859-1). O script teste_3_preparacao.py converte automaticamente para UTF-8 para compatibilidade total com o PostgreSQL.
> Decimais: O script também normaliza os valores monetários, substituindo a vírgula (,) pelo ponto (.) para tipos numéricos.
> Persistência: Os dados do banco de dados são persistidos em um volume Docker (postgres_data), então você não perde os dados ao reiniciar o container.
