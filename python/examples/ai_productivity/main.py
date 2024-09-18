import os
import dotenv
from openai import AzureOpenAI

from composio_openai import App, ComposioToolSet
from composio.utils.logging import get as get_logger

logger = get_logger(__name__)


# Load environment variables from .env
dotenv.load_dotenv()

# Initialize tools.
openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
composio_toolset = ComposioToolSet()

# Retrieve actions
# composio_toolset = ComposioToolSet(entity_id="Jessica")
actions = composio_toolset.get_tools(apps=[App.GITHUB])

# Setup openai assistant
assistant_instruction = (
    """You are an intelligent and proactive personal productivity assistant.
    Your primary tasks are:
    1. Regularly capture and analyze screenshots of the user's screen.
    2. Monitor user activity and provide timely, helpful interventions.

    Specific responsibilities:
    - Every few seconds, take a screenshot and analyze its content.
    - Compare recent screenshots to identify potential issues or patterns.
    - If you detect that the user is facing a technical or workflow problem:
        - Notify them with concise, actionable solutions.
        - Prioritize non-intrusive suggestions that can be quickly implemented.
    - If you notice extended use of potentially distracting websites or applications (e.g., social media, video streaming):
        - Gently remind the user about their productivity goals.
        - Suggest a brief break or a transition to a more focused task.
    - Maintain a balance between being helpful and not overly disruptive.
    - Tailor your interventions based on the time of day and the user's apparent work patterns.

    Operational instructions:
    - You will receive a 'CHECK' message at regular intervals. Upon receiving this:
        1. Take a screenshot using the screenshot tool.
        2. Then, analyse that screenshot using the image analyser tool.
        3. Then, check if the user is using distracting websites or applications.
        4. If they are, remind them to do something productive.
        5. If they are not, check if the user is facing a technical or workflow problem, based on previous history.
        6. If they are, notify them with concise, actionable solutions.
        7. Try to maintain history of the user's activity and notify them if they are doing something that is not right.

    Remember: Your goal is to enhance productivity while respecting the user's autonomy and work style."""
)

# Prepare assistant
assistant = openai_client.beta.assistants.create(
    name="Personal Productivity Assistant",
    instructions=assistant_instruction,
    model="gpt-4o",
    tools=actions,
)



# create a thread
thread = openai_client.beta.threads.create()
print("Thread ID: ", thread.id)
print("Assistant ID: ", assistant.id)

import time

def check_and_run_assistant():
    logger.info("Checking and running assistant")
    # Send 'CHECK' message to the assistant
    message = openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="CHECK",
    )

    # Execute Agent
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # logger.info(f"Run: {run}")

    # Execute function calls
    run_after_tool_calls = composio_toolset.wait_and_handle_assistant_tool_calls(
        client=openai_client,
        run=run,
        thread=thread,
    )

    # logger.info(f"Run after tool calls: {run_after_tool_calls}")

# Run the assistant check every 10 seconds
while True:
    check_and_run_assistant()
