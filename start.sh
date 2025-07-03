#!/bin/bash

# Salir si algo falla
set -e

echo "📁 Entrando a frontend..."
cd frontend

echo "📦 Instalando dependencias de frontend..."
npm install

echo "🏗️  Compilando frontend..."
npm run build

echo "📁 Entrando a backend..."
cd ..
cd backend

echo "🐍 Instalando dependencias de backend..."
pip install -r requirements.txt

echo "🚀 Iniciando servidor FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000

