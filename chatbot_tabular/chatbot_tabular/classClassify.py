from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chains import LLMChain

class Classify:
    def __init__(self, llm):
        self.llm = llm
        """
        Configures GPT using LangChain with default parameters.
        """

        # Prompt for detecting small talk
        self.small_talk_prompt = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template("""
            Question: {question}
            Detect the language of the question. If it is not English, output "Not English", otherwise:
            Determine if this is a "small talk" question or not. 
            "Small talk" questions are unrelated to the primary topic of interest and include casual remarks . 
            Output:
            - "Small Talk" if the question is casual.
            - "Not Small Talk" otherwise.
            """)
        ])

        # Prompt for classifying questions with column or table context
        self.column_related_prompt = ChatPromptTemplate.from_messages([
            HumanMessagePromptTemplate.from_template("""
            Detect the language of the question. If it is not English, output "Not English", otherwise:
            Determine the classification of the question:
                - "Small Talk" if the question is casual or conversational, such as asking about the weather, mood, or general greetings.
                - "Related to Columns" if the question involves or references the provided columns or table context.
                - "Unrelated to Table" if the question is professional but does not relate to the provided columns or table context, e.g., questions about topics that do not pertain to the content in the uploaded table.
            Output the classification only.
            Here is Question: {question} _ Columns: {columns}
            """)
        ])

    def classify_small_talk(self, question: str) -> str:
        """
        Classify if the input question is small talk.
        """
        chain = LLMChain(llm=self.llm, prompt=self.small_talk_prompt)
        return chain.run({"question": question})

    def classify_column_related(self, question: str, columns: str) -> str:
        """
        Classify if the input question is:
        - Small Talk
        - Related to Columns
        - Unrelated to Table
        """
        chain = LLMChain(llm=self.llm, prompt=self.column_related_prompt)
        return chain.run({"question": question, "columns": columns})