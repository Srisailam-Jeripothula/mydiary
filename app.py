from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os

from ai_utils import process_diary_entry
from ner_utils import extract_food_and_places, get_food_nutrition, get_travel_distance

# --------------------------------------
# Application & Database Setup
# --------------------------------------

app = Flask(__name__)
load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diary.db"
db = SQLAlchemy(app)

# --------------------------------------
# Database Model
# --------------------------------------

class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    polished_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --------------------------------------
# Home Page Route
# --------------------------------------

@app.route("/")
def home():
    return render_template("home.html")

# --------------------------------------
# Generate + Save Diary Entry
# --------------------------------------

@app.route("/generate", methods=["POST"])
def generate():
    """
    Handles new diary entry submission:
    - Polishes input
    - Extracts food/places
    - Gets nutrition and travel data
    - Saves to database
    - Renders results
    """
    raw_entry = request.form["entry"].strip()
    result = process_diary_entry(raw_entry)

    # Save to DB
    new_entry = DiaryEntry(
        content=raw_entry,
        polished_content=result["polished_text"]
    )
    db.session.add(new_entry)
    db.session.commit()

    return render_template(
        "result.html",
        date=new_entry.created_at.strftime("%B %d, %Y"),
        diary_entry=raw_entry,
        polished=result["polished_text"],
        foods_info=result["foods_info"],
        travel_info=result["travel_info"]
    )

# --------------------------------------
# View All Entries (Grouped by Date)
# --------------------------------------

@app.route("/entries")
def entries():
    all_entries = DiaryEntry.query.order_by(DiaryEntry.created_at.desc()).all()
    unique_dates = sorted({entry.created_at.strftime("%Y-%m-%d") for entry in all_entries}, reverse=True)
    return render_template("entries.html", dates=unique_dates)

# --------------------------------------
# View Entries for a Specific Date
# --------------------------------------

@app.route("/entries/<date>")
def entries_by_date(date):
    try:
        date_start = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format!", 400

    date_end = date_start.replace(hour=23, minute=59, second=59)

    entries_on_date = DiaryEntry.query.filter(
        DiaryEntry.created_at >= date_start,
        DiaryEntry.created_at <= date_end
    ).order_by(DiaryEntry.created_at.asc()).all()

    combined_content = "\n\n".join(entry.polished_content for entry in entries_on_date)

    # Extract food and place entities
    foods, places = extract_food_and_places(combined_content)

    # Nutrition data
    foods_info = [get_food_nutrition(food) for food in foods] if foods else []

    # Travel data
    travel_info = get_travel_distance(places[0], places[1]) if len(places) >= 2 else None

    return render_template(
        "entries_by_date.html",
        combined_content=combined_content,
        date=date_start.strftime("%B %d, %Y"),
        raw_date=date,
        foods_info=foods_info,
        travel_info=travel_info
    )

# --------------------------------------
# Edit Entries for a Specific Date
# --------------------------------------

@app.route("/edit/<date>", methods=["GET", "POST"])
def edit_day(date):
    try:
        date_start = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format!", 400

    date_end = date_start + timedelta(days=1)
    entries_on_date = DiaryEntry.query.filter(
        DiaryEntry.created_at >= date_start,
        DiaryEntry.created_at < date_end
    ).all()

    if request.method == "POST":
        updated_content = request.form["updated_content"]

        # Delete old entries
        for entry in entries_on_date:
            db.session.delete(entry)

        # Save new entry
        new_entry = DiaryEntry(content=updated_content)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for("entries_by_date", date=date))

    combined_content = "\n\n".join(e.content for e in entries_on_date)
    return render_template("edit_day.html", combined_content=combined_content, date=date)

# --------------------------------------
# Delete All Entries for a Date
# --------------------------------------

@app.route("/delete_day/<date>", methods=["POST"])
def delete_day(date):
    try:
        date_start = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format!", 400

    date_end = date_start + timedelta(days=1)
    entries_on_date = DiaryEntry.query.filter(
        DiaryEntry.created_at >= date_start,
        DiaryEntry.created_at < date_end
    ).all()

    for entry in entries_on_date:
        db.session.delete(entry)

    db.session.commit()
    return redirect(url_for("entries"))

# --------------------------------------
# Template Filter for Date Formatting
# --------------------------------------

@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")
    except:
        return value

# --------------------------------------
# App Runner
# --------------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
