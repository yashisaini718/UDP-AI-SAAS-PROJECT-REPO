from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

# the ingestion pipeline will first load the document and return a list of langchain pages for each document 
# and then split the documents into chunks

def load_document(file_path: str, document_id: str):
        ''' Returns a tuple of document_id and loaded pages[list]
        Args:
        document_id: id of the uploaded document
        file_path: path of the uploaded file'''

        pdf_file= Path(file_path) # converting string to path
        
        print(f"Processing {pdf_file.name}")

        try:
            loader= PyMuPDFLoader(str(pdf_file)) # needed to convert path to string
            pages= loader.load()

            # changing metadata
            # this document id will help in filtering the document to know which document to filter out 
            # for opportunity extraction
            for page in pages:

                page.metadata['source_file']= pdf_file.name
                page.metadata['file_type']= "pdf"
                page.metadata['document_id']= document_id

            print(f"Loaded {len(pages)} pages")

            return pages  #list of langchain documents
        
        except Exception as e:
            print(f"Error: {e}")

            raise
        

def chunk_document(pages, chunk_size= 500, chunk_overlap= 100):
        """ Split document into smaller chunks using fixed size chunking """

        splitter= RecursiveCharacterTextSplitter(
            chunk_size= chunk_size,
            chunk_overlap= chunk_overlap,
            length_function= lambda text: len(text.split()),
            separators= ["\n\n", "\n", " ", ""]
        )

        split_docs= splitter.split_documents(pages)

        print(f"split {len(pages)} into {len(split_docs)} chunks")

        return split_docs  #returns a list of chunks