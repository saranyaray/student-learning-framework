#!/usr/bin/env python3
"""
Main entry point for the Student Learning Framework
Combines document ingestion and QA pipeline in one script
"""

import argparse
import sys
from pathlib import Path

# Add src to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# Import after path setup
from config.settings import UPLOAD_DIR, VECTORSTORE_DIR
from src.ingestion.document_loader import DocumentLoader
from src.ingestion.vector_store import VectorStoreManager
from src.orchestration.crew_manager import StudentLearningCrew
from src.retrieval.context_retriever import ContextRetriever


def ingest_documents():
    """Ingest each document as its own vector store."""
    print("🔄 Starting per-document ingestion...")
    try:
        upload_dir = UPLOAD_DIR
        all_files = []
        for ext in ["*.pdf", "*.txt", "*.docx"]:
            all_files.extend(upload_dir.glob(ext))
        if not all_files:
            print("❌ No document files found in data/raw/")
            print("   Please upload documents via the API first")
            return False
        loader = DocumentLoader()
        vector_manager = VectorStoreManager()
        VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
        for file in all_files:
            print(f"📄 Processing: {file.name}")
            docs = loader.load(str(file))
            if not docs:
                print(f"❌ Skipping empty document: {file.name}")
                continue
            store_name = f"{file.stem}_faiss_index"
            store_path = VECTORSTORE_DIR / store_name
            vector_manager.from_documents(docs, str(store_path))
            print(f"✅ Vector store created: {store_path}")
        print("✅ Ingestion done. Each document has its own vector store!")
        return True
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_qa_pipeline():
    """Run the interactive QA pipeline with per-document selection."""
    print("🚀 Initializing Student Learning Framework...")
    try:
        store_paths = list(VECTORSTORE_DIR.glob("*_faiss_index"))
        if not store_paths:
            print("❌ No vector stores found. Please run ingestion first.")
            print("   Use: python main.py --ingest")
            return False

        print("\nAvailable documents:")
        for i, vpath in enumerate(store_paths, 1):
            print(f"  {i}) {vpath.name.replace('_faiss_index','')}")

        selected = input("\nPick document number (default 1): ").strip()
        if not selected:
            selected = "1"
        try:
            idx = int(selected) - 1
            store_path = store_paths[idx]
        except Exception:
            print("Invalid selection.")
            return False

        retriever = ContextRetriever(str(store_path))
        print(f"\n🔍 Using document: {store_path.name.replace('_faiss_index','')}")
        crew = StudentLearningCrew(retriever)

        print("\n" + "=" * 80)
        print("🎓 STUDENT LEARNING FRAMEWORK READY!")
        print("=" * 80)
        print("💡 Ask questions about your selected document")
        print("💡 Type 'quit', 'exit', or 'q' to stop")
        print("=" * 80)

        # Interactive loop
        while True:
            try:
                question = input("\n📝 Your question: ").strip()
                if question.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break
                if not question:
                    continue
                print("\n🤔 Processing your question...")
                result = crew.process_question(question)
                print("\n" + "=" * 60)
                print("👥 EXPERT RESPONSES")
                print("=" * 60)
                for role, response in result["expert_outputs"].items():
                    print(f"\n🔸 {role}:")
                    print("-" * 40)
                    print(response)
                print("\n" + "=" * 60)
                print("✨ FINAL ANSWER")
                print("=" * 60)
                print(result["final_answer"])
                print("=" * 60)
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error processing question: {e}")
                import traceback

                traceback.print_exc()
                continue
        return True
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Student Learning Framework - Multi-Agent RAG System"
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Run document ingestion to create vector store",
    )
    parser.add_argument("--qa", action="store_true", help="Run interactive QA pipeline")
    parser.add_argument(
        "--all", action="store_true", help="Run both ingestion and QA pipeline"
    )
    args = parser.parse_args()
    # If no arguments provided, show help
    if not any([args.ingest, args.qa, args.all]):
        print("🎓 Student Learning Framework")
        print("=" * 40)
        print("Available commands:")
        print("  python main.py --ingest    # Ingest documents")
        print("  python main.py --qa        # Run QA pipeline")
        print("  python main.py --all       # Do both")
        print("\nFirst time? Run: python main.py --all")
        return

    success = True
    if args.ingest or args.all:
        success = ingest_documents()
        if not success and args.all:
            print("❌ Ingestion failed, skipping QA pipeline")
            return
    if (args.qa or args.all) and success:
        run_qa_pipeline()


if __name__ == "__main__":
    main()
