import aiohttp
from aiohttp import web

# Agent Card
AGENT_CARD = {
    "name": "RecommendationAgent",
    "capabilities": ["generate_recommendations"],
    "endpoint": "http://localhost:8003",
    "auth": "none"
}

async def handle_recommendation_task(request):
    try:
        data = await request.json()
        profile = data.get("profile", {})
        market_data = data.get("market_data", {})

        income = profile.get("income", 0)
        expenses = profile.get("monthly_expenses", 0)
        savings_goal = profile.get("savings_goal", 0)
        risk_tolerance = profile.get("risk_tolerance", "moderate")

        # Simple budget rule: 50% needs, 30% wants, 20% savings/investments
        budget = {
            "needs": income * 0.5,
            "wants": income * 0.3,
            "savings_investments": income * 0.2
        }

        # Investment recommendation based on risk tolerance and market data
        investments = []
        if risk_tolerance == "high" and market_data.get("stocks", {}).get("trend") == "bullish":
            investments.append("Invest 70% in stocks, 30% in bonds")
        elif risk_tolerance == "moderate":
            investments.append("Invest 50% in stocks, 50% in bonds")
        else:
            investments.append("Invest 30% in stocks, 70% in bonds")

        recommendations = {
            "budget": budget,
            "investments": investments
        }
        return web.json_response({
            "task_id": data.get("task_id"),
            "result": recommendations,
            "status": "completed"
        })
    except Exception as e:
        return web.json_response({
            "task_id": data.get("task_id"),
            "result": f"Error generating recommendations: {str(e)}",
            "status": "failed"
        }, status=500)

async def get_agent_card(request):
    return web.json_response(AGENT_CARD)

app = web.Application()
app.add_routes([
    web.get('/.well-known/agent.json', get_agent_card),
    web.post('/tasks/send', handle_recommendation_task)
])

if __name__ == "__main__":
    web.run_app(app, port=8003)
