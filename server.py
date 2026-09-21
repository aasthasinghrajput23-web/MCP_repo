# server.py
# DEMO 1: "Under-the-Hood" Manual Flow — how an MCP Host (Inspector) and an
# MCP Server talk to each other without any LLM involved, and how the tools
# registry gets shared between them.

import httpx
from fastmcp import FastMCP

# Create a new, independent MCP server instance
mcp = FastMCP("Manual-Core-Server")


# TOOL 1: Free public temperature tool
@mcp.tool()
def get_temperature(city: str) -> str:
    """
    Use this tool to get the live temperature of any city.
    """
    try:
        # Build the request URL for the given city
        url = f"https://wttr.in/{city}?format=%t+%C"
        # Call the free wttr.in weather API
        response = httpx.get(url, timeout=10)
        if response.status_code == 200:
            return f"Live temperature in {city}: {response.text.strip()}"
        return f"Could not fetch temperature. Status code: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


# TOOL 2: Free public GitHub issue checker tool
@mcp.tool()
def fetch_public_issues(owner: str, repo: str) -> str:
    """
    Use this tool to view the open issues of any public GitHub repository.
    """
    try:
        # GitHub's REST API endpoint for a repo's open issues (top 3)
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page=3"
        # GitHub API requires a User-Agent header; Accept header selects the JSON format
        headers = {
            "User-Agent": "MCP-Manual-Demo",
            "Accept": "application/vnd.github+json",
        }
        response = httpx.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            issues = response.json()
            # NOTE: GitHub's issues API sometimes includes Pull Requests too
            # (they carry a "pull_request" key)
            if not issues:
                return f"No open issues found in {repo}."
            # Format the returned issues into a readable list
            result = f"--- Top open issues in {repo} ---\n"
            for issue in issues:
                result += f"• #{issue['number']}: {issue['title']}\n"
            return result
        return f"Could not connect to GitHub. Status: {response.status_code}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Starts the server on stdio transport so a client (like MCP Inspector)
# can connect to it and exchange JSON-RPC messages
if __name__ == "__main__":
    mcp.run()