import argparse
import subprocess
import re
import os
from concurrent.futures import ThreadPoolExecutor
import json

MAX_WORKERS = 30 
OUTPUT_DIR = "results"

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
    print("                                                         ® TRAXTOR\n")

def run(cmd):
    try:
        return subprocess.getoutput(cmd)
    except Exception as e:
        print(f"[!] Erro ao rodar comando: {cmd}. Erro: {e}")
        return ""

def feroxbuster_scan(target, wordlist, threads):
    print(f"[*] Feroxbuster: Iniciando em {target}...")
    cmd = f"feroxbuster -u {target} -w {wordlist} -d 4 -t {threads} --silent --no-recursion"
    output = run(cmd)

    dirs = set()
    for line in output.splitlines():
        m = re.search(r"((?:https?://|http://)[^\s]+?)(?:/\s|$)", line)
        if m:
            dirs.add(m.group(1).rstrip("/"))
            
    dirs_list = list(dirs)
    with open(f"{OUTPUT_DIR}/dirs_found.txt", "w") as f:
        f.write("\n".join(dirs_list))

    return dirs_list

def feroxbuster_parallel(target_url, wordlist, threads):
    print(f"[+] Iniciando Fuzzing de Diretórios com Feroxbuster em {target_url}...")
    found_dirs = feroxbuster_scan(target_url, wordlist, threads)
    print(f"[+] Diretórios válidos encontrados: {len(found_dirs)}")
    return found_dirs

def ffuf_single_target(directory, wordlist):
    print(f"[*] FFUF: Buscando arquivos em {directory}...")
    safe_name = directory.replace("https://", "").replace("http://", "").replace("/", "_").replace(":", "")
    outfile = f"{OUTPUT_DIR}/ffuf/{safe_name}.json"

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
            pass 

    return valid_endpoints

def ffuf_parallel(directories, wordlist):
    if not directories:
        print("[-] Nenhuma diretório para rodar FFUF.")
        return []

    print(f"\n[+] Iniciando Fuzzing de Arquivos/Endpoints com FFUF em {len(directories)} diretórios...")
    os.makedirs(f"{OUTPUT_DIR}/ffuf", exist_ok=True)
    all_endpoints = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_dir = [executor.submit(ffuf_single_target, d, wordlist) for d in directories]
        
        for future in future_to_dir:
            try:
                all_endpoints.extend(future.result())
            except Exception as exc:
                print(f"[*] FFUF falhou: {exc}")

    print(f"[+] Total de Endpoints encontrados por FFUF: {len(all_endpoints)}")
    
    with open(f"{OUTPUT_DIR}/all_endpoints.txt", "w") as f:
        f.write("\n".join(all_endpoints))
    
    return all_endpoints

def param_spider_scan(target):
    dom = target.replace("https://", "").replace("http://", "")
    print(f"\n[+] Iniciando ParamSpider em {dom}...")

    out = run(f"paramspider -d {dom} -s")
    params = [x for x in out.splitlines() if "=" in x]

    with open(f"{OUTPUT_DIR}/params.txt", "w") as f:
        f.write("\n".join(params))

    print(f"[+] Parâmetros encontrados: {len(params)}")
    return params

def kxss_scan(params):
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

def parameter_fuzzing(params, wordlist):
    if not params:
        print("[-] Nenhuma URL com parâmetro para fuzzing.")
        return

    print(f"\n[+] Iniciando Fuzzing de VALOR de Parâmetros (LFI/SQLi) em {len(params)} URLs...")
    
    fuzz_targets_file = f"{OUTPUT_DIR}/param_fuzz_targets.txt"
    
    processed_params = []
    for p in params:
        if '=' in p:
            parts = p.rsplit('=', 1)
            processed_params.append(f"{parts[0]}=FUZZ")

    with open(fuzz_targets_file, "w") as f:
        f.write("\n".join(processed_params))

    output_fuzz_file = f"{OUTPUT_DIR}/param_fuzz_hits.txt"
    
    cmd = (
        f"ffuf -request {fuzz_targets_file} -w {wordlist} "
        f"-mc 200,301,302,403 -fs 0 -ic -t {MAX_WORKERS} -o {output_fuzz_file}"
    )
    
    run(cmd)
    
    os.remove(fuzz_targets_file)

    if os.path.exists(output_fuzz_file) and os.path.getsize(output_fuzz_file) > 0:
        print(f"[+] Possíveis Hits de Fuzzing de Parâmetros (LFI/SQLi/etc.) salvos em {output_fuzz_file}")
    else:
        print("[+] Nenhum hit notável durante o fuzzing de parâmetros.")

