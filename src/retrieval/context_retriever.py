from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL, TOP_K_DOCUMENTS
import math

class ContextRetriever:
    def __init__(self, vector_store_path):
        self.vector_store_path = vector_store_path
        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        self.vector_store = FAISS.load_local(
            self.vector_store_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )

    def get_context(self, query, top_k=TOP_K_DOCUMENTS):
        """
        Smart similarity search that adapts to your data distribution
        """
        results_with_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        print(f"🔍 Similarity search for: '{query}'")
        print("=" * 50)
        
        # Calculate dynamic threshold based on your data
        if results_with_scores:
            distances = [abs(score) for _, score in results_with_scores]
            avg_distance = sum(distances) / len(distances)
            dynamic_threshold = avg_distance + 0.3  # Allow slightly above average
            
            print(f"📊 Distance range: {min(distances):.3f} - {max(distances):.3f}")
            print(f"📊 Average distance: {avg_distance:.3f}")
            print(f"📊 Dynamic threshold: {dynamic_threshold:.3f}")
        
        relevant_docs = []
        for i, (doc, distance) in enumerate(results_with_scores, 1):
            abs_distance = abs(distance)
            
            # Determine relevance level
            if abs_distance < 1.0:
                relevance = "🎯 Highly Relevant"
            elif abs_distance < 1.2:
                relevance = "✅ Relevant"
            elif abs_distance < 1.5:
                relevance = "⚠️ Somewhat Relevant"
            else:
                relevance = "❓ Possibly Relevant"
            
            print(f"{i}. {relevance} (distance: {distance:.3f})")
            print(f"   Content: {doc.page_content[:100]}...")
            print("-" * 40)
            
            relevant_docs.append(doc)
        
        print(f"✅ Returning all {len(relevant_docs)} documents - let AI agents decide relevance")
        
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        return context

    def get_context_with_mmr(self, query, top_k=TOP_K_DOCUMENTS, diversity_factor=0.5):
        """
        Use Maximum Marginal Relevance for better diversity
        """
        try:
            docs = self.vector_store.max_marginal_relevance_search(
                query, 
                k=top_k,
                fetch_k=top_k * 2,
                lambda_mult=diversity_factor
            )
            
            print(f"🎯 MMR search for: '{query}' (diversity: {diversity_factor})")
            print(f"✅ Found {len(docs)} diverse documents")
            
            context = "\n\n".join([doc.page_content for doc in docs])
            return context
            
        except Exception as e:
            print(f"❌ MMR search failed: {e}")
            # Fallback to regular similarity search
            return self.get_context(query, top_k)

    def semantic_search_detailed(self, query, top_k=TOP_K_DOCUMENTS):
        """
        Detailed semantic search with comprehensive scoring
        """
        try:
            query_embedding = self.embeddings.embed_query(query)
            results_with_scores = self.vector_store.similarity_search_by_vector_with_score(
                query_embedding, k=top_k
            )
            
            print(f"🧠 Semantic search results for: '{query}'")
            print("=" * 60)
            
            context_pieces = []
            for i, (doc, distance) in enumerate(results_with_scores, 1):
                abs_distance = abs(distance)
                similarity_percent = math.exp(-abs_distance) * 100
                
                print(f"{i}. Distance: {distance:.4f} | Similarity: {similarity_percent:.1f}%")
                print(f"   Content: {doc.page_content[:150]}...")
                print(f"   Metadata: {doc.metadata}")
                print("-" * 40)
                
                context_pieces.append(f"[Relevance: {similarity_percent:.1f}%]\n{doc.page_content}")
            
            return "\n\n".join(context_pieces)
            
        except Exception as e:
            print(f"❌ Detailed search failed: {e}")
            return self.get_context(query, top_k)

    def get_best_context(self, query, method="similarity", top_k=TOP_K_DOCUMENTS):
        """
        Get context using the best method for your query
        """
        if method == "similarity":
            return self.get_context(query, top_k)
        elif method == "mmr":
            return self.get_context_with_mmr(query, top_k)
        elif method == "detailed":
            return self.semantic_search_detailed(query, top_k)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'similarity', 'mmr', or 'detailed'")

    def smart_search(self, query, top_k=TOP_K_DOCUMENTS):
        """
        Smart search that always returns meaningful results
        """
        results_with_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
        
        print(f"🧠 Smart search for: '{query}'")
        print("=" * 50)
        
        for i, (doc, distance) in enumerate(results_with_scores, 1):
            abs_distance = abs(distance)
            
            # Determine relevance category
            if abs_distance < 0.2:
                relevance = "🎯 Highly Relevant"
            elif abs_distance < 0.5:
                relevance = "✅ Relevant"
            elif abs_distance < 1.0:
                relevance = "⚠️ Somewhat Relevant"
            else:
                relevance = "❓ Possibly Relevant"
            
            similarity_percent = math.exp(-abs_distance) * 100
            
            print(f"{i}. {relevance} (distance: {distance:.3f}, similarity: {similarity_percent:.1f}%)")
            print(f"   Content: {doc.page_content[:150]}...")
            print("-" * 40)
        
        # Return all documents - let the AI decide relevance
        context = "\n\n".join([doc.page_content for doc, _ in results_with_scores])
        return context
