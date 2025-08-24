from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from ai_agent import get_response_from_ai_agent

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

# Define API request schema matching your frontend
class RequestState(BaseModel):
    model_name: str
    model_provider: Literal["Groq", "OpenAI"]
    system_prompt: str
    messages: List[ChatMessage]  # List of dicts representing chat messages from frontend
    allow_search: bool

ALLOWED_MODEL_NAMES = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "mixtral-8x7b-32768",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "gpt-4o-mini",
]

app = FastAPI(title="LangGraph AI Agent API")

@app.post("/chat")
async def chat_endpoint(request: RequestState):
    if request.model_name not in ALLOWED_MODEL_NAMES:
        raise HTTPException(status_code=400, detail="Invalid model name. Kindly select a valid AI model.")

    # Convert frontend message dicts to proper LangChain message objects
    conversation_messages = []
    for msg in request.messages:
        role = msg.role.lower()
        content = msg.content
        if role == "user":
            conversation_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            conversation_messages.append(AIMessage(content=content))
        elif role == "system":
            conversation_messages.append(SystemMessage(content=content))
        else:
            # Ignore unknown roles or raise an error if preferred
            pass

    # Ensure system prompt is included if provided and missing
    if request.system_prompt and not any(isinstance(m, SystemMessage) for m in conversation_messages):
        conversation_messages.insert(0, SystemMessage(content=request.system_prompt))

    # Call your LangGraph AI agent with full conversation state
    ai_response = get_response_from_ai_agent(
        llm_id=request.model_name,
        query_messages=conversation_messages,
        allow_search=request.allow_search,
        system_prompt=request.system_prompt,
        provider=request.model_provider
    )

    return {"response": ai_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9999)
