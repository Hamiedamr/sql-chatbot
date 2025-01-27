from langchain_ollama import ChatOllama

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import BaseOutputParser


class CommaSeparatedListOutputParser(BaseOutputParser):
    """Parse the output of an LLM call to a comma-separated list."""

    def parse(self, text: str):
        """Parse the output of an LLM call."""
        return text.strip().split(", ")


class GenerateByLLM:

    def __init__(self):
        self.chat_model = ChatOllama(model="llama3.1:8b", temperature=0, verbose=True)
        self.system_prompt = "You are an AI who give information from given data"
        self.system_prompt_query = (
            "You are an AI who create sql query based on the "
            "user question and database tables and fields"
        )

    def generate_query_by_llm(self, tables, columns, query):
        template = self.system_prompt_query + (
            "\ntables: {tables} column: {columns}\n\nonly write query no other extra text can check multiple "
            "fields for conditions but use 'or' never use 'and' if not mandatory and don't forget to use SELECT *"
        )
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_template = "{questions}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        chat_prompt.format_messages(tables=tables, columns=columns, questions=query)

        chain = chat_prompt | self.chat_model | CommaSeparatedListOutputParser()
        response = chain.invoke(dict(tables=tables, columns=columns, questions=query))
        return response[0]

    def get_table_based_on_query(self, tables, query):
        template = (
            "Get the table names for sql query based on given table and question only write table names so it "
            "can use for query database,\ntables: {tables}\n\nOnly response table name"
        )
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_template = "{questions}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        chat_prompt.format_messages(tables=tables, questions=query)

        chain = chat_prompt | self.chat_model | CommaSeparatedListOutputParser()
        response = chain.invoke(dict(tables=tables, questions=query))
        return response

    def get_column_based_on_query(self, columns, query):
        template = (
            "Get the column names for sql query based on given columns and question only write column names "
            "so it can use for query database\ncolumns: {columns}"
        )
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_template = "{questions}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        chat_prompt.format_messages(columns=columns, questions=query)

        chain = chat_prompt | self.chat_model | CommaSeparatedListOutputParser()
        response = chain.invoke(dict(columns=columns, questions=query))
        return response[0]
