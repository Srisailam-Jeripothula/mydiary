# ---------------------------
# Imports
# ---------------------------
from transformers import pipeline
import spacy
import re
import os
import requests
from dotenv import load_dotenv

# ---------------------------
# Load .env for API keys
# ---------------------------
load_dotenv()
USDA_API_KEY = os.getenv("USDA_API_KEY")
ORS_API_KEY = os.getenv("ORS_API_KEY")

# ---------------------------
# Load pipelines
# ---------------------------
# 1. Location NER (dslim)
loc_ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

# 2. Food fallback: spaCy for noun chunks
nlp = spacy.load("en_core_web_sm")

# ---------------------------
# Entity Extraction Function
# ---------------------------
def extract_entities(text):
    # Locations using NER
    loc_results = loc_ner(text)
    places = [e['word'] for e in loc_results if e['entity_group'] == 'LOC']

    # Food fallback: noun chunks
    doc = nlp(text)
    foods = []
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.strip().lower()
        if chunk_text not in foods:
            # Check if USDA knows this
            check = lookup_nutrition(chunk_text, silent=True)
            if "Nutrition info not found" not in check:
                foods.append(chunk_text)

    return places, foods

# ---------------------------
# USDA Nutrition Lookup
# ---------------------------
def lookup_nutrition(food_item, silent=False):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_item}&api_key={USDA_API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        if data.get('foods'):
            item = data['foods'][0]
            name = item.get('description', food_item)
            nutrients = item.get('foodNutrients', [])
            calories = next((n['value'] for n in nutrients if 'Energy' in n['nutrientName']), None)
            protein = next((n['value'] for n in nutrients if 'Protein' in n['nutrientName']), None)
            if silent:
                return f"{name}: {calories} kcal, {protein}g protein"
            else:
                return f"{name}: {calories} kcal, {protein}g protein"
    return f"{food_item}: Nutrition info not found"

# ---------------------------
# OpenRouteService Travel Lookup
# ---------------------------
def lookup_travel_distance(places):
    if len(places) < 2:
        return "Need at least 2 places to calculate travel distance."

    origin, destination = places[0], places[1]

    geo_url = "https://api.openrouteservice.org/geocode/search"
    # Get coordinates
    origin_resp = requests.get(geo_url, params={"api_key": ORS_API_KEY, "text": origin})
    dest_resp = requests.get(geo_url, params={"api_key": ORS_API_KEY, "text": destination})

    if origin_resp.status_code != 200 or dest_resp.status_code != 200:
        return "Error fetching coordinates."

    try:
        origin_coords = origin_resp.json()['features'][0]['geometry']['coordinates']
        dest_coords = dest_resp.json()['features'][0]['geometry']['coordinates']
    except (KeyError, IndexError):
        return "Could not find coordinates for one or both places."

    # Get directions
    directions_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    directions_headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [origin_coords, dest_coords]
    }

    directions_resp = requests.post(directions_url, json=body, headers=directions_headers)
    if directions_resp.status_code != 200:
        return f"Error fetching directions: {directions_resp.text}"

    data = directions_resp.json()
    try:
        segment = data['routes'][0]['segments'][0]
        distance_km = segment['distance'] / 1000
        duration_min = segment['duration'] / 60
        return f"{origin} ➜ {destination}: {distance_km:.1f} km, ~{duration_min:.0f} mins by car"
    except (KeyError, IndexError):
        return "Could not parse directions response."

# ---------------------------
# TEST TEXT
# ---------------------------
text = "Today I ate an omelette with bread and tea, then I travelled from Nalgonda to Hyderabad."

# ---------------------------
# Run Extraction
# ---------------------------
places, foods = extract_entities(text)
print("\n✅ Places:", places)
print("✅ Foods:", foods)

# Nutrition Info
print("\n📊 Nutrition:")
for food in foods:
    result = lookup_nutrition(food)
    print(f"- {result}")

# Travel Info
print("\n🗺️ Travel:")
travel_note = lookup_travel_distance(places)
print(travel_note)
