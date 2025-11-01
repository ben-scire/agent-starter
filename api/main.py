from fastapi import FastAPI

from agent_starter.core.agent import SingleAgent

app = FastAPI(title="agent-starter")

agent = SingleAgent(
    system_prompt=(
        "You are a helpful single agent with access to a limited toolset.\n"
        "Answer concisely and prefer structured outputs."
    ),
    allowed_tools=["web.fetch"],
)


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/chat")
async def chat(payload: dict):
    query = payload.get("query", "")
    ans = agent.run(query)
    return ans.model_dump()
