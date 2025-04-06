import os
from tavily import TavilyClient
import chromadb
from chromadb.utils import embedding_functions


# Token class
class token:
    def __init__(self,username,query,courseID):
        self.courseID = courseID
        self.query = query
        self.response = None
        self.username = username

class vectordbclass:
    def __init__(self, path):
        self.path = path
        self.chroma_client = chromadb.PersistentClient(path=path)
        self.embedding_fn = embedding_functions
        self.sentence_transformer_ef = self.embedding_fn.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2")
        self.collection = self.chroma_client.get_or_create_collection(name=path, embedding_function=self.sentence_transformer_ef)
    
    def query(self, query_text, n_results=3):
        results = self.collection.query(query_texts=[query_text], n_results=n_results, include=['documents', 'metadatas'])
        actual_results = min(n_results, len(results['documents'][0]) if results['documents'] else 0)
        context = f'''The following are {actual_results} results from the vector database:\n'''
        
        for i in range(actual_results):
            context += '''\nResult {} Lecture No:{} Week:{} Course Name:{}\n Context: {}\n'''.format(
                i+1,
                results['metadatas'][0][i].get('lecture_no', 'N/A'),
                results['metadatas'][0][i].get('week', 'N/A'),
                results['metadatas'][0][i].get('courseID', 'N/A'),
                results['documents'][0][i]
            )
        return context if actual_results > 0 else "No results found."

# RAG Agent class
class RAG_Agent:
    def __init__(self,vectordb):
        self.vectordb = vectordb

    # Generating response based on the question
    def generate_response(self,tok1):
        context = self.vectordb.query(tok1.query,3)
        tok1.response = context
        return tok1

class Web_Agent:
    def __init__(self,TAVILY_API_KEY):
        self.web = TavilyClient(api_key=TAVILY_API_KEY)
    # Generating response based on the question
    def generate_response(self,tok1):
        context= self.web.search(tok1.query, search_depth="basic")["results"][:3]
        tok1.response = context
        return tok1

# Server handler class
class serverHandler:
    def __init__(self,vdb_path,TAVILY_API_KEY):
        self.vectordb = vectordbclass(vdb_path)
        self.TAVILY_API_KEY = TAVILY_API_KEY

    def handle_token_rag(self,tok1):
        new_model = RAG_Agent(self.vectordb)
        final_token = new_model.generate_response(tok1)
        return final_token
    
    def handle_token_web(self,tok1):
        new_model = Web_Agent(self.TAVILY_API_KEY)
        final_token = new_model.generate_response(tok1)
        return final_token
