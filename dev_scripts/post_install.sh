#!/bin/bash

pdm add --skip=:pre,post_install --dev pyaudio

redis-server

pip3 install pre-commit

pre-commit install

pre-commit autoupdate
