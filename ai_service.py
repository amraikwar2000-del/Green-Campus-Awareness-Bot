import os
import re
from config import Config

# System prompt required by specifications
SYSTEM_PROMPT = (
    "You are EcoBot, a friendly environmental awareness assistant for college campuses. "
    "Help students and staff adopt sustainable habits. Provide accurate, practical, "
    "easy-to-understand answers about recycling, water conservation, energy efficiency, "
    "biodiversity, pollution prevention, and climate change. Encourage responsible environmental "
    "behavior and suggest realistic campus activities. Never invent campus-specific facilities, "
    "recycling locations, statistics, or completed activities. If you do not know a campus-specific "
    "detail, ask the user or recommend checking with campus administration."
)

# Suggested follow-up chips bank
DEFAULT_SUGGESTED_QUESTIONS = [
    "How can I make my campus greener?",
    "How can I save water in college?",
    "Where should I dispose of plastic waste?",
    "What is composting?",
    "How can students reduce electricity consumption?"
]

# Curated environmental responses for offline/fallback mode
KNOWLEDGE_BASE = [
    {
        "keywords": [r"\bmake\s+.*campus\s+greener\b", r"\bgreen\s+campus\b", r"\bhow\s+can\s+i\s+help\b", r"\bstart\b"],
        "answer": (
            "🌿 **Top Ways to Make Your Campus Greener:**\n\n"
            "1. **Eliminate Single-Use Plastic:** Carry a reusable steel bottle and cloth bag to classes and the cafeteria.\n"
            "2. **Save Electricity:** Turn off classroom projectors, lab PCs, and ceiling fans when lectures finish.\n"
            "3. **Segregate Waste:** Drop wet food leftovers into green bins and paper/clean plastics into blue bins.\n"
            "4. **Green Your Commute:** Walk, ride a bicycle, or carpool with department peers.\n"
            "5. **Join or Form an Eco-Club:** Organize campus cleanliness drives and native tree plantation drives.\n\n"
            "*Tip: Check out our **Eco-Challenges tab** right here to start tracking your daily green deeds!*"
        ),
        "suggestions": [
            "How can I save water in college?",
            "Where should I dispose of plastic waste?",
            "How can students reduce electricity consumption?"
        ]
    },
    {
        "keywords": [r"\bsave\s+water\b", r"\bwater\s+conservation\b", r"\bleak\b", r"\btap\b", r"\bwater\b"],
        "answer": (
            "💧 **Practical Water Conservation Tips for College:**\n\n"
            "• **Check Faucets:** Ensure restroom taps in hostels and academic blocks are tightly shut. A slow drip wastes over 15 liters of clean water every day!\n"
            "• **Report Plumbing Faults:** Notice a leaking flush, sprinkler, or garden pipe? Report it immediately to the campus estate office.\n"
            "• **Mindful Hydration:** When refilling your water bottle, don't dump leftover clean water down the drain—use it to water balcony potted plants.\n"
            "• **Hostel Showers:** Keep hostel bucket baths or showers under 5 minutes to conserve hundreds of liters weekly."
        ),
        "suggestions": [
            "How can students reduce electricity consumption?",
            "What is composting?",
            "How can I make my campus greener?"
        ]
    },
    {
        "keywords": [r"\bplastic\b", r"\bdispose\s+.*plastic\b", r"\bsingle-use\b", r"\bbottles?\b", r"\bwrapper\b"],
        "answer": (
            "♻️ **Managing & Disposing of Plastic Waste on Campus:**\n\n"
            "1. **Rinse & Dry:** Clean recyclable plastic (water bottles, clean food wrappers) before dropping them into **Blue Recycling Bins**.\n"
            "2. **Crush PET Bottles:** Remove bottle caps and squeeze empty beverage bottles flat to save bin volume.\n"
            "3. **Avoid Canteen Plastics:** Request canteen vendors to serve meals on washable plates and avoid plastic disposable cutlery and straws.\n"
            "4. **Campus Specifics:** Inquire with your campus administration or facility manager about the location of dedicated plastic drop-off points or collection drives."
        ),
        "suggestions": [
            "What is composting?",
            "Where should I dispose of plastic waste?",
            "How can I make my campus greener?"
        ]
    },
    {
        "keywords": [r"\bcompost\b", r"\bcomposting\b", r"\bfood\s+waste\b", r"\borganic\b"],
        "answer": (
            "🌱 **What is Composting & How Can It Work on Campus?**\n\n"
            "Composting is the biological decomposition of organic matter (like food scraps, fruit peels, fallen autumn leaves, and tea grounds) into dark, nutrient-rich soil fertilizer!\n\n"
            "• **Green Materials (Nitrogen):** Fruit peels, leftover veggies, hostel mess salad leftovers.\n"
            "• **Brown Materials (Carbon):** Dry campus garden leaves, plain brown cardboard, shredded scrap paper.\n"
            "• **Campus Benefit:** An on-campus compost pit cuts methane emissions from landfills and supplies free fertilizer for campus flowering trees and herbal gardens!"
        ),
        "suggestions": [
            "How to organize a tree plantation drive?",
            "How can I make my campus greener?",
            "Where should I dispose of plastic waste?"
        ]
    },
    {
        "keywords": [r"\belectricity\b", r"\benergy\b", r"\bpower\b", r"\blights?\b", r"\bac\b", r"\bfans?\b"],
        "answer": (
            "⚡ **How Students Can Reduce Electricity Consumption:**\n\n"
            "1. **The 'Last Out, Lights Out' Rule:** Always flick off switches when leaving seminar rooms, club rooms, or dorms.\n"
            "2. **Defeat Phantom Power:** Laptop chargers, phone plugs, and desk lamps draw power even on standby. Unplug them when fully charged.\n"
            "3. **Air Conditioner Setting:** Keep AC temperatures at **24°C–25°C** in computer labs and auditoriums—each degree higher saves ~6% energy.\n"
            "4. **Take the Stairs:** Using the stairs instead of the elevator for 2–3 floors saves substantial electrical power and keeps you fit!"
        ),
        "suggestions": [
            "How can I save water in college?",
            "What is composting?",
            "How can I make my campus greener?"
        ]
    },
    {
        "keywords": [r"\btree\b", r"\bplant\b", r"\bplantation\b", r"\bbiodiversity\b", r"\bflora\b", r"\bfauna\b"],
        "answer": (
            "🌳 **Campus Tree Plantation & Biodiversity Protection:**\n\n"
            "• **Choose Native Species:** Native trees (like Neem, Peepal, Ashoka, or Gulmohar) thrive in local soil, withstand seasons without intensive irrigation, and sustain native butterflies and birds.\n"
            "• **Adopt-a-Tree Initiative:** Coordinate with your college botany department or green club to plant saplings during monsoon or Earth Day, and assign student guardians to water them weekly.\n"
            "• **Bird Water Bowls:** Set out shallow terracotta water saucers on shaded dormitory terraces to help birds survive scorching summer months."
        ),
        "suggestions": [
            "What is composting?",
            "How can I save water in college?",
            "How can I make my campus greener?"
        ]
    },
    {
        "keywords": [r"\bhello\b", r"\bhi\b", r"\bhey\b", r"\bgreetings\b", r"\bgood\s+(morning|afternoon|evening)\b"],
        "answer": (
            "👋 **Hello there! I'm EcoBot, your Green Campus Awareness Assistant.** 🌿\n\n"
            "I'm here to help you learn about sustainable campus living, waste recycling, saving water and power, and organizing eco-drives.\n\n"
            "How can I help you make our campus cleaner and greener today?"
        ),
        "suggestions": DEFAULT_SUGGESTED_QUESTIONS
    },
    {
        "keywords": [r"\bwho\s+are\s+you\b", r"\bwhat\s+can\s+you\s+do\b", r"\babout\s+you\b"],
        "answer": (
            "🤖 **I'm EcoBot!**\n\n"
            "I am an environmental assistant designed to guide college students, faculty, and campus staff toward sustainable everyday practices. "
            "You can ask me questions about recycling, water and power conservation, composting, tree plantation, climate change, and reducing canteen waste."
        ),
        "suggestions": DEFAULT_SUGGESTED_QUESTIONS
    }
]

