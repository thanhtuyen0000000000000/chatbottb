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
                Câu hỏi hiện tại {question}
                Nếu người dùng đưa ra câu hỏi hoặc bình luận không liên quan trực tiếp đến luật hôn nhân và gia đình, thuộc dạng giao tiếp thân thiện (small talk), hãy trả lời với giọng điệu chuyên nghiệp nhưng nhẹ nhàng, tạo cảm giác gần gũi. Nếu thích hợp, hãy hướng người dùng quay lại các vấn đề liên quan đến luật hôn nhân và gia đình mà họ quan tâm.
Ví dụ:

Nếu người dùng nhận xét về thời tiết hoặc ngày hôm nay, hãy đáp lại thân thiện và hỏi xem họ có câu hỏi gì liên quan đến luật mà cần được giải đáp.
Nếu người dùng chia sẻ tâm trạng, hãy đồng cảm và nhắc rằng chatbot luôn sẵn sàng hỗ trợ về các vấn đề luật pháp.
Nếu người dùng hỏi về sở thích hoặc điều không liên quan, hãy trả lời chung chung một cách lịch sự và nhẹ nhàng quay lại nội dung chuyên môn
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
        Provide the final answer that fits one of the 5 types above.
        If you cannot determine the answer, return "None".
        Do not explain your reasoning; only return the answer.
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


