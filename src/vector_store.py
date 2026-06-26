import chromadb


class VectorStore:

    def __init__(self, repo_name):

        self.client = chromadb.PersistentClient(
            path="./vector_store"
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=repo_name
            )
        )

    def document_exists(self, doc_id):

        result = self.collection.get(
            ids=[doc_id]
        )

        return len(result["ids"]) > 0

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
            n_results=k,
            include=[
                "distances",
                "metadatas",
                "documents"
            ]
        )