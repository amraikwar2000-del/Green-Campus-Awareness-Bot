from flask import Flask, render_template, request, jsonify, session
import uuid
import datetime
from config import Config
from database import get_db_connection, init_db
from ai_service import generate_chat_response, DEFAULT_SUGGESTED_QUESTIONS

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database tables and seed content on startup
with app.app_context():
    init_db()

@app.before_request
def ensure_session():
    """Assign a persistent session ID for conversation tracking."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

@app.route('/')
def index():
    """Renders the main single-page web application."""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the backend and AI integration status."""
    has_api_key = bool(Config.OPENAI_API_KEY and not Config.OPENAI_API_KEY.startswith("your-"))
    return jsonify({
        "status": "online",
        "app_name": "Green Campus Awareness Bot",
        "version": "1.0.0",
        "ai_provider": "OpenAI" if has_api_key else "Campus Knowledge Engine (Fallback)",
        "openai_configured": has_api_key,
        "model": Config.OPENAI_MODEL if has_api_key else "Local Environmental Rule Engine",
        "database": "SQLite (green_campus.db)"
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handles chatbot conversations and logs interactions."""
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    history = data.get("history", [])

    if not user_message:
        return jsonify({
            "error": "Message is required",
            "response": "Please type a message to start conversing with EcoBot."
        }), 400

    if len(user_message) > 1000:
        return jsonify({
            "error": "Message too long (max 1000 characters)"
        }), 400

    # Call AI service
    result = generate_chat_response(user_message, history)

    # Log interaction to SQLite
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO interactions (session_id, user_message, bot_response, source) VALUES (?, ?, ?, ?)",
            (session.get('session_id', 'anonymous'), user_message, result.get("response", ""), result.get("source", "ai"))
        )
        conn.commit()
        conn.close()
    except Exception as db_err:
        app.logger.error(f"Error logging interaction: {db_err}")

    return jsonify(result)

@app.route('/api/tips', methods=['GET'])
def get_tips():
    """Returns categorized environmental tips with optional filtering."""
    category = request.args.get('category', '').strip()
    search = request.args.get('search', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tips WHERE 1=1"
    params = []

    if category and category.lower() != 'all':
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Get distinct categories
    cursor.execute("SELECT DISTINCT category FROM tips")
    categories = [row['category'] for row in cursor.fetchall()]

    conn.close()

    tips_list = [dict(row) for row in rows]
    return jsonify({
        "tips": tips_list,
        "count": len(tips_list),
        "categories": categories
    })

@app.route('/api/challenges', methods=['GET'])
def get_challenges():
    """Returns all eco-challenges, completion status, and user rank score."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM challenges ORDER BY id ASC")
    challenges = [dict(row) for row in cursor.fetchall()]

    total_challenges = len(challenges)
    completed_challenges = sum(1 for c in challenges if c['is_completed'])
    total_points = sum(c['points'] for c in challenges if c['is_completed'])

    # Determine eco level badge
    if completed_challenges >= 6:
        badge = "Green Campus Ambassador 🏆"
        level = "Eco Legend"
    elif completed_challenges >= 4:
        badge = "Campus Guardian 🌿"
        level = "Eco Champion"
    elif completed_challenges >= 2:
        badge = "Green Sprout 🌱"
        level = "Active Contributor"
    else:
        badge = "Eco Seedling 🌰"
        level = "Beginner"

    completion_percentage = int((completed_challenges / total_challenges) * 100) if total_challenges > 0 else 0

    conn.close()

    return jsonify({
        "challenges": challenges,
        "total": total_challenges,
        "completed": completed_challenges,
        "total_points": total_points,
        "completion_percentage": completion_percentage,
        "badge": badge,
        "level": level
    })

@app.route('/api/challenges/complete', methods=['POST'])
def complete_challenge():
    """Toggles or sets completion status for a challenge."""
    data = request.get_json() or {}
    challenge_id = data.get('challenge_id')
    status = data.get('completed', True)

    if not challenge_id:
        return jsonify({"error": "challenge_id is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM challenges WHERE id = ?", (challenge_id,))
    challenge = cursor.fetchone()

    if not challenge:
        conn.close()
        return jsonify({"error": "Challenge not found"}), 404

    completed_int = 1 if status else 0
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") if completed_int else None

    cursor.execute(
        "UPDATE challenges SET is_completed = ?, completed_at = ? WHERE id = ?",
        (completed_int, now, challenge_id)
    )

    # Log into activity logs if marked completed
    if completed_int:
        cursor.execute(
            "INSERT INTO activity_logs (activity_type, title, points_earned, details) VALUES (?, ?, ?, ?)",
            ("challenge_completed", challenge['title'], challenge['points'], f"Completed eco-challenge: {challenge['title']}")
        )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "challenge_id": challenge_id,
        "is_completed": completed_int,
        "message": "Challenge progress updated successfully!"
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retrieves live dashboard statistics with sample campus metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tips count
    cursor.execute("SELECT COUNT(*) FROM tips")
    tips_count = cursor.fetchone()[0]

    # Completed challenges
    cursor.execute("SELECT COUNT(*) FROM challenges WHERE is_completed = 1")
    completed_challenges = cursor.fetchone()[0]

    # Activities recorded
    cursor.execute("SELECT COUNT(*) FROM activity_logs")
    activities_count = cursor.fetchone()[0]

    # Total interactions recorded
    cursor.execute("SELECT COUNT(*) FROM interactions")
    interactions_count = cursor.fetchone()[0]

    # Total eco points
    cursor.execute("SELECT SUM(points) FROM challenges WHERE is_completed = 1")
    earned_points = cursor.fetchone()[0] or 0

    conn.close()

    # Dynamic impact estimations based on recorded activities + baseline demo campus figures
    plastic_bottles_saved = 1420 + (completed_challenges * 25)
    water_saved_liters = 5800 + (completed_challenges * 120)
    energy_saved_kwh = 340 + (completed_challenges * 8)
    co2_reduced_kg = 210 + (completed_challenges * 5)

    return jsonify({
        "tips_count": tips_count,
        "completed_challenges": completed_challenges,
        "activities_count": activities_count,
        "interactions_count": interactions_count,
        "eco_points": earned_points,
        "plastic_bottles_saved": plastic_bottles_saved,
        "water_saved_liters": water_saved_liters,
        "energy_saved_kwh": energy_saved_kwh,
        "co2_reduced_kg": co2_reduced_kg,
        "disclaimer": "Sample statistics are demonstrations for college awareness and not real-time campus sensors."
    })

@app.route('/api/feedback', methods=['GET', 'POST'])
def handle_feedback():
    """Handles feedback submission and retrieves recent user reviews."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.get_json() or {}
        user_name = data.get('user_name', 'Anonymous Student').strip() or 'Anonymous Student'
        user_role = data.get('user_role', 'Student').strip() or 'Student'
        rating = data.get('rating')
        category = data.get('category', 'General').strip() or 'General'
        comment = data.get('comment', '').strip()

        if not rating or not (1 <= int(rating) <= 5):
            conn.close()
            return jsonify({"error": "Please provide a valid rating between 1 and 5"}), 400

        if not comment:
            conn.close()
            return jsonify({"error": "Comment cannot be empty"}), 400

        cursor.execute(
            "INSERT INTO feedback (user_name, user_role, rating, category, comment) VALUES (?, ?, ?, ?, ?)",
            (user_name, user_role, int(rating), category, comment)
        )
        conn.commit()

        # Log as campus feedback activity
        cursor.execute(
            "INSERT INTO activity_logs (activity_type, title, points_earned, details) VALUES (?, ?, ?, ?)",
            ("feedback_submitted", f"Feedback from {user_name} ({user_role})", 10, f"Rated {rating} stars: {category}")
        )
        conn.commit()

        conn.close()
        return jsonify({
            "success": True,
            "message": "Thank you for your valuable feedback! Your input helps keep our campus green."
        }), 201

    # GET: return latest 8 feedbacks
    cursor.execute("SELECT * FROM feedback ORDER BY id DESC LIMIT 8")
    feedbacks = [dict(row) for row in cursor.fetchall()]

    cursor.execute("SELECT AVG(rating), COUNT(*) FROM feedback")
    stats = cursor.fetchone()
    avg_rating = round(stats[0], 1) if stats[0] else 5.0
    total_feedback = stats[1]

    conn.close()
    return jsonify({
        "feedbacks": feedbacks,
        "average_rating": avg_rating,
        "total_count": total_feedback
    })

@app.route('/api/activities', methods=['GET'])
def get_activities():
    """Returns recent campus eco-activities log."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT 10")
    activities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"activities": activities})

if __name__ == '__main__':
    print(f"Starting Green Campus Awareness Bot on port {Config.PORT}...")
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
