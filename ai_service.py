"""
AI Service module for Green Campus Awareness Bot (EcoBot).
Handles OpenAI API calls with secure key retrieval, configurable models,
conversation history preservation, input validation, and an extensive
environmental campus knowledge engine fallback when API key is unconfigured.
"""

import os
import re
from dotenv import load_dotenv

load_dotenv()

# Required system prompt per project specification
ECOBOT_SYSTEM_PROMPT = (
    "You are EcoBot, a friendly environmental awareness assistant for college campuses. "
    "Help students and staff adopt sustainable habits. Provide accurate, practical, "
    "easy-to-understand answers about recycling, water conservation, energy efficiency, "
    "biodiversity, pollution prevention, and climate change. Encourage responsible environmental "
    "behavior and suggest realistic campus activities. Never invent campus-specific facilities, "
    "recycling locations, statistics, or completed activities. If you do not know a campus-specific "
    "detail, ask the user or recommend checking with campus administration."
)


def get_ai_status():
    """Check whether OpenAI API key is configured."""
    key = os.getenv("OPENAI_API_KEY", "").strip()
    is_live = bool(key and not key.startswith("your_") and not key.startswith("sk-placeholder") and len(key) > 15)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    return {
        "is_live": is_live,
        "model": model,
        "status_label": f"Live OpenAI ({model})" if is_live else "EcoBot Smart Campus Engine (Demo Mode)",
        "has_key": is_live
    }


def validate_user_message(message):
    """Validate user message content and length."""
    if not message or not isinstance(message, str):
        return False, "Message cannot be empty."

    cleaned = message.strip()
    if len(cleaned) == 0:
        return False, "Message cannot be empty."

    if len(cleaned) > 1000:
        return False, "Message is too long. Please keep questions under 1000 characters."

    return True, cleaned


def generate_chat_response(user_message, history=None):
    """
    Generate response for EcoBot.
    Attempts OpenAI API first if key is present; otherwise falls back gracefully
    to the rule-based & semantic campus environmental knowledge base.
    """
    # 1. Validate
    is_valid, validation_or_clean = validate_user_message(user_message)
    if not is_valid:
        return {
            "success": False,
            "response": validation_or_clean,
            "source": "validation_error"
        }

    cleaned_msg = validation_or_clean
    ai_status = get_ai_status()

    # 2. Try live OpenAI API if configured
    if ai_status["is_live"]:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            messages = [{"role": "system", "content": ECOBOT_SYSTEM_PROMPT}]

            # Add recent history (up to last 6 turns to manage context)
            if history and isinstance(history, list):
                for turn in history[-6:]:
                    role = turn.get("role")
                    content = turn.get("content")
                    if role in ("user", "assistant") and content:
                        messages.append({"role": role, "content": str(content)[:800]})

            # Add current user prompt
            messages.append({"role": "user", "content": cleaned_msg})

            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=650,
                temperature=0.7
            )

            bot_reply = completion.choices[0].message.content.strip()
            return {
                "success": True,
                "response": bot_reply,
                "source": "openai",
                "model": model_name
            }

        except Exception as e:
            # Fallback gracefully with error explanation and smart local knowledge
            fallback_reply = get_smart_fallback_response(cleaned_msg)
            return {
                "success": True,
                "response": fallback_reply,
                "source": "fallback",
                "note": f"OpenAI API call encountered an issue ({type(e).__name__}). EcoBot responded using the built-in campus environmental knowledge base."
            }

    # 3. Use Smart Local Campus Knowledge Base
    reply = get_smart_fallback_response(cleaned_msg)
    return {
        "success": True,
        "response": reply,
        "source": "smart_local_engine",
        "note": "Running in demonstration mode with built-in campus environmental knowledge base. Add OPENAI_API_KEY in .env for live GPT responses."
    }


