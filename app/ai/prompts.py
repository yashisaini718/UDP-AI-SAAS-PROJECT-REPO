import json

class PromptManager:
    
    @staticmethod
    def build_rag_prompt(query: str, context: str):
        template="""You are a helpful assistant.

        Answer the user's question using ONLY the provided context.

        If the answer is not present in the context, say:
        "I couldn't find that information in the provided documents."

        context: {context} 

        Question: {query}

        Answer: """
        return template.format(context=context, query=query)
    
    @staticmethod
    def extract_opportunity_prompt(context: str):
        template="""You are an expert information extraction system.

        Extract every distinct opportunity mentioned in the document.
        The same opportunity may appear in multiple sections of the document.
        Use the official title exactly as it appears in the document.
        Do not invent shorter or alternate titles.

        An opportunity can be:
        - Internship
        - Job
        - Scholarship
        - Funding
        - Hackathon
        - Competition
        - Research Program
        - Event
        - Workshop
        - Other

        Do NOT extract:
        - Sections of the same opportunity
        - Rounds of a competition
        - Timelines
        - Robot specifications
        - Judging criteria
        - Track characteristics
        - Instructions
        - Penalties

        If the document describes one competition with multiple rounds, return ONE opportunity for the competition.

        Rules:

        - Return ONLY a valid JSON array.
        - Do not include markdown, explanations, or extra text.
        - If no opportunity exists, return [].
        - Do not invent information.
        - Missing fields must be null.
        - Empty lists must be [].
        - Dates must use ISO format (YYYY-MM-DD).
        - If a date range is given (e.g. 10–13 April), use the last date as the deadline.
        - Infer the year only if it is obvious from the document.

        For each opportunity extract:

        {{
            "title": string,
            "summary": string,
            "organization": string | null,
            "category": "Internship" | "Job" | "Scholarship" | "Funding" | "Hackathon" | "Competition" | "Research" | "Event" | "Other",
            "priority": "High" | "Medium" | "Low",
            "description": string | null,
            "deadline": "YYYY-MM-DD" | null,
            "required_documents": [string],
            "action_items": [
                {{
                    "title": string,
                    "description": string,
                    "priority": "High" | "Medium" | "Low",
                    "due_date": "YYYY-MM-DD" | null
                }}
            ]
        }}

        Priority Rules:
        - High: deadline within 7 days, limited seats, mandatory submission, or immediate action.
        - Medium: deadline within one month or important opportunity.
        - Low: informational or no immediate deadline.

        Document:

        {context}
        """
        return template.format(context=context)
    