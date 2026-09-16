# ✈️ TripMind AI — AI-Based Trip Planner Chatbot

A professional AI-based trip planner chatbot built using *Flask + Vanilla JavaScript* that helps users plan personalized trips through an interactive web interface.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install flask
```

### 2. Run the server
```bash
cd trip-planner
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## 📁 Project Structure

```
trip-planner/
├── app.py         ← Flask backend (NLP + plan generation)
├── data.json      ← Destinations, hotels, cost data
├── index.html     ← Chat UI
├── style.css      ← All styling
├── script.js      ← Frontend logic
└── README.md
```

---

## 💬 Example Inputs

| Input | What Happens |
|-------|-------------|
| `Plan a 4-day Goa trip for couple with ₹25000` | Full plan generated instantly |
| `Plan 5 days from Delhi to Banaras for friends with ₹20000` | Two-city plan with intercity travel |
| `Plan a solo Manali trip for 3 days with 15k` | Solo adventure plan |
| `Jaipur` | Bot asks for missing details one by one |
| `reset` | Clears session, starts fresh |

---

## 🧠 Features

- **Smart NLP** — extracts destination, budget, duration, travel type from natural language
- **Two-destination support** — "Delhi to Banaras" splits days between cities
- **Day-wise itinerary** — personalized by travel type (solo/couple/friends/family)
- **Budget breakdown** — hotel, food, activities, transport with visual bars
- **Hotel recommendations** — budget / mid / luxury for every destination
- **Travel tips** — 5 authentic tips per destination
- **Voice input** — browser SpeechRecognition (Chrome/Edge)
- **10 built-in destinations** — Goa, Manali, Delhi, Banaras, Agra, Jaipur, Kerala, Mumbai, Shimla, Rishikesh
- **Unknown destinations** — generates reasonable fallback data

---

## 🗺️ Supported Destinations (Built-in)

Goa · Varanasi/Banaras · Delhi · Manali · Agra · Jaipur · Kerala · Mumbai · Shimla · Rishikesh

> For any other destination, the AI generates intelligent fallback data.

---

## ⚙️ API

`POST /chat`
```json
{ "message": "Plan a 4-day Goa trip for couple with 25000", "session_id": "abc123" }
```

`POST /reset`
```json
{ "session_id": "abc123" }
```

---

## 📌 Notes

- No API keys needed
- Works fully offline after initial font load
- Session state is in-memory (resets on server restart)
