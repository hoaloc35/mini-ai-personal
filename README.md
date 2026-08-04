# AI 383 -- Operation OS v4.0

**AI Ca Nhan Da Nang** -- Chay tren Android (Termux) + Windows

## Tinh Nang Chinh

- Chat AI thong minh (Gemini API, tieng Viet)
- Bach khoa toan thu + Tu hoc tu nguon
- Tim kiem web (DuckDuckGo)
- Quan ly task, file, ghi chu
- Plugin system mo rong
- Multi-Agent SubAgent System
- Translation (16+ ngon ngu)
- Code Runner sandbox an toan
- Creative AI: Image/Video/Music generation
- **v4.0: RAG Engine** (doc PDF/TXT/MD/CSV)
- **v4.0: MCP Protocol Client** (GitHub/Notion/Slack)
- **v4.0: Workflow Engine** (multi-step automation)
- **v4.0: Native Tool-Calling** (Gemini function-calling)

## Cai Dat

### Android (Termux)
\`\`\`bash
pkg update && pkg install python git
git clone https://github.com/hoaloc35/mini-ai-personal.git
cd mini-ai-personal
bash scripts/setup_android.sh
python main.py
\`\`\`

### Windows
\`\`\`cmd
git clone https://github.com/hoaloc35/mini-ai-personal.git
cd mini-ai-personal
scripts\\setup_windows.bat
python main.py
\`\`\`

Mo trinh duyet: http://localhost:8383

## API Key

Lay API key mien phi tai: https://aistudio.google.com/apikey
Them vao file .env: GEMINI_API_KEY=your_key_here

## License
MIT

## Author
**Nguyen Hoa Loc** (hoaloc35)
