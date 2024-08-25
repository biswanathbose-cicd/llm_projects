from dotenv import load_dotenv
import os
import pickle
import faiss

from google.cloud import storage
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
#Import Python modules
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains import RetrievalQA
from langchain.document_loaders.csv_loader import CSVLoader
# Load environment variables from .env file
load_dotenv()

# Access environment variables
api_key = os.getenv('GOOGLE_API_KEY')

#Load the models
llm = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key=api_key)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    
bucket_name = "codebasics1"
gcs_file_path = "faiss_index/index.faiss"  # Path to the FAISS index file in GCS
gcs_file_path_pkl = "faiss_index/index.pkl"
local_dir = "/tmp/faiss_index"  # Local directory where the file will be stored
local_file_path = os.path.join(local_dir, "index.faiss")  # Complete local path to the file
local_file_pkl = os.path.join(local_dir, "index.pkl")

# # Create local directory if it doesn't exist
# if not os.path.exists(local_dir):
#     os.makedirs(local_dir)
# Initialize GCS client
# Create local directory if it doesn't exist
if not os.path.exists(local_dir):
    os.makedirs(local_dir)
storage_client = storage.Client()

# Get the bucket
bucket = storage_client.bucket(bucket_name)

# Get the blob (file) from GCS
blob = bucket.blob(gcs_file_path)
blob_pkl = bucket.blob(gcs_file_path_pkl)
# Download the file to the local filesystem
blob.download_to_filename(local_file_path)
blob_pkl.download_to_filename(local_file_pkl)
# Debug: Check if the file exists and its size
if os.path.exists(local_file_path):
    print(f"File {local_file_path} downloaded successfully.")
    print(f"File size: {os.path.getsize(local_file_path)} bytes")
else:
    print(f"File {local_file_path} was not downloaded successfully.")
try:
    index = faiss.read_index(local_file_path)
    print("FAISS index loaded successfully.")
except Exception as e:
    print(f"Error loading FAISS index: {e}")
    # Exit or handle the error accordingly
    raise

def get_qa_chain():
    try:
        # Load the vector database from local folder
        vectordb = FAISS.load_local(local_dir,embeddings,allow_dangerous_deserialization=True)

        retriever = vectordb.as_retriever(score_threshold=0.7)
        prompt_template = """Given the following context and a question, generate an answer based on this context only.
        In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
        If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

        CONTEXT: {context}

        QUESTION: {question}"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        chain = RetrievalQA.from_chain_type(llm=llm,
                                            chain_type="stuff",
                                            retriever=retriever,
                                            input_key="query",
                                            return_source_documents=True,
                                            chain_type_kwargs={"prompt": PROMPT})
        return chain
    except Exception as e:
        return f"Error loading FAISS index: {str(e)}"
