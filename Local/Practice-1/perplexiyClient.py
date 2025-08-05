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

async def main():
    perplexity_token = os.getenv("PERPLEXITY_API_KEY")
    
    if not perplexity_token:
      print("❌ Error: PERPLEXITY_TOKEN not found")
      return
    
    print("🚀 Starting Perplexity MCP server...")
    
    env = {**os.environ, "PERPLEXITY_API_KEY": perplexity_token}
    
    server_params = StdioServerParameters(
      command="npx",
      args=["-y", "server-perplexity-ask"],
      env=env
    )
    
    try:
      async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
          await session.initialize()
          print("✅ Connected to MCP server!")
          
          # Then try with LangChain agent
          print("\n🤖 Testing with LangChain agent...")
          mcp_tools = await load_mcp_tools(session)
          print(mcp_tools)
          
          if mcp_tools:
            model = ChatGoogleGenerativeAI(
              model="gemini-2.0-flash-exp",
              temperature=0
            )
            agent = create_react_agent(model, mcp_tools)
            result = await agent.ainvoke({
                        "messages": [{"role": "user", "content": "Search for current updates on USA Tariffs"}]
                    })
            print(result["messages"][-1].content)
    except Exception as e: 
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())