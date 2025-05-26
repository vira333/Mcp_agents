import aiohttp
from aiohttp import web

# Agent Card
AGENT_CARD = {
    "name": "ProfileAgent",
    "capabilities": ["analyze_financial_profile"],
    "endpoint": "http://localhost:8001",
    "auth": "none"
}

async def handle_profile_task(request):
    try:
        data = await request.json()
        income = data.get("income", 0)
        expenses = data.get("expenses", {})
        goals = data.get("goals", {})
        risk_tolerance = data.get("risk_tolerance", "moderate")

        # Basic validation
        if income <= 0 or not expenses or not goals:
            return web.json_response({
                "task_id": data.get("task_id"),
                "result": "Invalid financial data provided",
                "status": "failed"
            }, status=400)

        profile = {
            "income": income,
            "monthly_expenses": expenses.get("monthly", 0),
            "savings_goal": goals.get("savings", 0),
            "risk_tolerance": risk_tolerance
        }
        return web.json_response({
            "task_id": data.get("task_id"),
            "result": profile,
            "status": "completed"
        })
    except Exception as e:
        return web.json_response({
            "task_id": data.get("task_id"),
            "result": f"Error analyzing profile: {str(e)}",
            "status": "failed"
        }, status=500)

async def get_agent_card(request):
    return web.json_response(AGENT_CARD)

app = web.Application()
app.add_routes([
    web.get('/.well-known/agent.json', get_agent_card),
    web.post('/tasks/send', handle_profile_task)
])

if __name__ == "__main__":
    web.run_app(app, port=8001)
