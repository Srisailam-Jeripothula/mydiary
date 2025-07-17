import spacy
import requests
import difflib
import os
from dotenv import load_dotenv

load_dotenv()

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# USDA API Setup
USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# OpenRouteService API Setup
ORS_API_KEY = os.getenv("ORS_API_KEY")
ORS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
ORS_GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"


def extract_food_and_places(text):
    """
    Extract food items (nouns matching whitelist) and places (GPE, LOC).
    Returns: (foods, places) as lists.
    """
    whitelist = {
        "chapathi", "roti", "rice", "curd", "paneer", "banana", "egg", "bread",
        "butter", "milk", "dal", "sprouts", "cheese", "almonds", "cashews",
        "dates", "poha", "dosa", "idli"
    }

    doc = nlp(text.lower())
    foods = {token.text for token in doc if token.pos_ in {"NOUN", "PROPN"} and token.text in whitelist}
    places = {ent.text for ent in doc.ents if ent.label_ in {"GPE", "LOC"}}

    return list(foods), list(places)


def get_food_nutrition(food):
    """
    Get nutrition info (calories, protein) for a food item using USDA API.
    Returns dict or None if not found.
    """
    if not USDA_API_KEY:
        return None

    params = {
        "api_key": USDA_API_KEY,
        "query": food,
        "pageSize": 1
    }

    try:
        res = requests.get(USDA_SEARCH_URL, params=params)
        res.raise_for_status()
        data = res.json()

        if not data.get("foods"):
            return None

        item = data["foods"][0]
        description = item.get("description", "").lower()

        if not difflib.get_close_matches(food.lower(), [description], cutoff=0.5):
            return None

        nutrients = {n["nutrientName"]: n["value"] for n in item.get("foodNutrients", [])}
        return {
            "calories": round(nutrients.get("Energy", 0), 2),
            "protein_g": round(nutrients.get("Protein", 0), 2)
        } if nutrients else None

    except:
        return None


def get_travel_distance(from_place, to_place):
    """
    Returns driving distance (km) and time (hr) between two places using OpenRouteService.
    Returns dict or None if fails.
    """
    if not ORS_API_KEY:
        return None

    try:
        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json"
        }

        def get_coords(place):
            resp = requests.get(ORS_GEOCODE_URL, params={"api_key": ORS_API_KEY, "text": place})
            resp.raise_for_status()
            features = resp.json().get("features")
            return features[0]["geometry"]["coordinates"] if features else None

        from_coords = get_coords(from_place)
        to_coords = get_coords(to_place)

        if not from_coords or not to_coords:
            return None

        body = {"coordinates": [from_coords, to_coords]}
        resp = requests.post(ORS_URL, headers=headers, json=body)
        resp.raise_for_status()

        segment = resp.json()["features"][0]["properties"]["segments"][0]
        return {
            "distance_km": round(segment["distance"] / 1000, 2),
            "duration_hr": round(segment["duration"] / 3600, 2)
        }

    except:
        return None
