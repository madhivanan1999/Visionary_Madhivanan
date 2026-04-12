import os
import json
import requests
from groq import Groq
from dotenv import load_dotenv

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MCP_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/call")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY is missing in the .env file.")

# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

# In-memory chat history
chat_memory = {}

# Maximum messages stored per user
MAX_HISTORY = 12


# --------------------------------------------------
# MCP TOOL CALLER
# --------------------------------------------------
def call_mcp_tool(tool_name: str, arguments: dict):
    """Call MCP server tools."""
    try:
        response = requests.post(
            MCP_URL,
            json={
                "tool": tool_name,
                "arguments": arguments
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("result", {})
    except Exception as e:
        return {"error": str(e)}


# --------------------------------------------------
# FETCH TASK DETAILS
# --------------------------------------------------
def get_current_task(telegram_id: str):
    """Fetch the currently assigned task."""
    result = call_mcp_tool(
        "fetch_pending_task",
        {"telegram_id": telegram_id}
    )
    if not result or "message" in result:
        return None
    return result


def get_completed_tasks(telegram_id: str):
    """
    Fetch completed tasks for revision.
    Requires MCP support. If unavailable,
    this function safely returns an empty list.
    """
    result = call_mcp_tool(
        "fetch_completed_tasks",
        {"telegram_id": telegram_id}
    )

    if isinstance(result, list):
        return result
    return []


# --------------------------------------------------
# SYSTEM PROMPT BUILDER
# --------------------------------------------------
def build_system_prompt(telegram_id: str) -> str:
    """Create a dynamic system prompt based on student tasks."""
    current_task = get_current_task(telegram_id)
    completed_tasks = get_completed_tasks(telegram_id)

    if not current_task:
        return (
            "You are an AI Tutor for a Smart Learning Bot. "
            "The student currently has no assigned task. "
            "Politely instruct them to use the /task command."
        )

    subject = current_task.get("subjects", "Unknown Subject")
    topic = current_task.get("topics", "Unknown Topic")
    module = current_task.get("module_no", "N/A")
    description = current_task.get("model_description", "N/A")

    completed_topics = [
        task.get("topics", "") for task in completed_tasks
    ]

    completed_text = (
        ", ".join(completed_topics)
        if completed_topics else "None"
    )

    return f"""
You are an AI Tutor for a Smart Learning Bot designed for students.

📘 CURRENT ASSIGNED TASK
Subject: {subject}
Topic: {topic}
Module: {module}
Description: {description}

📚 COMPLETED TOPICS FOR REVISION
{completed_text}

STRICT RULES:
1. Answer ONLY questions related to the CURRENT assigned topic.
2. Never ask the user to specify the topic if it is already assigned.

RESPONSE FORMAT:

📘 Simple Definition
- Provide a short and clear explanation in 2–3 sentences.

🔬 Technical Explanation
- Provide an academically accurate explanation.
- Include formulas and key concepts when applicable.

💡 Example
- Provide a practical or numerical example.

GUIDELINES:
- Keep responses concise and structured.
- Use simple English.
- Avoid unnecessary verbosity.
- Maintain continuity using previous messages.
"""


# --------------------------------------------------
# MEMORY MANAGEMENT
# --------------------------------------------------
def get_chat_history(telegram_id: str):
    """Retrieve or initialize chat history."""
    system_prompt = build_system_prompt(telegram_id)

    if telegram_id not in chat_memory:
        chat_memory[telegram_id] = [
            {"role": "system", "content": system_prompt}
        ]
    else:
        # Always refresh system prompt
        chat_memory[telegram_id][0] = {
            "role": "system",
            "content": system_prompt
        }

    return chat_memory[telegram_id]


def trim_chat_history(messages):
    """Limit chat history while preserving system prompt."""
    if len(messages) > MAX_HISTORY:
        return [messages[0]] + messages[-(MAX_HISTORY - 1):]
    return messages


# --------------------------------------------------
# NORMALIZE USER QUERY
# --------------------------------------------------
def normalize_user_query(user_message: str, telegram_id: str) -> str:
    """Convert vague queries into topic-aware questions."""
    task = get_current_task(telegram_id)
    if not task:
        return user_message

    topic = task.get("topics", "")
    vague_phrases = {
        "explain",
        "explain this",
        "teach me",
        "describe this",
        "what is this",
        "can you explain",
        "help me understand",
    }

    if user_message.strip().lower() in vague_phrases:
        return f"Explain {topic}"

    return user_message


# --------------------------------------------------
# GENERATE AI RESPONSE
# --------------------------------------------------
def generate_ai_response(user_message: str, telegram_id: str) -> str:
    """Generate AI response with memory and MCP tool calling."""

    # Normalize vague queries
    user_message = normalize_user_query(user_message, telegram_id)

    # Retrieve chat history
    messages = get_chat_history(telegram_id)

    # Add user message
    messages.append({"role": "user", "content": user_message})

    # MCP Tool Definitions
    tools = [
        {
            "type": "function",
            "function": {
                "name": "fetch_user",
                "description": "Fetch student details using telegram ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "telegram_id": {"type": "string"}
                    },
                    "required": ["telegram_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "fetch_pending_task",
                "description": "Fetch the student's current task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "telegram_id": {"type": "string"}
                    },
                    "required": ["telegram_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mark_task_complete",
                "description": "Mark a task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "telegram_id": {"type": "string"}
                    },
                    "required": ["telegram_id"],
                },
            },
        },
    ]

    try:
        # First LLM Call
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.4,
            max_tokens=600,
        )

        message = response.choices[0].message

        # Handle Tool Calls
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            tool_name = tool_call.function.name
            arguments = json.loads(
                tool_call.function.arguments or "{}"
            )

            arguments["telegram_id"] = telegram_id
            tool_result = call_mcp_tool(tool_name, arguments)

            messages.append({
                "role": "assistant",
                "tool_calls": message.tool_calls
            })

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result),
            })

            second_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.4,
                max_tokens=600,
            )

            final_response = second_response.choices[0].message.content
        else:
            final_response = message.content

        # Store assistant response
        messages.append(
            {"role": "assistant", "content": final_response}
        )

        # Trim history
        chat_memory[telegram_id] = trim_chat_history(messages)

        return final_response

    except Exception as e:
        return f"⚠️ AI service is temporarily unavailable.\nError: {str(e)}"


# --------------------------------------------------
# CLEAR CHAT HISTORY
# --------------------------------------------------
def clear_chat_history(telegram_id: str):
    """Clear chat history for a specific user."""
    if telegram_id in chat_memory:
        del chat_memory[telegram_id]