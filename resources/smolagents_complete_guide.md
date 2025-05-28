# A Complete Guide to smolagents

## Introduction

smolagents is a lightweight, powerful library for building AI agents that can solve complex tasks using code. Developed by Hugging Face, it offers a minimalist yet powerful approach to creating agents that "think in code" - generating and executing Python code to solve tasks and interact with tools.

The library is designed with several core principles:

- **Simplicity**: The logic fits in about 1,000 lines of code, keeping abstractions minimal
- **Code-First**: Unlike other agent frameworks that use JSON for tool calls, smolagents primarily uses a code-based approach which is more efficient and flexible
- **Model Agnostic**: Works with any LLM, whether local (transformers, ollama) or API-based (OpenAI, Anthropic, etc.)
- **Multimodal**: Supports text, vision, video, and audio inputs
- **Flexible Tooling**: Can use tools from various sources including LangChain, MCP, and Hugging Face Spaces
- **Hub Integration**: Easily share and load agents and tools to/from the Hugging Face Hub

## Installation

### Basic Installation

```bash
pip install smolagents
```

### Installation with Common Tools

```bash
pip install "smolagents[toolkit]"
```

### Other Installation Options

For specific needs, you can install various extra dependencies:

- **Model integration**: `pip install "smolagents[transformers]"` or `pip install "smolagents[openai]"` etc.
- **Multimodal capabilities**: `pip install "smolagents[vision]"` or `pip install "smolagents[audio]"`
- **Remote execution**: `pip install "smolagents[e2b]"` or `pip install "smolagents[docker]"`
- **Complete installation**: `pip install "smolagents[all]"`

## Core Concepts

### Agents

An agent in smolagents is a system that uses an LLM to interact with tools and solve tasks. The two main types are:

1. **CodeAgent**: Generates and executes Python code snippets as actions (recommended)
2. **ToolCallingAgent**: Uses JSON-like tool calling syntax (traditional approach)

### Tools

Tools are functions that agents can use to interact with the environment or perform specific tasks. Every tool has:

- **Name**: A descriptive identifier
- **Description**: Explanation of what the tool does
- **Input types and descriptions**: Parameters the tool accepts
- **Output type**: What the tool returns

### Models

Models are the LLMs that power the agent's reasoning. smolagents supports many model interfaces:

- **TransformersModel**: Local models using Hugging Face Transformers
- **InferenceClientModel**: Models from Inference API providers (Cerebras, Cohere, Fireworks, etc.)
- **LiteLLMModel**: Access to 100+ LLMs through LiteLLM
- **OpenAIServerModel**, **AzureOpenAIServerModel**, **AmazonBedrockServerModel**: Cloud provider models
- **MLXModel**: Apple MLX models

## Getting Started: Creating Your First Agent

### Basic Agent with Default Tools

```python
from smolagents import CodeAgent, InferenceClientModel

# Initialize model
model = InferenceClientModel(model_id="meta-llama/Llama-3.3-70B-Instruct")
# Or use default model: model = InferenceClientModel()

# Create agent with default tools
agent = CodeAgent(tools=[], model=model, add_base_tools=True)

# Run the agent
result = agent.run("What is the 118th number in the Fibonacci sequence?")
```

### Using a Local Model

```python
from smolagents import CodeAgent, TransformersModel

model = TransformersModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    max_new_tokens=4096,
    device_map="auto"
)

agent = CodeAgent(tools=[], model=model)
result = agent.run("What is the sum of the first 1000 prime numbers?")
```

### Using OpenAI, Anthropic, or Other API-based Models

```python
from smolagents import CodeAgent, LiteLLMModel
import os

model = LiteLLMModel(
    model_id="anthropic/claude-3-5-sonnet-latest",
    temperature=0.2,
    api_key=os.environ["ANTHROPIC_API_KEY"]
)

agent = CodeAgent(tools=[], model=model)
result = agent.run("Create a function to detect palindromes in a text file.")
```

## Working with Tools

### Using Built-in Tools

smolagents comes with several built-in tools when installed with the `toolkit` extra:

```python
from smolagents import WebSearchTool, CodeAgent, InferenceClientModel

# Initialize tools
search_tool = WebSearchTool()
# You can test tools directly
search_result = search_tool("What is the capital of France?")
print(search_result)

# Create agent with tools
agent = CodeAgent(
    tools=[search_tool],
    model=InferenceClientModel(),
    add_base_tools=True  # Adds default tools
)

result = agent.run("Who is the tallest NBA player in history?")
```

### Creating Custom Tools

#### Method 1: Using the @tool Decorator

```python
from smolagents import tool, CodeAgent, InferenceClientModel
from huggingface_hub import list_models

@tool
def model_download_tool(task: str) -> str:
    """
    Returns the most downloaded model of a given task on the Hugging Face Hub.

    Args:
        task: The task for which to get the most downloaded model.
    """
    most_downloaded_model = next(iter(list_models(filter=task, sort="downloads", direction=-1)))
    return most_downloaded_model.id

# Create agent with custom tool
agent = CodeAgent(tools=[model_download_tool], model=InferenceClientModel())
result = agent.run("What's the most popular text-to-image model on Hugging Face?")
```

#### Method 2: Subclassing Tool

```python
from smolagents import Tool, CodeAgent, InferenceClientModel
from typing import Optional, Dict, Any

class WeatherTool(Tool):
    name = "weather_tool"
    description = "Gets the current weather for a location"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        super().__init__()

    def forward(self, location: str) -> Dict[str, Any]:
        """
        Get the weather for a location.

        Args:
            location: City and country (e.g., "Paris, France")
        """
        # Implementation using weather API
        # For demo, returning mock data
        return {
            "location": location,
            "temperature": 22.5,
            "conditions": "Partly cloudy"
        }

# Create agent with custom tool class
weather_tool = WeatherTool(api_key="your_api_key")
agent = CodeAgent(tools=[weather_tool], model=InferenceClientModel())
```

