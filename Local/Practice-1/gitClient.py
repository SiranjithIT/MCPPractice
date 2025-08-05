# import asyncio
# import os
# from mcp.client.stdio import stdio_client
# from mcp import ClientSession
# from langchain_mcp_adapters.tools import load_mcp_tools
# from langgraph.prebuilt import create_react_agent
# from langchain_google_genai import ChatGoogleGenerativeAI
# from dotenv import load_dotenv

# load_dotenv()

# async def main():
#     # Your GitHub Personal Access Token
#     github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
#     if not github_token:
#         print("Error: GITHUB_PERSONAL_ACCESS_TOKEN not found in environment variables")
#         print("Please set it in your .env file or environment")
#         return
    
#     print("Starting GitHub MCP server...")
    
#     # Set up environment with GitHub token
#     env = {
#         **os.environ,  # Include existing environment variables
#         "GITHUB_PERSONAL_ACCESS_TOKEN": github_token
#     }
    
#     try:
#         # Import the correct parameter class
#         from mcp.client.stdio import StdioServerParameters
        
#         # Create server parameters object
#         server_params = StdioServerParameters(
#             command="npx",
#             args=["-y", "@modelcontextprotocol/server-github"],
#             env=env
#         )
        
#         # Connect to the local MCP server using stdio
#         async with stdio_client(server_params) as (read, write):
#             async with ClientSession(read, write) as session:
#                 print("Initializing session...")
#                 await session.initialize()
                
#                 print("✅ Connected to GitHub MCP server!")
                
#                 # List available tools
#                 tools_result = await session.list_tools()
#                 print(f"\n📋 Available tools ({len(tools_result.tools)}):")
#                 for tool in tools_result.tools:
#                     print(f"  • {tool.name}: {tool.description}")
                
#                 # List available resources (if any)
#                 try:
#                     resources_result = await session.list_resources()
#                     if resources_result.resources:
#                         print(f"\n📁 Available resources ({len(resources_result.resources)}):")
#                         for resource in resources_result.resources:
#                             print(f"  • {resource.name}: {resource.description}")
#                 except Exception as e:
#                     print(f"No resources available or error listing resources: {e}")
                
#                 # Load tools for LangChain integration
#                 print("\n🔧 Loading tools for LangChain...")
#                 mcp_tools = await load_mcp_tools(session)
#                 print(f"Loaded {len(mcp_tools)} tools for LangChain")
                
#                 # Example: Use the tools with a LangChain agent
#                 if mcp_tools:
#                     print("\n🤖 Creating agent with GitHub tools...")
#                     model = ChatGoogleGenerativeAI(
#                         model="gemini-2.5-flash",
#                         temperature=0
#                     )
#                     agent = create_react_agent(model, mcp_tools)
                    
#                     # Example query
#                     print("\n💬 Testing agent with a GitHub query...")
#                     result = await agent.ainvoke({
#                         "messages": [
#                             {
#                                 "role": "user", 
#                                 "content": "List any 5 public repositories of mine."
#                             }
#                         ]
#                     })
                    
#                     print("Agent response:")
#                     print(result["messages"][-1].content)
                
#     except Exception as e:
#         print(f"❌ Error connecting to MCP server: {e}")
#         print("\nTroubleshooting tips:")
#         print("1. Make sure Node.js is installed (npm/npx available)")
#         print("2. Check that GITHUB_PERSONAL_ACCESS_TOKEN is set correctly")
#         print("3. Verify your GitHub token has appropriate permissions")
#         print("4. Try running: npx -y @modelcontextprotocol/server-github --help")

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json

load_dotenv()

async def test_github_tools_directly(session):
    """Test GitHub tools directly without LangChain agent"""
    
    print("\n🔧 Testing GitHub tools directly...")
    
    try:
        # Test search_repositories with user-specific query
        print("1. Searching for your repositories...")
        
        # First, let's get your GitHub username
        user_result = await session.call_tool(
            "search_users", 
            arguments={"query": ""}  # This might help us get current user info
        )
        print(f"User search result: {user_result}")
        
    except Exception as e:
        print(f"Error testing tools directly: {e}")
    
    try:
        # Try searching repositories with different parameters
        print("\n2. Searching repositories with different criteria...")
        
        # Search for repositories sorted by updated (your recent ones should appear)
        repo_result = await session.call_tool(
            "search_repositories",
            arguments={
                "query": "user:@me",  # Try to search your own repos
                "sort": "updated",
                "order": "desc",
                "per_page": 10
            }
        )
        print("Repository search result:")
        for result in repo_result.content:
          print(result, end="\n\n")
        
    except Exception as e:
        print(f"Error searching repositories: {e}")
        
        # Try alternative approach
        try:
            print("\n3. Trying alternative repository search...")
            repo_result = await session.call_tool(
                "search_repositories",
                arguments={
                    "query": "is:public",
                    "sort": "updated", 
                    "order": "desc",
                    "per_page": 5
                }
            )
            print(f"Public repositories result: {repo_result}")
            
        except Exception as e2:
            print(f"Alternative search also failed: {e2}")

async def main():
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not github_token:
        print("❌ Error: GITHUB_PERSONAL_ACCESS_TOKEN not found")
        return
    
    print("🚀 Starting GitHub MCP server...")
    
    env = {**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": github_token}
    
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env=env
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connected to GitHub MCP server!")
                
                # Test tools directly first
                await test_github_tools_directly(session)
                
                # Then try with LangChain agent
                print("\n🤖 Testing with LangChain agent...")
                mcp_tools = await load_mcp_tools(session)
                
                if mcp_tools:
                    model = ChatGoogleGenerativeAI(
                        model="gemini-2.0-flash-exp",
                        temperature=0
                    )
                    agent = create_react_agent(model, mcp_tools)
                    
                    # More specific queries for your repositories
                    specific_queries = [
                        "Use the search_repositories tool to find repositories that I own. Search for repositories where I am the owner. My username is SiranjithIT",
                        "Get information about my GitHub profile and my repositories",
                        "Search for repositories I've created or contributed to recently",
                    ]
                    
                    for i, query in enumerate(specific_queries, 1):
                        print(f"\n💬 Agent Test {i}: {query}")
                        try:
                            result = await agent.ainvoke({
                                "messages": [{"role": "user", "content": query}]
                            })
                            
                            print("🤖 Agent response:")
                            print(result["messages"][-1].content)
                            print("-" * 60)
                            break  # Just run first query for now
                            
                        except Exception as e:
                            print(f"❌ Agent query {i} failed: {e}")
                
    except Exception as e: 
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())