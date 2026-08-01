import json

class PromptManager:

    @staticmethod
    def build_outline_prompt(outline_text: str):
        return f"""Identify the DISTINCT top-level opportunities in this document outline. Group rounds, tracks, phases, or sessions of one event under a single entry — do not list them separately.

            Return ONLY a JSON array: [{{"title": string, "category": string, "summary": string, "related_headings": [string]}}]
            If none, return [].

            Outline:
            {outline_text}
            """
    
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
    def extract_opportunity_prompt(context: str, known_anchors: list | None = None, section_headings: list | None = None):
        anchors = "; ".join(f'"{a.get("title")}"' for a in known_anchors) if known_anchors else "none yet"
        headings = ", ".join(section_headings) if section_headings else "unknown"

        template = """Determine how many opportunities are described. If multiple exist,extract each separately.
            If only one exists,extract only one. Do not infer new opportunities from section headings.
            Extract every DISTINCT opportunity (internship, job, scholarship, funding, hackathon, competition, research program, event, workshop) from the text below. Use each one's official title exactly as written — do not shorten or invent titles.

            Rounds, tracks, phases, days, or sub-sections of ONE event are the SAME opportunity, not separate ones. Do not extract timelines, specs, judging criteria, eligibility rules, or penalties as their own entries — fold eligibility into "description" instead.

            Known opportunities already found elsewhere in this document: {anchors}
            This text is from section(s): {headings}
            If this text is a round/track/session of a known opportunity above, reuse its exact title instead of creating a new one.

            Respond with a JSON array (empty array [] if none). Missing fields = null, empty lists = []. 
            Dates as YYYY-MM-DD; for a date range use the last date; infer the year only if obvious from the text.

            Each object:
            {{"title": str, "summary": str, "organization": str|null, "category": "Internship"|"Job"|"Scholarship"|"Funding"|"Hackathon"|"Competition"|"Research"|"Event"|"Other", 
            "priority": "High"|"Medium"|"Low", "description": str|null, "deadline": "YYYY-MM-DD"|null, "required_documents": [str], 
            "action_items": [{{"title": str, "description": str, "priority": "High"|"Medium"|"Low", "due_date": "YYYY-MM-DD"|null}}]}}

            Priority: High = deadline within 7 days, limited seats, or mandatory action. Medium = deadline within a month. Low = informational or no deadline.

            Text:
            {context}"""
        return template.format(context=context, anchors=anchors, headings=headings)
    

    @staticmethod
    def extract_single_opportunity_prompt(anchor: dict, context: str):
        title = anchor.get("title", "Unknown opportunity")
        category = anchor.get("category", "Other")

        return f"""Extract full structured details for ONE specific opportunity: "{title}" ({category}).

    The text below may include multiple rounds, tracks, or sections of this SAME opportunity — combine them into a single, complete record. Do not create separate entries for rounds/tracks/sessions.

    Respond with a single JSON object (not an array). Missing fields = null, empty lists = [].
    Dates as YYYY-MM-DD; for a date range use the last date; infer the year only if obvious from the text.

    Object shape:
    {{"title": "{title}", "summary": str, "organization": str|null, "category": "{category}", "priority": "High"|"Medium"|"Low", "description": str|null, "deadline": "YYYY-MM-DD"|null, "required_documents": [str], "action_items": [{{"title": str, "description": str, "priority": "High"|"Medium"|"Low", "due_date": "YYYY-MM-DD"|null}}]}}

    Priority: High = deadline within 7 days, limited seats, or mandatory action. Medium = deadline within a month. Low = informational or no deadline.

    Text (all sections belonging to "{title}"):
    {context}"""