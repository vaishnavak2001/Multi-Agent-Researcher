import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import operator
from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langchain_community.tools import DuckDuckGoSearchRun

# Load environment variables from .env file
load_dotenv()

llm= ChatGroq(model_name="llama-3.1-8b-instant")
search_tool = DuckDuckGoSearchRun()
#define the state
class AgentGraphState(TypedDict):
    """
    The state of our graph.
    It will pass through every node(Agent).
    """
    messages:Annotated[list,add_messages]
#define nodes
def researcher_node(state: AgentGraphState):
    """
    1.Extract the user's query.
    2.Searches the web using DuckDuckGoSearchRun tool.
    3.Summarizes the results using the llm

    """
    last_message=state["messages"][-1]
    query=last_message.content
    print(f"Researcher Node: Searching for query: {query}")
    try:
        search_results = search_tool.invoke(query)
    except Exception as e:
        search_results = f"Search failed with error: {str(e)}"
    prompt=f"""
    You are a research agent.
    here is the information found on the web regarding '{query}':
    {search_results}
    please list the 3 most important facts from this data.
    """
    response = llm.invoke(prompt)
    return{"messages":[response]}
def writer_node(state: AgentGraphState):
    """
    1.Read the Researcher's findings from the state.
    2.Writes a polished blog post.
    """
    messages = state["messages"]
    system_message = SystemMessage(
        content="You are a skilled blog post writer."
        "Based on the research provided above, write a short,engaging blog post."
        "Do not do more research.Just synthesize the facts."
    )
    writer_messages = messages + [system_message]
    print("Writer Node: Writing blog post based on research.")
    response = llm.invoke(writer_messages)
    return {"messages": [response]}
def check_content_quality(state: AgentGraphState):
    """
    Check if the last message (the blog post) is long enough.
    """
    last_message = state["messages"][-1]
    content = last_message.content
    print("Quality Check Node: Checking content quality.")
    if len(content) < 200:
        print("Content is too short, needs improvement.")
        return "poor_quality"
    print("Content quality is acceptable.")
    return "good_quality"

#assemlble the graph
builder=StateGraph(AgentGraphState)
builder.add_node("researcher",researcher_node)
builder.add_node("writer",writer_node)

builder.add_edge(START,"researcher")
builder.add_edge("researcher","writer")

builder.add_conditional_edges(
    "writer",
    check_content_quality,
    {
        "good_quality": END,
        "poor_quality": "writer"
    }
)


graph=builder.compile()


if __name__ == "__main__":
    print(" testing full graph")
    initial_state = {"messages": [HumanMessage(content="current price of bitcoin" )]}
    #run the graph
    result = graph.invoke(initial_state)
    print("\nFull Graph Result:")
    print(result['messages'][-1].content)
    print(result)

    print(f'\nContent: {result["messages"][0].content}')
    # Quick test to see the structure annotation
    print(f"State keys: {AgentGraphState.__annotations__.keys()}")

