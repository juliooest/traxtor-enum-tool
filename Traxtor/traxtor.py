import argparse
import subprocess
import re
import os
from concurrent.futures import ThreadPoolExecutor
import json


MAX_WORKERS = 30 # Número máximo de threads padrão para escaneamentos
OUTPUT_DIR = "output_ctf"

def banner():
    print("▄▄▄█████▓ ██▀███   ▄▄▄      ▒██   ██▒▄▄▄█████▓ ▒█████   ██▀███")
    print("▓  ██▒ ▓▒▓██ ▒ ██▒▒████▄    ▒▒ █ █ ▒░▓  ██▒ ▓▒▒██▒  ██▒▓██ ▒ ██▒")
    print("▒ ▓██░ ▒░▓██ ░▄█ ▒▒██  ▀█▄  ░░  █   ░▒ ▓██░ ▒░▒██░  ██▒▓██ ░▄█ ▒")
    print("░ ▓██▓ ░ ▒██▀▀█▄  ░██▄▄▄▄██  ░ █ █ ▒ ░ ▓██▓ ░ ▒██   ██░▒██▀▀█▄")
    print("  ▒██▒ ░ ░██▓ ▒██▒ ▓█   ▓██▒▒██▒ ▒██▒  ▒██▒ ░ ░ ████▓▒░░██▓ ▒██▒")
    print("  ▒ ░░   ░ ▒▓ ░▒▓░ ▒▒   ▓▒█░▒▒ ░ ░▓ ░  ▒ ░░   ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░")
    print("    ░      ░▒ ░ ▒░  ▒   ▒▒ ░░░   ░▒ ░    ░      ░ ▒ ▒░   ░▒ ░ ▒░")
    print("  ░        ░░   ░   ░   ▒    ░    ░    ░      ░ ░ ░ ▒    ░░   ░")
    print("            ░           ░  ░ ░    ░               ░ ░     ░")
    print("                                                         ® trax\n")

def run(cmd):
    """Executa um comando de shell e retorna a saída."""
    try:
        return subprocess.getoutput(cmd)
    except Exception as e:
        print(f"[!] Erro ao rodar comando: {cmd}. Erro: {e}")
        return ""

def feroxbuster_scan(target, wordlist, threads):
    """Escaneia um único alvo (URL) com Feroxbuster e retorna a lista de diretórios encontrados."""
    print(f"[*] Feroxbuster: Iniciando em {target}...")
    cmd = f"feroxbuster -u {target} -w {wordlist} -d 4 -t {threads} --silent --no-recursion"
    output = run(cmd)

    dirs = set()
    for line in output.splitlines():
        # Captura URLs completas (http(s)://.../)
        m = re.search(r"((?:https?://|http://)[^\s]+?)(?:/\s|$)", line)
        if m:
            dirs.add(m.group(1).rstrip("/"))

    return list(dirs)

def feroxbuster_parallel(target_url, wordlist, threads):
    """Gerencia a execução paralela de Feroxbuster (neste caso, é um único alvo, mas mantém a estrutura)."""
    banner()
    print(f"[+] Iniciando Fuzzing de Diretórios com Feroxbuster em {target_url}...")
    
    # Feroxbuster já é multi-threaded, então o rodamos uma vez
    found_dirs = feroxbuster_scan(target_url, wordlist, threads)
    
    print(f"[+] Diretórios válidos encontrados: {len(found_dirs)}")
    return found_dirs

def ffuf_single_target(directory, wordlist):
    """Roda FFUF em um único diretório para encontrar arquivos/endpoints."""
    print(f"[*] FFUF: Buscando arquivos em {directory}...")
    safe_name = directory.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "")
    outfile = f"{OUTPUT_DIR}/ffuf/{safe_name}.json"

    # Comando FFUF: -mc 200,301 (códigos de sucesso/redirecionamento)
    cmd = (
        f"ffuf -u {directory}/FUZZ -w {wordlist} "
        f"-mc 200,204,301,302,307,403 -fs 0 -ic -json -o {outfile} -t {MAX_WORKERS}"
    )
    run(cmd)

    valid_endpoints = []
    if os.path.exists(outfile):
        try:
            with open(outfile, 'r') as f:
                data = json.load(f)
                for result in data.get('results', []):
                    fuzz_result = result.get('input', {}).get('FUZZ')
                    if fuzz_result:
                        valid_endpoints.append(f"{directory}/{fuzz_result}")
        except json.JSONDecodeError:
            pass # Ignora arquivos JSON inválidos

    return valid_endpoints

