from groq import Groq
from config import GROQ_API_KEY


class LLM:

    def __init__(self):

        self.client = Groq(
            api_key=GROQ_API_KEY
        )

    def rewrite_query(
            self,
            query
    ):

        prompt = f"""
You are helping retrieve relevant code.
The repository contains ONLY Python code.
Expand the question into terms likely to appear in source code.

Include:
- filenames
- class names
- function names
- implementation concepts
- related programming terminology
- Never generate .java, .cpp, .cs, .js, etc.

Return a short search query only.

Question:
{query}
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        return (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

    def generate(
            self,
            prompt
    ):

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )

        return (
            response
            .choices[0]
            .message
            .content
        )