# 🎓 Student Learning Framework

A sophisticated multi-agent RAG (Retrieval Augmented Generation) system designed to enhance the learning experience through intelligent document processing and interactive Q&A capabilities.

**Author:**
- Saranya Ray

## 🌟 Features

- **📚 Document Management**
  - Upload and process various document formats
  - Automatic vector store creation for efficient retrieval
  - Document deletion and management capabilities

- **🤖 Multi-Agent System**
  - Analyst Agent for content understanding
  - Tutor Agent for educational guidance
  - Coach Agent for learning strategy
  - Synthesizer Agent for comprehensive answers

- **💬 Interactive Learning**
  - Natural language Q&A interface
  - Context-aware responses
  - Multi-document knowledge integration

- **📊 Analytics Dashboard**
  - Usage tracking
  - Response time monitoring
  - Learning progress visualization

## 🛠️ Technology Stack

- **Backend**
  - Python 3.10+
  - FastAPI for REST API
  - FAISS for vector storage
  - LangChain for RAG pipeline
  - Ollama for LLM serving

- **AI Models** (via Ollama)
  - Phi-3 for general reasoning and analysis
  - Gemma for educational guidance
  - Qwen2 for comprehensive responses

- **Frontend**
  - Streamlit for web interface
  - CoreUI React Admin Template (optional)
  - Plotly for visualizations

## 📋 Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)
- Git
- Ollama installed and running (`ollama serve`)

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone [your-repo-url]
   cd student-learning-framework
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Ollama**
   ```bash
   # Start Ollama server
   ollama serve

   # Pull required models
   ollama pull phi
   ollama pull gemma
   ollama pull qwen
   ```

5. **Initialize the system**
   ```bash
   python main.py --all  # Run both document ingestion and QA pipeline
   ```

## 📂 Project Structure

```
student-learning-framework/
├── config/              # Configuration settings
├── data/               # Document storage
│   ├── processed/      # Processed documents
│   └── raw/           # Raw document uploads
├── src/               # Source code
│   ├── agents/        # AI agents implementation
│   ├── ingestion/     # Document processing
│   ├── orchestration/ # Agent coordination
│   ├── retrieval/     # Context retrieval
│   ├── tasks/         # Learning tasks
│   └── utils/         # Utility functions
├── streamlit_app/     # Streamlit web interface
├── web_app/           # FastAPI backend
├── vectorstore/       # FAISS vector stores
└── tests/            # Unit tests
```

## 🎯 Usage

### Command Line Interface
```bash
python main.py --ingest  # Process documents
python main.py --qa      # Run Q&A pipeline
python main.py --all     # Do both
```

### Web Interface
```bash
cd streamlit_app
streamlit run main.py
```

### API Server
```bash
cd web_app
python -m uvicorn web_app.routes:app --reload --host 0.0.0.0 --port 8005
```

## 🔧 Configuration

Key configuration files:
- `config/settings.py`: System settings
- `.env`: Environment variables (create from template)
- `requirements.txt`: Python dependencies

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

[Your License] - See LICENSE file for details

##  Authors

### Lead Developer
**Reuel Sajeev Koshy**
- 🌟 System Architecture & Core Development
- 🤖 AI/ML Implementation
- 📊 System Integration

### Co-Developer
**Saranya Ray**
- 🎯 Feature Development
- 🔍 Testing & Quality Assurance
- 📚 Documentation

## Acknowledgments

- CoreUI for the admin template
- OpenAI for language models
- FastAPI for the web framework
- Streamlit for the UI framework

---
Made by Reuel Sajeev Koshy & Saranya Ray
