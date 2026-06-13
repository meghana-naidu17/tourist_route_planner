import heapq, random, math
from bayesian import predict_traffic, predict_next_state
TRANSPORT_CONFIG = {
    "Car":     {"cost_add": 200, "time_add": 0,  "speed_factor": 1.0, "emoji": "🚗"},
    "Bike":    {"cost_add": 80,  "time_add": 5,  "speed_factor": 1.2, "emoji": "🏍️"},
    "Bus":     {"cost_add": 40,  "time_add": 15, "speed_factor": 1.5, "emoji": "🚌"},
    "Walking": {"cost_add": 0,   "time_add": 40, "speed_factor": 3.0, "emoji": "🚶"},
}
TRAFFIC_MULT = {"low": 1.0, "medium": 1.25, "high": 1.6}


def generate_traffic(
        graph,
        weather="Sunny",
        time_of_day="Peak"):

    traffic = {}

    for a, nbrs in graph.items():

        for b in nbrs:

            current = predict_traffic(
                time_of_day,
                weather
            )

            predicted = predict_next_state(current)

            traffic[f"{a}_{b}"] = predicted

    return traffic


def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat, dlng = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def nearest_attraction(user_lat, user_lng, attraction_info):
    best, best_d = None, float("inf")
    for name, info in attraction_info.items():
        d = haversine(user_lat, user_lng, info["lat"], info["lng"])
        if d < best_d:
            best_d, best = d, name
    return best, round(best_d, 2)


def dijkstra(graph, start, end, optimize="distance", traffic=None):
    if traffic is None:
        traffic = {}
    ki = {"distance": 0, "cost": 1, "time": 2}[optimize]
    q = [(0, start, [], 0, 0, 0)]
    vis = set()
    while q:
        q.sort(key=lambda x: x[0])
        pr, node, path, td, tc, tt = q.pop(0)
        if node in vis:
            continue
        vis.add(node)
        path = path + [node]
        if node == end:
            return {"path": path, "d": td, "c": tc, "t": tt}
        for nb, e in graph.get(node, {}).items():
            if nb in vis:
                continue
            tf = TRAFFIC_MULT.get(traffic.get(f"{node}_{nb}", "low"), 1.0)
            nd = td + e["distance"]
            nc = tc + e["cost"]
            nt = tt + round(e["time"] * tf)
            q.append(([nd, nc, nt][ki], nb, path, nd, nc, nt))
    return None


def find_all_routes(graph, start, end, transport, optimize="distance", traffic=None):
    if traffic is None:
        traffic = generate_traffic(graph)
    cfg = TRANSPORT_CONFIG.get(transport, TRANSPORT_CONFIG["Car"])

    def apply(res):
        cost = 0 if transport == "Walking" else res["c"] + cfg["cost_add"]
        time = round(res["t"] * cfg["speed_factor"]) + cfg["time_add"]
        return {"path": res["path"], "distance": res["d"],
                "cost": cost, "time": time}

    results = {}
    for crit in ["distance", "cost", "time"]:
        r = dijkstra(graph, start, end, optimize=crit, traffic=traffic)
        if r:
            results[crit] = {**apply(r), "optimized_for": crit}

    primary = results.get(optimize)
    alts = [v for k, v in results.items()
            if k != optimize
            and v and v.get("path") != (primary or {}).get("path")]
    return primary, alts, traffic


from weather_data import get_weather

from weather_data import get_weather
from attractions import attraction_info

def build_route_segments(path, places, traffic, alt_roads):

    segments = []

    for i in range(len(path) - 1):

        a, b = path[i], path[i + 1]

        key = f"{a}_{b}"
        lvl = traffic.get(key, "low")
        tf = TRAFFIC_MULT.get(lvl, 1.0)

        e = places[a][b]

        via = e.get("via", [])
        bypasses = []

        if lvl == "high":
            bypasses = alt_roads.get(key, [])

        # Get coordinates of destination node
        lat = attraction_info[b]["lat"]
        lng = attraction_info[b]["lng"]

        weather = get_weather(lat, lng)

        segments.append({
            "from": a,
            "to": b,
            "distance": e["distance"],
            "cost": e["cost"],
            "time": round(e["time"] * tf),
            "traffic": lvl,
            "weather": weather,
            "via": via,
            "bypasses": bypasses
        })

    return segments