"""
Database management module for Green Campus Awareness Bot.
Uses SQLite for zero-configuration, reliable persistence of tips,
challenges, recorded eco-activities, user feedback, and chatbot interactions.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "greencampus.db")


def get_db_connection():
    """Establish and return a SQLite connection with row dictionary access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and seed baseline campus data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Tips Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            icon TEXT NOT NULL,
            impact_metric TEXT NOT NULL,
            tags TEXT
        )
    """)

    # Create Eco-Challenges Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            points INTEGER NOT NULL DEFAULT 50,
            icon TEXT NOT NULL,
            frequency TEXT NOT NULL DEFAULT 'Daily',
            is_completed INTEGER NOT NULL DEFAULT 0,
            completed_count INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Create Activity Log Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Student',
            activity_type TEXT NOT NULL,
            description TEXT NOT NULL,
            impact_value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Feedback Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Student',
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            category TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create Chat Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Seed Tips if empty
    cursor.execute("SELECT COUNT(*) as count FROM tips")
    if cursor.fetchone()["count"] == 0:
        seed_tips(cursor)

    # Seed Challenges if empty
    cursor.execute("SELECT COUNT(*) as count FROM challenges")
    if cursor.fetchone()["count"] == 0:
        seed_challenges(cursor)

    # Seed Activities if empty
    cursor.execute("SELECT COUNT(*) as count FROM activities")
    if cursor.fetchone()["count"] == 0:
        seed_activities(cursor)

    # Seed Feedback if empty
    cursor.execute("SELECT COUNT(*) as count FROM feedback")
    if cursor.fetchone()["count"] == 0:
        seed_feedback(cursor)

    conn.commit()
    conn.close()


def seed_tips(cursor):
    """Seed comprehensive, categorized environmental tips."""
    tips_data = [
        # Water Conservation
        (
            "Water Conservation",
            "Report Dripping Taps Promptly",
            "A single faucet dripping once per second can waste over 3,000 gallons (11,000 liters) of clean water per year. Report leaks in washrooms or labs to campus maintenance immediately.",
            "bi-droplet-half",
            "Saves ~30 Liters/day per tap",
            "water, facilities, maintenance"
        ),
        (
            "Water Conservation",
            "Carry a Refillable Water Bottle",
            "Filling your own insulated flask at campus purified water stations saves thousands of disposable plastic bottles and the 3x volume of water required to manufacture them.",
            "bi-cup-straw",
            "Diverts 150+ plastic bottles/year",
            "refill, plastic-free, hydration"
        ),
        (
            "Water Conservation",
            "Mindful Lab & Cafeteria Rinsing",
            "Turn off the tap while scrubbing lab glassware or washing hands. Use half-sink soaking methods rather than running continuous streams of water.",
            "bi-water",
            "Cuts water flow by 40%",
            "labs, dining, hygiene"
        ),

        # Energy Conservation
        (
            "Energy Conservation",
            "The Last-Out Light & Fan Rule",
            "Always switch off overhead lights, air conditioners, and projector displays when leaving empty lecture halls, study pods, or seminar rooms.",
            "bi-lightbulb",
            "Reduces 1.5 kWh/hour per hall",
            "electricity, classrooms, habits"
        ),
        (
            "Energy Conservation",
            "Unplug Phantom Load Chargers",
            "Laptops and phone chargers plugged into sockets draw electricity even when not charging any device. Unplug power strips at the end of the study session.",
            "bi-plug",
            "Saves up to 10% standby power",
            "dorm, electronics, power"
        ),
        (
            "Energy Conservation",
            "Embrace Natural Sunlight & Air",
            "Open classroom window blinds to take advantage of daylight. Natural light boosts focus and cognitive performance while giving campus HVAC systems a well-deserved rest.",
            "bi-brightness-high",
            "Lowers indoor cooling load",
            "wellness, daylight, climate"
        ),

        # Waste Management
        (
            "Waste Management",
            "Twin-Bin Waste Segregation",
            "Keep dry recyclables (paper, clean plastics, aluminum cans) strictly separate from wet food waste. Organic leftovers contaminate paper and render it unrecyclable.",
            "bi-recycle",
            "Prevents 80% bin contamination",
            "recycling, segregation, bins"
        ),
        (
            "Waste Management",
            "Say No to Single-Use Cutlery",
            "Keep a compact set of reusable stainless steel or bamboo cutlery in your backpack for cafeteria meals, campus festivals, and takeout lunches.",
            "bi-slash-circle",
            "Prevents 200 plastic utensils/year",
            "dining, zerowaste, lifestyle"
        ),
        (
            "Waste Management",
            "Campus Composting of Organic Waste",
            "Cafeteria vegetable scraps, coffee grounds, and fallen leaves can be turned into rich organic soil amendment for campus botanical gardens instead of producing methane in landfills.",
            "bi-flower1",
            "Converts scraps to fertile humus",
            "compost, soil, organic"
        ),

        # Air Quality
        (
            "Air Quality",
            "Indoor Air-Purifying Dorm Plants",
            "Plants like Snake Plants (Sansevieria), Spider Plants, and Peace Lilies filter volatile organic compounds (VOCs) and release fresh oxygen into study rooms and hostels.",
            "bi-wind",
            "Improves indoor air by 25%",
            "hostel, air, greenery"
        ),
        (
            "Air Quality",
            "Maintain No-Idling Zones",
            "Campus vehicle parking lots and pickup points generate high particulate matter when engines idle. Advocate for strict 60-second anti-idling policies on campus grounds.",
            "bi-exclamation-triangle",
            "Eliminates micro-pollutants",
            "traffic, emissions, health"
        ),

        # Biodiversity & Tree Plantation
        (
            "Biodiversity & Trees",
            "Plant & Adopt a Native Campus Sapling",
            "Native tree species require less artificial watering, resist local pests, and offer nesting sites and nectar for native birds, bees, and butterflies.",
            "bi-tree",
            "Absorbs ~22kg CO2/year when mature",
            "trees, plantation, wildlife"
        ),
        (
            "Biodiversity & Trees",
            "Create Pollinator Pockets",
            "Plant small clusters of indigenous flowering shrubs around campus pathways to support local pollinating insects critical for ecosystem health.",
            "bi-bug",
            "Protects bee & pollinator corridors",
            "pollinators, ecology, flora"
        ),

        # Sustainable Transportation
        (
            "Sustainable Transportation",
            "Pedal Power: Campus Cycling",
            "Biking between hostels, academic blocks, and campus libraries produces zero carbon emissions, reduces traffic congestion, and provides great cardiovascular exercise.",
            "bi-bicycle",
            "Eliminates 150g CO2 per kilometer",
            "bicycles, active travel, fitness"
        ),
        (
            "Sustainable Transportation",
            "Campus Carpooling & Public Transit",
            "Commuter students and staff sharing rides or taking the university shuttle slash carbon footprints and parking demand by more than 60%.",
            "bi-bus-front",
            "Cuts transport emissions in half",
            "transit, carpool, commute"
        )
    ]

    cursor.executemany("""
        INSERT INTO tips (category, title, content, icon, impact_metric, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    """, tips_data)


def seed_challenges(cursor):
    """Seed standard campus eco-challenges."""
    challenges_data = [
        (
            "Bring a Reusable Water Bottle",
            "Waste Management",
            "Carry and refill your own reusable water bottle all day across classes and sports practice instead of buying single-use bottled water.",
            40,
            "bi-cup-straw",
            "Daily",
            1,
            248
        ),
        (
            "Avoid Single-Use Plastic Today",
            "Waste Management",
            "Decline disposable straws, plastic shopping bags, disposable food wrappers, and plastic coffee cup lids for the entire day.",
            50,
            "bi-bag-x",
            "Daily",
            1,
            182
        ),
        (
            "Switch Off Lights & Fans When Not Needed",
            "Energy Conservation",
            "Inspect your study hall, dorm room, or laboratory and ensure all unoccupied lights, fans, and screens are switched off.",
            35,
            "bi-lightning-charge",
            "Daily",
            0,
            310
        ),
        (
            "Separate Wet and Dry Waste",
            "Waste Management",
            "Strictly segregate organic food leftovers from paper, cardboard, and clean plastics at all cafeteria and dorm disposal bins.",
            45,
            "bi-recycle",
            "Daily",
            1,
            195
        ),
        (
            "Participate in a Campus Cleanliness Drive",
            "Campus Community",
            "Join peers or the green club for a 30-minute campus litter cleanup along walkways, sports grounds, or garden benches.",
            75,
            "bi-trash",
            "Weekly",
            0,
            89
        ),
        (
            "Plant and Care for a Tree / Sapling",
            "Biodiversity & Trees",
            "Plant a sapling in the campus garden or nurture an indoor potted plant with water, soil aerating, and sunlight.",
            100,
            "bi-tree",
            "Weekly",
            0,
            64
        ),
        (
            "Zero-Emission Commute (Walk or Cycle)",
            "Sustainable Transportation",
            "Walk, cycle, or skateboard to all your campus lectures and activities today rather than using motorbikes or cars.",
            60,
            "bi-bicycle",
            "Daily",
            0,
            142
        ),
        (
            "Conduct a Dorm or Lab Energy Audit",
            "Energy Conservation",
            "Review power outlets, check for phantom plug draw, verify monitor sleep timers, and optimize heating/cooling settings.",
            80,
            "bi-shield-check",
            "Campus Drive",
            0,
            57
        )
    ]

    cursor.executemany("""
        INSERT INTO challenges (title, category, description, points, icon, frequency, is_completed, completed_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, challenges_data)


def seed_activities(cursor):
    """Seed initial campus activity demonstration records."""
    activities_data = [
        (
            "Aarav Sharma",
            "Student",
            "Plant and care for a tree",
            "Planted two Neem saplings near the South Campus library garden and set up drip mulch.",
            "2 Saplings Planted",
            "2026-10-14 10:30:00"
        ),
        (
            "Dr. Priya Venkat",
            "Faculty",
            "Energy Conservation",
            "Audited Department of Environmental Science labs and replaced halogen task lights with 8W LED tubes.",
            "Saved 120 kWh/mo",
            "2026-10-14 14:15:00"
        ),
        (
            "Rohan Patel",
            "Student",
            "Campus Cleanliness Drive",
            "Organized student hostel team cleanup collecting 14kg of recyclable cardboard and plastics.",
            "14 kg Recycled",
            "2026-10-15 09:00:00"
        ),
        (
            "Campus Green Society",
            "Staff",
            "Waste Segregation",
            "Installed dual-color color-coded waste stations at central cafeteria and food court.",
            "4 New Stations",
            "2026-10-15 11:45:00"
        ),
        (
            "Meera Nair",
            "Student",
            "Avoid Single-Use Plastic",
            "Completed 7 continuous days with zero disposable single-use cups and plastic cutlery.",
            "21 Items Diverted",
            "2026-10-15 16:20:00"
        )
    ]

    cursor.executemany("""
        INSERT INTO activities (student_name, role, activity_type, description, impact_value, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, activities_data)


def seed_feedback(cursor):
    """Seed community reviews and suggestions."""
    feedback_data = [
        (
            "Ananya Deshmukh",
            "Student",
            5,
            "Chatbot Accuracy",
            "EcoBot gave super practical advice on how to compost cafeteria scraps in our dorm pots. Loved the quick replies!",
            "2026-10-14 18:30:00"
        ),
        (
            "Prof. Rajesh Kumar",
            "Faculty",
            5,
            "Campus Ideas",
            "Fantastic awareness platform. Students in our mechanical department are already tracking energy conservation daily.",
            "2026-10-15 08:20:00"
        ),
        (
            "Sunita Verma",
            "Campus Staff",
            4,
            "UI Experience",
            "The green nature design is very clean and pleasant. Suggest adding more campus water refill station markers.",
            "2026-10-15 13:10:00"
        )
    ]

    cursor.executemany("""
        INSERT INTO feedback (user_name, role, rating, category, message, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, feedback_data)


# -------------------------------------------------------------
# Database Query Helpers
# -------------------------------------------------------------

def get_all_tips(category=None, search=None):
    """Retrieve tips with optional category and search filters."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tips WHERE 1=1"
    params = []

    if category and category.lower() != "all":
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (title LIKE ? OR content LIKE ? OR tags LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard])

    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_all_challenges():
    """Retrieve all eco-challenges."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM challenges ORDER BY id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def toggle_challenge(challenge_id):
    """Toggle a challenge's completion status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_completed, completed_count FROM challenges WHERE id = ?", (challenge_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    new_status = 0 if row["is_completed"] == 1 else 1
    new_count = row["completed_count"] + (1 if new_status == 1 else -1)
    if new_count < 0:
        new_count = 0

    cursor.execute("""
        UPDATE challenges
        SET is_completed = ?, completed_count = ?
        WHERE id = ?
    """, (new_status, new_count, challenge_id))
    conn.commit()

    cursor.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,))
    updated_row = dict(cursor.fetchone())
    conn.close()
    return updated_row


def add_activity(student_name, role, activity_type, description, impact_value):
    """Record an environmental activity completed on campus."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO activities (student_name, role, activity_type, description, impact_value)
        VALUES (?, ?, ?, ?, ?)
    """, (student_name, role, activity_type, description, impact_value))
    conn.commit()
    activity_id = cursor.lastrowid

    cursor.execute("SELECT * FROM activities WHERE id = ?", (activity_id,))
    record = dict(cursor.fetchone())
    conn.close()
    return record


def get_recent_activities(limit=10):
    """Retrieve recent campus eco-activities."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activities ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def add_feedback(user_name, role, rating, category, message):
    """Store user rating and suggestions."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (user_name, role, rating, category, message)
        VALUES (?, ?, ?, ?, ?)
    """, (user_name, role, rating, category, message))
    conn.commit()
    feedback_id = cursor.lastrowid

    cursor.execute("SELECT * FROM feedback WHERE id = ?", (feedback_id,))
    record = dict(cursor.fetchone())
    conn.close()
    return record


def get_all_feedback(limit=20):
    """Retrieve feedback and compute average rating."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT AVG(rating) as avg_rating, COUNT(*) as total_feedback FROM feedback")
    stats = cursor.fetchone()
    avg_rating = round(stats["avg_rating"], 1) if stats["avg_rating"] else 5.0
    total_feedback = stats["total_feedback"] if stats["total_feedback"] else 0

    conn.close()
    return {
        "items": rows,
        "avg_rating": avg_rating,
        "total_count": total_feedback
    }


def log_chat_message(session_id, role, message):
    """Log chatbot conversation for session audit."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_logs (session_id, role, message)
        VALUES (?, ?, ?)
    """, (session_id, role, message))
    conn.commit()
    conn.close()


def get_dashboard_stats():
    """Calculate aggregated metrics for the Green Campus Dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tips count
    cursor.execute("SELECT COUNT(*) as count FROM tips")
    total_tips = cursor.fetchone()["count"]

    # Activities count
    cursor.execute("SELECT COUNT(*) as count FROM activities")
    total_activities = cursor.fetchone()["count"]

    # Challenges completed
    cursor.execute("SELECT COUNT(*) as count FROM challenges WHERE is_completed = 1")
    completed_challenges = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM challenges")
    total_challenges = cursor.fetchone()["count"]

    # Total student challenge actions logged
    cursor.execute("SELECT SUM(completed_count) as total_actions FROM challenges")
    total_actions = cursor.fetchone()["total_actions"] or 0

    # Feedback average
    cursor.execute("SELECT AVG(rating) as avg_rating FROM feedback")
    avg_rating = round(cursor.fetchone()["avg_rating"] or 4.9, 1)

    # Activity breakdown by type
    cursor.execute("""
        SELECT activity_type, COUNT(*) as count
        FROM activities
        GROUP BY activity_type
        ORDER BY count DESC
    """)
    type_breakdown = [dict(r) for r in cursor.fetchall()]

    # Role breakdown
    cursor.execute("""
        SELECT role, COUNT(*) as count
        FROM activities
        GROUP BY role
    """)
    role_breakdown = [dict(r) for r in cursor.fetchall()]

    conn.close()

    # Demonstration environmental impact estimates
    # (Clear disclaimer provided in UI that stats are demonstration models)
    est_plastic_bottles_saved = 1450 + (total_actions * 4)
    est_water_saved_liters = 8600 + (total_actions * 25)
    est_kwh_energy_saved = 1240 + (total_actions * 3)
    est_trees_planted = 34 + (total_activities * 2)

    return {
        "total_tips": total_tips,
        "total_activities": total_activities,
        "completed_challenges": completed_challenges,
        "total_challenges": total_challenges,
        "total_actions": total_actions,
        "avg_rating": avg_rating,
        "type_breakdown": type_breakdown,
        "role_breakdown": role_breakdown,
        "impact_estimates": {
            "plastic_bottles_saved": est_plastic_bottles_saved,
            "water_saved_liters": est_water_saved_liters,
            "kwh_energy_saved": est_kwh_energy_saved,
            "trees_planted": est_trees_planted
        }
    }
