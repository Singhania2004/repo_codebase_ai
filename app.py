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


def main():

    github_url = input("Enter GitHub repo URL: ")

    # --------------------------------------------------
    # Load Repo
    # --------------------------------------------------

    loader = GitHubLoader(REPO_DIR)

    repo_path = loader.clone_repo(github_url)

    py_files = loader.get_python_files(repo_path)

    # --------------------------------------------------
    # Build Repository Index
    # --------------------------------------------------

    parser = CodeParser()

    indexer = RepoIndexer(parser)

    repo_index = indexer.build_index(py_files)

    print("\nRepository Summary")
    print("-" * 40)
    print(f"Files: {len(repo_index['files'])}")
    print(f"Functions: {len(repo_index['functions'])}")
    print(f"Classes: {len(repo_index['classes'])}")

    # --------------------------------------------------
    # Build Dependency Graph
    # --------------------------------------------------

    builder = GraphBuilder()

    graph = builder.build_graph(repo_index)

    print("\nGraph Summary")
    print("-" * 40)
    print(f"Nodes: {graph.number_of_nodes()}")
    print(f"Edges: {graph.number_of_edges()}")

    analyzer = GraphAnalyzer(graph)

    # --------------------------------------------------
    # Build Chunks
    # --------------------------------------------------

    chunks = indexer.build_chunks(repo_index)

    print(f"\nChunks Created: {len(chunks)}")

    # --------------------------------------------------
    # Embeddings + Vector DB
    # --------------------------------------------------

    embedder = Embedder()

    store = VectorStore()

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    print("\nGenerating embeddings...")

    for chunk in chunks:

        ids.append(chunk["id"])

        documents.append(chunk["text"])

        metadatas.append(
            {
                "type": chunk["type"]
            }
        )

        embeddings.append(
            embedder.embed(chunk["text"]).tolist()
        )

    store.add_documents(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print("Embeddings stored successfully.")

    # --------------------------------------------------
    # Hybrid Retriever
    # --------------------------------------------------

    retriever = HybridRetriever(
        graph=graph,
        analyzer=analyzer,
        embedder=embedder,
        vector_store=store
    )

    # --------------------------------------------------
    # LLM + Answer Generator
    # --------------------------------------------------

    llm = LLM()

    generator = AnswerGenerator(
        retriever=retriever,
        repo_index=repo_index,
        llm=llm
    )

    # --------------------------------------------------
    # Query Loop
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("AI Codebase Assistant Ready")
    print("Type 'exit' to quit")
    print("=" * 60)

    while True:

        query = input("\nQuestion: ")

        if query.lower() == "exit":
            break

        try:

            answer = generator.answer(query)

            print("\n" + "=" * 60)
            print("ANSWER")
            print("=" * 60)
            print(answer)

        except Exception as e:

            print("\nError:")
            print(e)


if __name__ == "__main__":
    main()