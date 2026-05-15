def get_risk_level(anomaly_score):

    if anomaly_score > 0.1:
        return {
            "level": "NORMAL",
            "color": "green"
        }

    elif anomaly_score > 0.02:
        return {
            "level": "LOW",
            "color": "yellow"
        }

    elif anomaly_score > -0.04:
        return {
            "level": "HIGH",
            "color": "orange"
        }

    elif anomaly_score > -0.12:
        return {
            "level": "VERY HIGH",
            "color": "red"
        }

    else:
        return {
            "level": "EXTREME",
            "color": "darkred"
        }