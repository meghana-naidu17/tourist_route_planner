
import json
from datetime import date, datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from attractions import places, attraction_info, alt_roads
from algorithm import (find_all_routes, generate_traffic, nearest_attraction,
                       build_route_segments, TRANSPORT_CONFIG)
from models import db, User, RouteHistory
from bayesian import predict_traffic, predict_next_state
from weather_data import get_weather, get_forecast, get_weather_for_attractions

 
app = Flask(__name__)
app.config['SECRET_KEY']                     = 'routewise-secret-2025'
app.config['SQLALCHEMY_DATABASE_URI']        = 'sqlite:///routewise.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
 
 
@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))
 
 
# ── Helpers ───────────────────────────────────────────────
def build_cost_breakdown(segments, transport):
    road_cost     = sum(s["cost"] for s in segments)
    cfg           = TRANSPORT_CONFIG[transport]
    transport_fee = cfg["cost_add"]
    items = [
        {
            "icon": "🛣️",
            "name": "Road / segment charges",
            "desc": f"{len(segments)} segment(s) × base fare",
            "amount": road_cost,
            "bar": "rust",
        },
        {
            "icon": {"Car": "🚗", "Bike": "🏍️", "Bus": "🚌", "Walking": "🚶"}.get(transport, "🚦"),
            "name": f"{transport} surcharge",
            "desc": "No cost — walking is free!" if transport == "Walking" else "Fuel / ticket / fare add-on",
            "amount": transport_fee,
            "bar": "teal",
        },
    ]
    total = sum(i["amount"] for i in items) or 1
    for item in items:
        item["pct"] = round(item["amount"] / total * 100)
    return items, total
 
 
def get_user_stats(user_id):
    today_routes = (RouteHistory.query
                    .filter_by(user_id=user_id)
                    .filter(db.func.date(RouteHistory.searched_at) == date.today())
                    .all())
    all_routes = RouteHistory.query.filter_by(user_id=user_id).all()
    return {
        "routes_today":     len(today_routes),
        "total_distance":   round(sum(r.distance or 0 for r in today_routes), 1),
        "total_cost":       sum(r.cost or 0 for r in today_routes),
        "total_routes_all": len(all_routes),
    }
 
 
# ── Auth ──────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user, remember="remember" in request.form)
            return redirect(url_for("dashboard"))
        error = "Invalid email or password."
    return render_template("login.html", error=error)
 
 
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    error = None
    if request.method == "POST":
        if request.form["password"] != request.form["confirm"]:
            error = "Passwords don't match."
        elif User.query.filter_by(email=request.form["email"]).first():
            error = "Email already registered."
        elif User.query.filter_by(username=request.form["username"]).first():
            error = "Username taken."
        else:
            u = User(
                username=request.form["username"],
                email=request.form["email"],
                password=generate_password_hash(request.form["password"]),
            )
            db.session.add(u)
            db.session.commit()
            flash("Account created! Log in now.", "success")
            return redirect(url_for("login"))
    return render_template("signup.html", error=error)
 
 
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
 
 
# ── Dashboard (new landing page after login) ──────────────
from datetime import date, datetime

# ----------------------------------
# Flask-Login User Loader
# ----------------------------------
@login_manager.user_loader
def load_user(uid):
    return db.session.get(User, int(uid))


# ----------------------------------
# Dashboard
# ----------------------------------
@app.route("/dashboard")
@login_required
def dashboard():

    history = (
        RouteHistory.query
        .filter_by(user_id=current_user.id)
        .order_by(RouteHistory.searched_at.desc())
        .limit(8)
        .all()
    )

    stats = get_user_stats(current_user.id)

    # Fix for dashboard greeting
    now_hour = datetime.now().hour

    # Live city weather
    city_weather = get_weather_for_attractions(attraction_info)

    # Forecast
    lats = [v["lat"] for v in attraction_info.values()]
    lngs = [v["lng"] for v in attraction_info.values()]

    clat = sum(lats) / len(lats)
    clng = sum(lngs) / len(lngs)

    forecast = get_forecast(clat, clng, days=3)

    # Traffic snapshot
    traffic_snap = generate_traffic(
        places,
        city_weather.get("category", "Sunny"),
        "Peak"
    )

    high_count = sum(
        1 for v in traffic_snap.values()
        if v == "high"
    )

    med_count = sum(
        1 for v in traffic_snap.values()
        if v == "medium"
    )

    return render_template(
        "dashboard.html",
        attraction_info=attraction_info,
        places=list(places.keys()),
        history=history,
        stats=stats,
        city_weather=city_weather,
        forecast=forecast,
        high_count=high_count,
        med_count=med_count,
        traffic_snap=traffic_snap,
        now_hour=now_hour
    )
 
 
# ── Root redirect ─────────────────────────────────────────
@app.route("/")
@login_required
def home():
    return redirect(url_for("dashboard"))
 
 
# ── Route Planner ─────────────────────────────────────────
@app.route("/planner")
@login_required
def planner():
    history = (RouteHistory.query
               .filter_by(user_id=current_user.id)
               .order_by(RouteHistory.searched_at.desc())
               .limit(5).all())
    return render_template(
        "index.html",
        places=list(places.keys()),
        attraction_info=attraction_info,
        history=history,
        weather="Sunny",
        time_of_day="Peak",
    )
 
 
