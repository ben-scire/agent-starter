# Agent Starter 🧠

Local-first AI agent framework powered by:
- **FastAPI** for serving and orchestration  
- **Ollama + Llama3** for local inference  
- **WebTools** for fetching and summarizing live URLs  

## Run locally
```bash
pip install -e .
uvicorn api.main:app --reload --env-file .env
