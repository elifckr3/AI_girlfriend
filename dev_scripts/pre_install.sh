#!/bin/bash

install_mac() {
    echo "Installing on macOS..."
    brew install portaudio 
    brew install ffmpeg 
    # brew install libportaudio2 # XXX-JESE no such package
}

install_ubuntu() {
    echo "Installing on Ubuntu..."
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev ffmpeg libportaudio2
}

install_windows() {
    echo "To install on Windows, use the following choco commands:"
    echo "choco install portaudio ffmpeg"
    echo "Note: This script cannot install packages directly on Windows."
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
