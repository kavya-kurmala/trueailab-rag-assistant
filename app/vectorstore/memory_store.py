import numpy as np


class MemoryVectorStore:
    def __init__(self):
        self.vectors = []

    def add(self, embedding, metadata):
        self.vectors.append({
            "embedding": np.array(embedding),
            "metadata": metadata
        })

    def cosine_similarity(self, vec1, vec2):
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        denominator = np.linalg.norm(vec1) * np.linalg.norm(vec2)

        if denominator == 0:
            return 0.0

        return float(np.dot(vec1, vec2) / denominator)

    def search(self, query_embedding, top_k=3, threshold=0.70):
        results = []

        for item in self.vectors:
            score = self.cosine_similarity(query_embedding, item["embedding"])

            results.append({
                "score": score,
                "metadata": item["metadata"]
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        filtered_results = [
            result for result in results
            if result["score"] >= threshold
        ]

        return filtered_results[:top_k]