from groq import Groq
from config import GROQ_API_KEY


class LLM:

    def __init__(self):

        self.client = Groq(
            api_key=GROQ_API_KEY
        )

    def generate(self, prompt):

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

        return response.choices[0].message.content