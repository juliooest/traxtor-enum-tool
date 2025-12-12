<img src="">
<br/>
<br/>
Ferramenta de Enumeração Multi-Threaded para CTF
<br/>
🚀 Visão Geral
O TRAXTOR é uma ferramenta Python multi-threaded feita pra agilizar enum web em CTF e Bug Bounty. Ele junta a força do Feroxbuster, FFUF, ParamSpider e kXSS num pipeline só, rápido e modular.
<br/>
Você escolhe o que quer rodar — diretórios, arquivos, parâmetros ou XSS.
<br/>
⚙️ Pipeline do TRAXTOR
Fluxo completo (--full):
Feroxbuster – encontra diretórios.
FFUF – fuzz de arquivos/endpoints.
ParamSpider – coleta URLs com parâmetros.
kXSS – testa XSS nas URLs encontradas.
<br/>
<br/>
⚠️ Aviso Legal
Uso somente para CTF, Bug Bounty autorizado ou sistemas seus. Fora disso é ilegal.
<br/>
🛠️ Instalação
1. Requisitos
Feroxbuster, FFUF, ParamSpider, kXSS, Python, 3jq
<br/>
2. Instalação Automática
chmod +x install_tools.sh
./install_tools.sh
<br/>
3. Execução
python3 traxtor.py [ARGUMENTOS]
<br/>
📖 Uso
💡 Modo Completo
python3 traxtor.py -u https://target.com -w /path/to/wordlist.txt --full -t 50
<br/>
🎯 Modo Modular
Só Ferox:
python3 traxtor.py -u https://target.com -w /path/to/wordlist.txt --ferox
<br/>
Só ParamSpider + kXSS:
python3 traxtor.py -u https://target.com -w /path/to/wordlist.txt --param --kxss
<br/>
🔧 Argumentos
Flag	Descrição	Default
-u, --url	URL alvo (obrigatório)	-
-w, --wordlist	Caminho da wordlist (obrigatório)	-
-t, --threads	Threads para Ferox e concurrency	30
--full	Pipeline completo	-
--ferox	Habilita Feroxbuster	-
--ffuf	Habilita FFUF	-
--param	Habilita ParamSpider	-
--kxss	Habilita kXSS	-
