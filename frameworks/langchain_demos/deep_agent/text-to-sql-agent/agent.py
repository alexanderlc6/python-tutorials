import argparse
import os
import sys

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_classic.chat_models import init_chat_model
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from rich.console import Console
from rich.panel import Panel
from langchain_openai import ChatOpenAI, OpenAI

load_dotenv()

console = Console()

def create_sql_deep_agent():
    """Create and return a text-to-SQL Deep Agent"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(base_dir)
    db_path = os.path.join(base_dir, 'chinook.db')
    db = SQLDatabase.from_uri(f'sqlite:///{db_path}', sample_rows_in_table_info=3)

    # model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'), model='qwen-max',
    #                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

    model = init_chat_model(model='gpt-5.1', api_key=os.getenv('OPENAI_API_KEY'), base_url="https://api.chatanywhere.tech")

    # Create SQL toolkit and get tools
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    sql_tools = toolkit.get_tools()

    # Create the Deep Agent with all parameters
    agent = create_deep_agent(
        model=model,
        memory=['./AGENTS.md'],
        skills=[
            './skills/'
        ],
        tools=sql_tools,
        subagents=[],
        # Persistent file storage
        backend=FilesystemBackend(root_dir=base_dir)
    )
    return agent

def main():
    """Main entry point for the SQL Deep Agent CLI"""

    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(base_dir)

    parser = argparse.ArgumentParser(
        description='Text-to-SQL Deep Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python agent.py "What are the top 5 best-selling artists?"
  python agent.py "Which employee generated the most revenue by country?"
  python agent.py "How many customers are from Canada?"
        '''
    )
    parser.add_argument(
        'question',
        type=str,
        help='Natural language question to answer using the Chinook database'
    )

    args = parser.parse_args()

    # Display the question
    console.print(
        Panel(f'[bold cyan]Question:[/bold cyan] {args.question}', border_style='cyan')
    )
    console.print()

    console.print('[dim]Creating SQL Deep Agent...[/dim]')
    agent = create_sql_deep_agent()

    console.print('[dim]Processing query...[/dim]\n')

    try:
        result = agent.invoke(
            {'message': [{'role': 'user', 'content': {args.question}}]}
        )

        # Extract and display the final answer
        final_message = result['messages'][-1]
        answer = (
            final_message.content
            if hasattr(final_message, 'content')
            else str(final_message)
        )

        console.print(
            Panel(f'[bold green]Answer:[/bold green]\n\n {answer}', border_style='green')
        )
    except Exception as e:
        console.print(
            Panel(f'[bold red]Error:[/bold red]\n\n {e}', border_style='red')
        )
        sys.exit(1)

if __name__ == '__main__':
    main()
