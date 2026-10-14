# Green Campus Awareness Bot 🌿

A modern, responsive, full-stack web application designed to promote environmental sustainability, waste reduction, water and energy conservation, and tree plantation among college students, faculty, and campus staff.

Featuring **EcoBot**, an AI-powered conversational assistant with OpenAI API integration and an intelligent built-in campus environmental knowledge engine.

---

## 🚀 Key Highlights & Features

### 1. 🤖 AI-Powered Chatbot (EcoBot)
- Answers environmental questions in clear, student-friendly language.
- Explains waste segregation (Green vs Blue bins), composting, water saving, and electricity reduction in hostels, labs, and classrooms.
- Pre-populated with quick-reply suggested questions:
  - *How can I make my campus greener?*
  - *How can I save water in college?*
  - *Where should I dispose of plastic waste?*
  - *What is composting?*
  - *How can students reduce electricity consumption?*
- Features an animated typing indicator, clear-chat functionality, message copy, and browser text-to-speech audio playback.
- **Fail-safe fallback:** If no OpenAI API key is supplied or quota is reached, EcoBot switches automatically to the offline **Campus Knowledge Engine** so the project can always be demonstrated reliably.

### 2. 🏆 Interactive Eco-Challenges & Gamification
- Real-time interactive sustainability challenges:
  1. *Bring a Reusable Water Bottle* (+25 XP)
  2. *Avoid Single-Use Plastics in Canteen* (+30 XP)
  3. *Switch Off Lights & Fans When Leaving* (+20 XP)
  4. *Join Campus Cleanliness Drive* (+50 XP)
  5. *Plant and Care for a Tree* (+60 XP)
  6. *Separate Wet & Dry Waste* (+25 XP)
  7. *Climb Stairs Instead of Elevators* (+15 XP)
  8. *Adopt Double-Sided Printing* (+20 XP)
- Progress bar dynamically tracks completion percentage, calculates earned XP points, and awards campus badges (*Eco Seedling 🌰*, *Green Sprout 🌱*, *Campus Guardian 🌿*, *Green Campus Ambassador 🏆*).

### 3. 💡 Categorized Green Tips
- Curated practical tips organized across 6 core campus domains:
  - **Water Conservation** (Faucet discipline, leak reporting, mindful refills)
  - **Energy Conservation** (Phantom loads, natural lighting, AC thermostats at 24°C)
  - **Waste Management** (3-bin source segregation, cloth tote bags, paper recycling)
  - **Air Quality** (Dorm air-purifying plants, smoke-free campus zones)
  - **Biodiversity & Tree Plantation** (Native flowering species, bird water bowls)
  - **Sustainable Transportation** (Campus bike shares, carpooling)
- Live instant search bar and category filter pills with an "Ask EcoBot" shortcut.

### 4. 📊 Green Campus Dashboard & Impact Metrics
- Live counters simulating campus environmental impact:
  - **Plastic Bottles Saved**
  - **Liters of Water Conserved**
  - **kWh Electricity Conserved**
  - **kg of CO₂ Emissions Prevented**
  - **Tips Shared & Activities Recorded**
- Includes a campus activity log and a clear disclaimer clarifying that sample figures are educational demonstration benchmarks.

### 5. ⭐ Community Feedback System
- Interactive 5-star rating widget.
- Role selector (*Student*, *Faculty / Teacher*, *Campus Staff*, *Alumni / Visitor*).
- Stores reviews in SQLite database and showcases testimonials on the page.

### 6. 🌐 Project Mission & UN SDG Alignment
- Aligned with **UN Sustainable Development Goals**:
  - **SDG 12:** Responsible Consumption & Production
  - **SDG 13:** Climate Action
  - **SDG 15:** Life on Land

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, Modern CSS (Glassmorphism, Nature theme), Vanilla JavaScript, Bootstrap 5.3, Bootstrap Icons |
| **Backend** | Python 3, Flask, Jinja2, Requests |
| **Database** | SQLite3 (`green_campus.db` - zero config, auto-initializing) |
| **AI Integration**| OpenAI API (`gpt-4o-mini` / `gpt-3.5-turbo`) + EcoBot Campus Knowledge Engine |
| **Environment** | `python-dotenv` for secure environment variable handling |

---

## 📁 Project Structure

