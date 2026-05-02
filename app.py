# ============================================================
# app.py - Flask Backend for AI Trip Planner Chatbot
# ============================================================
 
from flask import Flask, request, jsonify, render_template
import json
import os
import re
 
app = Flask(__name__)
 
# ── Load destination data from data.json ──────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE_DIR, "data.json"), "r", encoding="utf-8") as f:
    DATA = json.load(f)
 
DESTINATIONS = DATA["destinations"]
TRAVEL_TYPES = DATA["travel_types"]
 
# ── City coordinates (lat, lng) for distance-based fallback ───
CITY_COORDS = {
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "bengaluru": (12.9716, 77.5946),
    "hyderabad": (17.3850, 78.4867),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "lucknow": (26.8467, 80.9462),
    "chandigarh": (30.7333, 76.7794),
    "amritsar": (31.6340, 74.8723),
    "surat": (21.1702, 72.8311),
    "goa": (15.2993, 74.1240),
    "manali": (32.2396, 77.1887),
    "kerala": (10.8505, 76.2711),
    "kochi": (9.9312, 76.2673),
    "varanasi": (25.3176, 82.9739),
    "agra": (27.1767, 78.0081),
    "shimla": (31.1048, 77.1734),
    "rishikesh": (30.0869, 78.2676),
    "udaipur": (24.5854, 73.7125),
    "andaman": (11.7401, 92.6586),
    "ooty": (11.4102, 76.6950),
    "amritsar": (31.6340, 74.8723),
    "darjeeling": (27.0360, 88.2627),
    "leh_ladakh": (34.1526, 77.5771),
    "mysore": (12.2958, 76.6394),
    "pondicherry": (11.9416, 79.8083),
    "spiti": (32.2461, 78.0156),
    "coorg": (12.3375, 75.8069),
    "pushkar": (26.4897, 74.5515),
    "hampi": (15.3350, 76.4600),
    "mussoorie": (30.4598, 78.0664),
    "kolkata": (22.5726, 88.3639),
    "patna": (25.5941, 85.1376),
    "bhopal": (23.2599, 77.4126),
    "indore": (22.7196, 75.8577),
    "nagpur": (21.1458, 79.0882),
    "coimbatore": (11.0168, 76.9558),
    "visakhapatnam": (17.6868, 83.2185),
    "dehradun": (30.3165, 78.0322),
    "jodhpur": (26.2389, 73.0243),
    "kota": (25.2138, 75.8648),
    "ludhiana": (30.9010, 75.8573),
    "nawanshahr": (31.1258, 76.1160),
    "jalandhar": (31.3260, 75.5762),
}

