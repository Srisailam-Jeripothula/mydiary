from flask import Flask, render_template, request
from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Load environment variables
load_dotenv()


# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///diary.db"  # saves in root folder
db = SQLAlchemy(app)

# Define the database model
class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Home page with the form
@app.route("/")
def home():
    return render_template("home.html")

# Generate diary entry & save to database
@app.route("/generate", methods=["POST"])
def generate():
    user_input = request.form["entry"]

    # MOCK for now instead of OpenAI
    diary_entry_text = f"This is a fake diary entry based on what you wrote:\n\n{user_input}"

    # Save to database
    new_entry = DiaryEntry(content=diary_entry_text)
    db.session.add(new_entry)
    db.session.commit()

    return render_template("result.html", diary_entry=diary_entry_text)
@app.route("/entries")
def entries():
    all_entries = DiaryEntry.query.order_by(DiaryEntry.created_at.desc()).all()
    return render_template("entries.html", entries=all_entries)
print(app.url_map)


# Run the app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures DB & tables exist
    app.run(debug=True)
