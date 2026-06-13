# ── Graph: edges with distance/cost/time + scenic_via waypoints ──────────────
places = {
    "Beach": {
        "Museum": {"distance": 5,  "cost": 100, "time": 15,
                   "via": [{"name":"Marina Promenade","icon":"🌊","desc":"India's longest urban beach promenade. Great sunrise views."}]},
        "Park":   {"distance": 7,  "cost": 120, "time": 20,
                   "via": [{"name":"Elliots Beach","icon":"🏄","desc":"Quieter southern beach popular with locals in the evenings."}]},
        "Harbor": {"distance": 3,  "cost": 60,  "time": 10,
                   "via": [{"name":"Fishing Village","icon":"⛵","desc":"Traditional fishing boats and fresh catch markets every morning."}]},
    },
    "Museum": {
        "Beach":  {"distance": 5,  "cost": 100, "time": 15, "via": []},
        "Temple": {"distance": 4,  "cost": 80,  "time": 10,
                   "via": [{"name":"Flower Market","icon":"🌸","desc":"Fragrant wholesale flower market. Marigold garlands and jasmine in abundance."}]},
        "Mall":   {"distance": 6,  "cost": 110, "time": 18,
                   "via": [{"name":"Art District","icon":"🎨","desc":"Street murals and indie galleries line this creative quarter."}]},
    },
    "Park": {
        "Beach":  {"distance": 7,  "cost": 120, "time": 20, "via": []},
        "Temple": {"distance": 3,  "cost": 60,  "time": 8,
                   "via": [{"name":"Heritage Lane","icon":"🏛️","desc":"Colonial-era buildings and tree-lined boulevards."}]},
        "Zoo":    {"distance": 4,  "cost": 70,  "time": 12,
                   "via": [{"name":"Botanical Garden","icon":"🌿","desc":"150-year-old garden with rare orchids and a lily pond."}]},
    },
    "Temple": {
        "Museum": {"distance": 4,  "cost": 80,  "time": 10, "via": []},
        "Park":   {"distance": 3,  "cost": 60,  "time": 8,  "via": []},
        "Fort":   {"distance": 6,  "cost": 90,  "time": 14,
                   "via": [{"name":"Old City Gate","icon":"🏰","desc":"16th-century Portuguese gate — perfect photo stop."},
                            {"name":"Spice Bazaar","icon":"🌶️","desc":"Aromatic spice lanes with cardamom, cloves and pepper."}]},
    },
    "Harbor": {
        "Beach":  {"distance": 3,  "cost": 60,  "time": 10, "via": []},
        "Fort":   {"distance": 5,  "cost": 85,  "time": 12,
                   "via": [{"name":"Lighthouse Point","icon":"🔦","desc":"Working 1884 lighthouse. Panoramic sea views from the top."}]},
        "Mall":   {"distance": 8,  "cost": 140, "time": 22,
                   "via": [{"name":"Sea Bridge","icon":"🌉","desc":"Scenic 2 km bridge over the backwaters — stunning at dusk."}]},
    },
    "Fort": {
        "Temple": {"distance": 6,  "cost": 90,  "time": 14, "via": []},
        "Harbor": {"distance": 5,  "cost": 85,  "time": 12, "via": []},
        "Zoo":    {"distance": 9,  "cost": 150, "time": 25,
                   "via": [{"name":"Countryside Road","icon":"🌾","desc":"Scenic drive past paddy fields and rural villages."}]},
    },
    "Zoo": {
        "Park":   {"distance": 4,  "cost": 70,  "time": 12, "via": []},
        "Fort":   {"distance": 9,  "cost": 150, "time": 25, "via": []},
        "Mall":   {"distance": 5,  "cost": 90,  "time": 14,
                   "via": [{"name":"Food Street","icon":"🍜","desc":"South Indian street food: dosas, idlis and filter coffee."}]},
    },
    "Mall": {
        "Museum": {"distance": 6,  "cost": 110, "time": 18, "via": []},
        "Harbor": {"distance": 8,  "cost": 140, "time": 22, "via": []},
        "Zoo":    {"distance": 5,  "cost": 90,  "time": 14, "via": []},
    },
}

