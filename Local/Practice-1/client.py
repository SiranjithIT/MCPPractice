# import asyncio
# from mcp import ClientSession
# from mcp.client.streamable_http import streamablehttp_client

# async def main():
#   async with streamablehttp_client("http://localhost:8000/mcp") as (
#     read_stream,
#     write_stream,
#     _,
#   ):
#     async with ClientSession(read_stream, write_stream) as session:
#       await session.initialize()
#       tools = await session.list_tools()
#       print(f"Available tools: {[tool.name for tool in tools.tools]}")

# if __name__ == "__main__":
#   asyncio.run(main())

import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
async def main():
  SERVER_URL = "http://127.0.0.1:8000/mcp"
  async with streamablehttp_client(SERVER_URL) as (read, write, _):
    async with ClientSession(read, write) as session:
      await session.initialize()
      tools = await load_mcp_tools(session)
      #print(tools)
      model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
      agent = create_react_agent(model, tools)
      weather_result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in Salem, India?"}]}
      )
      print("Weather result:", weather_result["messages"][-1].content)
      
asyncio.run(main())
