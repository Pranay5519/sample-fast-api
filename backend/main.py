from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Annotated

# ------------------- Load environment -------------------
load_dotenv()

# ------------------- Initialize Model -------------------
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# ------------------- Chat State -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# ------------------- Node -------------------
def chat_node(state: ChatState):
    user_message = state["messages"]

    # Pass a list of messages (conversation) to Gemini
    response = model.invoke(user_message)

    return {
        "messages": [
            state["messages"][-1],  # keep user message
            AIMessage(content=response.content)  # clean text response
        ]
    }


# ------------------- In-Memory Checkpointer -------------------
checkpointer = InMemorySaver()

# ------------------- Build Graph -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# ------------------- FastAPI App -------------------
app = FastAPI(title="LangGraph Gemini Chatbot API")

class ChatRequest(BaseModel):
    user_input: str
    thread_id: str = "default"  # allows session/thread continuation

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_msg = HumanMessage(content=request.user_input)

    result = chatbot.invoke(
        {"messages": [user_msg]},
        config={"configurable": {"thread_id": request.thread_id}}
    )

    ai_message = next(msg for msg in result["messages"] if isinstance(msg, AIMessage))

    return ChatResponse(response=ai_message.content)