# ── Attraction metadata ───────────────────────────────────────────────────────
attraction_info = {
    "Beach":  {
        "icon": "🏖️", "category": "Nature",   "rating": 4.5,
        "lat": 13.0827, "lng": 80.2707,
        "tagline": "India's longest urban beach — sunrise walks & seafood",
        "highlights": ["Sunrise views", "Fresh seafood stalls", "Camel rides"],
        "best_time": "Early morning or sunset",
    },
    "Museum": {
        "icon": "🏛️", "category": "Culture",  "rating": 4.7,
        "lat": 13.0600, "lng": 80.2750,
        "tagline": "South India's premier cultural museum since 1851",
        "highlights": ["Bronze gallery", "Ancient coins", "Children's museum"],
        "best_time": "Weekday mornings",
    },
    "Park": {
        "icon": "🌳", "category": "Nature",   "rating": 4.3,
        "lat": 13.0500, "lng": 80.2100,
        "tagline": "Green lungs of the city — lakes, deer and picnic lawns",
        "highlights": ["Boating lake", "Rose garden", "Deer park"],
        "best_time": "Mornings & evenings",
    },
    "Temple": {
        "icon": "🛕", "category": "Heritage", "rating": 4.8,
        "lat": 13.0878, "lng": 80.2785,
        "tagline": "1200-year-old Dravidian temple with intricate stone carvings",
        "highlights": ["Gopuram tower", "Evening aarti", "Chariot festival"],
        "best_time": "6–8 AM or 6–8 PM",
    },
    "Harbor": {
        "icon": "⚓", "category": "Scenic",   "rating": 4.4,
        "lat": 13.0900, "lng": 80.2880,
        "tagline": "Historic port with colonial warehouses and fishing trawlers",
        "highlights": ["Fishing harbour", "Colonial warehouses", "Sunset cruises"],
        "best_time": "Late afternoon",
    },
    "Fort": {
        "icon": "🏯", "category": "Heritage", "rating": 4.6,
        "lat": 13.1000, "lng": 80.2900,
        "tagline": "16th-century fort with ramparts overlooking the sea",
        "highlights": ["Cannon ramparts", "Sea views", "Sound & light show"],
        "best_time": "Evening for the light show",
    },
    "Zoo": {
        "icon": "🦁", "category": "Wildlife", "rating": 4.2,
        "lat": 13.0100, "lng": 80.2200,
        "tagline": "One of India's oldest zoos — tigers, elephants and lions",
        "highlights": ["Bengal tigers", "White peacocks", "Nocturnal house"],
        "best_time": "Weekday mornings",
    },
    "Mall": {
        "icon": "🛍️", "category": "Shopping", "rating": 4.0,
        "lat": 13.0700, "lng": 80.2300,
        "tagline": "Largest shopping mall in the region — food court and cinema",
        "highlights": ["International brands", "Food court", "IMAX cinema"],
        "best_time": "Weekends after 4 PM",
    },
}

# ── Alternative (bypass) roads for high-traffic segments ─────────────────────
# Key = "From_To", value = list of bypass route options
alt_roads = {
    "Beach_Museum": [
        {"label": "Via Inner Road", "extra_km": 1, "extra_min": 3,
         "desc": "Avoids the coastal highway bottleneck. Passes through residential lanes."},
        {"label": "Via Expressway Slip", "extra_km": 2, "extra_min": -2,
         "desc": "Slightly longer but high-speed — actually saves time despite distance."},
    ],
    "Beach_Park": [
        {"label": "Via ECR Bypass", "extra_km": 2, "extra_min": 5,
         "desc": "East Coast Road bypass — quieter toll road parallel to the beach."},
    ],
    "Temple_Fort": [
        {"label": "Via Old Bazaar Road", "extra_km": 1, "extra_min": 4,
         "desc": "Narrow but traffic-free heritage lane through the old quarter."},
        {"label": "Via Ring Road North", "extra_km": 3, "extra_min": -1,
         "desc": "Ring road is fast — recommended during peak hours."},
    ],
    "Harbor_Mall": [
        {"label": "Via South Bypass", "extra_km": 2, "extra_min": 2,
         "desc": "Avoid the harbour junction signal by looping south."},
    ],
    "Fort_Zoo": [
        {"label": "Via Highway 32", "extra_km": 1, "extra_min": -5,
         "desc": "4-lane highway — fastest option even with a slight detour."},
    ],
    "Museum_Mall": [
        {"label": "Via Metro Parallel Road", "extra_km": 1, "extra_min": 3,
         "desc": "Service road alongside metro line — minimal signals."},
    ],
}