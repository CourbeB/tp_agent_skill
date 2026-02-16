import os
import sys

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Created directory: {path}")
    else:
        print(f"ℹ️ Directory already exists: {path}")

def create_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
    print(f"✅ Created file: {path}")

def main():
    print("🚀 Initializing RAG Project Structure...")

    # Directories
    dirs = [
        "data/raw",
        "data/processed",
        "src/ingestion",
        "src/retrieval",
        "src/generation",
        "notebooks"
    ]

    for d in dirs:
        create_directory(d)

    # requirements.txt
    requirements = """langchain
chromadb
openai
tiktoken
python-dotenv
"""
    create_file("requirements.txt", requirements)

    # main.py
    main_py = """import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("RAG System Initialized")
    # Add your RAG logic here

if __name__ == "__main__":
    main()
"""
    create_file("src/main.py", main_py)

    print("\n✨ RAG Project initialized successfully!")
    print("👉 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Add your documents to data/raw")

if __name__ == "__main__":
    main()
