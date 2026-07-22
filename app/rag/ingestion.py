from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

# the ingestion pipeline will first load the documents and return a list of langchain documents 
# and then split the documents into chunks

class IngestionPipeline:
    def load_all_documents(directory):
        documents=[]

        dir=Path(directory) # converting string to path

        pdf_files=[file for file in dir.glob("**/*.pdf")] # list of path of files
        print(f"{len(pdf_files)} PDFs to process")

        for pdf_file in pdf_files :
            print(f"Processing {pdf_file.name}")
            try:
                loader=PyMuPDFLoader(str(pdf_file)) # needed to convert path to string
                docs=loader.load()
                # changing metadata
                for doc in docs:
                    doc.metadata['source_file']=pdf_file.name
                    doc.metadata['file_type']="pdf"
                documents.extend(docs)
                print(f"Loaded {len(documents)} pages")
            except Exception as e:
                print(f"Error: {e}")
        
        print(f"Total PDF files loaded : {len(documents)}")
        return documents
    
    def chunk_documents(documents, chunk_size=500, chunk_overlap=100):
        """ Split document into smaller chunks """
        splitter=RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda text: len(text.split()),
            separators=["\n\n", "\n", " ", ""]
        )
        split_docs=splitter.split_documents(documents)
        print(f"split {len(documents)} into {len(split_docs)} chunks")

        return split_docs
        