# ── Travel cost lookup table: (source, destination) -> cost ───
# Costs are approximate one-way per person in INR (train/bus/flight mix)
TRAVEL_COST_TABLE = {
    # To GOA
    ("mumbai", "goa"): 800, ("pune", "goa"): 900, ("bangalore", "goa"): 1200,
    ("bengaluru", "goa"): 1200, ("hyderabad", "goa"): 2000, ("delhi", "goa"): 4500,
    ("new delhi", "goa"): 4500, ("chennai", "goa"): 2500, ("kolkata", "goa"): 5000,
    ("ahmedabad", "goa"): 2500, ("surat", "goa"): 2200,

    # To MANALI
    ("delhi", "manali"): 1200, ("new delhi", "manali"): 1200,
    ("chandigarh", "manali"): 700, ("amritsar", "manali"): 900,
    ("mumbai", "manali"): 5000, ("bangalore", "manali"): 6000,
    ("bengaluru", "manali"): 6000, ("kolkata", "manali"): 5500,
    ("ludhiana", "manali"): 800, ("nawanshahr", "manali"): 850,
    ("jalandhar", "manali"): 850, ("jaipur", "manali"): 2000,

    # To JAIPUR
    ("delhi", "jaipur"): 500, ("new delhi", "jaipur"): 500,
    ("mumbai", "jaipur"): 2500, ("ahmedabad", "jaipur"): 1000,
    ("bangalore", "jaipur"): 4000, ("bengaluru", "jaipur"): 4000,
    ("kolkata", "jaipur"): 2500, ("agra", "jaipur"): 400,
    ("ludhiana", "jaipur"): 1200, ("nawanshahr", "jaipur"): 1300,
    ("chandigarh", "jaipur"): 1100,

    # To KERALA (Kochi)
    ("mumbai", "kerala"): 2000, ("delhi", "kerala"): 4000,
    ("new delhi", "kerala"): 4000, ("bangalore", "kerala"): 800,
    ("bengaluru", "kerala"): 800, ("hyderabad", "kerala"): 1500,
    ("chennai", "kerala"): 700, ("kolkata", "kerala"): 4500,
    ("coimbatore", "kerala"): 400,

    # To DELHI
    ("mumbai", "delhi"): 1500, ("bangalore", "delhi"): 3500,
    ("bengaluru", "delhi"): 3500, ("hyderabad", "delhi"): 2500,
    ("chennai", "delhi"): 2500, ("kolkata", "delhi"): 1500,
    ("jaipur", "delhi"): 500, ("chandigarh", "delhi"): 500,
    ("amritsar", "delhi"): 600, ("ludhiana", "delhi"): 550,
    ("nawanshahr", "delhi"): 600, ("jalandhar", "delhi"): 580,

    # To SHIMLA
    ("delhi", "shimla"): 700, ("new delhi", "shimla"): 700,
    ("chandigarh", "shimla"): 250, ("mumbai", "shimla"): 4000,
    ("ludhiana", "shimla"): 500, ("nawanshahr", "shimla"): 550,
    ("amritsar", "shimla"): 700,

    # To RISHIKESH
    ("delhi", "rishikesh"): 450, ("new delhi", "rishikesh"): 450,
    ("mumbai", "rishikesh"): 3500, ("dehradun", "rishikesh"): 150,
    ("haridwar", "rishikesh"): 80, ("chandigarh", "rishikesh"): 600,
    ("ludhiana", "rishikesh"): 800,

    # To AGRA
    ("delhi", "agra"): 300, ("new delhi", "agra"): 300,
    ("jaipur", "agra"): 400, ("mumbai", "agra"): 2500,
    ("lucknow", "agra"): 500,

    # To VARANASI
    ("delhi", "varanasi"): 800, ("new delhi", "varanasi"): 800,
    ("mumbai", "varanasi"): 2000, ("kolkata", "varanasi"): 700,
    ("lucknow", "varanasi"): 300, ("patna", "varanasi"): 300,

    # To UDAIPUR
    ("delhi", "udaipur"): 1200, ("new delhi", "udaipur"): 1200,
    ("jaipur", "udaipur"): 600, ("mumbai", "udaipur"): 1500,
    ("ahmedabad", "udaipur"): 700,

    # To ANDAMAN
    ("kolkata", "andaman"): 6000, ("chennai", "andaman"): 5500,
    ("delhi", "andaman"): 8000, ("new delhi", "andaman"): 8000,
    ("mumbai", "andaman"): 8000, ("bangalore", "andaman"): 7000,
    ("bengaluru", "andaman"): 7000,

    # To OOTY
    ("bangalore", "ooty"): 600, ("bengaluru", "ooty"): 600,
    ("chennai", "ooty"): 500, ("mumbai", "ooty"): 2500,
    ("coimbatore", "ooty"): 150, ("delhi", "ooty"): 5000,

    # To AMRITSAR
    ("delhi", "amritsar"): 700, ("new delhi", "amritsar"): 700,
    ("chandigarh", "amritsar"): 500, ("ludhiana", "amritsar"): 300,
    ("nawanshahr", "amritsar"): 400, ("jalandhar", "amritsar"): 200,
    ("mumbai", "amritsar"): 4000, ("bangalore", "amritsar"): 5500,

    # To DARJEELING
    ("kolkata", "darjeeling"): 700, ("delhi", "darjeeling"): 3000,
    ("new delhi", "darjeeling"): 3000, ("mumbai", "darjeeling"): 4000,
    ("patna", "darjeeling"): 1000, ("bangalore", "darjeeling"): 5000,
    ("nawanshahr", "darjeeling"): 3500,

    # To LEH LADAKH
    ("delhi", "leh_ladakh"): 5000, ("new delhi", "leh_ladakh"): 5000,
    ("chandigarh", "leh_ladakh"): 3000, ("manali", "leh_ladakh"): 1500,
    ("mumbai", "leh_ladakh"): 6000, ("bangalore", "leh_ladakh"): 7000,
    ("nawanshahr", "leh_ladakh"): 3500, ("amritsar", "leh_ladakh"): 4000,

    # To MYSORE
    ("bangalore", "mysore"): 300, ("bengaluru", "mysore"): 300,
    ("chennai", "mysore"): 700, ("delhi", "mysore"): 4500,
    ("new delhi", "mysore"): 4500, ("mumbai", "mysore"): 2500,
    ("coimbatore", "mysore"): 500,

    # To PONDICHERRY
    ("chennai", "pondicherry"): 250, ("bangalore", "pondicherry"): 600,
    ("bengaluru", "pondicherry"): 600, ("mumbai", "pondicherry"): 3000,
    ("delhi", "pondicherry"): 5000, ("new delhi", "pondicherry"): 5000,
    ("hyderabad", "pondicherry"): 2000,

    # To SPITI
    ("delhi", "spiti"): 1500, ("new delhi", "spiti"): 1500,
    ("chandigarh", "spiti"): 1000, ("manali", "spiti"): 1000,
    ("shimla", "spiti"): 1200, ("mumbai", "spiti"): 5000,
    ("nawanshahr", "spiti"): 1300,

    # To COORG
    ("bangalore", "coorg"): 500, ("bengaluru", "coorg"): 500,
    ("mysore", "coorg"): 400, ("chennai", "coorg"): 1200,
    ("mumbai", "coorg"): 2500, ("delhi", "coorg"): 5000,
    ("new delhi", "coorg"): 5000,

    # To PUSHKAR
    ("delhi", "pushkar"): 700, ("new delhi", "pushkar"): 700,
    ("jaipur", "pushkar"): 200, ("mumbai", "pushkar"): 2500,
    ("ahmedabad", "pushkar"): 900, ("nawanshahr", "pushkar"): 1500,
    ("chandigarh", "pushkar"): 1200,

    # To HAMPI
    ("bangalore", "hampi"): 700, ("bengaluru", "hampi"): 700,
    ("hyderabad", "hampi"): 600, ("mumbai", "hampi"): 2000,
    ("delhi", "hampi"): 4500, ("new delhi", "hampi"): 4500,
    ("chennai", "hampi"): 1200,

    # To MUSSOORIE
    ("delhi", "mussoorie"): 500, ("new delhi", "mussoorie"): 500,
    ("dehradun", "mussoorie"): 100, ("chandigarh", "mussoorie"): 700,
    ("mumbai", "mussoorie"): 4000, ("nawanshahr", "mussoorie"): 900,
    ("ludhiana", "mussoorie"): 950,

    # To KOLKATA
    ("delhi", "kolkata"): 1500, ("new delhi", "kolkata"): 1500,
    ("mumbai", "kolkata"): 2500, ("bangalore", "kolkata"): 3500,
    ("bengaluru", "kolkata"): 3500, ("chennai", "kolkata"): 2000,
    ("patna", "kolkata"): 600, ("varanasi", "kolkata"): 700,
    ("nawanshahr", "kolkata"): 2500,
}

