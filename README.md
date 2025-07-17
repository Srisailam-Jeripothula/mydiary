# 🧠 AI-Augmented Diary Web Application

## 📌 Overview

This project is a **Flask-based personal diary application** that leverages **Natural Language Processing (NLP)** and **AI models** to transform unstructured, daily text entries into structured, actionable insights. It was developed to address a personal need: making sense of messy diary entries that mention food, travel, and daily routines without structure or clarity.

The app automatically:
- Cleans and polishes free-form text using an AI grammar correction model.
- Extracts food items and queries nutritional data via the USDA FoodData Central API.
- Detects place mentions and calculates travel distance between them using OpenRouteService.
- Returns structured summaries (nutrition and travel) with no manual tagging or input formatting.

---

## 🎯 Motivation

While journaling daily experiences, I noticed:
- Entries were too informal or grammatically inconsistent for later reflection.
- It was difficult to recall what I had eaten or where I had been.
- Existing food/nutrition tracking apps were too structured or intrusive.

To solve this, I built a lightweight, private web app that **passively extracts useful insights** from natural writing — mimicking how an AI assistant might support everyday wellbeing and self-awareness.

---

## 🔍 Key Capabilities

| Feature                | Description |
|------------------------|-------------|
| ✨ Text Polishing       | Uses `flan-t5-large` grammar synthesis model to improve grammar, spelling, and structure |
| 🍱 Food Entity Extraction | spaCy-based NER pipeline to identify foods and query nutrition from the USDA API |
| 🗺️ Place Detection & Distance | Detects place mentions and computes travel distance (if multiple locations are found) |
| 📆 Date-based Journaling | Stores entries by date and allows retrieval by calendar view |
| 💬 No Manual Tagging     | Works on raw text input — no need for structured forms or formatting |

---

## 🧠 Tech Stack

- **Python 3.10+**, **Flask**
- **spaCy** for NER with custom rule-based enhancements
- **Transformers** (`pszemraj/flan-t5-large-grammar-synthesis`) via Hugging Face for grammar correction
- **External APIs**:
  - [USDA FoodData Central](https://fdc.nal.usda.gov/)
  - [OpenRouteService](https://openrouteservice.org/)
- **Frontend**: Jinja2 templates, Bootstrap (optional), minimal JS

---

## 🧪 Current Development State

| Component            | Status       |
|----------------------|--------------|
| Entity Extraction    | ✅ Working with fuzzy matching for food/place |
| Grammar Polishing    | ✅ Integrated with HuggingFace model |
| USDA Integration     | ✅ Returns average nutrition data |
| OpenRouteService     | ✅ Distance calculated if 2+ places are found |
| UI & Diary Retrieval | ✅ Functional, minimal design |
| Quantity Detection   | 🔜 Planned (not implemented) |
| Docker Deployment    | 🔜 Planned |

> ⚠️ Currently designed for personal use — not intended for multi-user deployment or public access yet.

---

## 🗂️ Project Structure

├── app.py # Flask app controller
├── ai_utils.py # AI text polishing & workflow integration
├── ner_utils.py # Entity extraction + API calls
├── templates/
│ ├── index.html # Diary input form
│ ├── result.html # Processed output display
│ └── entries_by_date.html
├── static/
├── .env # Contains API keys (excluded from Git)
├── requirements.txt

---

## 📈 Use Case

**For Users:** A smarter, more insightful way to keep track of what you eat and where you go.

**For Recruiters/Developers:**  
A demonstration of my ability to:
- Integrate NLP models into production-ready Flask apps
- Perform entity extraction and enrich text with external APIs
- Build full-stack AI tools that solve personal problems
- Handle real-time data (nutrition, distance) using open datasets
- Create intuitive, user-focused interfaces using Jinja2 templates

---

## 🔮 Future Enhancements

- Mood & sentiment analysis with emoji indicators  
- Food quantity detection & portion estimation  
- Enhanced fuzzy matching for better food recognition  
- Handwritten diary OCR support using Tesseract or Vision APIs  
- User authentication and private multi-user diaries  

---

## 👤 Author

**Srisailam Jeripothula**  
🎓 Master's in AI/ML | 🔍 Data Analyst | 🛠️ Engineer  
📍 Hyderabad, India  
📫 [LinkedIn](https://www.linkedin.com/in/srisailamjeripothula/) | 📧 srisailam585@gmail.com 

---

