-- ============================================================================
-- 1. CRIAÇÃO DAS TABELAS
-- ============================================================================

DROP TABLE IF EXISTS operadoras;
CREATE TABLE operadoras (
    registro_ans INT PRIMARY KEY,
    cnpj VARCHAR(20),
    razao_social VARCHAR(255),
    nome_fantasia VARCHAR(255),
    modalidade VARCHAR(100),
    logradouro VARCHAR(255),
    numero VARCHAR(50),
    complemento VARCHAR(255),
    bairro VARCHAR(100),
    cidade VARCHAR(100),
    uf CHAR(2),
    cep VARCHAR(20),
    ddd VARCHAR(5),
    telefone VARCHAR(20),
    fax VARCHAR(20),
    endereco_eletronico VARCHAR(255),
    representante VARCHAR(255),
    cargo_representante VARCHAR(100),
    regiao_comercializacao VARCHAR(50),
    data_registro_ans DATE
);

DROP TABLE IF EXISTS demonstracoes_contabeis;
CREATE TABLE demonstracoes_contabeis (
    data_referencia DATE,
    registro_ans INT,
    cd_conta_contabil VARCHAR(50),
    descricao TEXT,
    saldo_inicial NUMERIC(18, 2),
    saldo_final NUMERIC(18, 2)
);

CREATE INDEX idx_contabil_data ON demonstracoes_contabeis(data_referencia);
CREATE INDEX idx_contabil_reg ON demonstracoes_contabeis(registro_ans);
CREATE INDEX idx_contabil_desc ON demonstracoes_contabeis(descricao);

-- ============================================================================
-- 2. IMPORTAÇÃO DOS DADOS
-- ============================================================================

COPY operadoras FROM '/inputs/teste_3/Relatorio_cadop.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'LATIN1');

-- Importando todos os arquivos contábeis listados anteriormente
COPY demonstracoes_contabeis FROM '/inputs/teste_3/demonstracoes_contabeis/1T2023.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'UTF8');
COPY demonstracoes_contabeis FROM '/inputs/teste_3/demonstracoes_contabeis/1T2024.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'UTF8');
COPY demonstracoes_contabeis FROM '/inputs/teste_3/demonstracoes_contabeis/2t2023.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'UTF8');
COPY demonstracoes_contabeis FROM '/inputs/teste_3/demonstracoes_contabeis/2T2024.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'UTF8');
COPY demonstracoes_contabeis FROM '/inputs/teste_3/demonstracoes_contabeis/3T2023.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'UTF8');
COPY demonstracoes_contabeis FROM '/inputs/teste_3/demonstracoes_contabeis/3T2024.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'UTF8');
COPY demonstracoes_contabeis FROM '/inputs/teste_3/demonstracoes_contabeis/4T2023.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'UTF8');
COPY demonstracoes_contabeis FROM '/inputs/teste_3/demonstracoes_contabeis/4T2024.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'UTF8');

-- ============================================================================
-- 3. QUERIES ANALÍTICAS (FINAL)
-- ============================================================================

/* Top 10 operadoras com maiores despesas no último trimestre */
WITH UltimoTrimestre AS (
    SELECT MAX(data_referencia) as data_max FROM demonstracoes_contabeis
)
SELECT 
    o.registro_ans,
    o.razao_social,
    SUM(dc.saldo_final) as total_despesas
FROM demonstracoes_contabeis dc
JOIN operadoras o ON dc.registro_ans = o.registro_ans
WHERE 
    -- Ignora maiúsculas e % pula a parte do texto com erro de acento
    dc.descricao ILIKE '%EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS%MEDICO HOSPITALAR%'
    AND dc.data_referencia = (SELECT data_max FROM UltimoTrimestre)
GROUP BY o.registro_ans, o.razao_social
ORDER BY total_despesas DESC
LIMIT 10;

/* Top 10 operadoras com maiores despesas no último ano */
WITH UltimoAno AS (
    SELECT EXTRACT(YEAR FROM MAX(data_referencia)) as ano_max FROM demonstracoes_contabeis
)
SELECT 
    o.registro_ans,
    o.razao_social,
    SUM(dc.saldo_final) as total_despesas_ano
FROM demonstracoes_contabeis dc
JOIN operadoras o ON dc.registro_ans = o.registro_ans
WHERE 
    dc.descricao ILIKE '%EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS%MEDICO HOSPITALAR%'
    AND EXTRACT(YEAR FROM dc.data_referencia) = (SELECT ano_max FROM UltimoAno)
GROUP BY o.registro_ans, o.razao_social
ORDER BY total_despesas_ano DESC
LIMIT 10;