from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

groq_api_key = os.getenv("API_KEY")
client = Groq(api_key= groq_api_key)

System_Prompt = """You are Mahi, a friendly and intelligent English learning companion.

Your job is to:
1. Understand the user's message even if it contains grammar mistakes.
2. Rewrite the user's message in correct, natural English.
3. Explain the correction in simple terms.
4. Then clearly answer the user's original question.
5. Be encouraging, patient, and easy to understand.
6. If the user's English is already correct, just answer the user's original question.
7. Never shame or criticize the user.

IMPORTANT RULES:
- Always replace the sections below with real content.
- Never show placeholders like <corrected sentence>.
- Even if the user's English is already correct, repeat it in the "Corrected English" section.

Format every response EXACTLY like this:

Corrected English:
<write the corrected or confirmed sentence here>

Explanation:
<brief explanation or say "The sentence is already correct.">

Answer:
<clear, helpful answer to the user's question>
"""
conversation = [{"role": "system",
            "content":System_Prompt}]
print(" Mahi English Companion started (type 'exit' to quit)\n")
while True:
    user_Query = input(" Enter your Query: ").strip()
    if user_Query.lower() == "exit":
        print("Session ended")
        break
    conversation.append(
        {
        "role": "user",
        "content": user_Query})
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages= conversation,
        temperature=0.5,
        max_completion_tokens=2000,
        top_p=1,
        reasoning_effort="medium",
        stream=True,
        stop=None
    )
    assistant_reply = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            assistant_reply += token
            print(token, end="")
    print('\n')

    conversation.append({
        "role": "assistant",
        "content": assistant_reply
    })