import asyncio
import io
import sys
import warnings
from idlelib.rpc import response_queue
from pathlib import Path
from typing import Literal

import yaml
from PIL import Image
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from gradio import Markdown
from langchain_core.messages import ToolMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
import os

warnings.filterwarnings("ignore", message="Core Pydantic V1 functionality")

'''
Content Builder Agent

A content writer agent configured entirely through files on disk:
- AGENTS.md defines brand voice and style guide
- skills/ provides specialized workflows (blog posts, social media)
- skills/*/scripts/ provides tools bundled with each skill
- subagents handle research and other delegated tasks

Usage:
    uv run python content_writer.py "Write a blog post about AI agents"
    uv run python content_writer.py "Create a LinkedIn post about prompt engineering"
'''

EXAMPLE_DIR = Path(__file__).parent
console = Console()

# Web search tool for the researcher subagent
@tool
def web_search(
        query: str,
        max_results: int = 5,
        topic: Literal['general', 'news'] = 'general'
) -> dict:
    '''Search the web for current information'''
    try:
        from tavily import TavilyClient
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            return {'error':'TAVILY_API_KEY not set'}

        client = TavilyClient(api_key=api_key)
        return client.search(query, max_results=max_results, topic=topic)
    except Exception as e:
        return {'error': f'Search failed:{e}'}

@tool
def generate_cover(prompt: str, slug: str) -> str:
    '''Generate a cover image for a blog post.'''
    try:
        import dashscope
        # model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'), model='qwen-max',
        #            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        # response = dashscope.MultiModalConversation.call(
        #     model='qwen-vl-plus',
        #     messages=[{"role": "user", "content": [{'text': prompt}]}],
        ##     result_format='message'
        ## output = response.output.choices[0].message.content
        response = dashscope.ImageSynthesis.call(
            model='wanx-v1',
            prompt=prompt,
            n=1,
            size='1024x1024'
        )

        # if response.status_code == 200:
        if hasattr(response, 'output') and hasattr(response.output, 'results'):
            img_url = response.output.results[0].url

            import requests
            img_data = requests.get(img_url).content
            # Save image
            output_path = EXAMPLE_DIR / 'blogs' / slug / 'hello.png'
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(img_data)

            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))
            # Check validity and not corrupt
            # try:
            # img.verify()
            # except Exception as e:
                # print(f'Invalid image: {e}')
            # Format
            # if img.mode in ('RGBA', 'P'):
            #     img = img.convert('RGB')
            # Image resize
            # img = img.resize((800, 600))
            # Compress image
            # img.save(output_path, "JPEG", quality=85, optimize=True)
            # Convert image format
            # img.save(output_path, "PNG")

            return f'Image saved to {output_path}'
        # Adapt for other LLM models
        elif hasattr(response, 'output') and 'b64_image' in str(response.output):
            import base64
            b64_data = response.output.b64_image
            img_data = base64.b64decode(b64_data)
            # Save image(slug define for image dir: "What Are the Top 5 Best-Selling Artists?" -> "top-5-best-selling-artists")
            output_path = EXAMPLE_DIR / 'blogs' / slug / 'hello.png'
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(img_data)
            return f'Image saved to {output_path}'
        else:
            raise Exception(f'Image generation failed: {response.message}')

        return 'No image generated.'
    except Exception as e:
        return f'Error: {e}'

@tool
def generate_social_image(prompt: str, platform: str, slug: str) -> str:
    '''Generate an image for a social media post.'''
    try:
        import dashscope
        # model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'), model='qwen-max',
        #            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
        # response = dashscope.MultiModalConversation.call(
        #     model='qwen-vl-plus',
        #     messages=[{"role": "user", "content": [{'text': prompt}]}],
        ##     result_format='message'
        ## output = response.output.choices[0].message.content
        response = dashscope.ImageSynthesis.call(
            model='wanx-v1',
            prompt=prompt,
            n=1,
            size='1024x1024'
        )

        # if response.status_code == 200:
        if hasattr(response, 'output') and hasattr(response.output, 'results'):
            img_url = response.output.results[0].url

            import requests
            img_data = requests.get(img_url).content
            # Save image
            output_path = EXAMPLE_DIR / 'blogs' / slug / 'hello.png'
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(img_data)

            return f'Image saved to {output_path}'
        # Adapt for other LLM models
        elif hasattr(response, 'output') and 'b64_image' in str(response.output):
            import base64
            b64_data = response.output.b64_image
            img_data = base64.b64decode(b64_data)
            # Save image(slug define for image dir: "What Are the Top 5 Best-Selling Artists?" -> "top-5-best-selling-artists")
            output_path = EXAMPLE_DIR / platform / slug / 'hello.png'
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(img_data)
            return f'Image saved to {output_path}'
        else:
            raise Exception(f'Image generation failed: {response.message}')

        return 'No image generated.'
    except Exception as e:
        return f'Error: {e}'

