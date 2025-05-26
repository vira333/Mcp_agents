import aiohttp
import asyncio
import json

AGENT_REGISTRY = [
    "http://localhost:8001/.well-known/agent.json",
    "http://localhost:8002/.well-known/agent.json",
    "http://localhost:8003/.well-known/agent.json",
    "http://localhost:8004/.well-known/agent.json"
]

async def fetch_agent_card(session, url):
    async with session.get(url) as response:
        return await response.json()

async def send_task(session, endpoint, task):
    async with session.post(f"{endpoint}/tasks/send", json=task) as response:
        return await response.json()

async def orchestrate_financial_plan(user_input):
    async with aiohttp.ClientSession() as session:
        # Discover agents
        agents = {}
        for url in AGENT_REGISTRY:
            card = await fetch_agent_card(session, url)
            agents[card["name"]] = card

        # Step 1: Analyze user profile
        profile_task = {"task_id": "1", **user_input}
        profile_response = await send_task(session, agents["ProfileAgent"]["endpoint"], profile_task)
        if profile_response["status"] != "completed":
            print(f"Error: {profile_response['result']}")
            return {"error": profile_response["result"]}
        profile = profile_response["result"]
        print(f"Profile:\n{json.dumps(profile, indent=2)}")

        # Step 2: Fetch market data
        market_task = {"task_id": "2"}
        market_response = await send_task(session, agents["MarketAgent"]["endpoint"], market_task)
        if market_response["status"] != "completed":
            print(f"Error: {market_response['result']}")
            return {"error": market_response["result"]}
        market_data = market_response["result"]
        print(f"Market Data:\n{json.dumps(market_data, indent=2)}")

        # Step 3: Generate recommendations
        recommendation_task = {"task_id": "3", "profile": profile, "market_data": market_data}
        recommendation_response = await send_task(session, agents["RecommendationAgent"]["endpoint"], recommendation_task)
        if recommendation_response["status"] != "completed":
            print(f"Error: {recommendation_response['result']}")
            return {"error": recommendation_response["result"]}
        recommendations = recommendation_response["result"]
        print(f"Recommendations:\n{json.dumps(recommendations, indent=2)}")

        # Step 4: Summarize plan
        summary_task = {"task_id": "4", "profile": profile, "market_data": market_data, "recommendations": recommendations}
        summary_response = await send_task(session, agents["SummaryAgent"]["endpoint"], summary_task)
        if summary_response["status"] != "completed":
            print(f"Error: {summary_response['result']}")
            return {"error": summary_response["result"]}
        summary = summary_response["result"]
        print(f"Financial Plan Summary:\n{summary}")

        return {
            "profile": profile,
            "market_data": market_data,
            "recommendations": recommendations,
            "summary": summary
        }

if __name__ == "__main__":
    user_input = {
        "income": 5000,
        "expenses": {"monthly": 3000},
        "goals": {"savings": 10000},
        "risk_tolerance": "moderate"
    }
    asyncio.run(orchestrate_financial_plan(user_input))
