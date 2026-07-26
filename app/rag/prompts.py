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
    def extract_json_prompt(text: str):
        template="""
    You are an expert information extraction system.

    Your task is to analyze the following text and extract all useful structured information.

    IMPORTANT INSTRUCTIONS

    1. Read the entire text before extracting information.
    2. Extract only information that is explicitly present or can be reasonably inferred.
    3. Do NOT invent facts, dates, company names, deadlines, or requirements.
    4. If a field is not present, return null.
    5. If a list has no items, return an empty list [].
    6. Return ONLY valid JSON.
    7. Do not include explanations, markdown, or extra text.

    Return ONLY valid JSON.
    Do not include:
    - ```json
    - ```
    - Any explanation
    - Any text before or after the JSON.

    Your response must start with {{ and end with }}.

    Extract the following fields:

    - title
        The main title of the opportunity, event, funding program, internship, job, scholarship, hackathon, competition, or document.

    - summary
        A concise summary (2 to 4 sentences) describing the opportunity along with the organising body.

    - category
        One of:
        Internship
        Job
        Funding
        Scholarship
        Hackathon
        Competition
        Research
        Event
        Other

    - priority
        High, Medium, or Low.

    Determine priority using these guidelines:

    High:
    - Deadline within 7 days
    - Limited seats
    - Immediate action required
    - Mandatory submission

    Medium:
    - Deadline within one month
    - Important opportunity

    Low:
    - No immediate deadline
    - General informational content

    - description
        Detailed description if available. Also include the eligiblity for the opportunity.

    - deadline
        Extract every application deadline or submission deadline.
        If a deadline exists:
        - Return it in ISO 8601 format (YYYY-MM-DD).
        - If the document contains a date range (e.g. "10 to 13 April"), return the LAST date as the deadline.
        - If the year is not mentioned, infer it from the document if possible; otherwise use null.
        - If no deadline exists, return null.

    - required_documents
        Extract every required document.
    Example:
    [
        "Resume",
        "Transcript",
        "Passport Photo",
        "Recommendation Letter"
    ]

    - action_items
        Generate actionable tasks from the text.
        Each task should be short and executable.
    Example:
    [
    {{
    "title": "Update Resume",
    "description": "Update the resume according to the eligibility criteria.",
    "priority": "High",
    "due_date": null
    }},
    {{
        "task": "Fill Application Form",
        "description": "Fill the required form",
        "priority": "High",
         "due_date": null
    }}
    ]

    Expected Output Format

    {{
    "title": "...",
    "summary": "...",
    "organization": "...",
    "category": "...",
    "priority": "...",
    "description": "...",
    "deadline": null,
    "required_documents": [],
    "action_items": [],
    }}

    TEXT TO ANALYZE
    {text}
    """
        return template.format(text=text)