def calculate_travel_cost(source_city, destination_key):
    """Calculate travel cost from source city to destination."""
    source = source_city.lower().strip()
    dest_map = {
        "goa": "goa", "manali": "manali", "jaipur": "jaipur",
        "kerala": "kerala", "delhi": "delhi", "shimla": "shimla",
        "rishikesh": "rishikesh", "agra": "agra", "varanasi": "varanasi",
        "udaipur": "udaipur", "andaman": "andaman", "ooty": "ooty",
        "mumbai": "mumbai", "amritsar": "amritsar", "darjeeling": "darjeeling",
        "leh_ladakh": "leh_ladakh", "mysore": "mysore", "pondicherry": "pondicherry",
        "spiti": "spiti", "coorg": "coorg", "pushkar": "pushkar",
        "hampi": "hampi", "mussoorie": "mussoorie", "kolkata": "kolkata",
    }
    dest = dest_map.get(destination_key, destination_key)

    # Same city / nearby — local bus/auto cost
    if source == dest or source in [dest, destination_key]:
        return 200

    # Direct lookup
    key = (source, dest)
    if key in TRAVEL_COST_TABLE:
        return TRAVEL_COST_TABLE[key]

    # Reverse lookup (bidirectional)
    rev_key = (dest, source)
    if rev_key in TRAVEL_COST_TABLE:
        return TRAVEL_COST_TABLE[rev_key]

    # Distance-based fallback using Haversine
    import math
    src_coords = CITY_COORDS.get(source)
    dest_name_for_coord = destination_key if destination_key in CITY_COORDS else dest
    dst_coords = CITY_COORDS.get(dest_name_for_coord)

    if src_coords and dst_coords:
        lat1, lon1 = math.radians(src_coords[0]), math.radians(src_coords[1])
        lat2, lon2 = math.radians(dst_coords[0]), math.radians(dst_coords[1])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        distance_km = 6371 * 2 * math.asin(math.sqrt(a))

        # Estimate cost based on distance
        if distance_km < 100:
            return 200
        elif distance_km < 300:
            return int(distance_km * 4)   # ~bus/train rate
        elif distance_km < 800:
            return int(distance_km * 3.5) # train rate
        elif distance_km < 1500:
            return int(distance_km * 3)   # train/budget flight
        else:
            return int(distance_km * 4.5) # flight

    # Ultimate fallback
    return DESTINATIONS.get(destination_key, {}).get("costs", {}).get("travel_per_person", 2000)


