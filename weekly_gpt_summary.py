import openai
import os
import logging

logger = logging.getLogger("macro-bot")

def generate_weekly_summary_gpt(past_week_events, next_week_events):
    try:
        client = openai.OpenAI()
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            logger.warning("[WARNING] OPENAI_API_KEY not set.")
            return None

        prompt = (
            "You're a macro trader writing a blunt weekly wrap-up. "
            "Summarize what happened last week and what to watch next week in one straight-to-the-point sentence. "
            "Be concise, useful, and direct. No fluff. No intro.\n\n"
            f"Last week: {', '.join(past_week_events) or 'Notable earnings and sentiment shifts'}\n"
            f"Next week: {', '.join(next_week_events) or 'FOMC minutes, NVDA earnings, Powell speaking'}"
        )

        logger.info("[DEBUG] Calling GPT for weekly summary...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=60,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.warning(f"[WARNING] generate_weekly_summary_gpt failed: {e}")
        return None