def ffuf_parallel(directories, wordlist):
    """Gerencia a execução paralela de FFUF sobre a lista de diretórios."""
    if not directories:
        print("[-] Nenhuma diretório para rodar FFUF.")
        return []

    print(f"\n[+] Iniciando Fuzzing de Arquivos/Endpoints com FFUF em {len(directories)} diretórios...")
    os.makedirs(f"{OUTPUT_DIR}/ffuf", exist_ok=True)
    all_endpoints = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Mapeia a função ffuf_single_target para cada diretório na lista
        future_to_dir = [executor.submit(ffuf_single_target, d, wordlist) for d in directories]
        
        for future in future_to_dir:
            try:
                # O resultado de cada thread é uma lista de endpoints encontrados para aquele diretório
                all_endpoints.extend(future.result())
            except Exception as exc:
                print(f"[*] FFUF falhou: {exc}")

    print(f"[+] Total de Endpoints encontrados por FFUF: {len(all_endpoints)}")
    
    # Salvando endpoints em um txt
    with open(f"{OUTPUT_DIR}/all_endpoints.txt", "w") as f:
        f.write("\n".join(all_endpoints))
    
    return all_endpoints

def param_spider_scan(target):
    """Roda ParamSpider e retorna a lista de URLs com parâmetros."""
    dom = target.replace("https://", "").replace("http://", "")
    print(f"\n[+] Iniciando ParamSpider em {dom}...")

    out = run(f"paramspider -d {dom} -s")
    params = [x for x in out.splitlines() if "=" in x]

    with open(f"{OUTPUT_DIR}/params.txt", "w") as f:
        f.write("\n".join(params))

    print(f"[+] Parâmetros encontrados: {len(params)}")
    return params

def kxss_scan(params):
    """Roda kXSS na lista de URLs com parâmetros para encontrar possíveis XSS."""
    if not params:
        print("[-] Nenhuma URL com parâmetro para rodar kXSS.")
        return

    print(f"\n[+] Iniciando kXSS em {len(params)} URLs...")

    input_file = f"{OUTPUT_DIR}/params_for_kxss.txt"
    with open(input_file, "w") as f:
        f.write("\n".join(params))

    output_file = f"{OUTPUT_DIR}/xss_hits.txt"
    run(f"kxss -f {input_file} -o {output_file}")

    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        hits = len(open(output_file).read().strip().splitlines())
        print(f"[+] Possíveis XSS encontrados: {hits} (salvo em {output_file})")
    else:
        print("[+] Nenhum XSS encontrado.")


def main():
    parser = argparse.ArgumentParser(
        description="Ferramenta Multi-Threaded de Enumeração para CTF.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Argumentos Obrigatórios
    parser.add_argument("-u", "--url", required=True, help="Alvo ex: https://site.com")
    parser.add_argument("-w", "--wordlist", required=True, help="Wordlist de diretórios/arquivos")
    
    # Argumentos para Controle de Execução
    parser.add_argument("-t", "--threads", default=MAX_WORKERS, type=int, 
                        help=f"Número de threads para o Feroxbuster (Padrão: {MAX_WORKERS})")
    
    # Argumentos de Módulos (Escolhas)
    parser.add_argument("--ferox", action="store_true", help="Rodar Feroxbuster (Diretórios)")
    parser.add_argument("--ffuf", action="store_true", help="Rodar FFUF (Arquivos/Endpoints) nos diretórios encontrados pelo Feroxbuster")
    parser.add_argument("--param", action="store_true", help="Rodar ParamSpider (Parâmetros)")
    parser.add_argument("--kxss", action="store_true", help="Rodar kXSS nas URLs encontradas pelo ParamSpider")
    parser.add_argument("--full", action="store_true", help="Rodar Feroxbuster, FFUF, ParamSpider e kXSS (pipeline completo)")
    
    args = parser.parse_args()
    
    # Cria o diretório de saída
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"[*] AutoCTFEnum iniciado em {args.url}...\n")
    
    # --- Lógica de Execução do Pipeline ---
    
    # 1. Feroxbuster (Diretórios)
    dirs = []
    if args.ferox or args.full:
        dirs = feroxbuster_parallel(args.url, args.wordlist, args.threads)
    
    # 2. FFUF (Arquivos/Endpoints)
    if (args.ffuf or args.full) and dirs:
        ffuf_parallel(dirs, args.wordlist)
    
    # 3. ParamSpider (Parâmetros)
    params = []
    if args.param or args.full:
        params = param_spider_scan(args.url)
        
    # 4. kXSS (Vulnerabilidades)
    if (args.kxss or args.full) and params:
        kxss_scan(params)

    # Mensagem final
    print("\n[+] Processo de Enumeração Concluído.")
    print(f"Output salvo em /{OUTPUT_DIR}")

if __name__ == "__main__":
    main()