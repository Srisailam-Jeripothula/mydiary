from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diary.db"
db = SQLAlchemy(app)

# DB Model
class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Home page
@app.route("/")
def home():
    return render_template("home.html")

# Save entry
@app.route("/generate", methods=["POST"])
def generate():
    user_input = request.form["entry"].strip()
    new_entry = DiaryEntry(content=user_input)
    db.session.add(new_entry)
    db.session.commit()

    date = new_entry.created_at.strftime("%B %d, %Y")
    return render_template("result.html", diary_entry=user_input, date=date)

# All entries grouped by date
@app.route("/entries")
def entries():
    all_entries = DiaryEntry.query.order_by(DiaryEntry.created_at.desc()).all()
    unique_dates = sorted({ entry.created_at.strftime("%Y-%m-%d") for entry in all_entries }, reverse=True)
    return render_template("entries.html", dates=unique_dates)

# View entries by date
@app.route("/entries/<date>")
def entries_by_date(date):
    date_start = datetime.strptime(date, "%Y-%m-%d")
    date_end = date_start.replace(hour=23, minute=59, second=59)
    entries_on_date = DiaryEntry.query.filter(
        DiaryEntry.created_at >= date_start,
        DiaryEntry.created_at <= date_end
    ).order_by(DiaryEntry.created_at.asc()).all()

    combined_content = "\n\n".join(entry.content for entry in entries_on_date)

    return render_template(
        "entries_by_date.html",
        combined_content=combined_content,
        date=date_start.strftime("%B %d, %Y"),  # pretty
        raw_date=date  # ISO
    )

# Edit entries by date
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
        for entry in entries_on_date:
            db.session.delete(entry)
        new_entry = DiaryEntry(content=updated_content)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for("entries_by_date", date=date))

    combined_content = "\n\n".join(e.content for e in entries_on_date)
    return render_template(
        "edit_day.html",
        combined_content=combined_content,
        date=date
    )

# Delete entries by date
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
@app.template_filter('datetimeformat')
def datetimeformat(value):
    try:
        dt = datetime.strptime(value, "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")
    except:
        return value


print(app.url_map)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
