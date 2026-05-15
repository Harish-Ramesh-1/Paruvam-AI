import os
import warnings

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

try:
    from google import genai
    from google.genai import types as genai_types

    USING_NEW_GEMINI = True
except ImportError:
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning
    )
    import google.generativeai as genai

    USING_NEW_GEMINI = False


def generate_environment_report(data):

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    prompt = f"""INTERNAL CONTEXT — for your reasoning only. Do not copy, list, or quote these numbers in your reply; the user already sees them in the app.

Temperature (°C): {data["temperature"]}
Humidity (%): {data["humidity"]}
Rainfall (mm): {data.get("rainfall", "n/a")}
US AQI: {data["aqi"]}
PM2.5 (µg/m³): {data.get("pm2_5", "n/a")}, PM10 (µg/m³): {data.get("pm10", "n/a")}
App risk tier (do not use these words as labels in your answer): {data["risk_level"]}
Model flags this snapshot as atypical (outlier): {data.get("anomaly_detected", "n/a")}

Write exactly four numbered sections for a general reader. Use warm, cumulative, human-readable prose—facts woven into sentences, not bullet dumps. Never mention coordinates, map cells, grid IDs, model scores, or the named risk tier (e.g. LOW, HIGH). Do not restate the raw readings; only interpret what they mean for comfort, health, and daily life. You may paraphrase the situation in everyday language (e.g. a settled day vs. a day to stay alert).

1. Environmental summary — one short paragraph: what the day “feels” like overall and what stands out in plain language.
2. Possible health risks — grounded in that picture (heat, humidity, air only as relevant), still without repeating figures.
3. Precautions — practical habits for today, in full sentences.
4. Affected sectors — who should be extra mindful (workers, children, respiratory conditions, etc.) in plain terms.

Keep it concise. Vary wording across requests; no markdown beyond the numbered list."""

    if USING_NEW_GEMINI:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.9,
                top_p=0.95,
            )
        )
        return response.text

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=(
            "You interpret environmental conditions for lay readers. Never repeat raw metrics, "
            "coordinates, or grid identifiers in the answer—only clear, human implications."
        )
    )

    # Generate the response
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.9,
            top_p=0.95,
        )
    )

    return response.text