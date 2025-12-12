#!/bin/bash

REQUIRED_TOOLS=("python3" "python3-pip" "git" "go" "jq")

check_status() {
    if [ $? -ne 0 ]; then
        echo "❌ ERRO: Falha ao executar o comando: $1"
        exit 1
    fi
}


detect_pkg_manager() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v yum &> /dev/null; then
        echo "yum"
    else
        echo "unknown"
    fi
}

install_system_deps() {
    echo " Detectando gerenciador de pacotes..."
    PKG_MANAGER=$(detect_pkg_manager)

    if [ "$PKG_MANAGER" == "apt" ]; then
        echo "✅ Gerenciador de pacotes detectado: APT."
        sudo apt update
        check_status "apt update"
        echo "📦 Instalando dependências básicas (${REQUIRED_TOOLS[*]})..."
        sudo apt install -y "${REQUIRED_TOOLS[@]}"
        check_status "apt install"

    elif [ "$PKG_MANAGER" == "dnf" ] || [ "$PKG_MANAGER" == "yum" ]; then
        echo "✅ Gerenciador de pacotes detectado: DNF/YUM."
        echo "📦 Instalando dependências básicas (${REQUIRED_TOOLS[*]})..."
        sudo $PKG_MANAGER install -y "${REQUIRED_TOOLS[@]}"
        check_status "$PKG_MANAGER install"

    else
        echo "❌ ERRO: Gerenciador de pacotes não suportado (apenas apt, dnf ou yum)."
        exit 1
    fi
}


install_go_tools() {
    echo -e "\n🛠️  Instalando Ferramentas Go (ffuf, kxss)..."
    
    echo "Instalando ffuf..."
    go install github.com/ffuf/ffuf/v2@latest
    check_status "go install ffuf"

    echo "Instalando kxss..."
    go install github.com/Emoe/kxss@latest
    check_status "go install kxss"

    if [ -d "$HOME/go/bin" ] && ! echo "$PATH" | grep -q "$HOME/go/bin"; then
        echo "⚠️ Adicionando $HOME/go/bin ao PATH. Você pode precisar reiniciar o terminal."
        export PATH=$PATH:$HOME/go/bin
    fi
}

install_python_tools() {
    echo -e "\n🐍  Instalando Ferramentas Python (paramspider)..."
    
    mkdir -p "$HOME/tools"
    cd "$HOME/tools" || exit
    
    echo "Clonando ParamSpider do GitHub..."
    if [ -d "ParamSpider" ]; then
        echo "Repositório ParamSpider já existe. Atualizando..."
        cd ParamSpider || exit
        git pull
    else
        git clone https://github.com/devansh-chh/ParamSpider.git
        check_status "git clone ParamSpider"
        cd ParamSpider || exit
    fi

    echo "Instalando dependências Python para ParamSpider..."
    pip3 install -r requirements.txt
    check_status "pip3 install requirements.txt para ParamSpider"
    
    echo "ParamSpider instalado em $HOME/tools/ParamSpider."
    echo "Você pode executá-lo diretamente com: python3 $HOME/tools/ParamSpider/paramspider.py"
    
    cd - > /dev/null
}

install_feroxbuster() {
    echo -e "\n🔥  Instalando Feroxbuster..."
    ARCH=$(dpkg --print-architecture)

    if [ "$ARCH" == "amd64" ]; then
        DOWNLOAD_URL="https://github.com/epi052/feroxbuster/releases/latest/download/feroxbuster_x86_64.deb"
        echo "Baixando e instalando .deb para Feroxbuster (amd64)..."
        wget -q $DOWNLOAD_URL -O /tmp/feroxbuster.deb
        check_status "wget feroxbuster"
        sudo dpkg -i /tmp/feroxbuster.deb
        check_status "dpkg feroxbuster"
        rm /tmp/feroxbuster.deb
    else
        echo "⚠️ ATENÇÃO: Feroxbuster não instalado automaticamente. Arquitetura ($ARCH) não suportada via .deb."
        echo "Tente: 'cargo install feroxbuster' (requer Rust) ou baixe o binário manualmente."
    fi
}

main() {
    banner
    echo "Iniciando instalação de dependências e ferramentas..."

    # 1. Dependências do sistema (apt/dnf)
    install_system_deps

    # 2. Ferramentas Go
    install_go_tools

    # 3. Ferramentas Python
    install_python_tools

    # 4. Feroxbuster
    install_feroxbuster
    
    echo -e "\n\n🎉 INSTALAÇÃO CONCLUÍDA! 🎉"
    echo "Para garantir que as ferramentas Go estejam acessíveis, você pode precisar executar:"
    echo "source ~/.bashrc  (ou ~/.zshrc)"
}

main