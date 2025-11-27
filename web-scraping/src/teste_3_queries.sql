-- ============================================================================
-- 1. CRIAÇÃO DAS TABELAS
-- ============================================================================

-- Tabela de Operadoras (Dados Cadastrais)
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
    data_registro_ans DATE -- Importante formatar a data corretamente na importação
);

-- Tabela de Demonstrações Contábeis (Dados Financeiros)
DROP TABLE IF EXISTS demonstracoes_contabeis;
CREATE TABLE demonstracoes_contabeis (
    data_referencia DATE,
    registro_ans INT,
    cd_conta_contabil VARCHAR(50),
    descricao TEXT,
    saldo_inicial NUMERIC(18, 2),
    saldo_final NUMERIC(18, 2)
);

-- Índices para otimizar as queries analíticas
CREATE INDEX idx_contabil_data ON demonstracoes_contabeis(data_referencia);
CREATE INDEX idx_contabil_reg ON demonstracoes_contabeis(registro_ans);
CREATE INDEX idx_contabil_desc ON demonstracoes_contabeis(descricao);

-- ============================================================================
-- 2. IMPORTAÇÃO DOS DADOS (Exemplos de COPY)
-- Ajustar os caminhos '/caminho/para/arquivo.csv' conforme o ambiente.
-- O Encoding 'LATIN1' é padrão da ANS. O delimitador costuma ser ';'.
-- ============================================================================

/*
-- Exemplo para importar Operadoras:
COPY operadoras 
FROM '/app/inputs/teste_3/Relatorio_cadop.csv' 
WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'LATIN1');

-- Exemplo para importar Contábil (Repetir para cada arquivo trimestral):
COPY demonstracoes_contabeis 
FROM '/app/inputs/teste_3/demonstracoes_contabeis/1T2023.csv' 
WITH (FORMAT CSV, HEADER, DELIMITER ';', ENCODING 'LATIN1');
*/

-- ============================================================================
-- 3. QUERIES ANALÍTICAS
-- ============================================================================

/* As 10 operadoras com maiores despesas em 
   "EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR" 
   no último trimestre?
*/

WITH UltimoTrimestre AS (
    -- Descobre qual é a data mais recente na base
    SELECT MAX(data_referencia) as data_max FROM demonstracoes_contabeis
)
SELECT 
    o.registro_ans,
    o.razao_social,
    SUM(dc.saldo_final) as total_despesas
FROM demonstracoes_contabeis dc
JOIN operadoras o ON dc.registro_ans = o.registro_ans
WHERE 
    dc.descricao = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR'
    AND dc.data_referencia = (SELECT data_max FROM UltimoTrimestre)
GROUP BY o.registro_ans, o.razao_social
ORDER BY total_despesas DESC
LIMIT 10;


/* As 10 operadoras com maiores despesas nessa categoria no último ano? */

WITH UltimoAno AS (
    -- Pega o ano da data mais recente
    SELECT EXTRACT(YEAR FROM MAX(data_referencia)) as ano_max FROM demonstracoes_contabeis
)
SELECT 
    o.registro_ans,
    o.razao_social,
    SUM(dc.saldo_final) as total_despesas_ano
FROM demonstracoes_contabeis dc
JOIN operadoras o ON dc.registro_ans = o.registro_ans
WHERE 
    dc.descricao = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR'
    AND EXTRACT(YEAR FROM dc.data_referencia) = (SELECT ano_max FROM UltimoAno)
GROUP BY o.registro_ans, o.razao_social
ORDER BY total_despesas_ano DESC
LIMIT 10;