def finalize_summary():
    summary_file = f"{OUTPUT_DIR}/vulnerability_summary.txt"
    
    xss_hits = f"{OUTPUT_DIR}/xss_hits.txt"
    fuzz_hits = f"{OUTPUT_DIR}/param_fuzz_hits.txt"
    
    if (os.path.exists(xss_hits) and os.path.getsize(xss_hits) > 0) or \
       (os.path.exists(fuzz_hits) and os.path.getsize(fuzz_hits) > 0):
        
        print("\n[*] Consolidando hits de vulnerabilidade...")
        
        with open(summary_file, "w") as out:
            out.write("================================================\n")
            out.write("=== TRAXTOR - RESUMO DE POTENCIAIS VULNERABILIDADES ===\n")
            out.write("================================================\n\n")

            if os.path.exists(xss_hits) and os.path.getsize(xss_hits) > 0:
                out.write("--- [ 1. POSSÍVEIS REFLEXÕES XSS (kXSS) ] ---\n")
                with open(xss_hits, "r") as f:
                    out.write(f.read())
                out.write("\n-----------------------------------------------\n\n")

            if os.path.exists(fuzz_hits) and os.path.getsize(fuzz_hits) > 0:
                out.write("--- [ 2. HITS DE FUZZING DE PARÂMETROS (LFI/SQLi/etc.) ] ---\n")
                out.write("URLs que tiveram respostas notáveis durante o fuzzing de valores de parâmetro:\n")
                with open(fuzz_hits, "r") as f:
                    out.write(f.read())
                out.write("\n--------------------------------------------------------------\n\n")
        
        print(f"[+] Resumo de Vulnerabilidades criado em: {summary_file}")
    
    else:
        if os.path.exists(fuzz_hits): os.remove(fuzz_hits)
        if os.path.exists(xss_hits): os.remove(xss_hits)
        print("[-] Nenhuma vulnerabilidade notável encontrada para consolidar.")

def main():
    parser = argparse.ArgumentParser(
        description="Ferramenta Multi-Threaded de Enumeração para CTF (TRAXTOR).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("-u", "--url", required=True, help="Alvo ex: https://site.com")
    parser.add_argument("-w", "--wordlist", required=True, help="Wordlist de diretórios/arquivos (também usada para fuzzing de parâmetros)")
    
    parser.add_argument("-t", "--threads", default=MAX_WORKERS, type=int, 
                        help=f"Número de threads para o Feroxbuster (Padrão: {MAX_WORKERS})")
    
    parser.add_argument("--ferox", action="store_true", help="Rodar Feroxbuster (Diretórios)")
    parser.add_argument("--ffuf", action="store_true", help="Rodar FFUF (Arquivos/Endpoints)")
    parser.add_argument("--param", action="store_true", help="Rodar ParamSpider (Parâmetros)")
    parser.add_argument("--kxss", action="store_true", help="Rodar kXSS nas URLs encontradas")
    parser.add_argument("--fuzz-param", action="store_true", help="Rodar Fuzzing de Valores de Parâmetros (requer --param)")
    parser.add_argument("--full", action="store_true", help="Rodar TODOS os módulos (pipeline completo)")
    
    args = parser.parse_args()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    banner()
    print(f"[*] TRAXTOR iniciado em {args.url}...\n")
    
    dirs = []
    if args.ferox or args.full:
        dirs = feroxbuster_parallel(args.url, args.wordlist, args.threads)
    
    if (args.ffuf or args.full) and dirs:
        ffuf_parallel(dirs, args.wordlist)
    
    params = []
    if args.param or args.full or args.fuzz_param or args.kxss:
        params = param_spider_scan(args.url)
        
    if (args.kxss or args.full) and params:
        kxss_scan(params)

    should_fuzz_param = (args.fuzz_param or args.full)
    if should_fuzz_param and params:
        parameter_fuzzing(params, args.wordlist)

    finalize_summary()
    
    print("\n[+] Processo de Enumeração Concluído.")
    print(f"Output salvo em /{OUTPUT_DIR}")
    
    if not should_fuzz_param and params:
        
        print("\n\n#####################################################################")
        print("❓ Deseja iniciar o Fuzzing de Parâmetros (LFI/SQLi/etc.) agora?")
        print(f"   (Será usada a wordlist principal: {args.wordlist})")
        
        resposta = input("Digite 'S' para Sim ou qualquer tecla para Não: ").upper()
        
        if resposta == 'S':
            print("Iniciando Fuzzing de Parâmetros interativamente...")
            parameter_fuzzing(params, args.wordlist)
        else:
            print("Fuzzing de Parâmetros ignorado. Use a flag --fuzz-param na próxima vez.")
            
    print("\n[+] Fim da execução do TRAXTOR.")

if __name__ == "__main__":
    main()