@app.route("/find_route", methods=["POST"])
@login_required
def find_route():
    start       = request.form.get("start")
    end         = request.form.get("end")
    transport   = request.form.get("transport", "Car")
    optimize    = request.form.get("optimize", "distance")
    user_lat    = request.form.get("user_lat", "")
    user_lng    = request.form.get("user_lng", "")
    weather     = request.form.get("weather", "Sunny")
    time_of_day = request.form.get("time_of_day", "Peak")
 
    error = primary = alts = traffic = None
    nearest = nearest_dist = None
    segments = []
    path_edges = set()
    cost_items = []
    cost_total = 0
 
    if user_lat and user_lng:
        try:
            nearest, nearest_dist = nearest_attraction(
                float(user_lat), float(user_lng), attraction_info)
            start = nearest
        except Exception:
            nearest = None
 
    if not start or not end or start == end:
        error = "⚠️ Start and destination must be different!"
    else:
        traffic = generate_traffic(places, weather, time_of_day)
        primary, alts, traffic = find_all_routes(
            places, start, end, transport, optimize, traffic)
 
        if not primary:
            error = "No route found between selected locations."
        else:
            segments = build_route_segments(
                primary["path"], places, traffic, alt_roads)
            for s in segments:
                path_edges.add(f"{s['from']}_{s['to']}")
            cost_items, cost_total = build_cost_breakdown(segments, transport)
 
            rh = RouteHistory(
                user_id=current_user.id,
                start=start, end=end,
                transport=transport, optimize=optimize,
                distance=primary["distance"],
                cost=primary["cost"],
                time=primary["time"],
                path=json.dumps(primary["path"]),
            )
            db.session.add(rh)
            db.session.commit()
 
    history = (RouteHistory.query
               .filter_by(user_id=current_user.id)
               .order_by(RouteHistory.searched_at.desc())
               .limit(5).all())
 
    high_bypass_count = sum(
        1 for s in segments if s["traffic"] == "high" and s["bypasses"])
 
    return render_template(
        "index.html",
        places=list(places.keys()),
        attraction_info=attraction_info,
        primary=primary,
        alternatives=alts,
        transport=transport,
        transport_emoji=TRANSPORT_CONFIG[transport]["emoji"],
        optimize=optimize,
        start=start, end=end,
        error=error,
        segments=segments,
        path_edges=path_edges,
        traffic=traffic or {},
        user_lat=user_lat, user_lng=user_lng,
        nearest=nearest, nearest_dist=nearest_dist,
        cost_items=cost_items, cost_total=cost_total,
        high_bypass_count=high_bypass_count,
        history=history,
        weather=weather, time_of_day=time_of_day,
    )
 
 
# ── History page ──────────────────────────────────────────
@app.route("/history")
@login_required
def history_page():
    all_history = (RouteHistory.query
                   .filter_by(user_id=current_user.id)
                   .order_by(RouteHistory.searched_at.desc())
                   .all())
    return render_template("history.html",
                           history=all_history,
                           attraction_info=attraction_info)
 
 
# ── API: Nearest attraction ───────────────────────────────
@app.route("/api/nearest")
@login_required
def api_nearest():
    try:
        lat  = float(request.args.get("lat"))
        lng  = float(request.args.get("lng"))
        name, dist = nearest_attraction(lat, lng, attraction_info)
        info = attraction_info[name]
        return jsonify({"name": name, "dist_km": dist,
                        "icon": info["icon"], "category": info["category"],
                        "lat": info["lat"], "lng": info["lng"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
 
 
# ── API: Live traffic ─────────────────────────────────────
@app.route("/api/traffic")
@login_required
def api_traffic():
    weather     = request.args.get("weather", "Sunny")
    time_of_day = request.args.get("time_of_day", "Peak")
    return jsonify(generate_traffic(places, weather, time_of_day))
 
 
# ── API: Live weather for a location ─────────────────────
@app.route("/api/weather")
@login_required
def api_weather():
    try:
        lat  = float(request.args.get("lat", 13.05))
        lng  = float(request.args.get("lng", 80.25))
        name = request.args.get("name", "")
        return jsonify(get_weather(lat, lng, name))
    except Exception as e:
        return jsonify({"error": str(e)}), 400
 
 
# ── API: Forecast ─────────────────────────────────────────
@app.route("/api/forecast")
@login_required
def api_forecast():
    try:
        lat  = float(request.args.get("lat", 13.05))
        lng  = float(request.args.get("lng", 80.25))
        days = int(request.args.get("days", 3))
        return jsonify(get_forecast(lat, lng, days))
    except Exception as e:
        return jsonify({"error": str(e)}), 400
 
 
# ── API: Search suggestions ───────────────────────────────
@app.route("/api/search")
@login_required
def api_search():
    q = request.args.get("q", "").lower().strip()
    if not q:
        return jsonify([])
    results = [
        {"name": name, "icon": info["icon"], "category": info["category"],
         "rating": info["rating"], "tagline": info["tagline"]}
        for name, info in attraction_info.items()
        if q in name.lower() or q in info["category"].lower() or q in info["tagline"].lower()
    ]
    return jsonify(results[:6])
 
 
# ── API: Stats ribbon ─────────────────────────────────────
@app.route("/api/stats")
@login_required
def api_stats():
    return jsonify(get_user_stats(current_user.id))
 
 
# ── API: Notifications ────────────────────────────────────
@app.route("/api/notifications")
@login_required
def api_notifications():
    traffic = generate_traffic(places, "Sunny", "Peak")
    alerts = []
    for key, level in traffic.items():
        if level == "high":
            parts = key.split("_", 1)
            if len(parts) == 2:
                a, b = parts
                alerts.append({"text": f"Heavy traffic on {a} → {b} right now",
                                "level": "high", "unread": True})
        elif level == "medium" and len(alerts) < 3:
            parts = key.split("_", 1)
            if len(parts) == 2:
                a, b = parts
                alerts.append({"text": f"Moderate traffic on {a} → {b}",
                                "level": "medium", "unread": False})
    return jsonify(alerts[:5])
 
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)