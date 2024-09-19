#!/bin/bash

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv ~/.venvs/scheduler_agent

# Activate the virtual environment
echo "Activating virtual environment..."
source ~/.venvs/scheduler_agent/bin/activate

# Install libraries from requirements.txt 
echo "Installing libraries from requirements.txt..."
pip install -r requirements.txt

# Login to your account
echo "Login to your Composio acount"
composio login

# Add trello tool
echo "Add google calendar and gmail tool. Finish the flow"
composio add googlecalendar
composio add gmail

echo "Enable trigger"
composio triggers enable gmail_new_gmail_message

# Copy env backup to .env file
if [ -f ".env.example" ]; then
    echo "Copying .env.example to .env..."
    cp .env.example .env
else
    echo "No .env.example file found. Creating a new .env file..."
    touch .env
fi

# Prompt user to fill the .env file
echo "Please fill in the .env file with the necessary environment variables."

echo "Setup completed successfully!"