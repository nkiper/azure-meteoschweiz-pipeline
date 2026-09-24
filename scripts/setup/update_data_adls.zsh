#!/bin/zsh
source .venv/bin/activate
python download_data.py
python upload_to_adls.py