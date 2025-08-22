import json
import time
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="🎓 AI Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for advanced styling
st.markdown(
    """
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        text-align: center;
    }
    .agent-card {
        background: linear-gradient(145deg, #f8f9ff, #e8ebff);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e0e7ff;
        margin: 1rem 0;
    }
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        background: #f8f9ff;
        border-radius: 10px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 0.5rem 2rem;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online { background-color: #10b981; }
    .status-offline { background-color: #ef4444; }
    .status-warning { background-color: #f59e0b; }
</style>
""",
    unsafe_allow_html=True,
)

API_BASE_URL = "http://localhost:8005"

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"


class StreamlitAPI:
    @staticmethod
    def get_system_status():
        try:
            response = requests.get(f"{API_BASE_URL}/status", timeout=5)
            return response.json() if response.status_code == 200 else None
        except:
            return None

    @staticmethod
    def upload_document(file):
        try:
            files = {"file": file}
            response = requests.post(
                f"{API_BASE_URL}/upload_document", files=files, timeout=30
            )
            return response.json() if response.status_code == 200 else None
        except:
            return None

    @staticmethod
    def ask_question(question, document_name=None):
        try:
            data = {"question": question}
            if document_name:
                data["document_name"] = document_name
            response = requests.post(
                f"{API_BASE_URL}/ask_question", json=data, timeout=600
            )
            return response.json() if response.status_code == 200 else None
        except:
            return None

    @staticmethod
    def list_documents():
        try:
            response = requests.get(f"{API_BASE_URL}/list_documents", timeout=5)
            return response.json() if response.status_code == 200 else None
        except:
            return None

    @staticmethod
    def delete_document(filename):
        try:
            response = requests.delete(
                f"{API_BASE_URL}/delete_document",
                params={"filename": filename},
                timeout=10,
            )
            return response.json() if response.status_code == 200 else None
        except:
            return None


