import streamlit as st

st.set_page_config(
    page_title="CodeLens – AI Codebase Assistant",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimal CSS — only style custom elements, never override Streamlit's theme variables
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

/* User chat bubble */
.bubble-user {
    background: #2563eb;
    color: #fff;
    border-radius: 16px 16px 4px 16px;
    padding: 10px 14px;
    margin: 4px 0;
    display: inline-block;
    max-width: 80%;
    font-size: 0.92rem;
    line-height: 1.5;
    float: right;
    clear: both;
}

/* Assistant chat bubble wrapper */
.bubble-bot-wrap {
    clear: both;
    margin: 4px 0;
}

/* Node tag pills */
.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 99px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    margin: 2px 3px 2px 0;
}
.tag-semantic { background: #dbeafe; color: #1d4ed8; }
.tag-graph    { background: #dcfce7; color: #15803d; }

/* Stat row */
.stat-row {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid rgba(128,128,128,0.15);
    font-size: 0.82rem;
}

/* Clearfix */
.cf::after { content: ""; display: table; clear: both; }

/* Mono font for code-y labels */
.mono { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "pipeline_ready": False,
    "generator": None,
    "repo_stats": {},
    "graph_stats": {},
    "chat_history": [],
    "pipeline_log": [],
    "repo_name": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Pipeline ───────────────────────────────────────────────────────────────────
def run_pipeline(github_url: str):
    st.session_state.pipeline_log = []
    log = st.session_state.pipeline_log

    progress = st.progress(0, text="Starting…")

    def tick(pct, msg):
        log.append(msg)
        progress.progress(pct, text=msg)

    try:
        from config import REPO_DIR
        from src.github_loader import GitHubLoader
        from src.parser import CodeParser
        from src.repo_indexer import RepoIndexer
        from src.graph_builder import GraphBuilder
        from src.graph_analyzer import GraphAnalyzer
        from src.embedder import Embedder
        from src.vector_store import VectorStore
        from src.retriever import HybridRetriever
        from src.llm import LLM
        from src.answer_generator import AnswerGenerator

        tick(5,  "Cloning repository…")
        loader = GitHubLoader(REPO_DIR)
        repo_path = loader.clone_repo(github_url)
        repo_name = repo_path.name
        py_files  = loader.get_python_files(repo_path)
        log.append(f"✓ Cloned {repo_name} — {len(py_files)} Python files")

        tick(20, "Parsing source files…")
        parser    = CodeParser()
        indexer   = RepoIndexer(parser)
        repo_index = indexer.build_index(py_files)
        st.session_state.repo_stats = {
            "Files":     len(repo_index["files"]),
            "Functions": len(repo_index["functions"]),
            "Classes":   len(repo_index["classes"]),
        }
        log.append(f"✓ Indexed {st.session_state.repo_stats}")

        tick(40, "Building dependency graph…")
        builder  = GraphBuilder()
        graph    = builder.build_graph(repo_index)
        analyzer = GraphAnalyzer(graph)
        st.session_state.graph_stats = {
            "Nodes": graph.number_of_nodes(),
            "Edges": graph.number_of_edges(),
        }
        log.append(f"✓ Graph — {st.session_state.graph_stats}")

        tick(55, "Chunking code…")
        chunks = indexer.build_chunks(repo_index)
        log.append(f"✓ {len(chunks)} chunks created")

        tick(65, "Generating embeddings…")
        embedder = Embedder()
        store    = VectorStore(repo_name)

        ids, docs, metas, embs = [], [], [], []
        for chunk in chunks:
            if store.document_exists(chunk["id"]):
                continue
            ids.append(chunk["id"])
            docs.append(chunk["text"])
            metas.append({"type": chunk["type"]})
            embs.append(embedder.embed(chunk["text"]).tolist())

        if ids:
            store.add_documents(ids=ids, documents=docs, metadatas=metas, embeddings=embs)
            log.append(f"✓ {len(ids)} embeddings stored")
        else:
            log.append("✓ Already indexed — 0 new embeddings")

        tick(85, "Setting up LLM & retriever…")
        llm       = LLM()
        retriever = HybridRetriever(
            graph=graph, analyzer=analyzer,
            embedder=embedder, vector_store=store, llm=llm
        )
        generator = AnswerGenerator(
            retriever=retriever, repo_index=repo_index, llm=llm
        )

        st.session_state.generator      = generator
        st.session_state.pipeline_ready = True
        st.session_state.chat_history   = []
        st.session_state.repo_name      = repo_name

        tick(100, f"✅ {repo_name} is ready!")
        log.append("Pipeline complete.")

    except Exception as exc:
        progress.empty()
        st.error(f"**Pipeline failed:** {exc}")
        log.append(f"✗ {exc}")
        st.session_state.pipeline_ready = False


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔭 CodeLens")
    st.caption("AI Codebase Assistant")
    st.divider()

    # Repo input
    st.markdown("**Repository**")
    github_url = st.text_input(
        "GitHub URL",
        placeholder="https://github.com/owner/repo",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns(2)
    with col1:
        load = st.button("Load", use_container_width=True, type="primary")
    with col2:
        reset = st.button("Reset", use_container_width=True, disabled=not st.session_state.pipeline_ready)

    if reset:
        for k in ["pipeline_ready", "generator", "chat_history", "repo_stats", "graph_stats", "pipeline_log", "repo_name"]:
            st.session_state[k] = False if k == "pipeline_ready" else (None if k == "generator" else ([] if k in ["chat_history", "pipeline_log"] else ({} if k in ["repo_stats", "graph_stats"] else "")))
        st.rerun()

    if load:
        if not github_url.strip():
            st.warning("Enter a GitHub URL first.")
        else:
            run_pipeline(github_url.strip())

    # Stats
    if st.session_state.pipeline_ready:
        st.divider()
        st.markdown(f"**{st.session_state.repo_name}**")
        all_stats = {**st.session_state.repo_stats, **st.session_state.graph_stats}
        for label, val in all_stats.items():
            st.markdown(
                f'<div class="stat-row"><span>{label}</span><span class="mono"><b>{val}</b></span></div>',
                unsafe_allow_html=True,
            )

    # Pipeline log
    if st.session_state.pipeline_log:
        st.divider()
        with st.expander("Pipeline log", expanded=False):
            for line in st.session_state.pipeline_log:
                st.caption(line)

    # Suggestions
    if st.session_state.pipeline_ready:
        st.divider()
        st.markdown("**Suggested questions**")
        suggestions = [
            "What is the overall architecture?",
            "How does the data flow through the system?",
            "What are the main entry points?",
            "How does the retriever work?",
        ]
        for q in suggestions:
            if st.button(q, key=f"sug_{q}", use_container_width=True):
                st.session_state["_prefill"] = q
                st.rerun()


# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("### Ask anything about your codebase")

if st.session_state.pipeline_ready:
    st.success(f"**{st.session_state.repo_name}** loaded and ready.", icon="✅")
else:
    st.info("Load a GitHub repository from the sidebar to get started.", icon="👈")

st.divider()

# Chat history
if not st.session_state.chat_history:
    st.markdown(
        "<div style='text-align:center;padding:48px 0;opacity:0.45;'>"
        "<div style='font-size:2rem'>💬</div>"
        "<div>Your conversation will appear here.</div>"
        "</div>",
        unsafe_allow_html=True,
    )
else:
    for turn in st.session_state.chat_history:
        if turn["role"] == "user":
            # Right-aligned user bubble
            st.markdown(
                f'<div class="cf"><div class="bubble-user">{turn["content"]}</div></div>',
                unsafe_allow_html=True,
            )
        else:
            with st.chat_message("assistant"):
                st.markdown(turn["content"])

                nodes = turn.get("nodes", [])
                if nodes:
                    semantic = [n for n in nodes if n.get("source") == "semantic"][:4]
                    graph_n  = [n for n in nodes if n.get("source") == "graph"][:4]
                    with st.expander(f"Retrieved context — {len(nodes)} nodes"):
                        if semantic:
                            st.caption("Semantic")
                            for n in semantic:
                                score = f"  dist={n['score']:.4f}" if n["score"] != 999 else ""
                                st.markdown(
                                    f'<span class="tag tag-semantic">{n["id"]}{score}</span>',
                                    unsafe_allow_html=True,
                                )
                        if graph_n:
                            st.caption("Graph neighbours")
                            for n in graph_n:
                                st.markdown(
                                    f'<span class="tag tag-graph">{n["id"]}</span>',
                                    unsafe_allow_html=True,
                                )

st.divider()

# Input
prefill = st.session_state.pop("_prefill", "")

with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([6, 1])
    with cols[0]:
        query = st.text_input(
            "Question",
            value=prefill,
            placeholder="e.g. How does the hybrid retriever work?",
            label_visibility="collapsed",
            disabled=not st.session_state.pipeline_ready,
        )
    with cols[1]:
        send = st.form_submit_button(
            "Send",
            use_container_width=True,
            type="primary",
            disabled=not st.session_state.pipeline_ready,
        )

if send and query.strip():
    user_q = query.strip()
    st.session_state.chat_history.append({"role": "user", "content": user_q, "nodes": []})

    with st.spinner("Thinking…"):
        try:
            gen = st.session_state.generator
            captured = []
            _orig = gen.retriever.retrieve

            def _patched(q, k=5):
                nodes = _orig(q, k)
                captured.extend(nodes)
                return nodes

            gen.retriever.retrieve = _patched
            answer = gen.answer(user_q)
            gen.retriever.retrieve = _orig

            st.session_state.chat_history.append({
                "role": "assistant", "content": answer, "nodes": captured
            })
        except Exception as e:
            st.session_state.chat_history.append({
                "role": "assistant", "content": f"⚠️ Error: `{e}`", "nodes": []
            })

    st.rerun()

# Clear button
if st.session_state.chat_history:
    if st.button("Clear conversation"):
        st.session_state.chat_history = []
        if st.session_state.generator:
            st.session_state.generator.chat_history = []
        st.rerun()