## Secure Code Execution

Since CodeAgent executes LLM-generated Python code, security is an important consideration. smolagents provides several options for secure execution:

### Local Python Interpreter (Default)

By default, CodeAgent uses a secure local Python interpreter that:

- Only allows explicitly authorized imports
- Prevents access to protected submodules
- Limits operations count to prevent infinite loops
- Restricts available operations

```python
from smolagents import CodeAgent, InferenceClientModel

# Allow certain imports
agent = CodeAgent(
    tools=[],
    model=InferenceClientModel(),
    additional_authorized_imports=['pandas', 'numpy', 'matplotlib.pyplot']
)
```

### E2B Sandboxed Execution

For enhanced security, you can execute code in an E2B sandbox:

```python
from smolagents import CodeAgent, InferenceClientModel

# First set the E2B_API_KEY environment variable
# Install with: pip install "smolagents[e2b]"

agent = CodeAgent(
    tools=[],
    model=InferenceClientModel(),
    executor_type="e2b"
)
```

### Docker Sandboxed Execution

Alternatively, use Docker for sandboxed execution:

```python
from smolagents import CodeAgent, InferenceClientModel

# First install Docker and install with: pip install "smolagents[docker]"

agent = CodeAgent(
    tools=[],
    model=InferenceClientModel(),
    executor_type="docker"
)
```

## Multi-Agent Systems

For complex tasks, you can create hierarchical multi-agent systems where one agent delegates to others:

```python
from smolagents import CodeAgent, InferenceClientModel, WebSearchTool

model = InferenceClientModel()

# Create specialized agent for web search
web_agent = CodeAgent(
    tools=[WebSearchTool()],
    model=model,
    name="web_search",
    description="Runs web searches for you. Give it your query as an argument."
)

# Create manager agent that can delegate to web_agent
manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[web_agent]
)

result = manager_agent.run("Research the impact of climate change on coral reefs")
```

## Inspecting Agent Runs

To understand how your agent works and troubleshoot issues:

```python
# Run your agent
agent.run("Your task here")

# Check the logs
for step in agent.logs:
    print(f"Step {step['step_number']}:")
    print(f"Code executed: {step['code']}")
    print(f"Output: {step['output']}")
    print(f"Duration: {step['duration']} seconds")
    print("---")

# Get chat messages format
messages = agent.write_memory_to_messages()
for msg in messages:
    print(f"{msg['role']}: {msg['content']}")
```

## Advanced Features

### Running Agents with Additional Arguments

Pass images, files, or other data to your agent:

```python
agent.run(
    "Describe what's in this image",
    additional_args={
        "image_url": "https://example.com/image.jpg"
    }
)
```

### Adding Planning Steps

Improve agent performance with periodic planning steps:

```python
agent = CodeAgent(
    tools=[],
    model=InferenceClientModel(),
    planning_interval=3  # Add planning step every 3 normal steps
)
```

### Interactive UI with Gradio

Create an interactive UI for your agent:

```python
from smolagents import CodeAgent, InferenceClientModel, GradioUI

agent = CodeAgent(tools=[], model=InferenceClientModel())
GradioUI(agent).launch()
```

### Sharing and Loading Agents

Share your agent to the Hugging Face Hub:

```python
agent.push_to_hub("username/my-agent")
```

Load an agent from the Hub:

```python
from smolagents import from_hub

agent = from_hub("username/my-agent", trust_remote_code=True)
```

## Command Line Interface

smolagents provides command-line tools for quick agent usage:

```bash
# General purpose CodeAgent
smolagent "Plan a trip to Tokyo in March" --model-type "InferenceClientModel" --model-id "Qwen/Qwen2.5-Coder-32B-Instruct" --tools "web_search"

# Web browser agent
webagent "Find the price of the latest iPhone on apple.com" --model-type "LiteLLMModel" --model-id "gpt-4o"
```

## Best Practices for Building Effective Agents

### 1. Simplify Workflows

- Reduce the number of LLM calls and tool uses
- Combine multiple tools into single actions where possible
- Use deterministic functions rather than agentic decisions when appropriate

### 2. Improve Information Flow

- Write clear task descriptions
- Add extensive logging in tools
- Make error messages informative and actionable

### 3. Use Stronger Models for Complex Tasks

- For complex reasoning, use more capable models
- Consider using specialized models for specific subtasks

### 4. Create Clear Tool Descriptions

- Write comprehensive tool descriptions
- Provide examples of proper tool usage
- Include explicit format requirements for inputs

### 5. Debug Effectively

- Start with stronger models to isolate issues
- Add more guidance in task descriptions
- Use planning intervals for complex tasks
- Examine agent logs step by step

## Conclusion

smolagents provides a flexible, code-first approach to building AI agents that can solve a wide variety of tasks. By leveraging the power of Python code execution, these agents can perform complex operations, create compositional workflows, and interact with external systems.

Whether you're building a simple assistant or a sophisticated multi-agent system, smolagents offers the tools, security options, and integrations needed to create effective solutions. The library's focus on simplicity, flexibility, and security makes it an excellent choice for developing AI agents that can think in code.

For the latest features and updates, visit the [smolagents documentation](https://huggingface.co/docs/smolagents) or the [GitHub repository](https://github.com/huggingface/smolagents).
