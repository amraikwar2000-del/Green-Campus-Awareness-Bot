import sqlite3
import os
from config import Config

DB_PATH = os.path.join(os.path.dirname(__file__), Config.DATABASE_NAME)

def get_db_connection():
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and populates default campus data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table: Interactions (Chatbot query & response logs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            source TEXT DEFAULT 'ai',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table: Eco-Challenges
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            points INTEGER DEFAULT 20,
            icon TEXT DEFAULT 'bi-leaf',
            difficulty TEXT DEFAULT 'Easy',
            is_completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP
        )
    ''')

    # Table: Categorized Environmental Tips
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            impact_level TEXT DEFAULT 'Medium',
            icon TEXT DEFAULT 'bi-lightbulb'
        )
    ''')

    # Table: User Feedback
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT DEFAULT 'Anonymous Student',
            user_role TEXT DEFAULT 'Student',
            rating INTEGER NOT NULL,
            category TEXT DEFAULT 'General',
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table: Activity Logs (Completed student eco-deeds & campus milestones)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT NOT NULL,
            title TEXT NOT NULL,
            points_earned INTEGER DEFAULT 10,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()

    # Populate initial seed challenges if none exist
    cursor.execute("SELECT COUNT(*) FROM challenges")
    if cursor.fetchone()[0] == 0:
        seed_challenges = [
            ("Bring a Reusable Water Bottle", "Plastic Reduction", "Carry a reusable flask or bottle to campus and avoid buying packaged mineral water bottles.", 25, "bi-cup-straw", "Easy", 1),
            ("Avoid Single-Use Plastics", "Waste Management", "Say NO to plastic straws, cutlery, polythene bags, and styrofoam containers in the college canteen.", 30, "bi-slash-circle", "Easy", 0),
            ("Switch Off Lights & Fans", "Energy Conservation", "Power down classroom projectors, fans, lab monitors, and lights when leaving an empty lecture room.", 20, "bi-power", "Easy", 1),
            ("Join Campus Cleanliness Drive", "Campus Cleanliness", "Spend 30 minutes with peers picking up litter and sanitizing campus gardens and cafeteria zones.", 50, "bi-trash3", "Medium", 0),
            ("Plant and Care for a Tree", "Biodiversity", "Adopt a native sapling on campus grounds, water it regularly, and log its growth with the botany club.", 60, "bi-tree", "Medium", 0),
            ("Separate Wet & Dry Waste", "Waste Management", "Ensure food scraps and compostables go into green bins, and paper/plastics into blue bins.", 25, "bi-recycle", "Easy", 1),
            ("Climb Stairs Instead of Elevators", "Energy & Health", "Take the stairs for floors 1 to 4 to cut lift electricity usage while staying active.", 15, "bi-arrow-up-right-circle", "Easy", 0),
            ("Adopt Double-Sided Printing", "Paper Saving", "Print lab manuals, notes, and study guides back-to-back or submit digital PDFs when allowed.", 20, "bi-printer", "Easy", 0),
        ]
        cursor.executemany(
            "INSERT INTO challenges (title, category, description, points, icon, difficulty, is_completed) VALUES (?, ?, ?, ?, ?, ?, ?)",
            seed_challenges
        )
        conn.commit()

    # Populate initial tips if none exist
    cursor.execute("SELECT COUNT(*) FROM tips")
    if cursor.fetchone()[0] == 0:
        seed_tips = [
            # Water Conservation
            ("Turn Off Taps Firmly in Restrooms", "Water Conservation", "A dripping faucet can waste up to 15-20 liters of clean water daily. Always ensure hostel and campus washroom taps are turned off completely.", "High", "bi-droplet-fill"),
            ("Report Campus Plumbing Leaks Promptly", "Water Conservation", "If you spot leaking outdoor sprinklers, broken pipes, or overflowing cooling tanks, alert maintenance staff immediately via the student portal.", "High", "bi-wrench-adjustable"),
            ("Use Refill Stations Responsibly", "Water Conservation", "Only fill the water you need to drink. Use leftover water from bottles to hydrate campus garden flowerbeds rather than dumping it down the sink.", "Medium", "bi-water"),

            # Energy Conservation
            ("Unplug Chargers & Laptop Adapters", "Energy Conservation", "Chargers plugged into empty wall sockets still draw phantom load electricity. Unplug them when your device reaches 80-100%.", "Medium", "bi-plug-fill"),
            ("Maximize Natural Daylighting", "Energy Conservation", "Open window blinds during morning study sessions in library pods instead of switching on overhead fluorescent bank lights.", "Medium", "bi-sun-fill"),
            ("Optimize Air Conditioner Thermostats", "Energy Conservation", "In seminar halls and computer labs, set AC units to 24°C - 26°C. Each degree higher saves approximately 6% in air conditioning power.", "High", "bi-thermometer-sun"),

            # Waste Management
            ("Practice Source Segregation (3 Bins)", "Waste Management", "Divide waste into: Green (Organic food leftovers, tea bags), Blue (Recyclable clean plastics, cans), and Grey/Red (Non-recyclable sanitary/hazardous items).", "High", "bi-recycle"),
            ("Carry a Cloth Tote Bag for Books & Canteen", "Waste Management", "Fold a lightweight canvas tote in your college backpack to eliminate the need for plastic bags while shopping at campus stationery or grocery outlets.", "Medium", "bi-bag-check-fill"),
            ("Recycle Old Note Sheets & Exam Bluebooks", "Waste Management", "Collect finished semester spiral notebooks and donate them to the student council paper recycling drives for pulp re-processing.", "Medium", "bi-journal-check"),

            # Air Quality
            ("Protect Campus Indoor Air with Green Plants", "Air Quality", "Place Snake Plants, Peace Lilies, or Money Plants in dorm rooms and study lounges to naturally filter formaldehyde and volatile organics.", "Medium", "bi-flower1"),
            ("Enforce Campus Zero-Smoking Zones", "Air Quality", "Keep designated outdoor and indoor spaces completely smoke-free to safeguard vulnerable students with asthma and maintain fresh campus air.", "High", "bi-wind"),

            # Biodiversity and Tree Plantation
            ("Plant Native Flowering Species for Pollinators", "Biodiversity", "Native trees like Neem, Gulmohar, and Indian Coral attract local bees, butterflies, and birds while requiring 70% less irrigation than exotic ornamental plants.", "High", "bi-tree-fill"),
            ("Build Bird Feeders & Clay Water Bowls", "Biodiversity", "Place shallow terracotta water saucers in shaded balcony perches during sweltering summer exam months for visiting sparrows and robins.", "Medium", "bi-egg-fill"),

            # Sustainable Transportation
            ("Carpool or Share Campus Transit Passes", "Sustainable Transportation", "Coordinate carpools or electric campus shuttle bookings with departmental peers to reduce individual vehicle emissions and parking gridlock.", "High", "bi-car-front-fill"),
            ("Embrace Bicycles for Internal Campus Travel", "Sustainable Transportation", "Use pedal cycles or public bike-share stands between lecture halls, sports grounds, and student hostels to foster zero emissions.", "High", "bi-bicycle")
        ]
        cursor.executemany(
            "INSERT INTO tips (title, category, content, impact_level, icon) VALUES (?, ?, ?, ?, ?)",
            seed_tips
        )
        conn.commit()

    # Populate initial feedback testimonials if none exist
    cursor.execute("SELECT COUNT(*) FROM feedback")
    if cursor.fetchone()[0] == 0:
        seed_feedback = [
            ("Aarav Sharma", "Student (Environmental Club)", 5, "Chatbot Experience", "EcoBot answered my queries about cafeteria compost pits instantly! Love the interactive eco-challenges.", "2026-10-10 14:20:00"),
            ("Prof. Meera Sen", "Faculty (Botany Dept)", 5, "Campus Usability", "An exceptional initiative. The categorization of native tree tips and energy conservation advice is very accurate for university grounds.", "2026-10-11 09:45:00"),
            ("Rohan Varma", "Student (Hostel Representative)", 4, "Eco-Challenges", "The checklist gamification motivates hostellers to switch off common room lights. Added 3 more challenges to my daily routine!", "2026-10-12 18:30:00")
        ]
        cursor.executemany(
            "INSERT INTO feedback (user_name, user_role, rating, category, comment, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            seed_feedback
        )
        conn.commit()

    # Populate initial activity logs if none exist
    cursor.execute("SELECT COUNT(*) FROM activity_logs")
    if cursor.fetchone()[0] == 0:
        seed_activities = [
            ("challenge_completed", "Brought Reusable Water Bottle to Engineering Block", 25, "Diverted ~2 single-use PET bottles from campus landfill.", "2026-10-13 10:15:00"),
            ("challenge_completed", "Switched Off Lab Computers & Lights after Python Practical", 20, "Conserved approx 1.8 kWh across Department Lab B.", "2026-10-13 16:40:00"),
            ("tree_plantation", "Student Green Club Planted 12 Neem Saplings", 120, "Campus North Garden quadrant now has active drip irrigation.", "2026-10-14 08:30:00")
        ]
        cursor.executemany(
            "INSERT INTO activity_logs (activity_type, title, points_earned, details, created_at) VALUES (?, ?, ?, ?, ?)",
            seed_activities
        )
        conn.commit()

    conn.close()
