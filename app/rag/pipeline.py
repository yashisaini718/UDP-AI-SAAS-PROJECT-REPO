from app.rag.prompts import PromptManager

class RagPipeline():
    def __init__(self, retriever, llm):
        self.retriever=retriever
        self.llm=llm
    
    def query(self, query, top_k=3):
        results=self.retriever.retrieve(query,top_k)
        if results:
            context="\n\n".join([doc['content'] for doc in results])
        else:
            context=""
        if not context:
            return "No relevant context found"
        prompt=PromptManager.build_rag_prompt(query,context)
        response= self.llm.invoke(prompt)
        return response.content