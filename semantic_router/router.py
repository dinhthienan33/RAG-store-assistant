import numpy as np

class SemanticRouter():
    def __init__(self, embedding, routes, threshold=0.5):
        """
        Initialize the SemanticRouter with embedding model, routes, and a threshold for route selection.
        Args:
            embedding: An embedding model that supports an 'encode' method to generate embeddings.
            routes: A list of Route objects with 'name' and 'samples'.
            threshold: A confidence threshold for selecting the route. If no route exceeds this threshold, a fallback can be triggered.
        """
        self.routes = routes
        self.embedding = embedding
        self.threshold = threshold
        self.routesEmbedding = {}

        # Pre-compute and normalize route embeddings once during initialization.
        for route in self.routes:
            route_embeddings = self.embedding.encode(route.samples)
            normalized_embeddings = route_embeddings / np.linalg.norm(route_embeddings, axis=1, keepdims=True)
            self.routesEmbedding[route.name] = normalized_embeddings

    def get_routes(self):
        """Return the list of available routes."""
        return self.routes

    def guide(self, query):
        """
        Guide the chatbot by determining the most suitable route for a query based on similarity scores.
        Args:
            query: The query for which the route is determined.
        Returns:
            A tuple containing the best route name and the similarity score.
        """
        # Encode and normalize the query embedding.
        query_embedding = self.embedding.encode([query])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        scores = []

        # Calculate the cosine similarity between the query embedding and each route's embeddings.
        for route in self.routes:
            route_embeddings = self.routesEmbedding[route.name]
            score = np.mean(np.dot(route_embeddings, query_embedding.T).flatten())
            scores.append((score, route.name))

        # Sort scores in descending order (highest score first).
        scores.sort(reverse=True, key=lambda x: x[0])

        best_score, best_route = scores[0]

        # Apply a threshold to avoid selecting a route if the confidence is too low.
        if best_score >= self.threshold:
            return best_route, best_score
        else:
            # If no route exceeds the threshold, return None or a default fallback route.
            return None, best_score
