import os
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch  # updated import for Tavily search

from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


# System prompt defines AI persona
system_prompt = "Act as an AI chatbot who is smart and friendly"


# Initialize tool with max results limit
search_tool = TavilySearch(max_results=2)


def build_agent(llm, allow_search=True, system_prompt=system_prompt):
    graph = StateGraph(MessagesState)

    def call_model(state):
        messages = state["messages"]

        # Prepend system prompt only once at the start
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=system_prompt)] + messages

        response = llm.invoke(messages)
        return {"messages": messages + [response]}

    graph.add_node("model", call_model)

    if allow_search:
        tool_node = ToolNode([search_tool])
        graph.add_node("tools", tool_node)

        # If the AI wants to call the tool, route accordingly
        graph.add_conditional_edges("model", tools_condition)
        graph.add_edge("tools", "model")
        graph.add_edge("model", END)
    else:
        graph.add_edge("model", END)

    graph.set_entry_point("model")

    return graph.compile()


def get_response_from_ai_agent(llm_id, query_messages, allow_search, system_prompt, provider):
    if provider == "Groq":
        llm = ChatGroq(model=llm_id)
    elif provider == "OpenAI":
        llm = ChatOpenAI(model=llm_id)
    else:
        raise ValueError(f"Unknown provider '{provider}'")
    
    if allow_search:
        llm = llm.bind_tools([search_tool])

    agent = build_agent(llm, allow_search=allow_search, system_prompt=system_prompt)

    # 'query_messages' is a list of HumanMessage, AIMessage etc. representing conversation history
    state = {"messages": query_messages}
    result = agent.invoke(state)

    ai_messages = [m.content for m in result.get("messages", []) if isinstance(m, AIMessage)]
    return ai_messages[-1] if ai_messages else None


# from langchain_core.messages import HumanMessage, AIMessage

# def run_chat():
#     conversation = []  # Holds all past messages

#     while True:
#         user_input = input("You: ").strip()
#         if user_input.lower() in ["exit", "quit"]:
#             print("Goodbye!")
#             break

#         # Append user message
#         conversation.append(HumanMessage(content=user_input))

#         # Call AI agent with full conversation history
#         response = get_response_from_ai_agent(
#             llm_id="meta-llama/llama-4-scout-17b-16e-instruct",
#             query_messages=conversation,
#             allow_search=True,
#             system_prompt="Act as an AI chatbot who is smart and friendly",
#             provider="Groq"
#         )

#         print("AI:", response)

#         # Append AI response to conversation history
#         conversation.append(AIMessage(content=response))

# if __name__ == "__main__":
#     run_chat()
