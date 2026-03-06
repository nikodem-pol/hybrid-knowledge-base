from .base import BaseSQLGenerator

class LLMSQLGenerator(BaseSQLGenerator):

    def __init__(self, llm_adapter):
        self.llm = llm_adapter

    def generate_sql(self, question: str, schema: str) -> str:

        prompt = f"""
                        You are an expert SQL generator.

                        Given this database schema:

                        {schema}

                        Generate a SAFE SELECT SQL query for the following question:

                        Question: {question}

                        Rules:
                        - Only generate SELECT queries
                        - Do NOT generate DELETE, UPDATE, INSERT
                        - Do NOT explain
                        - Return ONLY SQL
                        - Return SQL in plain text not in markdown format
                        """

        response = self.llm.generate(prompt)
        return response.strip()