```
AI Bot/
├── app.py                     # Flask application & REST API routes
├── config.py                  # Environment variable configuration & defaults
├── database.py                # SQLite database models, initialization & seed data
├── ai_service.py              # OpenAI API integration + local knowledge engine fallback
├── test_app.py                # Automated unit tests for all endpoints
├── requirements.txt           # Python backend dependencies
├── .env.example               # Template for environment secrets
├── .gitignore                 # Excludes .env, *.db, and __pycache__ from git
├── README.md                  # Comprehensive documentation
├── templates/
│   └── index.html             # Main responsive single-page web application
└── static/
    ├── css/
    │   └── style.css          # Nature-inspired modern design system & micro-animations
    ├── js/
    │   ├── main.js            # App coordinator, dashboard counters, toast system
    │   ├── chat.js            # Chatbot controller, message rendering, audio speech
    │   ├── challenges.js      # Gamified eco-challenges & XP points calculator
    │   ├── tips.js            # Categorized green tips explorer & live search
    │   └── feedback.js        # 5-star rating widget & testimonial submission
    └── img/
        ├── ecobot_avatar.svg  # Friendly leafy planet mascot vector graphic
        └── hero_illustration.svg # Sustainable campus vector landscape
```

---

## ⚙️ Installation & Setup Instructions

### Prerequisites
- Python 3.9+ (Python 3.10, 3.11, 3.12, 3.13, 3.14 supported)
- `pip` package manager
- Modern web browser (Chrome, Edge, Firefox, Safari)

### Step 1: Clone or Navigate to Project Directory
```powershell
cd "e:\AI Bot"
```

### Step 2: Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy `.env.example` to create your own `.env` file:
```powershell
copy .env.example .env
```

Open `.env` in a text editor and add your OpenAI API key:
```ini
# Flask Secret Key
SECRET_KEY=your-random-secret-key-here

# OpenAI API Key (Obtain from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-proj-yourActualOpenAiKeyHere
OPENAI_MODEL=gpt-4o-mini

# Database & Server Settings
DATABASE_NAME=green_campus.db
FLASK_DEBUG=True
PORT=5000
```

> **Security Note:**
> - Never commit your `.env` file to version control.
> - The API key is securely accessed **only on the server-side** by Flask.
> - If you do not have an OpenAI key, **the app still runs completely in Campus Knowledge Engine mode** without breaking!

---

## ▶️ Running the Application

Start the Flask development server:
```powershell
python app.py
```

You will see:
```text
🌿 Starting Green Campus Awareness Bot on port 5000...
 * Running on http://127.0.0.1:5000 (Press CTRL+C to quit)
```

Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🧪 Running Unit Tests

To run the automated test suite verifying all routes, database operations, and AI fallback:
```powershell
python test_app.py
```
Expected output:
```text
Ran 8 tests in 0.18s
OK
```

---

## 📡 REST API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `GET /` | `GET` | Renders the web application |
| `GET /api/status` | `GET` | Returns server health and AI configuration status |
| `POST /api/chat` | `POST` | Accepts `{ message, history }`, returns AI or Knowledge Engine response |
| `GET /api/tips` | `GET` | Retrieves tips (supports `?category=...` and `?search=...`) |
| `GET /api/challenges` | `GET` | Returns all eco-challenges, completion status, XP points, and rank |
| `POST /api/challenges/complete` | `POST` | Toggles challenge status `{ challenge_id, completed }` |
| `GET /api/stats` | `GET` | Returns campus impact metrics (bottles, water, kWh, CO₂) |
| `POST /api/feedback` | `POST` | Submits feedback `{ user_name, user_role, rating, category, comment }` |
| `GET /api/feedback` | `GET` | Retrieves recent community feedback and average rating |
| `GET /api/activities` | `GET` | Retrieves recent campus eco-activities feed |

---

## 🎓 College Project Demonstration Guide

When presenting this project:
1. **Hero Section:** Showcase the nature-inspired forest green design, animated quick stats, and the responsive mascot.
2. **AI Chatbot:**
   - Click the suggested questions (e.g., *"How can I save water in college?"*).
   - Test typing a custom question: *"Where should I dispose of plastic bottles on campus?"*.
   - Demonstrate the **Copy message** and **Speech synthesis (Audio read-aloud)** buttons.
3. **Daily Eco-Challenges:**
   - Mark a challenge as completed (e.g., *"Bring a Reusable Water Bottle"*).
   - Show how the **XP counter**, **progress bar**, and **rank badge** instantly update in real-time.
4. **Categorized Tips:**
   - Use the category pills (*Water*, *Energy*, *Waste*, *Air*, *Trees*, *Transit*).
   - Test the live search bar (*e.g., search "AC" or "tree"*).
   - Click **Ask Bot** on a tip to automatically transition into a conversation with EcoBot.
5. **Dashboard & Feedback:**
   - Point out the dynamic metrics and sample data disclaimer note.
   - Submit a 5-star review using the interactive stars and see it appear in the community reviews feed.

---

## 🔒 Security Best Practices Implemented
- **No Client-Side Secrets:** API keys are never present in frontend HTML or JavaScript.
- **Sanitized SQL Queries:** All database transactions use parameterized queries to prevent SQL injection.
- **HTML Escaping:** User inputs and chat messages are escaped to mitigate XSS attacks.
- **Graceful Error Handling:** Network and quota failures are caught without crashing the application.

---

## 📜 License
Developed for educational, university, and community sustainability initiatives. Free to use and extend.
