"""
Green Campus Awareness Bot - Flask Application
Full-stack web application providing an AI-powered environmental assistant,
interactive eco-challenges, categorized green tips, campus activity logging,
real-time impact dashboard, and community feedback.
"""

import os
import sys

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

import database
import ai_service

# Load environment configuration
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "green_campus_secret_key_2026")
app.config["JSON_SORT_KEYS"] = False

# Initialize SQLite database and seed initial data
database.init_db()


# -----------------------------------------------------------------------------
# Frontend Routes
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    """Render main application."""
    initial_tab = request.args.get("tab", "home")
    ai_status = ai_service.get_ai_status()
    return render_template("index.html", initial_tab=initial_tab, ai_status=ai_status)


@app.route("/chatbot")
def chatbot_page():
    """Direct route to the AI Chatbot view."""
    ai_status = ai_service.get_ai_status()
    return render_template("index.html", initial_tab="chatbot", ai_status=ai_status)


@app.route("/challenges")
def challenges_page():
    """Direct route to the Eco-Challenges view."""
    ai_status = ai_service.get_ai_status()
    return render_template("index.html", initial_tab="challenges", ai_status=ai_status)


@app.route("/tips")
def tips_page():
    """Direct route to the Green Tips view."""
    ai_status = ai_service.get_ai_status()
    return render_template("index.html", initial_tab="tips", ai_status=ai_status)


@app.route("/dashboard")
def dashboard_page():
    """Direct route to the Campus Dashboard view."""
    ai_status = ai_service.get_ai_status()
    return render_template("index.html", initial_tab="dashboard", ai_status=ai_status)


@app.route("/about")
def about_page():
    """Direct route to the About view."""
    ai_status = ai_service.get_ai_status()
    return render_template("index.html", initial_tab="about", ai_status=ai_status)


@app.route("/feedback")
def feedback_page():
    """Direct route to the Feedback view."""
    ai_status = ai_service.get_ai_status()
    return render_template("index.html", initial_tab="feedback", ai_status=ai_status)


# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------

@app.route("/api/status", methods=["GET"])
def api_status():
    """Check AI integration and system health."""
    return jsonify({
        "success": True,
        "app_name": "Green Campus Awareness Bot",
        "version": "1.0.0",
        "ai": ai_service.get_ai_status()
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Handle chatbot messages.
    Supports session tracking, conversation history, input validation,
    and automatic database logging.
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    session_id = data.get("session_id", "default_session").strip() or "default_session"
    history = data.get("history", [])

    if not message:
        return jsonify({
            "success": False,
            "error": "Message is required."
        }), 400

    # Log user message
    try:
        database.log_chat_message(session_id, "user", message)
    except Exception as e:
        app.logger.warning(f"Failed to log user chat message: {e}")

    # Generate response
    result = ai_service.generate_chat_response(message, history=history)

    if result.get("success"):
        bot_response = result.get("response", "")
        # Log bot message
        try:
            database.log_chat_message(session_id, "assistant", bot_response)
        except Exception as e:
            app.logger.warning(f"Failed to log assistant chat message: {e}")

        return jsonify({
            "success": True,
            "response": bot_response,
            "source": result.get("source"),
            "model": result.get("model", "local_engine"),
            "note": result.get("note")
        })
    else:
        return jsonify({
            "success": False,
            "error": result.get("response", "Could not process message.")
        }), 400


@app.route("/api/tips", methods=["GET"])
def api_tips():
    """Retrieve environmental tips with optional category and search filters."""
    category = request.args.get("category", "all")
    search = request.args.get("search", "").strip()

    tips = database.get_all_tips(category=category, search=search)
    return jsonify({
        "success": True,
        "count": len(tips),
        "tips": tips
    })


@app.route("/api/challenges", methods=["GET"])
def api_challenges():
    """Retrieve all campus eco-challenges."""
    challenges = database.get_all_challenges()
    return jsonify({
        "success": True,
        "count": len(challenges),
        "challenges": challenges
    })


@app.route("/api/challenges/toggle", methods=["POST"])
def api_toggle_challenge():
    """Toggle completion of an eco-challenge."""
    data = request.get_json(silent=True) or {}
    challenge_id = data.get("challenge_id")

    if not challenge_id:
        return jsonify({"success": False, "error": "challenge_id is required"}), 400

    try:
        challenge_id = int(challenge_id)
    except ValueError:
        return jsonify({"success": False, "error": "Invalid challenge_id"}), 400

    updated = database.toggle_challenge(challenge_id)
    if not updated:
        return jsonify({"success": False, "error": "Challenge not found"}), 404

    return jsonify({
        "success": True,
        "challenge": updated
    })


@app.route("/api/activities", methods=["GET", "POST"])
def api_activities():
    """Log a new activity (POST) or fetch recent activities (GET)."""
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("student_name", "").strip() or "Anonymous Student"
        role = data.get("role", "Student").strip()
        activity_type = data.get("activity_type", "").strip()
        description = data.get("description", "").strip()
        impact_value = data.get("impact_value", "").strip() or "1 Action Completed"

        if not activity_type or not description:
            return jsonify({
                "success": False,
                "error": "Activity type and description are required."
            }), 400

        record = database.add_activity(name, role, activity_type, description, impact_value)
        return jsonify({
            "success": True,
            "message": "Eco-activity successfully recorded! Thank you for helping keep campus green 🌿",
            "activity": record
        }), 201

    # GET
    limit = request.args.get("limit", 15, type=int)
    activities = database.get_recent_activities(limit=limit)
    return jsonify({
        "success": True,
        "count": len(activities),
        "activities": activities
    })


@app.route("/api/feedback", methods=["GET", "POST"])
def api_feedback():
    """Submit user feedback (POST) or fetch community reviews (GET)."""
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        user_name = data.get("user_name", "").strip() or "Campus Member"
        role = data.get("role", "Student").strip()
        category = data.get("category", "General Suggestion").strip()
        message = data.get("message", "").strip()
        rating = data.get("rating", 5)

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                rating = 5
        except (ValueError, TypeError):
            rating = 5

        if not message:
            return jsonify({
                "success": False,
                "error": "Feedback message cannot be empty."
            }), 400

        record = database.add_feedback(user_name, role, rating, category, message)
        return jsonify({
            "success": True,
            "message": "Thank you! Your feedback helps us improve campus green initiatives 🌿",
            "feedback": record
        }), 201

    # GET
    limit = request.args.get("limit", 15, type=int)
    feedback_data = database.get_all_feedback(limit=limit)
    return jsonify({
        "success": True,
        "data": feedback_data
    })


@app.route("/api/dashboard/stats", methods=["GET"])
def api_dashboard_stats():
    """Retrieve aggregated metrics and demonstration impact data."""
    stats = database.get_dashboard_stats()
    return jsonify({
        "success": True,
        "stats": stats
    })


# -----------------------------------------------------------------------------
# Main Application Entry Point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    print(f"[*] Green Campus Awareness Bot starting on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=debug)