# ── Source city keyword extraction ─────────────────────────────
SOURCE_CITY_KEYWORDS = list(CITY_COORDS.keys())

# ── Keyword maps ───────────────────────────────────────────────
DESTINATION_KEYWORDS = {
    # Existing
    "goa": "goa", "beaches goa": "goa",
    "manali": "manali", "rohtang": "manali",
    "jaipur": "jaipur", "pink city": "jaipur", "rajasthan": "jaipur",
    "kerala": "kerala", "munnar": "kerala", "alleppey": "kerala", "kochi": "kerala",
    "delhi": "delhi", "new delhi": "delhi",
    "agra": "agra", "taj mahal": "agra",
    "shimla": "shimla",
    "varanasi": "varanasi", "banaras": "varanasi", "kashi": "varanasi",
    "mumbai": "mumbai", "bombay": "mumbai",
    "udaipur": "udaipur", "lake city": "udaipur",
    "rishikesh": "rishikesh", "yoga city": "rishikesh",
    "ooty": "ooty", "udhagamandalam": "ooty",
    "andaman": "andaman", "port blair": "andaman",
    # New
    "amritsar": "amritsar", "golden temple": "amritsar", "wagah": "amritsar",
    "darjeeling": "darjeeling", "toy train darjeeling": "darjeeling",
    "leh": "leh_ladakh", "ladakh": "leh_ladakh", "pangong": "leh_ladakh", "spiti": "spiti",
    "mysore": "mysore", "mysuru": "mysore",
    "pondicherry": "pondicherry", "puducherry": "pondicherry", "pondy": "pondicherry",
    "coorg": "coorg", "kodagu": "coorg", "madikeri": "coorg",
    "pushkar": "pushkar", "pushkar camel fair": "pushkar",
    "hampi": "hampi", "vijayanagara": "hampi",
    "mussoorie": "mussoorie", "mussorie": "mussoorie", "mussoori": "mussoorie",
    "queens of hills": "mussoorie", "queen of hills": "mussoorie",
    "kolkata": "kolkata", "calcutta": "kolkata",
    "udaypur": "udaipur",
    "hrishikesh": "rishikesh",
    "andamans": "andaman",
    "darjiling": "darjeeling", "darjeeeling": "darjeeling",
}

