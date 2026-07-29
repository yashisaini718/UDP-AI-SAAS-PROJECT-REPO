from app.ai.prompts import PromptManager
import json

class RagPipeline():

    def __init__( self, retriever, llm):
        ''' Initialising retriever and llm'''
        self.retriever = retriever
        self.llm = llm


    def extract_window( self, context)-> list[dict]:
        ''' Returns a list of opportunities from a window
        Args: 
        context: the retrieved chunks from the vectordb
        '''
        prompt = PromptManager.extract_opportunity_prompt(context=context)

        response = self.llm.invoke( prompt)

        # get the number of tokens used for this response
        print(response.response_metadata)

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
        print(response.response_metadata)

        return {
            "answer": response.content,
        }
