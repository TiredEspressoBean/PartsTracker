import json

import gradio as gr
from uuid import uuid4
import asyncio
from langgraph_sdk import get_client
import re

client = get_client(url="http://localhost:2024")

# --- Helpers ---
def format_think_tags(text):
    think_blocks = re.findall(r"<think>(.*?)</think>", text, re.DOTALL)
    for block in think_blocks:
        text = text.replace(f"<think>{block}</think>", f"**🧠 Thinking:**\n> {block.strip()}")
    return text

async def stream_langgraph_response(prompt, history):
    messages = history + [{"role": "user", "content": prompt}]
    assistant_response = ""
    has_yielded = False

    async for chunk in client.runs.stream(None, "agent", input={"messages": messages}):
        print(chunk)

        # Skip metadata and non-message events
        if chunk.event != 'values':
            continue

        latest_msg = chunk.data["messages"][-1]

        # Skip if it's echoing user input
        if latest_msg.get("type") == "human":
            continue

        # Handle AI response
        if latest_msg.get("type") == "ai":
            new_content = latest_msg.get("content", "")
            assistant_response += new_content
            formatted = format_think_tags(assistant_response)
            yield {"role": "assistant", "content": formatted}
            has_yielded = True

    # Fallback if nothing was yielded
    if not has_yielded:
        yield {"role": "assistant", "content": "⚠️ No response was returned from LangGraph."}


async def gradio_chat(messages, _, graph_state, uuid_state):
    if isinstance(messages, str):
        print("[DEBUG] Single string message detected")
        messages = [{"role": "user", "content": messages}]
    elif isinstance(messages, str) and messages.startswith("["):
        try:
            messages = json.loads(messages)
        except json.JSONDecodeError:
            messages = [{"role": "user", "content": messages}]

    if not messages:
        return

    print("Parsed messages:", messages)

    last_user_message = [m for m in messages if m["role"] == "user"][-1]["content"]
    prior_history = messages[:-1]

    async for assistant_message in stream_langgraph_response(last_user_message, prior_history):
        yield assistant_message, graph_state, uuid_state


def alpha(messages, _, graph_state, uuid_state):
    yield [  # echo user's message
        {"role": "assistant", "content": "Hello World"}], graph_state, uuid_state

# --- States ---
uuid_state = gr.BrowserState(uuid4, storage_key="uuid_state", secret="demo")
graph_state = gr.BrowserState(dict(), storage_key="graph_state", secret="demo")

# --- Launch as standalone ChatInterface ---
gr.ChatInterface(
    fn=gradio_chat,
    type='messages',
    title="LangGraph SDK Chat",
    description="Streaming assistant with tool feedback and thoughts.",
    chatbot=gr.Chatbot(type="messages", show_copy_button=True, height=350),
    textbox=gr.Textbox(
        placeholder="Ask about LangGraph or any connected tools...",
        show_label=False,
        submit_btn=True,
        stop_btn=True,
        lines=1,
        elem_id="chat-textbox",
    ),
).launch()
