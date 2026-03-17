import httpx
from langchain_core.tools import InjectedToolArg, tool
from markdownify import markdownify
from tavily import TavilyClient
from typing_extensions import Annotated, Literal

tavily_client = TavilyClient()

# Fetch and convert webpage content to markdown format
def fetch_webpage_content(url: str, timeout: float = 10.0) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return markdownify(response.text)
    except Exception as e:
        return f'Error fetching content from {url}:{str(e)}'

@tool(parse_docstring=False)
def tavily_search(
        query: str,
        max_results: Annotated[int, InjectedToolArg] = 1,
        topic: Annotated[
            Literal['general', 'news', 'finance'], InjectedToolArg
        ] = 'general',
) -> str:
    """
    Search the web using Tavily API.

    Args:
        query: The search query string.

    Returns:
        Search results as a string.
    """
    search_results = tavily_client.search(
        query,
        max_results=max_results,
        topic = topic
    )

    # Fetch full content for each URL
    result_texts = []
    for result in search_results.get('result', []):
        url = result['url']
        title = result['title']

        # Fetch webpage content
        content = fetch_webpage_content(url)
        res_text = f'''## {title}
**URL:** {url}

{content}

---
'''
        result_texts.append(res_text)
    # Format final response
    response = f'''  Found {len(result_texts)} results for '{query}':
{chr(10).join(result_texts)}'''
    return response

# Tool for strategic reflection on research progress and decision-making.
@tool(parse_docstring= False)
def think_tool(reflection: str) -> str:
    """
        Use this tool to think through reasoning steps.

        Args:
            reasoning: The thought process to analyze.

        Returns:
            None
        """
    return f'Reflection recorded: {reflection}'

