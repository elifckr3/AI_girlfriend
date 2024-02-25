#!/bin/bash

# pdm add --skip=:pre,post_install --dev pyaudio

check_pre_commit() {
    if command -v pre-commit >/dev/null 2>&1; then
        echo "pre-commit is already installed."
    else
        echo "Installing pre-commit..."
        pip3 install pre-commit
        # Install pre-commit hooks after installation
        install_pre_commit_hooks
    fi
}

install_pre_commit_hooks() {
    echo "Installing pre-commit hooks..."
    pre-commit install
}


check_pre_commit

pre-commit autoupdate

redis-server --daemonize yes
