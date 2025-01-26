from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
class Answer:
    def __init__(self, llm):
        self.llm = llm
        """
        Configures GPT using LangChain with default parameters.
        """
        # Prompt templates for each category
        self.prompts = {
            2: ChatPromptTemplate.from_messages([
                HumanMessagePromptTemplate.from_template("""
                If the user asks a question or makes a comment unrelated to the table, categorized as small talk, respond professionally yet gently to create a friendly tone. If appropriate, ask the user to upload data.
                Examples:
                    - If the user comments on the weather or the day, respond kindly and ask if they have any questions and if they can upload the table.
                    - If the user shares their mood, empathize and remind them that the chatbot is always ready to assist with table-related queries.
                    - If the user asks about hobbies or unrelated topics, politely redirect back to the relevant topic.
                Here is {question}
                """)
            ]),
            4: ChatPromptTemplate.from_messages([
                HumanMessagePromptTemplate.from_template("""
                Understand the context of the question, the SQL query, and the result to determine the type of the answer and decide the answer.
    There are 5 types of answers:
            - Answer is True or False.
            - Answer is a number. For example: 9 or 12.52
            - Answer is a string. For example: Automotive
            - Answer is a list of numbers. For example: [48.0, 83.0]
            - Answer is a list of strings. For example: ['United States', 'China']
    Instructions:
        1. You will be provided with a question, an SQL query, and the result of executing the query.
        2. Analyze the result carefully to match the correct answer type based on the question. For example:
            - If the question asks for specific values (e.g., "What are the top 3 values of..."), focus on the numeric fields in the result.
            - If the question asks for names, titles, or descriptions (e.g., "Which professions..."), focus on the textual fields in the result.
            - If the question is about existence or verification (e.g., "Are there any..."), provide a Boolean answer (True/False).
        3. If the result contains a list of tuples, flatten it appropriately to match the expected type. For example:
            If the result contains duplicates (e.g., [('es',), ('es',), ('es',)]), return the full list (e.g., ['es', 'es', 'es']).
            Do not remove duplicates unless explicitly required by the question.
        4. If the result from the SQL Query is empty (e.g., None, [], or phrases like "Không có", "No data", "None"), decide the answer as follows:
            - If the question have negative words like 'no' ,'not',... then answer True
    Input:
        Question: {question}
        SQL Query: {sql_query}
        Result from SQL Query: {result}
    Output:
        Provide the answer that bases on one of the 5 types above. Yoi don't need to explain.
        The final answer must natural and friendly (repeat the question of user) base on the answer and the question. Use the question is context for answer.
        For example: "how many file in this row", the answer is 20, so the final answer is "There are 20 row in this file"
                """)
            ])
        }

    def answer_smalltalk(self, question: str, category: int) -> str:
        # Select the appropriate prompt template
        if category not in self.prompts:
            raise ValueError(f"Unsupported category: {category}")

        prompt_template = self.prompts[category]
        
        # Use LLMChain to process the query
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        return chain.run({"question": question})
    
    def answrer_embed(self, question: str, sql_query:str, result: str, category: int) -> str:
        # Select the appropriate prompt template
        if category not in self.prompts:
            raise ValueError(f"Unsupported category: {category}")

        prompt_template = self.prompts[category]
        
        # Use LLMChain to process the query
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        return chain.run({"question": question, "sql_query": sql_query,"result":result})