import aiohttp
from aiohttp import web

# Mock market data
MOCK_MARKET_DATA = {
    "stocks": {"trend": "bullish", "returns": "8%"},
    "bonds": {"trend": "stable", "returns": "3%"}
}

# Agent Card
AGENT_CARD = {
    "name": "MarketAgent",
    "capabilities": ["fetch_market_data"],
    "endpoint": "http://localhost:8002",
    "auth": "none"
}

async def handle_market_task(request):
    try:
        data = await request.json()
        market_data = MOCK_MARKET_DATA
        return web.json_response({
            "task_id": data.get("task_id"),
            "result": market_data,
            "status": "completed"
        })
    except Exception as e:
        return web.json_response({
            "task_id": data.get("task_id"),
            "result": f"Error fetching market data: {str(e)}",
            "status": "failed"
        }, status=500)

async def get_agent_card(request):
    return web.json_response(AGENT_CARD)

app = web.Application()
app.add_routes([
    web.get('/.well-known/agent.json', get_agent_card),
    web.post('/tasks/send', handle_market_task)
])

if __name__ == "__main__":
    web.run_app(app, port=8002)
