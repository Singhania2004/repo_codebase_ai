import chromadb


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="./vector_store"
        )

        self.collection = self.client.get_or_create_collection(
            "codebase"
        )

    def add_documents(
            self,
            ids,
            documents,
            metadatas,
            embeddings
    ):

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

    def search(
            self,
            query_embedding,
            k=5
    ):

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )