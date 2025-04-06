import google.generativeai as genai
from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()
import os
import chromadb
from chromadb.utils import embedding_functions
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
import markdown


# Read file to string
def read_file_to_string(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content

# Remove stopwords from text
def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)
    filtered_text = ' '.join(word for word in words if word.lower() not in stop_words)
    return filtered_text

# Compute cosine similarity between query and results
def compute_similarity(query_text, results, model_name="all-mpnet-base-v2"):
   
    # Generate query embedding
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
    query_embedding = np.array(embedding_function([query_text])[0])
    
    query_embedding = query_embedding.flatten()  # Shape (768,)

    result_embeddings = np.array(results['embeddings'])

    # Ensure result embeddings have consistent shape
    if len(result_embeddings.shape) == 3:  # Handles cases with extra dimension
        result_embeddings = result_embeddings.squeeze(axis=1)

    similarities = []
    
    for result_embedding in result_embeddings:
        result_embedding = result_embedding.flatten()  # Ensure it has shape (768,)
        
        # Compute cosine similarity
        score = np.dot(query_embedding, result_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(result_embedding)
        )
        similarities.append(score)

    return similarities

# Vector database class
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
    
    def query_db(self, query_text,n_results=1):
        results = self.collection.query(query_texts=[query_text], n_results=n_results, include=['documents', 'metadatas', 'embeddings'])
        return results
    
# Token class
class token:
    def __init__(self,username,timestamp,query,websearch, courseID):
        self.courseID = courseID
        self.query = query
        self.websearch = websearch
        self.response = None
        self.username = username
        self.timestamp = timestamp

# LLM Agent class
class LLM_Agent:
    def __init__(self,GEMINI_API_KEY,TAVILY_API_KEY,vectordb,faqdb,assigndb):
        self.vectordb = vectordb
        self.faqdb = faqdb
        self.assigndb = assigndb
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        ## START CHAT ADDED HERE
        self.model = model.start_chat()

        self.web = TavilyClient(api_key=TAVILY_API_KEY)

        # Instructions for the AI assistant
        self.main_instruction = '''You are Sahayog, an AI assistant designed to help students on an online course platform. 
        Your main goal is to provide clear, easy-to-understand answers to their questions, ensuring that all content is beginner-friendly.
        For each query from the student, the backend provides either web search results from Tavily or Course Related material from a RAG architecture. 
        DO NOT mention the idea of giving context to the student. For example , do not reply " provided context doesn't seem to relate ...".
        Maintain a good conversational tone with the student.
        If non-academic questions are asked advice the student to academics.
        When responding to students, always use simple, accessible language, and break down complex topics into easy-to-follow steps. 
        If necessary, explain technical terms in simple language or use analogies to make them relatable. 
        ONLY In case the question and the context are not related, provide an answer based on the previous chat and your own knowledge.
        Remember the context of the conversation. Remember previous messages and in case of continued conversation on the same topic preserve the connection between the consecutive messages.
        For each query from the student you will be provided with either web search results from Tavily or Course Related material from a RAG architecture. Use the context to answer but do not mention that the context has been provided by us. 
        '''

        # Instructions for the AI assistant when provided with web search results
        self.instruction_websearch = '''
        You are provided with web search results via the Tavily client to find relevant resources such as articles, tutorials, and videos. 
        DO NOT mention the idea of giving context to the student
        Focus on topics from biology, linguistics, computer science and programming in python, calculus, and software engineering.  
        Limit responses to educational content from these domains.  
        In case of irrelevant interpretations or results unrelated to the course topics gently redirect the student to focus on academic.  
        For ambiguous terms, prioritize course-specific meanings.  
            - For example, if asked "what is a cell," provide results related to the biological cell (from the Biology course) rather than a prison cell.  
        For all questions you must provide links to the resources or courses on the platform for further exploration. \n\n\n 
        Focus on beginner-friendly, trustworthy, and educational resources.  
        '''       
    
        # Instructions for the AI assistant when provided with RAG architecture results
        self.instruction_rag = '''You are provided with the top N search results from a database in the following format:
        "The following are the top N results from the database:
        Result 1: Lecture: U, Week: X, Course: Y, Context: Z
        Result 2: Lecture: A, Week: B, Course: C, Context: D
        ..."
        Your task is to generate a direct, informative answer to the user’s query, ensuring that the response is not just a summary but a well-explained response to their question.
        DO NOT mention the idea of giving context to the student 
        Answer the question first, making sure the explanation is clear and structured. 
        At the end of your response, explicitly reference the relevant Week, Lecture, and Course where the topic is covered.
        If multiple results are relevant, synthesize the information effectively without unnecessary repetition. 
        For all questions, ensure your response is well-supported by the provided context and guide the student to the appropriate course material for further learning.
        '''
       
        self.model.send_message(self.main_instruction).text

    
    # Get web search context
    def get_web_context(self,query):
        
        context_raw = self.web.search(query, search_depth="basic")["results"][:3]
        context_string = ''
        for res1 in context_raw:
            context_string+='URL:'+res1.get('url')
            try:
                context_string+=remove_stopwords(res1['content'])
            except Exception as e:
                print('exception remove stopwords: ',str(e))
            context_string+='\n\n'
        
        return context_string
    
    # Get response if the question is similar to the FAQ or Assignments
    def get_faq_assign_response(self,query_text):
        query_text = remove_stopwords(query_text)
        results_assigndb = self.assigndb.query_db(query_text,1)
        similarity_scores_assign = compute_similarity(query_text, results_assigndb)
        if similarity_scores_assign[0] > 0.75:
            return "THIS QUESTION IS FROM ASSIGNMENT HENCE I COULDN'T ANSWER IT"
        else:
            results_faqdb = self.faqdb.query_db(query_text,1)
            similarity_scores = compute_similarity(query_text, results_faqdb)
            if similarity_scores[0] > 0.75:
                return results_faqdb['metadatas'][0][0]['answer']
            else:
                return ""

    # Generating response based on the question
    def generate_response(self,tok1):
        result= self.get_faq_assign_response(tok1.query)
        if result != "":
            tok1.response = result
            return tok1
        
        if tok1.websearch:
            context = self.get_web_context(tok1.query)
            prompt = self.instruction_websearch +f'Question: {tok1.query}  \n\n Context:'+context
            tok1.response = markdown.markdown(self.model.send_message(prompt).text)
        else:
            if tok1.courseID == "null":
                context = self.vectordb.query(tok1.query,1)
                prompt = self.instruction_rag + f'\n\nQuestion: {tok1.query}\n\n USE THE FOLLOWING FOR RESPONSE ONLY IF IT MAKES SENSE Context: {context}\n\n'
                tok1.response = markdown.markdown(self.model.send_message(prompt).text)
            else:
                context = self.vectordb.query(tok1.query,3)
                prompt = self.instruction_rag + f'\n\nQuestion: {tok1.query}\n\n USE THE FOLLOWING FOR RESPONSE ONLY IF IT MAKES SENSE Context: {context}\n\n'
                tok1.response = markdown.markdown(self.model.send_message(prompt).text)
        return tok1

# Server handler class
class serverHandler:
    def __init__(self,GEMINI_API_KEY,TAVILY_API_KEY,vdb_path, faqdb_path, assigndb_path):
        self.GEMINI_API_KEY = GEMINI_API_KEY
        self.TAVILY_API_KEY = TAVILY_API_KEY
        self.vectordb = vectordbclass(vdb_path)
        self.faqdb = vectordbclass(faqdb_path)
        self.assigndb = vectordbclass(assigndb_path)
        self.user_map = {}

    def handle_token(self,tok1):
        if tok1.username not in self.user_map:
            new_model = LLM_Agent(self.GEMINI_API_KEY,self.TAVILY_API_KEY,self.vectordb,self.faqdb,self.assigndb)
            self.user_map[tok1.username] = new_model

        final_token = self.user_map[tok1.username].generate_response(tok1)
        return final_token
    
    def delete_user(self,username):
        if username in self.user_map:
            del self.user_map[username]
        return
    
    def print_map(self):
        for k in self.user_map:
            print("user map:"+k)

    def no_of_users(self):
        return len(self.user_map)
