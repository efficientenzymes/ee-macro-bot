import os
import logging

logger = logging.getLogger("macro-bot")

USE_GPT = os.getenv("USE_GPT", "false").lower() == "true"

def generate_positioning_blurb(events, sentiment, is_weekly=False):
    logger.info("[DEBUG] generate_positioning_blurb running")
    logger.info(f"[DEBUG] USE_GPT = {USE_GPT}")
    logger.info(f"[DEBUG] Events = {events}")
    logger.info(f"[DEBUG] Sentiment = {sentiment}")

    if not USE_GPT:
        logger.info("[INFO] GPT disabled — using fallback blurb.")
        return "Markets calm. Stay tactical. Watch for rotation."

    try:
        import openai
        key = os.getenv("OPENAI_API_KEY")

        if not key:
            logger.error("[ERROR] OPENAI_API_KEY is missing.")
            return "API key not set."

        logger.info(f"[DEBUG] GPT Key starts with: {key[:8]}...")
        openai.api_key = key

        prompt = f"""You're a seasoned macro trader writing a 1–2 sentence summary.
Today’s events: {', '.join(events[:5])}
VIX={sentiment['vix']} ({sentiment['vix_level']}), MOVE={sentiment['move']} ({sentiment['move_level']}), Put/Call={sentiment['put_call']} ({sentiment['put_call_level']})
Context: {'Weekly' if is_weekly else 'Daily'} outlook. Be blunt and real.

Examples:
- CPI sets tone — any upside surprise could spark fade.
- Bonds tame, but risk assets stretched. Rotation risk.

Write your line:"""

        logger.info("[DEBUG] Sending prompt to GPT...")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=50
        )
        logger.info("[DEBUG] GPT response received.")
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.warning(f"[WARNING] GPT failed: {e}")
        return "Market positioning unavailable today."
