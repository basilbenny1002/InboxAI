import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define available tools/functions
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_unread_emails_summary",
            "description": "Get summaries of all unread emails in the inbox",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_last_email_summary",
            "description": "Get summary of the most recent/last unread email",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_unread_email_categories",
            "description": "Get categories for all unread emails",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_emails_from_sender",
            "description": "Check how many unread emails are from a specific sender (e.g., GitHub, Google, LinkedIn)",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender_query": {
                        "type": "string",
                        "description": "Sender name or keyword to search for"
                    }
                },
                "required": ["sender_query"]
            }
        }
    }
]

def call_llm(prompt: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert email summarizer. Summarize emails concisely in 2-3 sentences, mentioning key points from both the email body and any attachments."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

def intelligent_command_handler(user_message: str, function_map: dict) -> dict:
    """
    Intelligent command handler using function calling
    
    Args:
        user_message: The user's input
        function_map: Dictionary mapping function names to actual Python functions
        
    Returns:
        dict with "reply" and optionally "data" keys
    """
    
    messages = [
        {
            "role": "system",
            "content": """You are InboxAI, a friendly and helpful email assistant. 

When users greet you (hello, hi, hey, etc.), respond warmly and naturally.
When users ask about their emails, use the appropriate function to help them.
Keep responses conversational and natural - don't be robotic.

Examples:
- "hello" → Greet them back warmly
- "what's my last email?" → Use get_last_email_summary
- "show unread emails" → Use get_unread_emails_summary
- If the user asks about categories, labels, types, or classification of emails,
use get_unread_email_categories.
- If the user asks whether they have emails from a specific sender
(e.g., "GitHub", "Google", "LinkedIn", "from X"),
use check_emails_from_sender with the sender name as parameter.
- "summarize my inbox" → Use get_unread_emails_summary"""
        },
        {
            "role": "user",
            "content": user_message
        }
    ]
    
    # First API call - let Groq decide what to do
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=500,
        temperature=0.7
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # If no function call needed (e.g., just saying hello), return conversational response
    if not tool_calls:
        return {
            "reply": response_message.content or "I'm here to help with your emails!"
        }
    
    # Execute the function calls
    messages.append(response_message)
    
    function_results = []
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
        
        # Call the actual Python function
        if function_name in function_map:
            # Pass arguments if the function expects them
            if function_args:
                function_response = function_map[function_name](**function_args)
            else:
                function_response = function_map[function_name]()
                
            function_results.append({
                "name": function_name,
                "result": function_response
            })
            
            # Add function response to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(function_response)
            })
    
    # Second API call - let Groq format the response naturally
    final_response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    final_content = final_response.choices[0].message.content
    
    # Return in the format expected by main.py
    if function_results:
        first_result = function_results[0]["result"]
        
        # If the function already returned proper format with "reply" key, use it
        if isinstance(first_result, dict) and "reply" in first_result:
            return first_result
        
        # Otherwise, wrap the LLM's response
        return {
            "reply": final_content,
            "data": first_result if isinstance(first_result, dict) else {}
        }
    
    return {
        "reply": final_content
    }