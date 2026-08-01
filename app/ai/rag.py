from app.ai.prompts import PromptManager
import json

class RagPipeline():

    def __init__( self, retriever, llm):
        ''' Initialising retriever and llm'''
        self.retriever = retriever
        self.llm = llm

    def extract_outline(self, outline_text: str) -> list[dict]:
        if not outline_text:
            return []
        prompt = PromptManager.build_outline_prompt(outline_text=outline_text)
        response = self.llm.invoke(prompt)
        print (response)
        try:
            parsed = json.loads(response.content)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
        
    def extract_for_anchor(self, anchor: dict, context: str) -> dict:
        ''' Extracts one complete opportunity object for a single known anchor.
        Unlike extract_window, this expects exactly one opportunity, so
        json_object mode is safe here — no array/object mismatch, since we're
        genuinely asking for one object. '''
        prompt = PromptManager.extract_single_opportunity_prompt(anchor=anchor, context=context)
        response = self.llm.invoke(prompt, response_format={"type": "json_object"})
        print(response.response_metadata)
        try:
            parsed = json.loads(response.content)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    def extract_window( self, context, known_anchors, section_headings)-> list[dict]:
        ''' Returns a list of opportunities from a window
        Args: 
        context: the retrieved chunks from the vectordb
        '''
        prompt = PromptManager.extract_opportunity_prompt(context=context, known_anchors=known_anchors, section_headings=section_headings)

        response = self.llm.invoke(prompt)

        # get the number of tokens used for this response
        #print(response.response_metadata)

        try:
            parsed= json.loads(response.content)
            return parsed

        except json.JSONDecodeError:
            return []

    def query(self, query, top_k= 3):
        ''' Returns the response for a user query
        Args:
        query: User-written query to semantically search vectordb
        top_k: the top k retrieved results to compare with
        '''
        results = self.retriever.retrieve(query,top_k)

        if results:
            context = "\n\n".join( [doc['content'] for doc in results])
        else:

            context = ""

        if not context :
            return "No relevant context found"
        
        prompt = PromptManager.build_rag_prompt( query, context)

        response = self.llm.invoke( prompt)

        # get the number of tokens used for this response
        #print(response.response_metadata)

        response = response.content.replace("\n", " ")

        return {
            "answer": response
        }
