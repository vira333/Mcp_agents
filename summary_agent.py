import aiohttp
import os
from aiohttp import web
from openai import AzureOpenAI

# Load Azure Open AI credentials
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Initialize Azure Open AI client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-02-15-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

# Agent Card
AGENT_CARD = {
    "name": "SummaryAgent",
    "capabilities": ["summarize_plan"],
    "endpoint": "http://localhost:8004",
    "auth": "none"
}

async def handle_summary_task(request):
    try:
        data = await request.json()
        profile = data.get("profile", {})
        market_data = data.get("market_data", {})
        recommendations = data.get("recommendations", {})

        prompt = f"""
        Summarize a financial plan for a user with:
        - Monthly income: ${profile.get('income', 0)}
        - Monthly expenses: ${profile.get('monthly_expenses', 0)}
        - Savings goal: ${profile.get('savings_goal', 0)}
        - Risk tolerance: {profile.get('risk_tolerance', 'moderate')}
        - Market trends: Stocks ({market_data.get('stocks', {}).get('trend', 'unknown')}, {market_data.get('stocks', {}).get('returns', 'N/A')}), Bonds ({market_data.get('bonds', {}).get('trend', 'unknown')}, {market_data.get('bonds', {}).get('returns', 'N/A')})
        - Budget: Needs ${recommendations.get('budget', {}).get('needs', 0)}, Wants ${recommendations.get('budget', {}).get('wants', 0)}, Savings/Investments ${recommendations.get('budget', {}).get('savings_investments', 0)}
        - Investments: {', '.join(recommendations.get('investments', []))}
        Provide a concise, user-friendly summary.
        """

        # Call Azure Open AI
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a financial assistant providing clear, concise summaries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()

        return web.json_response({
            "task_id": data.get("task_id"),
            "result": summary,
            "status": "completed"
        })
    except Exception as e:
        return web.json_response({
            "task_id": data.get("task_id"),
            "result": f"Error generating summary: {str(e)}",
            "status": "failed"
        }, status=500)

async def get_agent_card(request):
    return web.json_response(AGENT_CARD)

app = web.Application()
app.add_routes([
    web.get('/.well-known/agent.json', get_agent_card),
    web.post('/tasks/send', handle_summary_task)
])

if __name__ == "__main__":
    web.run_app(app, port=8004)