def load_subagents(config_path: Path) -> list:
    '''Load subagent definitions from YAML and wire up tools.'''
    # Map tool names to actual tool objects
    available_tools = {
        'web_search': web_search
    }

    with open(config_path) as f:
        config = yaml.safe_load(f)

    subagents = []
    for name,spec in config.items():
        subagent = {
            'name': name,
            'description': spec['description'],
            'system_prompt': spec['system_prompt']
        }

        if 'model' in spec:
            subagent['model'] = spec['model']
        if 'tool' in spec:
            subagent['tools'] = [available_tools[tool] for tool in spec['tools']]
        subagents.append(subagent)

    return subagents


def create_content_writer():
    """Create a content writer agent configured by filesystem files."""
    return create_deep_agent(
        memory=["./AGENTS.md"],           # Loaded by MemoryMiddleware
        skills=["./skills/"],             # Loaded by SkillsMiddleware
        tools=[generate_cover, generate_social_image],  # Image generation
        subagents=load_subagents(EXAMPLE_DIR / "subagents.yaml"),  # Custom helper
        backend=FilesystemBackend(root_dir=EXAMPLE_DIR),
    )


class AgentDisplay:
    """Manages the display of agent progress."""

    def __init__(self):
        self.printed_count = 0
        self.current_status = ""
        self.spinner = Spinner("dots", text="Thinking...")

    def update_status(self, status: str):
        self.current_status = status
        self.spinner = Spinner("dots", text=status)

    def print_message(self, msg):
        """Print a message with nice formatting."""
        if isinstance(msg, HumanMessage):
            console.print(Panel(str(msg.content), title="You", border_style="blue"))

        elif isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, list):
                text_parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
                content = "\n".join(text_parts)

            if content and content.strip():
                console.print(Panel(Markdown(content), title="Agent", border_style="green"))

            if msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.get("name", "unknown")
                    args = tc.get("args", {})

                    if name == "task":
                        desc = args.get("description", "researching...")
                        console.print(f"  [bold magenta]>> Researching:[/] {desc[:60]}...")
                        self.update_status(f"Researching: {desc[:40]}...")
                    elif name in ("generate_cover", "generate_social_image"):
                        console.print(f"  [bold cyan]>> Generating image...[/]")
                        self.update_status("Generating image...")
                    elif name == "write_file":
                        path = args.get("file_path", "file")
                        console.print(f"  [bold yellow]>> Writing:[/] {path}")
                    elif name == "web_search":
                        query = args.get("query", "")
                        console.print(f"  [bold blue]>> Searching:[/] {query[:50]}...")
                        self.update_status(f"Searching: {query[:30]}...")

        elif isinstance(msg, ToolMessage):
            name = getattr(msg, "name", "")
            if name in ("generate_cover", "generate_social_image"):
                if "saved" in msg.content.lower():
                    console.print(f"  [green]✓ Image saved[/]")
                else:
                    console.print(f"  [red]✗ Image failed: {msg.content}[/]")
            elif name == "write_file":
                console.print(f"  [green]✓ File written[/]")
            elif name == "task":
                console.print(f"  [green]✓ Research complete[/]")
            elif name == "web_search":
                if "error" not in msg.content.lower():
                    console.print(f"  [green]✓ Found results[/]")


async def main():
    """Run the content writer agent with streaming output."""
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "Write a blog post about how AI agents are transforming software development"

    console.print()
    console.print("[bold blue]Content Builder Agent[/]")
    console.print(f"[dim]Task: {task}[/]")
    console.print()

    agent = create_content_writer()
    display = AgentDisplay()

    console.print()

    # Use Live display for spinner during waiting periods
    with Live(display.spinner, console=console, refresh_per_second=10, transient=True) as live:
        async for chunk in agent.astream(
            {"messages": [("user", task)]},
            config={"configurable": {"thread_id": "content-writer-demo"}},
            stream_mode="values",
        ):
            if "messages" in chunk:
                messages = chunk["messages"]
                if len(messages) > display.printed_count:
                    # Temporarily stop spinner to print
                    live.stop()
                    for msg in messages[display.printed_count:]:
                        display.print_message(msg)
                    display.printed_count = len(messages)
                    # Resume spinner
                    live.start()
                    live.update(display.spinner)

    console.print()
    console.print("[bold green]✓ Done![/]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/]")
