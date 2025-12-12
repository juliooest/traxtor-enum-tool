🚜 TRAXTOR - Ferramenta de Enumeração Multi-Threaded para CTF
🚀 Visão Geral
O TRAXTOR é uma ferramenta Python multi-threaded, desenvolvida especificamente para ambientes de Capture The Flag (CTF) e Bug Bounty. Seu objetivo é automatizar e acelerar o processo de enumeração web, combinando as funcionalidades de ferramentas líderes como Feroxbuster, FFUF, ParamSpider e kXSS em um único pipeline eficiente.

A ferramenta suporta execução modular, permitindo que o usuário escolha quais fases do scan executar (diretórios, arquivos, parâmetros ou XSS), otimizando o tempo de varredura.

⚙️ O Pipeline do TRAXTOR
O TRAXTOR segue um pipeline lógico de enumeração. O fluxo completo (--full) é representado abaixo:

Feroxbuster: Descobre diretórios válidos.

FFUF: Busca arquivos/endpoints dentro dos diretórios encontrados (Multi-threaded).

ParamSpider: Extrai URLs com parâmetros.

kXSS: Testa as URLs parametrizadas para XSS.

⚠️ Aviso Legal
Esta ferramenta destina-se estritamente a fins educacionais e éticos, incluindo competições Capture The Flag (CTF) e testes de segurança autorizados (como Bug Bounty em escopo permitido ou testes de penetração em sistemas próprios). O uso não autorizado contra sistemas de terceiros é ilegal e antiético.

🛠️ Instalação
1. Requisitos
O script depende das seguintes ferramentas de linha de comando:

Feroxbuster (Fuzzing de Diretórios)

FFUF (Fuzzing de Arquivos/Endpoints)

ParamSpider (Descoberta de Parâmetros)

kXSS (Análise de Reflexão XSS)

Python 3

jq (Para processar JSON do FFUF)

2. Automação da Instalação (Recomendado)
Utilize o script install_tools.sh para instalar automaticamente todas as dependências no seu sistema Linux (compatível com apt e dnf/yum):
# 1. Dê permissão de execução
chmod +x install_tools.sh

# 2. Execute o script
./install_tools.sh

3. Execução do Programa
Após a instalação das ferramentas, você pode executar o script principal:
python3 traxtor.py [ARGUMENTOS]

📖 Uso
💡 Modo Completo (Full Pipeline)
O modo mais rápido e completo para CTFs, que executa Feroxbuster, FFUF, ParamSpider e kXSS em sequência, usando threads para aceleração.
python3 traxtor.py -u https://target.com -w /path/to/wordlist.txt --full -t 50

🎯 Modo Modular
Você pode escolher rodar apenas módulos específicos:
Exemplo: Apenas Fuzzing de Diretórios (Feroxbuster)
python3 traxtor.py -u https://target.com -w /path/to/wordlist.txt --ferox

Exemplo: Apenas Descoberta de Parâmetros e XSS
python3 traxtor.py -u https://target.com -w /path/to/wordlist.txt --param --kxss

-u,--url, Alvo Obrigatório. URL do alvo (ex: https://site.com).,-
-w,--wordlist, Wordlist Obrigatória. Caminho para a wordlist de diretórios/arquivos.,-
-t,--threads, Número de threads para o Feroxbuster e concurrent.futures.,30, 
--full, "Modo Rápido: Executa todo o pipeline (Ferox, FFUF, Param, kXSS).",- 
--ferox,H abilita o Fuzzing de Diretórios com Feroxbuster.,-
--ffuf, Habilita o Fuzzing de Arquivos/Endpoints nos diretórios encontrados (requer --ferox rodando antes).,-
--param, Habilita a Descoberta de Parâmetros com ParamSpider.,-
--kxss, Habilita o Scan de XSS nas URLs com parâmetros encontradas (requer --param rodando antes).,-
