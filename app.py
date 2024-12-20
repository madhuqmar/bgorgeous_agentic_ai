import streamlit as st
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_openai.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
import mysql.connector

# Load environment variables from .env file
load_dotenv(".env")

# Define the database query function
def execute_query(query):
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
    )
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def query_database_tool(input_query):
    try:
        return execute_query(input_query)
    except Exception as e:
        return f"Error: {e}"

# Define your LLM
llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

# Define tools
tools = [
    Tool(name="Query Database", func=query_database_tool, description="Executes SQL queries on the database.")
]

# Initialize the agent
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

# Streamlit app
st.title("BGorgeous Agentic AI Demo")
st.write("Book or reschedule appointments by chatting with the agent.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("How can I assist you?"):
    # Display user message in chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = agent.run(prompt)
                st.markdown(response)
            except Exception as e:
                response = f"An error occurred: {e}"
                st.error(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