def get_fallback_response(user_message: str):
    """Provides a tailored environmental answer based on curated knowledge when OpenAI API is not configured."""
    lower_msg = user_message.strip().lower()

    for item in KNOWLEDGE_BASE:
        for pattern in item["keywords"]:
            if re.search(pattern, lower_msg):
                return {
                    "response": item["answer"],
                    "suggestions": item["suggestions"],
                    "source": "knowledge_engine",
                    "note": "Response generated by EcoBot Campus Environmental Knowledge Engine."
                }

    # Generic intelligent environmental fallback
    generic_answer = (
        f"🌿 That's a great question about sustainable living!\n\n"
        f"Adopting eco-friendly habits on campus starts with small everyday actions: "
        f"reducing single-use packaging, turning off unused lab equipment and lights, carrying a refillable flask, "
        f"and separating recyclables into proper bins.\n\n"
        f"For campus-specific facilities, designated waste drop-offs, or tree plantation permissions, "
        f"we recommend checking with your campus administration or environmental society."
    )
    return {
        "response": generic_answer,
        "suggestions": DEFAULT_SUGGESTED_QUESTIONS[:3],
        "source": "knowledge_engine",
        "note": "Response generated by EcoBot Campus Environmental Knowledge Engine."
    }

def generate_chat_response(user_message: str, history: list = None):
    """
    Handles chatbot interaction. If OPENAI_API_KEY is configured and valid,
    calls OpenAI Chat Completions API with the required system instructions.
    Otherwise gracefully falls back to the local knowledge engine.
    """
    user_message = user_message.strip()
    if not user_message:
        return {
            "error": "Message cannot be empty",
            "response": "Please enter an environmental question to chat with EcoBot!",
            "source": "error"
        }

    api_key = Config.OPENAI_API_KEY

    # Check if OpenAI API key is configured
    if not api_key or api_key.startswith("your-") or "YOUR_OPENAI_API_KEY" in api_key:
        fallback = get_fallback_response(user_message)
        fallback["api_status"] = "unconfigured"
        fallback["api_notice"] = (
            "EcoBot is currently operating in Campus Knowledge Engine mode. "
            "Add your OpenAI API key in .env file to enable live generative AI responses."
        )
        return fallback

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Append limited prior conversation history for context (up to last 6 messages)
        if history and isinstance(history, list):
            for msg in history[-6:]:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    role = "user" if msg["role"] == "user" else "assistant"
                    messages.append({"role": role, "content": str(msg["content"])[:1000]})

        # Append current user query
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )

        bot_content = response.choices[0].message.content

        # Select dynamic suggested questions
        suggestions = [
            "How can I save water in college?",
            "What is composting?",
            "How can students reduce electricity consumption?",
            "Where should I dispose of plastic waste?"
        ]

        return {
            "response": bot_content,
            "suggestions": suggestions,
            "source": "openai",
            "model": Config.OPENAI_MODEL,
            "api_status": "connected"
        }

    except Exception as e:
        # Graceful fallback on API error / quota limit / network issue
        fallback = get_fallback_response(user_message)
        fallback["api_status"] = "error"
        fallback["api_error"] = str(e)
        fallback["api_notice"] = (
            f"OpenAI service notice: {str(e)[:120]}... EcoBot fell back to the local Campus Knowledge Engine."
        )
        return fallback