TRAVEL_TYPE_KEYWORDS = {
    "friends": "friends", "friend": "friends", "group": "friends", "buddies": "friends",
    "couple": "couple", "romantic": "couple", "honeymoon": "couple", "partner": "couple",
    "family": "family", "kids": "family", "children": "family", "parents": "family",
    "solo": "solo", "alone": "solo", "myself": "solo", "backpacker": "solo",
}
 
# ── Session-style conversation state (in-memory per request) ──
# We keep a global dict keyed by a simple session token sent from JS
sessions = {}
 
 
# ─────────────────────────────────────────────────────────────
# HELPER: extract info from raw text
# ─────────────────────────────────────────────────────────────
def extract_info(text):
    """Parse destination, days, budget, travel_type from free text."""
    text_lower = text.lower().strip()
    result = {}

    # Handle "skip" for source_city
    if text_lower in ("skip", "skip source", "no source"):
        result["source_city"] = "__skip__"
        return result
 
    # Destination — match longer keywords first to avoid partial matches
    # Prefer "to <place>" or "in <place>" pattern
    to_match = re.search(r"\b(?:to|visit|going to|go to|in|for)\s+([a-z\s]+?)(?:\s+for|\s+from|\s+trip|\s+with|\s+\d|,|$)", text_lower)
    if to_match:
        candidate = to_match.group(1).strip()
        for kw, dest in sorted(DESTINATION_KEYWORDS.items(), key=lambda x: -len(x[0])):
            if kw in candidate:
                result["destination"] = dest
                break
    if "destination" not in result:
        for kw, dest in sorted(DESTINATION_KEYWORDS.items(), key=lambda x: -len(x[0])):
            if kw in text_lower:
                result["destination"] = dest
                break
 
    # Duration — look for patterns like "3 day", "3-day", "3days", "for 3 days"
    day_match = re.search(r"(\d+)\s*-?\s*day", text_lower)
    if day_match:
        result["days"] = int(day_match.group(1))
 
    # Budget — look for numbers after budget-related words or ₹/rs/inr
    budget_match = re.search(
        r"(?:budget|under|within|rs\.?|₹|inr)[\s:]*(\d[\d,]*)", text_lower
    )
    if not budget_match:
        budget_match = re.search(r"(\d[\d,]{2,})", text_lower)  # bare large number
    if budget_match:
        result["budget"] = int(budget_match.group(1).replace(",", ""))
 
    # Travel type
    for kw, ttype in TRAVEL_TYPE_KEYWORDS.items():
        if kw in text_lower:
            result["travel_type"] = ttype
            break

    # Source city — look for "from <city>" pattern first, then bare city names
    from_match = re.search(r"\bfrom\s+([a-z\s]+?)(?:\s+to|\s+trip|\s+for|\s+with|$)", text_lower)
    if from_match:
        candidate = from_match.group(1).strip()
        for city in SOURCE_CITY_KEYWORDS:
            if city in candidate:
                result["source_city"] = city
                break
    if "source_city" not in result:
        for city in SOURCE_CITY_KEYWORDS:
            if re.search(r"\b" + re.escape(city) + r"\b", text_lower):
                # Make sure it's not the destination
                dest_in_text = result.get("destination", "")
                if city != dest_in_text:
                    result["source_city"] = city
                    break

    return result
 
 
