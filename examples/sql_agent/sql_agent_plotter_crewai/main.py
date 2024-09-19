import os
from pathlib import Path

import dotenv
from composio_crewai import ComposioToolSet
from crewai import Agent, Crew, Task
from langchain_openai import ChatOpenAI

from composio import Action, App



llm = ChatOpenAI(model="gpt-4-turbo")

while True:
    main_task = input("Enter the task you want to perform (or type 'exit' to quit): ")
    if main_task.lower() == "exit":
        break

    code_interpreter_tools = ComposioToolSet(output_dir=Path.home() / "composio_output").get_tools(apps=[App.CODEINTERPRETER])
    sql_tools = ComposioToolSet(output_dir=Path.home() / "composio_output").get_tools(apps=[App.SQLTOOL])

    code_interpreter_agent = Agent(
        role="Python Code Interpreter Agent",
        goal=f"""Run I a code to get acheive a task given by the user""",
        backstory="""You are an agent that helps users run Python code.""",
        verbose=True,
        tools=code_interpreter_tools,
        llm=llm,
        memory=True,
    )

    code_interpreter_task = Task(
        description=f"""Run Python code to get acheive a task - {main_task}""",
        expected_output=f"""Python code executed successfully. The result of the task is returned - {main_task}""",
        agent=code_interpreter_agent,
    )

    sql_agent = Agent(
        role="SQL Agent",
        goal=f"""Run SQL queries to get acheive a task given by the user""",
        backstory=(
            "You are an agent that helps users run SQL queries. "
            "Connect to the local SQlite DB at connection string = company.db"
            "Try to analyze the tables first by listing all the tables and columns "
            "and doing distinct values for each column and once sure, make a query to get the data you need."
        ),
        verbose=True,
        tools=sql_tools,
        llm=llm,
        memory=True,
        allow_delegation=True,
    )

    sql_task = Task(
        description=f"""Run SQL queries to get acheive a task - {main_task}""",
        expected_output=f"""SQL queries executed successfully. The result of the task is returned - {main_task}""",
        agent=sql_agent,
    )

    crew = Crew(
        agents=[sql_agent, code_interpreter_agent],
        tasks=[sql_task, code_interpreter_task],
        memory=True,
        manager_agent=sql_agent,
        cache=False,
    )

    result = crew.kickoff()
    print(result)
