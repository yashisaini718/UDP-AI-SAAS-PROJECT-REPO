
class PromptManager:
    
    @staticmethod
    def build_rag_prompt(query, context):
        template="""You are a helpful assistant.

        Answer the user's question using ONLY the provided context.

        If the answer is not present in the context, say:
        "I couldn't find that information in the provided documents."

        context: {context} 

        Question: {query}

        Answer: """
        return template.format(context=context, query=query)

