import streamlit as st
from dotenv import load_dotenv
from services.llm import LLMClient
from services.router import AgentRouter
from agents.weather_agent import WeatherAgent
from agents.document_agent import DocumentAgent
from services.document_store import extract_text

load_dotenv()
st.set_page_config(page_title="Weather & Document AI", page_icon="🌦️", layout="wide")
st.title("🌦️ Agentic AI Chatbot")
st.caption("Two specialized agents: Weather Intelligence and Document Understanding")

@st.cache_resource
def build_system():
    llm = LLMClient()
    return llm, AgentRouter(llm), WeatherAgent(), DocumentAgent(llm)

try:
    llm, router, weather_agent, document_agent = build_system()
except Exception as exc:
    st.error(f"Configuration error: {exc}")
    st.info("Create a .env file using .env.example and add your GROQ_API_KEY.")
    st.stop()

with st.sidebar:
    st.header("📄 Upload a document")
    uploaded = st.file_uploader("Upload resume or document", type=["pdf", "txt"])
    if uploaded:
        try:
            text = extract_text(uploaded.name, uploaded.getvalue())
            st.session_state["document_text"] = text
            st.session_state["document_name"] = uploaded.name
            st.success(f"Loaded: {uploaded.name}")
            st.caption(f"{len(text):,} characters extracted")
        except Exception as exc:
            st.error(f"Could not read document: {exc}")
    if st.button("Clear uploaded document"):
        st.session_state.pop("document_text", None)
        st.session_state.pop("document_name", None)
        st.rerun()
    st.divider()
    st.markdown("**Try these questions**")
    st.markdown("- What is the weather in Chennai today?\n- Show the last 10 days weather in Bengaluru\n- Forecast for London tomorrow\n- What are the skills in my resume?\n- Summarize my project experience")

if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("table") is not None:
            st.dataframe(message["table"], use_container_width=True)
        if message.get("chart") is not None:
            st.plotly_chart(message["chart"], use_container_width=True)

question = st.chat_input("Ask about weather or your uploaded document...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Understanding your request and selecting the right agent..."):
            try:
                route = router.route(question, bool(st.session_state.get("document_text")))
                if route["agent"] == "weather":
                    result = weather_agent.handle(route)
                else:
                    doc = st.session_state.get("document_text", "")
                    result = document_agent.handle(question, doc)
                st.markdown(result["answer"])
                if result.get("table") is not None:
                    st.dataframe(result["table"], use_container_width=True)
                if result.get("chart") is not None:
                    st.plotly_chart(result["chart"], use_container_width=True)
                st.caption(f"Handled by: {route['agent'].title()} Agent")
                st.session_state.messages.append({
                    "role": "assistant", "content": result["answer"],
                    "table": result.get("table"), "chart": result.get("chart")
                })
            except Exception as exc:
                msg = f"Unable to complete the request: {exc}"
                st.error(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})
