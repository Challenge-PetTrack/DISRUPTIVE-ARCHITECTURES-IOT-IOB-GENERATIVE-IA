#!/bin/bash
echo "=== PetTrack BCS API - Setup ==="

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "=== Setup concluido! ==="
echo "Para rodar: source venv/bin/activate && uvicorn main:app --reload --port 8000"
