from config import REPO_DIR

from src.github_loader import GitHubLoader
from src.parser import CodeParser
from src.repo_indexer import RepoIndexer
from src.graph_builder import GraphBuilder
from src.graph_analyzer import GraphAnalyzer
from src.embedder import Embedder
from src.vector_store import VectorStore
from src.retriever import HybridRetriever



def main():

    github_url = input("Enter GitHub repo URL: ")

    loader = GitHubLoader(REPO_DIR)

    repo_path = loader.clone_repo(github_url)

    py_files = loader.get_python_files(repo_path)

    parser = CodeParser()

    indexer = RepoIndexer(parser)

    repo_index = indexer.build_index(py_files)

    print("\nFILES:", len(repo_index["files"]))
    print("FUNCTIONS:", len(repo_index["functions"]))
    print("CLASSES:", len(repo_index["classes"]))

    print("\nFirst 10 Functions:\n")

    for func in repo_index["functions"][:10]:

        print(func["id"])

    print("\nClasses:\n")

    for cls in repo_index["classes"]:

        print(cls["id"])

        for method in cls["methods"]:

            print("   └──", method["id"])

    
    builder = GraphBuilder()

    graph = builder.build_graph(repo_index)

    print("\nNodes:", graph.number_of_nodes())
    print("Edges:", graph.number_of_edges())

    print("\nCALL RELATIONSHIPS:\n")

    for u, v, data in graph.edges(data=True):

        if data["relation"] == "CALLS":

            print(f"{u}")
            print("   ↓")
            print(v)
            print()

    analyzer = GraphAnalyzer(graph)

    print()

    print(
        analyzer.imported_files("train.py")
    )

    print(
        analyzer.what_does_it_call(
            "train.py::main"
        )
    )


    embedder = Embedder()

    store = VectorStore()

    chunks = indexer.build_chunks(repo_index)

    ids = []
    documents = []
    metadatas = []
    embeddings = []

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
        ids,
        documents,
        metadatas,
        embeddings
    )

    query = "How is dataloader created?"

    query_embedding = embedder.embed(query).tolist()

    results = store.search(
        query_embedding,
        k=5
    )

    print(results["ids"][0])


if __name__ == "__main__":
    main()