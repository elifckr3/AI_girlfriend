#!/bin/bash

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

install_package_mac() {
    if brew list --formula | grep -q "^$1\$"; then
        :
    else
        echo "Installing ($1) on macOS..."
        brew install "$1"
    fi
}

install_package_ubuntu() {
    echo "Installing ($1) on Ubuntu..."
    sudo apt-get update
    sudo apt-get install -y "$1"
}

install_packages() {
    local os="$1"
    shift
    local packages=("$@")
    local not_found=()

    for pkg in "${packages[@]}"; do
        if ! command_exists "$pkg"; then
            not_found+=("$pkg")
        fi
    done

    if [ ${#not_found[@]} -eq 0 ]; then
        echo "All required packages are already installed."
    else
        case "$os" in
            mac)
                for pkg in "${not_found[@]}"; do
                    install_package_mac "$pkg"
                done
                ;;
            ubuntu)
                for pkg in "${not_found[@]}"; do
                    install_package_ubuntu "$pkg"
                done
                ;;
            *)
                echo "Unsupported OS."
                ;;
        esac
    fi
}

install_mac() {
    local packages=("portaudio" "ffmpeg" "redis")
    install_packages "mac" "${packages[@]}"
}

install_ubuntu() {
    local packages=("portaudio19-dev" "ffmpeg" "redis" "libportaudio2")
    install_packages "ubuntu" "${packages[@]}"
}

install_windows() {
    printf "Windows is not supported for development environment.\n"
    printf "We recommend setting up a dual boot with Ubuntu for better development experience.\n"
    printf "Here is a guide on how to dual boot Ubuntu on Windows: https://ubuntu.com/tutorials/install-ubuntu-desktop#windows-dual-boot\n"
}

case "$(uname -s)" in
    Darwin)
        install_mac
        ;;
    Linux)
        install_ubuntu
        ;;
    CYGWIN*|MINGW32*|MSYS*|MINGW*)
        install_windows
        ;;
    *)
        echo "Unsupported OS. Exiting."
        ;;
esac
