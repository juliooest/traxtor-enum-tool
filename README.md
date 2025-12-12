Ferramenta de Enumeração Multi-Threaded para CTF

🚀 Visão Geral
O TRAXTOR é uma ferramenta Python multi-threaded feita pra agilizar enum web em CTF e Bug Bounty. <br/ >Ele junta a força do Feroxbuster, FFUF, ParamSpider e kXSS num pipeline só, rápido e modular.

Você escolhe o que quer rodar — diretórios, arquivos, parâmetros ou XSS.

⚙️ Pipeline do TRAXTOR
Fluxo completo (--full):
<br/>
Feroxbuster – encontra diretórios.
<br/>
FFUF – fuzz de arquivos/endpoints. <br/>
ParamSpider – coleta URLs com parâmetros. <br/>
kXSS – testa XSS nas URLs encontradas. <br/>

⚠️ Aviso Legal
<br/>
Uso somente para CTF, Bug Bounty autorizado ou sistemas seus. Fora disso é ilegal.

🛠️ Instalação
1. Requisitos
Feroxbuster, FFUF, ParamSpider, kXSS, Python, 3jq

2. Instalação Automática
chmod +x install_tools.sh
./install_tools.sh

3. Execução
python3 traxtor.py [ARGUMENTOS]

📖 Uso
<br/>
💡 Modo Completo
python3 traxtor.py -u https://target.com -w /path/to/wordlist.txt --full -t 50

🎯 Modo Modular
<br/>
Só Ferox:
<br/>
python3 traxtor.py -u https://target.com -w /path/to/wordlist.txt --ferox

Só ParamSpider + kXSS:
<br/>
python3 traxtor.py -u https://target.com -w /path/to/wordlist.txt --param --kxss

🔧 Argumentos
<br/>
Flag	Descrição	Default
<br/>
-u, --url	URL alvo (obrigatório)	-
<br/>
-w, --wordlist	Caminho da wordlist (obrigatório)	-
<br/>
-t, --threads	Threads para Ferox e concurrency	30
<br/>
--full	Pipeline completo	- <br/>
--ferox	Habilita Feroxbuster	-
<br/>
--ffuf	Habilita FFUF	-
<br/>
--param	Habilita ParamSpider	-
<br/>
--kxss	Habilita kXSS	-
