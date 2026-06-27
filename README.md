<div align="center">
  <h1>🔭 CodeLens – AI Codebase Assistant</h1>
  <p><strong>A Hybrid RAG System for Natural Language Q&A over Python Repositories</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](#)
  [![Streamlit](https://img.shields.io/badge/Streamlit-%23FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](#)
  [![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange?style=for-the-badge)](#)
  [![Groq](https://img.shields.io/badge/Groq-LLM-purple?style=for-the-badge)](#)
  [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](#)
</div>

<img width="1918" height="911" alt="Screenshot 2026-06-27 190756" src="https://github.com/user-attachments/assets/a5b183ad-f94a-4615-8ed2-ebcb1524f1d1" />

## 📖 Project Overview

CodeLens is an AI-powered codebase assistant that lets you have a natural language conversation with any Python GitHub repository. Point it at a repo, and ask questions like *"How does the retriever work?"*, *"What are the main entry points?"*, or *"Walk me through the data flow"* — and get precise, code-grounded answers.

Under the hood, CodeLens combines **semantic vector search** with **dependency graph traversal** to retrieve the most relevant code context before generating answers using a large language model. It parses Python source files using the AST, builds a function/class call graph, embeds code chunks with a sentence transformer, and stores them in a persistent vector database — all automatically, from a single GitHub URL.

The project ships both a terminal interface (`app.py`) and a **Streamlit web app** (`streamlit_app.py`) for interactive use.

---

## 🌐 Live Demo

https://repocodebaseai.streamlit.app/

---

## ✨ Key Features

- **GitHub-first workflow**: Paste any public repo URL — CodeLens clones, parses, and indexes it automatically.
- **AST-based code parsing**: Extracts functions, classes, methods, docstrings, arguments, and call relationships using Python's `ast` module.
- **Dependency graph construction**: Builds a directed graph of `CONTAINS`, `CALLS`, and `IMPORTS` relationships using NetworkX, enabling graph-aware context retrieval.
- **Hybrid retrieval**: Combines dense semantic search (via `chromadb` + `sentence-transformers`) with graph neighbour expansion (callers & callees) for richer context.
- **Query rewriting**: The LLM rewrites the user's question into code-centric terminology before embedding, improving retrieval precision.
- **Conversation memory**: Maintains a rolling chat history so follow-up questions resolve references correctly (*"How does it handle errors?"* → knows what *"it"* is).
- **Persistent vector store**: ChromaDB caches embeddings per repo — re-opening a repo skips re-embedding.
- **Streamlit UI**: Clean, theme-respecting web interface with a pipeline progress bar, repository stats, suggested questions, and a retrieved-context inspector.

---

## 🧠 System Architecture

CodeLens is structured as a sequential pipeline of composable modules:

```
GitHub URL
    │
    ▼
GitHubLoader          Clone repo, collect .py files
    │
    ▼
CodeParser            AST parse → functions, classes, methods, imports, calls
    │
    ▼
RepoIndexer           Build repo_index dict + text chunks per node
    │
    ▼
GraphBuilder          NetworkX DiGraph: CONTAINS / CALLS / IMPORTS edges
    │
    ▼
Embedder              SentenceTransformer (BAAI/bge-small-en-v1.5)
    │
    ▼
VectorStore           ChromaDB persistent collection (per repo)
    │
    ▼
HybridRetriever       Query rewrite → semantic search → graph neighbour expansion
    │
    ▼
AnswerGenerator       Context assembly → prompt → LLM → answer + chat history
```

### Retrieval Strategy

1. **Query rewrite**: The LLM expands the user question into code-domain terms (class names, function names, filenames, patterns).
2. **Semantic search**: The rewritten query is embedded and searched against the vector store to retrieve the top-k most similar code chunks.
3. **Graph expansion**: For each semantically retrieved node, its callers (`who_calls`) and callees (`what_does_it_call`) are fetched from the dependency graph and added as supporting context.
4. **Context assembly**: Semantic nodes (high relevance) and graph nodes (supporting dependencies) are assembled into a structured prompt.

---

## 📂 Repository Structure

```text
.
├── app.py                  # Terminal entry point (interactive Q&A loop)
├── streamlit_app.py        # Streamlit web interface
├── config.py               # REPO_DIR and GROQ_API_KEY configuration
├── requirements.txt        # Python dependencies
├── vector_store/           # ChromaDB persistent storage (auto-created)
├── repos/                  # Cloned repositories (auto-created)
└── src/
    ├── github_loader.py    # Clone repo, enumerate .py files
    ├── parser.py           # AST-based code parser (CodeVisitor, CodeParser)
    ├── repo_indexer.py     # Build index + text chunks
    ├── graph_builder.py    # NetworkX dependency graph
    ├── graph_analyzer.py   # Graph queries (who_calls, what_does_it_call)
    ├── embedder.py         # SentenceTransformer wrapper
    ├── vector_store.py     # ChromaDB wrapper
    ├── retriever.py        # HybridRetriever (semantic + graph)
    ├── llm.py              # Groq LLM wrapper (rewrite + generate)
    └── answer_generator.py # Context assembly, prompt, chat history
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Code Parsing | Python `ast` module |
| Dependency Graph | NetworkX |
| Embeddings | `sentence-transformers` — `BAAI/bge-small-en-v1.5` |
| Vector Store | ChromaDB (persistent) |
| LLM | Groq API — `llama-3.3-70b-versatile` |
| Web UI | Streamlit |
| Repo Cloning | GitPython |

---

## 🚀 Setup & Installation

### 1. Clone this repository

```bash
git clone https://github.com/Singhania2004/repo_codebase_ai.git
cd repo_codebase_ai
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API key and paths

Create a `.env` file in the project root:

```python
# .env
GROQ_API_KEY = "your_groq_api_key_here"
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

---

## 🖥️ Usage

### Streamlit Web App (recommended)

```bash
streamlit run streamlit_app.py
```

1. Open `http://localhost:8501` in your browser.
2. Paste a GitHub URL in the sidebar and click **Load**.
3. Watch the pipeline progress bar — cloning, parsing, graph building, and embedding happen automatically.
4. Ask questions in the chat input. 
5. Expand **Retrieved context** under any answer to inspect which nodes were pulled (semantic vs. graph).

### Terminal Interface

```bash
python app.py
```

Enter a GitHub URL when prompted, wait for the pipeline to complete, then type questions at the `Question:` prompt. Type `exit` to quit.


---


## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request.

## 📝 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.
