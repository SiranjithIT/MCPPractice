import asyncio
import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json

load_dotenv()
async def main():
  SERVER_URL = "http://127.0.0.1:8000/mcp"
  async with streamablehttp_client(SERVER_URL) as (read, write, _):
    async with ClientSession(read, write) as session:
      await session.initialize()
      tools = await load_mcp_tools(session)
      #print(tools)
      model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
      agent = create_react_agent(model, tools)
      weather_result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Generate a calculator code in C++ and execute it using the tool and give me the results along with the code. Give the inputs by yourself and test the code. Code and result are mandatory"}]}
      )
      print("Execution result:", weather_result["messages"][-1].content)

if __name__ == "__main__":
  asyncio.run(main())