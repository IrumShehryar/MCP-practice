import asyncio
import os
from contextlib import AsyncExitStack
from pathlib import Path

# GEMINI CODE - COMMENTED OUT FOR GROQ
# import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load .env from the script's directory
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# GEMINI CODE - COMMENTED OUT FOR GROQ
# GEMINI_MODEL = "gemini-2.0-flash"

# Groq model constant
GROQ_MODEL = "llama-3.3-70b-versatile"


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        
        # ANTHROPIC CODE - COMMENTED OUT FOR GEMINI
        # api_key = os.getenv("ANTHROPIC_API_KEY")
        # if not api_key:
        #     raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        # self.anthropic = Anthropic(api_key=api_key)
        
        # GEMINI CODE - COMMENTED OUT FOR GROQ
        # api_key = os.getenv("GOOGLE_API_KEY")
        # if not api_key:
        #     raise ValueError("GOOGLE_API_KEY environment variable not set")
        # genai.configure(api_key=api_key)
        # self.model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Groq setup
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.client = Groq(api_key=api_key)

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        if is_python:
            path = Path(server_script_path).resolve()
            server_params = StdioServerParameters(
                command="uv",
                args=["--directory", str(path.parent), "run", path.name],
                env=None,
            )
        else:
            server_params = StdioServerParameters(command="node", args=[server_script_path], env=None)

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Groq and available tools"""
        messages = [{"role": "user", "content": query}]

        response = await self.session.list_tools()
        
        # Convert MCP tools to Groq/OpenAI format
        def clean_schema(schema):
            """Remove unsupported fields from schema for Groq"""
            if not isinstance(schema, dict):
                return schema
            
            cleaned = {}
            allowed_fields = {"type", "properties", "required", "items", "description", "enum"}
            
            for key, value in schema.items():
                if key in allowed_fields:
                    if key == "properties" and isinstance(value, dict):
                        # Recursively clean properties
                        cleaned[key] = {k: clean_schema(v) for k, v in value.items()}
                    elif key == "items" and isinstance(value, dict):
                        # Recursively clean items
                        cleaned[key] = clean_schema(value)
                    else:
                        cleaned[key] = value
            
            return cleaned
        
        tools = []
        for tool in response.tools:
            # Clean the input schema
            input_schema = tool.inputSchema
            if isinstance(input_schema, dict):
                parameters = clean_schema(input_schema)
            else:
                parameters = {"type": "object", "properties": {}}
            
            groq_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": parameters
                }
            }
            tools.append(groq_tool)

        # Initial Groq API call
        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=tools if tools else None,
            tool_choice="auto" if tools else None
        )

        # Process response and handle tool calls
        final_text = []

        if response.choices[0].message.content:
            final_text.append(response.choices[0].message.content)
        
        # Check for tool calls in response
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                # Parse JSON arguments safely
                import json
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except (json.JSONDecodeError, AttributeError):
                    # Fallback if arguments aren't proper JSON
                    try:
                        tool_args = eval(tool_call.function.arguments)
                    except:
                        tool_args = {}
                
                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                if result.content:
                    final_text.append(result.content[0].text)

                # ANTHROPIC CODE - COMMENTED OUT FOR GEMINI
                # # Continue conversation with tool results
                # if hasattr(content, "text") and content.text:
                #     messages.append({"role": "assistant", "content": content.text})
                # messages.append({"role": "user", "content": result.content})

                # # Get next response from Claude
                # response = self.anthropic.messages.create(
                #     model=ANTHROPIC_MODEL,
                #     max_tokens=1000,
                #     messages=messages,
                # )

                # final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())