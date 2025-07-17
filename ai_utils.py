from transformers import pipeline
from ner_utils import extract_food_and_places, get_food_nutrition, get_travel_distance

# Initialize the text rewriter model
rewriter_pipe = pipeline(
    "text2text-generation",
    model="pszemraj/flan-t5-large-grammar-synthesis"
)

def polish_text(text):
    """
    One simple pass: grammar, spelling, punctuation, style.
    """
    result = rewriter_pipe(
        text,
        max_length=150,
        num_beams=5,
        early_stopping=True
    )[0]['generated_text']
    return result


def process_diary_entry(raw_text):
    """
    Full pipeline:
    - Polishes raw text
    - Extracts food and place entities
    - Gets nutritional and travel information
    - Returns structured summary data
    """

    # Step 1: Grammar-polish the input
    polished = polish_text(raw_text)

    # Step 2: Extract foods and places from polished text
    foods, places = extract_food_and_places(polished)

    # Step 3: Nutrition data summary
    food_summaries = []
    for food in foods:
        info = get_food_nutrition(food)
        if info:
            cal = info.get("calories", "?")
            protein = info.get("protein_g", "?")
            food_summaries.append(f"{food.title()}: {cal} kcal, {protein}g protein")
        else:
            food_summaries.append(f"{food.title()}: Nutrition info not found")

    # Step 4: Travel distance summary
    travel_summary = None
    if len(places) >= 2:
        from_place, to_place = places[0], places[1]
        travel = get_travel_distance(from_place, to_place)
        if travel:
            km = travel.get("distance_km", "?")
            duration = travel.get("duration_hr", "?")
            travel_summary = f"Traveled from {from_place} to {to_place}, covering {km} km in approx. {duration} hours."
        else:
            travel_summary = f"Could not retrieve travel info from {from_place} to {to_place}."
    elif len(places) == 1:
        travel_summary = f"Only one place detected: {places[0]}. Unable to calculate distance."

    # Final structured result
    return {
        "polished_text": polished,
        "foods_info": food_summaries,
        "travel_info": travel_summary
    }
