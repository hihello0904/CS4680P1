# OpenAI API Test File
# Uses gpt-5-mini model

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load prompt template
with open('investment_projection_prompt_monthly.txt', 'r', encoding='utf-8') as f:
    prompt_template = f.read()

# Define variables
monthly_contribution_amount = 500.00
risk_tolerance = "Average"
interests = "technology, healthcare, renewable energy"

# Replace variables in prompt
prompt = prompt_template.replace("{monthly_contribution_amount}", str(monthly_contribution_amount))
prompt = prompt.replace("{risk_tolerance}", risk_tolerance)
prompt = prompt.replace("{interests}", interests)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "user", "content": prompt}
    ],
)

print(f"Response: {response.choices[0].message.content}")