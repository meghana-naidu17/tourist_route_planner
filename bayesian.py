import random

# Bayesian Traffic Prediction

def predict_traffic(time_of_day, weather, road_type="normal"):

    if weather == "Rainy":
        if time_of_day == "Peak":
            probs = ["high"] * 7 + ["medium"] * 2 + ["low"]
        else:
            probs = ["medium"] * 6 + ["high"] * 2 + ["low"] * 2

    elif weather == "Cloudy":
        if time_of_day == "Peak":
            probs = ["medium"] * 6 + ["high"] * 2 + ["low"] * 2
        else:
            probs = ["low"] * 6 + ["medium"] * 3 + ["high"]

    else:  # Sunny
        if time_of_day == "Peak":
            probs = ["medium"] * 5 + ["low"] * 4 + ["high"]
        else:
            probs = ["low"] * 8 + ["medium"] * 2

    return random.choice(probs)


# Hidden Markov Model (Traffic State Transition)

HMM_TRANSITIONS = {
    "low": {
        "low": 0.7,
        "medium": 0.25,
        "high": 0.05
    },
    "medium": {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.3
    },
    "high": {
        "low": 0.05,
        "medium": 0.25,
        "high": 0.7
    }
}
def traffic_probability(level):
    data = {
        "low": 0.20,
        "medium": 0.55,
        "high": 0.85
    }
    return round(data[level] * 100)

def predict_next_state(current_state):

    transitions = HMM_TRANSITIONS[current_state]

    rand = random.random()

    cumulative = 0

    for state, probability in transitions.items():
        cumulative += probability

        if rand <= cumulative:
            return state

    return current_state