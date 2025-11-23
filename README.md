# ☕ AI Coffee Shop Voice Agent (Name-Last Version)

This project is an **AI-powered coffee ordering voice agent** built using  
**LiveKit Agents**, **Deepgram STT**, **Google Gemini**, and **Murf TTS**.

The agent behaves like a real barista:

- First asks for the drink details  
- Then size  
- Then milk  
- Then extras  
- **Finally asks: “Whose name should this order be under?”**  
- Saves the order (including name) exactly as spoken  
- Stores every completed order as a JSON file in `/orders`

UTF-8 output is fully Windows-safe (no emojis used).

---

## 📸 Reference File Used

The following project reference file was used during build:

`/mnt/data/dff05c7d-0874-47cd-a4a7-0f490a9b84fd.png`

---

## ⭐ Features

- Voice-driven, natural coffee ordering
- Asks for customer name **at the end** (real café behavior)
- Saves each order with timestamp & session ID
- Clean ASCII output (no emoji → no Windows errors)
- Based on:
  - Deepgram STT  
  - Google Gemini Flash  
  - Murf TTS  
  - LiveKit Agents framework  

---

## 🧠 Tech Stack

| Component | Technology |
|----------|------------|
| Speech-to-Text | Deepgram Nova-3 |
| LLM | Google Gemini 2.5 Flash |
| Text-to-Speech | Murf |
| Audio Transport | LiveKit |
| Voice Activity Detection | Silero / LiveKit |
| Runtime | Python 3.11 |

---

## 📂 Project Structure

```
backend/
 ├── src/
 │    └── agent.py          # Main AI barista logic
 ├── orders/                # Auto-saved JSON orders
 ├── .env.local             # API keys and configuration
frontend/                   # If included
README.md
```

---

## 🔧 Installation

### 1. Clone this repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate       # Windows
```

### 3. Install dependencies

If you have a requirements file:

```bash
pip install -r requirements.txt
```

If not, install directly:

```bash
pip install livekit-agents livekit-plugins-deepgram livekit-plugins-google ^
livekit-plugins-murf livekit-plugins-silero python-dotenv
```

---

## 🔑 Environment Variables

Create:

```
backend/.env.local
```

Add:

```
DEEPGRAM_API_KEY=your_key
GOOGLE_API_KEY=your_key
MURF_API_KEY=your_key
```

---

## ▶ Running the Voice Agent

### **Option 1 — Using LiveKit Cloud Worker**

```bash
lk cloud auth
lk cloud worker run .
```

### **Option 2 — Local LiveKit Server**

1. Download server from GitHub releases:
   https://github.com/livekit/livekit-server/releases

2. Run server:

```bash
./livekit-server --dev
```

3. Start your agent:

```bash
python backend/src/agent.py
```

---

## 🖥 Windows Notice (Important)

Windows terminal defaults to CP1252 → breaks emoji printing.  
This project uses **ASCII only**, so no error.

If any script needs UTF-8:

```powershell
chcp 65001
$env:PYTHONIOENCODING="utf-8"
```

---

## 💾 Saved Orders

Orders are saved here:

```
backend/orders/order_YYYYMMDD_HHMMSS.json
```

Example:

```json
{
  "drinkType": "latte",
  "size": "medium",
  "milk": "oat",
  "extras": ["vanilla"],
  "name": "Alok",
  "timestamp": "2025-11-23T14:22:10",
  "session_id": "session_20251123_142210"
}
```

---

## 🎯 Custom Behavior (Name Collected Last)

This agent matches real café flow:

1. Drink  
2. Size  
3. Milk  
4. Extras  
5. **Ask for name at the end**  
6. Confirm + save order  

---

## 🛠 Troubleshooting

### ModuleNotFoundError: No module named 'livekit'

Install:

```bash
pip install livekit-agents
```

### Deepgram/Google/Murf not working

Check your `.env.local`.

### UnicodeEncodeError (Windows)

No emojis used → already fixed.

---

## 📜 License

MIT — free for personal and commercial use.

---

## 🙌 Author

Built by **Alok Sinha** using LiveKit + Python.

