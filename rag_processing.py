from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
load_dotenv()

CHROMA_DB_PATH="./chroma_db"
embeddings=GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

def ingest_pdf(file_path:str):
    print(f"Starting ingestion for the file {file_path}")

    loader=PyPDFLoader(file_path)
    documents=loader.load()

    text_splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=0)
    texts=text_splitter.split_documents(documents)
    vectordb=Chroma(embedding_function=embeddings,persist_directory=CHROMA_DB_PATH)
    vectordb.add_documents(texts)
    print(f"Finished ingestion for the file {file_path}")


