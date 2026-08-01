#!/bin/bash
# ===============================================
# AI 383 -- Setup cho Android (Termux)
# ===============================================

echo "AI 383 -- Cai dat tren Termux"
echo "================================="

# Cap nhat Termux
echo "Cap nhat packages..."
pkg update -y && pkg upgrade -y

# Cai Python
echo "Cai dat Python..."
pkg install -y python python-pip

# Cai dependencies he thong
echo "Cai dat dependencies..."
pkg install -y libxml2 libxslt

# Cai Python packages
echo "Cai dat Python packages..."
pip install -r requirements.txt

# Tao file .env
if [ ! -f ".env" ]; then
    echo "Tao file .env..."
    cat > .env << 'EOF'
# AI 383 Configuration
# Lay API key mien phi tai: https://aistudio.google.com/apikey
GEMINI_API_KEY=your_api_key_here

# Server
HOST=0.0.0.0
PORT=8383

# Model (mac dinh: gemini-2.0-flash — mien phi)
MODEL_NAME=gemini-2.0-flash

# === Creative AI Tools (tuy chon) ===
# Image Generation
# IMAGE_GEN_API_KEY=your_key_here
# IMAGE_GEN_PROVIDER=gemini
# IMAGE_GEN_MODEL=imagen-3.0-generate-002

# Video Generation
# VIDEO_GEN_API_KEY=your_key_here
# VIDEO_GEN_PROVIDER=runway
# VIDEO_GEN_ENDPOINT=https://api.runwayml.com/v1

# Music Generation
# MUSIC_GEN_API_KEY=your_key_here
# MUSIC_GEN_PROVIDER=suno
# MUSIC_GEN_ENDPOINT=https://api.suno.ai/v1
EOF
    echo "Hay mo file .env va them GEMINI_API_KEY!"
fi

# Tao thu muc can thiet
mkdir -p data uploads knowledge_base

echo ""
echo "Cai dat hoan tat!"
echo ""
echo "Buoc tiep theo:"
echo "  1. Chinh sua file .env — them GEMINI_API_KEY"
echo "  2. Chay: python main.py"
echo "  3. Mo trinh duyet: http://localhost:8383"
echo ""
echo "Lay API key mien phi:"
echo "  https://aistudio.google.com/apikey"
echo ""
