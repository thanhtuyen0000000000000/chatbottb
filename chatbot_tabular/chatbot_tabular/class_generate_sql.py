from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv

class GenerateSQL:
    def __init__(self, llm):
        self.llm = llm
        # self.memory = ConversationBufferMemory(memory_key="history", input_key="query")
        self.prompt_template = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template(
                """
        The instruction:
        Ensure the query matches the focus of the question by:
        - The first line in columns is name table. Need to keep the name table in "".
        - Identifying the most relevant column(s) based on the question and columns(e.g., for "highest loan amount," use columns related to loan amounts).
        - If any column name matches a reserved keyword in SQLite (e.g: Transaction,...), ensure it is wrapped in double quotes ("") to avoid syntax errors.
        - If the question involves a list (e.g., 'list', 'name',...), use SELECT, ORDER BY, and LIMIT clauses appropriately, ensuring that numeric columns exclude rows with `None` or NULL values, don't use DISTINCT.
        - If the question involves ranking (e.g., 'top', 'highest', 'lowest',...), use SELECT, ORDER BY, and LIMIT clauses appropriately, ensuring that numeric columns exclude rows with `None` or NULL values, don't use DISTINCT.In cases where multiple results tie for the same rank:
            - Use additional criteria like "ROWID" or another column that preserves insertion order to prioritize the first occurrence.
        - Use the appropriate aggregate functions (e.g., COUNT, SUM,...) only if the question asks for totals or counts and do not use DISTINCT unless uniqueness is explicitly requested.
        - Use DISTINCT only if the question contains keywords like "different value", "unique", "distinct", or similar, indicating a need for uniqueness in the results. Otherwise, avoid using DISTINCT unless explicitly requested.
        - When calculating derived metrics (e.g., word counts), use appropriate expressions and ensure the logic is accurate (e.g., `LENGTH(text) - LENGTH(REPLACE(text, ' ', '')) + 1` for word count).
        - When comparing or filtering lists in a column (e.g., JSON or array-like fields), always explicitly filter out invalid values. Specifically:
            - Ensure conditions like `column = '[]' OR column IS NULL OR column = ''` are applied to exclude empty or invalid list-like values.
        - Ensure the SQL query reflects the context of the question and retrieves accurate results.
        Only provide the SQL query; do not include any explanations or additional text.
        Now let write an SQL query to answer the question: '{question}' based on the columns: '{data}'.
    """

            )
        ])

    def transform(self, question: str, columns: str) -> str:
        chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        result = chain.run({"question": question, "data": columns})
        return result