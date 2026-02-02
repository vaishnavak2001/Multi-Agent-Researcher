import streamlit as st
from langchain_core.messages import HumanMessage
from agent_graph import graph

st.title("Researcher-Writer Agent Graph Demo")
st.markdown("Researcher+Writer+Editor(langgraph)")

query = st.text_input("Enter a research topic:")
if st.button("start research"):
    if query:
        st.write(f"Starting agents for  **{query}**...")
        log_container = st.empty()
        initial_state={"messages": [HumanMessage(content=query)]}
        
        try:
            for step in graph.stream(initial_state):
                for node_name, update in step.items():
                    if node_name == "researcher":
                        with st.expander("View Research Findings",expanded= False):
                            st.write(f"**Node:{node_name}**")
                            st.write(update["messages"][-1].content)
                    elif node_name == "writer":
                        st.subheader("Final Blog Post")
                        st.markdown(update["messages"][-1].content)
                    else:
                        st.write(f"**processing:{node_name}..**")


        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("please enter a query.")