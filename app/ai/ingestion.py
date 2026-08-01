from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path

# the ingestion pipeline will first load the document and return a list of langchain pages for each document 
# and then split the documents into chunks

import re

_HEADING_PATTERNS = [
    re.compile(r'^\s*(round|track|session|day|phase|stage|part)\s*[\-:#]?\s*\d+', re.IGNORECASE),
    re.compile(r'^\s*\d+(\.\d+)*[\).]?\s+[A-Z]'),
    re.compile(r'^\s*#{1,6}\s+\S'),
    re.compile(r'^\s*[A-Z][A-Z0-9 &\-]{4,60}$'),
]

def _is_heading(line: str) -> bool:
    line = line.strip()
    if not line or len(line) > 80:
        return False
    return any(p.match(line) for p in _HEADING_PATTERNS)

def detect_sections(pages):
    document_id = pages[0].metadata.get("document_id")
    source_file = pages[0].metadata.get("source_file")
    file_type = pages[0].metadata.get("file_type")

    sections = []
    current_heading = "Document start"
    current_lines = []

    def flush():
        text = "\n".join(current_lines).strip()
        if text:
            sections.append({
                "heading": current_heading, "text": text,
                "document_id": document_id, "source_file": source_file, "file_type": file_type,
            })

    for page in pages:
        for line in page.page_content.split("\n"):
            if _is_heading(line):
                flush()
                current_heading = line.strip()
                current_lines = []
            else:
                current_lines.append(line)
    flush()
    return sections

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

        sections = detect_sections(pages)
        
        splitter= RecursiveCharacterTextSplitter(
            chunk_size= chunk_size,
            chunk_overlap= chunk_overlap,
            length_function= lambda text: len(text.split()),
            separators= ["\n\n", "\n", " ", ""]
        )

        split_docs = []
        
        for i, section in enumerate(sections):
            split_docs.extend(splitter.create_documents(
                texts=[section["text"]],
                metadatas=[{"document_id": section["document_id"], "source_file": section["source_file"],
                            "file_type": section["file_type"], "section_heading": section["heading"], "section_index": i}]
            ))
        return split_docs