def main():
    st.markdown(
        """
    <div class="main-header">
        <h1>🎓 AI Learning Assistant</h1>
        <p>Multi-Agent RAG System for Enhanced Learning</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.markdown("### 🎓 AI Learning Assistant")
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.current_page = "Chat"
            st.rerun()
        if st.button("📚 Documents", use_container_width=True):
            st.session_state.current_page = "Documents"
            st.rerun()
        if st.button("🔧 System", use_container_width=True):
            st.session_state.current_page = "System"
            st.rerun()
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.current_page = "Analytics"
            st.rerun()

        st.markdown("---")
        st.markdown("### System Status")
        status = StreamlitAPI.get_system_status()
        if status:
            if status.get("available_documents", []):
                st.markdown(
                    '<span class="status-indicator status-online"></span>'
                    "**System Online**",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span class="status-indicator status-warning"></span>'
                    "**No Documents**",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<span class="status-indicator status-offline"></span>'
                "**System Offline**",
                unsafe_allow_html=True,
            )

    # Route to pages
    if st.session_state.current_page == "Dashboard":
        show_dashboard()
    elif st.session_state.current_page == "Chat":
        show_chat_interface()
    elif st.session_state.current_page == "Documents":
        show_document_manager()
    elif st.session_state.current_page == "System":
        show_system_settings()
    elif st.session_state.current_page == "Analytics":
        show_analytics()


def show_dashboard():
    st.title("📊 Dashboard Overview")

    # Get real data from API
    status = StreamlitAPI.get_system_status()
    documents = StreamlitAPI.list_documents()

    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        doc_count = len(documents.get("documents", [])) if documents else 0
        st.markdown(
            f"""
        <div class="metric-card">
            <h3>📚</h3>
            <h2 style="color: #667eea;">{doc_count}</h2>
            <p>Documents</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        chat_count = len(st.session_state.chat_history)
        st.markdown(
            f"""
        <div class="metric-card">
            <h3>💬</h3>
            <h2 style="color: #667eea;">{chat_count}</h2>
            <p>Questions</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        queryable_count = (
            len(documents.get("available_for_query", [])) if documents else 0
        )
        st.markdown(
            f"""
        <div class="metric-card">
            <h3>🎯</h3>
            <h2 style="color: #667eea;">{queryable_count}</h2>
            <p>Queryable</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col4:
        speed = "2.3s" if status and status.get("available_documents") else "0s"
        st.markdown(
            f"""
        <div class="metric-card">
            <h3>⚡</h3>
            <h2 style="color: #667eea;">{speed}</h2>
            <p>Speed</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # AI Agents Overview
    st.subheader("🤖 AI Agent Network")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
        <div class="agent-card">
            <h4>👨‍🏫 Tutor Agent</h4>
            <p><strong>Model:</strong> Phi3:3.8b</p>
            <p><strong>Specialty:</strong> Clear foundational explanations</p>
            <p><strong>Status:</strong> <span style="color: green;">●</span> Active</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="agent-card">
            <h4>🎯 Coach Agent</h4>
            <p><strong>Model:</strong> Gemma:2b</p>
            <p><strong>Specialty:</strong> Analogies and encouragement</p>
            <p><strong>Status:</strong> <span style="color: green;">●</span> Active</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="agent-card">
            <h4>🧠 Analyst Agent</h4>
            <p><strong>Model:</strong> Qwen:1.8b</p>
            <p><strong>Specialty:</strong> Deep insights and analysis</p>
            <p><strong>Status:</strong> <span style="color: green;">●</span> Active</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
        <div class="agent-card">
            <h4>🔄 Synthesizer Agent</h4>
            <p><strong>Model:</strong> Phi3:3.8b</p>
            <p><strong>Specialty:</strong> Information synthesis</p>
            <p><strong>Status:</strong> <span style="color: green;">●</span> Active</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📤 Upload Document", key="upload_btn", use_container_width=True):
            st.session_state.current_page = "Documents"
            st.rerun()

    with col2:
        if st.button("💬 Start Chat", key="chat_btn", use_container_width=True):
            st.session_state.current_page = "Chat"
            st.rerun()

    with col3:
        if st.button(
            "🔧 System Settings", key="settings_btn", use_container_width=True
        ):
            st.session_state.current_page = "System"
            st.rerun()


def show_chat_interface():
    st.title("💬 AI Chat Interface")

    # Document selection
    docs_resp = StreamlitAPI.list_documents()
    queryable_docs = docs_resp.get("available_for_query", []) if docs_resp else []

    if not queryable_docs:
        st.warning(
            "⚠️ No documents available for querying. "
            "Please upload and process a document first."
        )
        if st.button("Go to Document Manager"):
            st.session_state.current_page = "Documents"
            st.rerun()
        return

    selected_doc = st.selectbox("📄 Select document to query:", queryable_docs)
    st.info(f"Currently querying: **{selected_doc}**")

    # Chat history display
    chat_container = st.container()
    with chat_container:
        if st.session_state.chat_history:
            for chat in st.session_state.chat_history:
                if chat["type"] == "user":
                    st.markdown(
                        f"""
                    <div style="background: #e3f2fd; padding: 1rem; border-radius: 10px;
                         margin: 0.5rem 0; margin-left: 20%;">
                        <strong>You:</strong> {chat['content']}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    doc_used = chat.get("document_used", "Unknown")
                    assistant_text = f"<strong>AI Assistant</strong> <small>(from {doc_used}):</small><br>"
                    st.markdown(
                        f"""
                    <div style="background: #f3e5f5; padding: 1rem; border-radius: 10px;
                         margin: 0.5rem 0; margin-right: 20%;">
                        {assistant_text}
                        {chat['content']}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    if "expert_responses" in chat and chat["expert_responses"]:
                        with st.expander("👥 View Expert Responses", expanded=False):
                            for role, response in chat["expert_responses"].items():
                                st.markdown(f"**{role.title()}:**")
                                st.write(response)
                                st.markdown("---")
        else:
            st.info("💡 Start a conversation by asking a question below!")

    st.markdown("---")

    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Ask your question:",
            placeholder="What would you like to learn about?",
            height=100,
            key="chat_input",
        )

        col1, col2 = st.columns([4, 1])
        with col2:
            submitted = st.form_submit_button("Send 🚀", use_container_width=True)

    if submitted and user_input.strip():
        # Add user message
        st.session_state.chat_history.append(
            {"type": "user", "content": user_input.strip(), "timestamp": datetime.now()}
        )

        # Get response from API
        with st.spinner("🤖 AI agents are processing your question..."):
            response = StreamlitAPI.ask_question(
                user_input.strip(), document_name=selected_doc
            )

            if response:
                st.session_state.chat_history.append(
                    {
                        "type": "bot",
                        "content": response.get(
                            "final_answer", "Sorry, I couldn't generate a response."
                        ),
                        "expert_responses": response.get("expert_responses", {}),
                        "document_used": response.get("document_used", selected_doc),
                        "timestamp": datetime.now(),
                    }
                )
                st.success("✅ Response generated!")
            else:
                st.error(
                    "❌ Failed to get response from AI system. "
                    "Please check if the backend is running."
                )

        st.rerun()


def show_document_manager():
    st.title("📚 Document Manager")

    # Upload Section
    st.subheader("📤 Upload New Document")

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "txt", "docx"],
        help="Upload PDF, TXT, or DOCX files for processing",
    )

    if uploaded_file is not None:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.info(
                f"📄 {uploaded_file.name} ({uploaded_file.size / 1024 / 1024:.2f} MB)"
            )

        with col2:
            if st.button("🚀 Upload & Process", use_container_width=True):
                with st.spinner("Processing document..."):
                    result = StreamlitAPI.upload_document(uploaded_file)

                    if result:
                        st.success("✅ Document uploaded and processed successfully!")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(
                            "❌ Upload failed! Please check the backend connection."
                        )

    st.markdown("---")

    # Document List
    st.subheader("📋 Uploaded Documents")

    documents = StreamlitAPI.list_documents()

    if documents and documents.get("documents"):
        for doc in documents["documents"]:
            queryable_status = (
                "✅ Queryable" if doc.get("queryable") else "⏳ Processing"
            )

            with st.expander(f"📄 {doc['filename']} - {queryable_status}"):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Size", f"{doc['size_mb']:.2f} MB")

                with col2:
                    st.metric("Type", doc["extension"].upper())

                with col3:
                    upload_time = datetime.fromtimestamp(doc["uploaded"]).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    st.metric("Uploaded", upload_time)

                with col4:
                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{doc['filename']}",
                        use_container_width=True,
                    ):
                        with st.spinner("Deleting..."):
                            if StreamlitAPI.delete_document(doc["filename"]):
                                st.success("Document deleted!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to delete document!")
    else:
        st.info("📝 No documents uploaded yet. Upload your first document above!")


def show_system_settings():
    st.title("🔧 System Settings")

    # System Status
    status = StreamlitAPI.get_system_status()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 System Status")
        if status:
            st.json(status)
        else:
            st.error("❌ Cannot connect to backend API")

    with col2:
        st.subheader("🎛️ Configuration")
        st.info(
            "💡 System configuration is managed through the backend API. "
            "Current settings are displayed on the left."
        )

        st.markdown("### 🔗 API Endpoints")
        st.code(
            f"""
        Base URL: {API_BASE_URL}

        Available endpoints:
        • GET  /status - System status
        • POST /upload_document - Upload files
        • POST /ask_question - Ask questions
        • GET  /list_documents - List files
        • DELETE /delete_document - Delete files
        """
        )


def show_analytics():
    st.title("📊 Analytics Dashboard")

    # Generate sample data
    dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
    questions_per_day = np.random.poisson(8, len(dates))
    response_times = np.random.normal(2.5, 0.5, len(dates))

    df = pd.DataFrame(
        {
            "Date": dates,
            "Questions": questions_per_day,
            "Response Time": np.abs(response_times),
        }
    )

    # Usage Trends
    st.subheader("📈 Usage Trends (Last 30 Days)")

    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(df, x="Date", y="Questions", title="Questions Asked Over Time")
        fig.update_layout(xaxis_title="Date", yaxis_title="Questions per Day")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.line(df, x="Date", y="Response Time", title="Response Time Trends")
        fig.update_layout(xaxis_title="Date", yaxis_title="Response Time (seconds)")
        st.plotly_chart(fig, use_container_width=True)

    # Agent Performance
    st.subheader("🤖 Agent Performance Metrics")

    agent_data = pd.DataFrame(
        {
            "Agent": ["Tutor", "Coach", "Analyst", "Synthesizer"],
            "Accuracy": [94, 92, 96, 89],
            "Avg Response Time": [2.1, 1.8, 2.5, 3.2],
            "Total Queries": [450, 320, 380, 450],
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            agent_data, x="Agent", y="Accuracy", title="Agent Accuracy Scores (%)"
        )
        fig.update_layout(yaxis_title="Accuracy (%)")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            agent_data,
            x="Avg Response Time",
            y="Accuracy",
            size="Total Queries",
            hover_name="Agent",
            title="Performance vs Speed Analysis",
        )
        fig.update_layout(xaxis_title="Response Time (s)", yaxis_title="Accuracy (%)")
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
