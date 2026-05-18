#!/bin/bash
echo "=== PetTrack BCS API - Setup ==="

# Cria venv
python3 -m venv venv

# Ativa
source venv/bin/activate

# Instala dependencias
pip install -r requirements.txt

echo "=== Setup concluido! ==="
echo "Para rodar: source venv/bin/activate && uvicorn main:app --reload --port 8000"