def get_smart_fallback_response(msg):
    """
    Rich environmental campus awareness rule and semantic engine.
    Ensures that college students and staff receive thorough, friendly,
    actionable, and formatted responses for any campus sustainability query.
    """
    text = msg.lower().strip()

    # Common greetings
    if re.search(r"^(hi|hello|hey|greetings|good\s*(morning|afternoon|evening)|yo\b)", text):
        return (
            "Hello there! 🌿 I'm **EcoBot**, your campus green guide. "
            "I'm here to help you adopt sustainable habits, save water and electricity, "
            "reduce plastic waste, and keep our college clean and thriving.\n\n"
            "What would you like to explore today? You can try asking:\n"
            "• *How can I make my campus greener?*\n"
            "• *How can I save water in college?*\n"
            "• *Where should I dispose of plastic waste?*\n"
            "• *What is composting?*\n"
            "• *How can students reduce electricity consumption?*"
        )

    # Question 1: How can I make my campus greener?
    if "make" in text and "campus" in text and ("greener" in text or "green" in text):
        return (
            "### 🌱 Top Ways to Make Your Campus Greener:\n\n"
            "1. **Eliminate Single-Use Plastics:** Carry a reusable stainless steel water bottle and cloth tote bag to classes and food courts.\n"
            "2. **Audit Energy Habits:** Switch off projector screens, ACs, lights, and fans whenever you leave seminar rooms or study pods.\n"
            "3. **Practice Twin-Bin Segregation:** Ensure food waste goes strictly into organic/wet bins and clean paper/plastics into dry recyclable bins.\n"
            "4. **Adopt Native Campus Flora:** Participate in campus tree plantation drives or adopt a potted plant for your dormitory desk.\n"
            "5. **Commute Sustainably:** Walk, cycle, or carpool to campus instead of driving solo.\n"
            "6. **Join or Start a Green Club:** Mobilize student peers for weekly campus cleanliness drives and awareness workshops!\n\n"
            "*Campus Tip: Check with campus administration or your student council for upcoming environmental club drives and recycling points!*"
        )

    # Question 2: How can I save water in college?
    if "save water" in text or "water conservation" in text or ("water" in text and ("college" in text or "dorm" in text or "hostel" in text or "save" in text)):
        return (
            "### 💧 Practical Water Conservation Tips for College:\n\n"
            "• **Report Leaks Immediately:** A single dripping faucet wastes up to 30 liters daily! Alert hostel wardens or facilities maintenance when you spot dripping taps or running flush tanks.\n"
            "• **Turn Off While Brushing/Scrubbing:** Don't let taps run continuously when lathering soap, brushing teeth, or washing lab beakers.\n"
            "• **Take Shorter Showers:** Cutting 2–3 minutes from your hostel shower can save 20–30 liters of heated water each time.\n"
            "• **Mindful Laundry Loads:** Only run washing machines in dorms when you have full laundry loads.\n"
            "• **Refill Smartly:** Don't dump out half-full water bottles down the sink—use leftover water to hydrate campus flower beds and potted shrubs!\n\n"
            "*Did you know? Producing one plastic bottled beverage requires up to three times the water contained inside it! Refill your own flask instead.*"
        )

    # Question 3: Where should I dispose of plastic waste?
    if "dispose" in text and "plastic" in text or ("where" in text and "plastic" in text) or "plastic waste" in text:
        return (
            "### ♻️ How to Properly Dispose of Plastic Waste on Campus:\n\n"
            "1. **Empty & Rinse First:** Recycling centers cannot process plastic containers coated with food grease, milk, or sauces. Give your bottles and containers a quick rinse.\n"
            "2. **Use the Dry / Recyclable Bin:** Deposit clean PET bottles, hard plastic lunchboxes, and caps into the blue or dry waste bins.\n"
            "3. **Separate Soft & Multi-Layer Plastic:** Snack wrappers and chip packets (metallized films) are non-recyclable in standard municipal lines—look for specialized drop boxes or minimize purchasing them.\n"
            "4. **Campus Recycling Points:** Most college cafeterias, library lobbies, and dorm entrances feature designated recycling collection points. If your department lacks one, check with campus facilities to install dedicated bins!\n\n"
            "*Best Practice: The cleanest plastic is the plastic you never buy! Bring a reusable thermos for your daily tea, coffee, or smoothie.*"
        )

    # Question 4: What is composting?
    if "what is composting" in text or "compost" in text:
        return (
            "### 🍂 What is Composting?\n\n"
            "**Composting** is nature's ultimate recycling process! It is the natural biological decomposition of organic matter (such as cafeteria fruit peels, vegetable scraps, coffee grounds, and dry leaves) by beneficial microorganisms into dark, crumbly, nutrient-rich soil known as **humus** or 'black gold'.\n\n"
            "**Why is it crucial for colleges?**\n"
            "• **Diverts Waste:** Food waste in landfills rots anaerobically and produces **methane**, a greenhouse gas 28x more potent than CO2.\n"
            "• **Nourishes Campus Soil:** Campus compost can fertilize college gardens, botanical reserves, and potted plants without chemical fertilizers.\n\n"
            "**The Easy 4-Element Recipe:**\n"
            "1. *Greens (Nitrogen):* Veggie scraps, tea bags, fruit peels.\n"
            "2. *Browns (Carbon):* Fallen campus leaves, shredded cardboard, dry twigs.\n"
            "3. *Moisture:* Damp like a wrung-out sponge.\n"
            "4. *Air (Oxygen):* Turned occasionally to keep microbes active."
        )

    # Question 5: How can students reduce electricity consumption?
    if "reduce electricity" in text or "save electricity" in text or "electricity consumption" in text or "energy" in text:
        return (
            "### ⚡ How Students Can Slash Campus Electricity Use:\n\n"
            "• **Kill Vampire / Phantom Power:** Chargers and adapters plugged into wall sockets draw power even when your phone or laptop is unplugged. Turn the wall switch off!\n"
            "• **Optimize Classroom AC & Fans:** Set air conditioners to an eco-optimal **24°C–25°C (75°F–77°F)**. Each 1°C increase saves 6% cooling electricity.\n"
            "• **Leverage Natural Daylighting:** Open classroom and dorm window shades during morning and afternoon study hours.\n"
            "• **Activate Sleep Mode on Computers:** Set laptop displays to turn off after 5 minutes of inactivity in the library or computer labs.\n"
            "• **The 'Last-Out' Responsibility:** If you are the last student leaving a lecture theatre, lab, or club room, ensure all lights, projector, and fans are toggled off.\n\n"
            "*Tip: Together, a university student body can reduce campus greenhouse emissions by several metric tons each semester just by practicing the Last-Out rule!*"
        )

    # Tree plantation and biodiversity
    if "tree" in text or "plant" in text or "plantation" in text or "biodiversity" in text:
        return (
            "### 🌳 Tree Plantation & Biodiversity on Campus:\n\n"
            "Trees are the lungs of our college campus! A single mature tree absorbs up to **22 kg of carbon dioxide** every year while releasing fresh oxygen and lowering local ambient temperatures through shade and transpiration.\n\n"
            "**Top Campus Biodiversity Actions:**\n"
            "• **Select Native Species:** Native trees (like Neem, Peepal, Gulmohar, Oak, or indigenous fruit trees) require less water and support native bird species.\n"
            "• **Nurture After Planting:** The real work starts after planting! Set up a watering schedule with hostel peers for the first 6–12 months.\n"
            "• **Create Pollinator Zones:** Encourage planting indigenous flowering bushes for bees and butterflies.\n\n"
            "*Take our Eco-Challenge: Check out the 'Plant and Care for a Tree' challenge in the Eco-Challenges tab!*"
        )

    # Climate change and air pollution
    if "climate change" in text or "global warming" in text or "air pollution" in text or "pollution" in text:
        return (
            "### 🌍 Understanding Climate Change & Air Pollution on Campus:\n\n"
            "**Climate change** is driven by human greenhouse gas emissions (carbon dioxide, methane, nitrous oxide) trapping heat in Earth's atmosphere. This causes extreme weather, rising sea levels, and biodiversity loss.\n\n"
            "**How Colleges Contribute and Can Lead:**\n"
            "• **Campus Carbon Footprint:** Electricity consumption, diesel generators, cafeteria food waste, and commuter transport are major campus emission sources.\n"
            "• **Air Quality:** Idling cars and two-wheelers in college parking lots generate hazardous PM2.5 particles. Advocating for **No-Idling Zones** and bicycle pathways keeps campus air crisp and clean.\n"
            "• **Campus Solar:** Urging university administration to transition rooftop acreage into photovoltaic solar arrays can power 30–60% of campus demand with clean sun energy!"
        )

    # Recycling and waste management
    if "recycl" in text or "waste" in text or "segregat" in text:
        return (
            "### 🗑️ Campus Waste Management & Recycling 101:\n\n"
            "The golden rule of campus waste is the **Hierarchy of Waste:**\n"
            "1. **Refuse:** Say no to single-use promotional items, brochures, and plastic giveaways.\n"
            "2. **Reduce:** Print double-sided notes or keep digital textbooks on tablets.\n"
            "3. **Reuse:** Bring your own travel mug, containers, and stationery cases.\n"
            "4. **Recycle:** Paper, aluminum cans, clean cardboard, and clean plastics.\n"
            "5. **Rot (Compost):** Apple cores, banana peels, and hostel garden clippings.\n\n"
            "*Remember: Contamination ruins recycling! Always empty liquids before placing cups or bottles into recycling bins.*"
        )

    # General sustainable habits / advice
    return (
        "### 🌿 EcoBot's Green Campus Advice:\n\n"
        f"Thank you for asking about **'{msg}'**!\n\n"
        "Here are three practical, high-impact actions you and your fellow students can take right away:\n"
        "1. **Audit Daily Habits:** Little actions compound—reusing a water flask, switching off lights in empty classrooms, and saying no to plastic cutlery prevent hundreds of pounds of waste each semester.\n"
        "2. **Collaborate with Campus Clubs:** Environmental action is more fun and impactful when done together. Join your campus Eco Club or organize department green drives.\n"
        "3. **Engage with Administration:** If your college needs better recycling bins, composting units, or bicycle racks, draft a student proposal for campus facilities!\n\n"
        "Would you like more specific tips on **Water Conservation**, **Energy Saving**, **Waste Recycling**, or **Tree Plantation**? Just let me know!"
    )
