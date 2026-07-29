import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

groq_api_key= os.getenv("GROQ_API_KEY")

def get_llm():
    ''' Returns a reusable instance of langchain's ChatGroq class '''
    return ChatGroq(
        model= "llama-3.3-70b-versatile", # load the llm model
        groq_api_key= groq_api_key,
        temperature= 0.1, # decides the deterministic nature of answers
        max_tokens= 1024 # limits the output to max 1024 tokens
    )
