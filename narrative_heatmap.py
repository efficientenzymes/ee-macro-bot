import openai
import os

def generate_narrative_heatmap(chart_summaries, sentiment_summary, liquidity_summary, correlation_lines):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    joined_corr = "\n".join(correlation_lines)
    joined_charts = "\n".join(chart_summaries)

    prompt = f'''
You're a macro strategist writing a weekend memo.

Below is this week's context:

🧠 Sentiment Summary:
{sentiment_summary}

💧 Liquidity Summary:
{liquidity_summary}

🔗 Correlation Changes:
{joined_corr}

📊 Spread Commentary:
{joined_charts}

Based on this, identify the dominant macro narratives for the week.
Split into two categories:
• Gaining Momentum
• Losing Momentum

Keep it concise and institutional in tone.
'''.strip()

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300,
        )
        return "🗺️ **Narrative Heatmap**\n" + response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Failed to generate narrative heatmap: {e}"