# ─────────────────────────────────────────────────────────────
# HELPER: generate the full trip plan
# ─────────────────────────────────────────────────────────────
def generate_plan(destination, days, budget, travel_type, source_city=None):
    dest_data = DESTINATIONS[destination]
    travel_data = TRAVEL_TYPES[travel_type]
    costs = dest_data["costs"]
 
    # ── Budget breakdown ───────────────────────────────────────
    if source_city and source_city != "__skip__":
        travel_cost = calculate_travel_cost(source_city, destination)
    else:
        travel_cost = costs["travel_per_person"]
    food_cost = costs["food_per_day"] * days
    activity_cost = costs["activities_per_day"] * days
    transport_cost = costs["local_transport_per_day"] * days
 
    # Hotel — pick tier based on remaining budget
    hotel_budget_per_night = (budget - travel_cost - food_cost - activity_cost - transport_cost) / max(days, 1)
 
    if hotel_budget_per_night >= 8000:
        hotel_tier = "luxury"
    elif hotel_budget_per_night >= 2000:
        hotel_tier = "midrange"
    else:
        hotel_tier = "budget"
 
    hotels = dest_data["hotels"]
    hotel_cost = hotels[hotel_tier][0]["price_per_night"] * days
    total_cost = travel_cost + food_cost + activity_cost + transport_cost + hotel_cost
 
    # ── Day-wise itinerary (cap to available days in data) ────
    available_days = dest_data["days"]
    itinerary = []
    for d in range(1, days + 1):
        day_key = str(((d - 1) % len(available_days)) + 1)  # cycle if days > 3
        day_info = available_days[day_key]
        itinerary.append({
            "day": d,
            "title": day_info["title"] if d <= len(available_days) else f"Day {d} — Leisure & Exploration",
            "places": day_info["places"],
            "activities": day_info["activities"] + travel_data["activities_add"][:1],
            "food": day_info["food"],
        })
 
    # ── Build response payload ─────────────────────────────────
    plan = {
        "destination": dest_data["name"],
        "source_city": source_city.title() if source_city else None,
        "days": days,
        "budget": budget,
        "travel_type": travel_type,
        "travel_emoji": travel_data["emoji"],
        "best_time": dest_data["best_time"],
        "description": dest_data["description"],
        "map_link": dest_data["map_link"],
        "itinerary": itinerary,
        "budget_breakdown": {
            "travel": travel_cost,
            "hotel": hotel_cost,
            "food": food_cost,
            "activities": activity_cost,
            "local_transport": transport_cost,
            "total": total_cost,
            "within_budget": total_cost <= budget,
        },
        "hotels": {
            "recommended_tier": hotel_tier,
            "budget": hotels["budget"],
            "midrange": hotels["midrange"],
            "luxury": hotels["luxury"],
        },
        "tips": dest_data["tips"],
        "travel_tips": travel_data["tips"],
        "vibe": travel_data["vibe"],
    }
    return plan
 
 
# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")
 
 
@app.route("/chat", methods=["POST"])
def chat():
    """Main chatbot API endpoint."""
    body = request.get_json(force=True)
    user_msg = body.get("message", "").strip()
    session_id = body.get("session_id", "default")
 
    # Initialise session state if new
    if session_id not in sessions:
        sessions[session_id] = {}
 
    state = sessions[session_id]
 
    # Check if we're currently waiting for source_city answer
    required_done = all(k in state for k in ["destination", "days", "budget", "travel_type"])
    waiting_for_source = required_done and "source_city" not in state

    # Merge newly extracted info into state
    extracted = extract_info(user_msg)

    # Handle "skip" for source_city
    if extracted.get("source_city") == "__skip__":
        state["source_city"] = None  # None = use default cost
        extracted.pop("source_city")
    elif waiting_for_source:
        # We are specifically asking for source city — parse the reply as city only
        # Do NOT let it overwrite destination or other fields
        msg_lower = user_msg.lower().strip()
        found_city = None
        for city in SOURCE_CITY_KEYWORDS:
            if city in msg_lower:
                found_city = city
                break
        if found_city:
            state["source_city"] = found_city
        else:
            # Treat entire message as city name (fallback)
            state["source_city"] = msg_lower
        # Skip normal state.update to avoid overwriting destination
    else:
        state.update(extracted)
 
    # ── Determine missing fields & ask follow-ups ──────────────
    missing = []
    if "destination" not in state:
        missing.append("destination")
    if "days" not in state:
        missing.append("days")
    if "budget" not in state:
        missing.append("budget")
    if "travel_type" not in state:
        missing.append("travel_type")
    # source_city is optional — ask only if other required fields are filled
    if not missing and "source_city" not in state:
        missing.append("source_city")
 
    if missing:
        # Ask for the first missing piece
        field = missing[0]
        prompts = {
            "destination": {
                "text": "🗺️ Where would you like to go? We support these destinations:\n\n• **Goa** 🏖️ • **Manali** 🏔️ • **Jaipur** 🏰 • **Kerala** 🌿 • **Delhi** 🕌\n• **Agra** 🕌 • **Shimla** ❄️ • **Varanasi** 🪔 • **Mumbai** 🌆 • **Udaipur** 💧\n• **Rishikesh** 🧘 • **Ooty** 🍵 • **Andaman** 🏝️ • **Amritsar** 🕍 • **Darjeeling** 🚂\n• **Leh Ladakh** 🏔️ • **Mysore** 👑 • **Pondicherry** 🇫🇷 • **Spiti** ✨ • **Coorg** ☕\n• **Pushkar** 🐪 • **Hampi** 🏛️ • **Mussoorie** 🌄 • **Kolkata** 🎭",
                "quick_replies": ["Goa", "Manali", "Jaipur", "Kerala", "Delhi", "Leh Ladakh", "Amritsar", "Kolkata"],
            },
            "source_city": {
                "text": "📍 **Where are you travelling from?** (Your departure city — helps calculate travel cost)\n\nExample: Delhi, Mumbai, Chandigarh, Ludhiana, Amritsar, Bangalore, Kolkata...\n\n_(You can also type **'skip'** to use default travel cost)_",
                "quick_replies": ["Delhi", "Mumbai", "Chandigarh", "Amritsar", "Ludhiana", "Skip"],
            },
            "days": {
                "text": "📅 How many days are you planning to travel?",
                "quick_replies": ["2 days", "3 days", "5 days", "7 days"],
            },
            "budget": {
                "text": "💰 What is your total budget per person (in ₹)?",
                "quick_replies": ["₹5,000", "₹10,000", "₹20,000", "₹50,000"],
            },
            "travel_type": {
                "text": "👥 Who are you travelling with?",
                "quick_replies": ["Solo 🎒", "Friends 👫", "Couple ❤️", "Family 👨‍👩‍👧‍👦"],
            },
        }
        resp = prompts[field]
        return jsonify({"type": "followup", "text": resp["text"], "quick_replies": resp["quick_replies"]})
 
    # ── All info collected — generate plan ─────────────────────
    try:
        plan = generate_plan(
            destination=state["destination"],
            days=min(state["days"], 7),   # cap at 7 days
            budget=state["budget"],
            travel_type=state["travel_type"],
            source_city=state.get("source_city"),
        )
        # Clear session after plan is generated
        sessions[session_id] = {}
        return jsonify({"type": "plan", "plan": plan})
 
    except Exception as e:
        return jsonify({"type": "error", "text": f"Sorry, something went wrong: {str(e)}"})
 
 
@app.route("/reset", methods=["POST"])
def reset():
    """Reset session state."""
    body = request.get_json(force=True)
    session_id = body.get("session_id", "default")
    sessions[session_id] = {}
    return jsonify({"status": "reset"})
 
 
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)