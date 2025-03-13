Got it! I'll design a meta-prompt that takes a project or task description as input, decomposes it into a structured series of steps, and outputs a JSON schema compatible with the OpenAI Agents SDK. This schema will dynamically generate custom agents, their tools, handoff structures, output types, and any nested dependencies. The meta-prompt will also include clarifying follow-up questions when necessary to resolve ambiguity or edge cases.

I'll also provide a Python script that parses the structured output into OpenAI Agent SDK format, ensuring it can be directly used for agent orchestration.

I'll notify you once the meta-prompt and the corresponding Python parser are ready!

# Multi-Agent Workflow Meta-Prompt Design and Parser Script

## Meta-Prompt Overview

The meta-prompt is designed to take a high-level project or task description and generate a **structured plan** for a multi-agent workflow. It guides the model to break the task into components, assign dedicated AI agents with specific roles and tools, and outline how these agents will collaborate. The output is a JSON configuration compatible with the OpenAI Agents SDK, which can be directly used in a function-calling agent system. Key aspects of this meta-prompt include:

1. **Task Decomposition** – It instructs the model to break down the input project description into smaller, manageable sub-tasks or steps that individual agents can handle. Each step should represent a clear objective or unit of work derived from the overall project.

2. **Agent Role Assignment & Instructions** – For each sub-task, the prompt ensures an agent is created with a specific role and purpose. Each agent is essentially an LLM with its own instructions (a custom prompt defining its behavior) ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=,to%20agents%20to%20be%20validated)). For example, one agent might be a “Researcher” focused on data gathering, while another is a “Planner” or “Developer” focused on execution. The meta-prompt asks the model to provide a concise role description and custom instructions for each agent so they stay focused on their given task.

3. **Tool Allocation per Agent** – The prompt directs the model to assign relevant tools to each agent based on the sub-task requirements. In the Agents SDK, agents can be equipped with tools (functions they can call) to aid in their tasks ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=,to%20agents%20to%20be%20validated)) ([GitHub - openai/openai-agents-python: A lightweight, powerful framework for multi-agent workflows](https://github.com/openai/openai-agents-python#:~:text=%40function_tool%20def%20get_weather%28city%3A%20str%29%20,city%7D%20is%20sunny)). For instance, a research agent might get a `web_search` tool, or a calculation agent might get a `calculator` tool. The meta-prompt will have the model list any such tools (by name or function) under each agent, along with possibly a brief description of what the tool does. This ensures each agent has the capabilities needed to complete its step.

4. **Handoff Structure Definition** – To enable multi-agent collaboration, the prompt instructs the model to define **handoffs** between agents ([OpenAI Agents SDK](https://openai.github.io/openai-agents-python/#:~:text=,to%20agents%20to%20be%20validated)) ([GitHub - openai/openai-agents-python: A lightweight, powerful framework for multi-agent workflows](https://github.com/openai/openai-agents-python#:~:text=triage_agent%20%3D%20Agent%28%20name%3D,handoffs%3D%5Bspanish_agent%2C%20english_agent%5D%2C)). Handoffs determine how control or data passes from one agent to another. For example, after the “Researcher” agent finishes gathering information, it might hand off to the “Planner” agent to use that information. The meta-prompt will produce a structure (e.g., a sequence or a set of conditions) that specifies the order of execution or the conditions under which one agent delegates to another. This could be as simple as a linear sequence (Agent A → Agent B → Agent C) or a conditional branch (Agent Triage delegates to Agent X or Y based on context). The JSON output will capture these relationships clearly (e.g., an agent may include a list of agents it can hand off to, or a separate workflow map is provided).

5. **Output Format Specifications** – The prompt requires the model to specify the expected output format for each step or agent’s result. This means for each agent, defining what form its output should take (for example, “a summary text of findings”, “a JSON object with certain fields”, “Python code”, etc.). In the Agents SDK, this correlates with setting an `output_type` or schema for the agent, which forces the LLM to produce a structured output matching that schema ([GitHub - openai/openai-agents-python: A lightweight, powerful framework for multi-agent workflows](https://github.com/openai/openai-agents-python#:~:text=Final%20output%20is%20the%20last,agent%20produces%20in%20the%20loop)). By specifying output formats, we ensure that each agent’s output can be easily consumed by the next agent (or by the final user) and that the overall workflow meets the expected deliverables. If needed, the meta-prompt can include a schema or format description for these outputs (for instance, requiring a JSON with specific keys for an agent that outputs data).

6. **Clarification Handling** – The meta-prompt is proactive about ambiguity. It guides the model to detect if the project description is underspecified or has potential edge cases that need clarification. If ambiguities are found, the model is instructed to output clarifying questions instead of (or in addition to) a final plan. This mechanism ensures that the workflow is not built on incorrect assumptions. In practice, the meta-prompt might produce a JSON field like `"clarifying_questions"` with a list of questions whenever it feels the input is unclear. The developer or user can then answer these questions and rerun the planning prompt with the additional details. This step helps resolve uncertainties before agents are instantiated.

7. **Structured JSON Output** – The final answer from the meta-prompt is formatted as a **single JSON object** that encapsulates the entire multi-agent workflow configuration. All agents, their roles, tools, handoff logic, and output requirements are organized in this JSON. Structuring the output in JSON (a machine-readable format) ensures compatibility with the OpenAI function-calling system and the Agents SDK, which expects structured definitions for agents and tools. The meta-prompt explicitly instructs the model to produce valid JSON with the appropriate nesting (arrays, objects, fields for each aspect of the plan) and to quote all strings properly. This structured output can be directly parsed by a program to instantiate the agents.

8. **Extensibility and Nesting** – The prompt allows for additional custom structure or nesting in the JSON if required by the task. Complex projects might need grouping of sub-tasks or conditional sub-flows; the meta-prompt does not forbid nested arrays/objects (for example, a step might have sub-steps, or an agent might manage a small internal sequence). It’s designed to be flexible: the model can introduce additional keys or nested sections as long as the JSON remains valid and true to the task requirements. This ensures that even if the workflow has a non-trivial structure, it can be represented completely in the output JSON.

By covering the points above, the meta-prompt helps generate a robust multi-agent blueprint. The resulting JSON will list all agents (with their configuration), define how they interact via handoffs, outline the expected outputs at each stage, and flag any missing information. This JSON can then be consumed by an OpenAI Agents SDK runner or a custom orchestrator to actually create and run the agents.

## Meta-Prompt Template

Below is an example meta-prompt template that incorporates all the requirements. This prompt would be given to the language model (ChatGPT or similar) along with the project description to produce the structured workflow JSON:

````text
[System: You are an AI developer assistant that designs multi-agent workflows.]

You will receive a **project description** from a user. Based on this description, you must produce a **JSON configuration** for a multi-agent AI workflow that can accomplish the task using OpenAI’s Agents SDK.

**Requirements for the workflow design**:
- **Step Breakdown**: Break the project into clear sub-tasks or steps.
- **Agents**: For each sub-task, create an agent with a descriptive **name** and **role**. Give each agent a set of **instructions** (as a system prompt) focusing on its task.
- **Tools**: Assign relevant **tools** to agents if needed (e.g., web search, code execution, calculation). List the tools an agent should use to complete its task. If no tools are needed for an agent, you can omit the tools list or leave it empty.
- **Handoffs**: Define how agents will collaborate. If one agent’s output is needed by another, specify a handoff. For example, if Agent A should pass its results to Agent B, indicate that relationship. Use handoffs for conditional delegation as well (e.g., a decision agent routes to different agents based on context).
- **Output Formats**: For each agent or step, specify the expected **output format** or schema. For example, an agent might output a JSON summary, or a piece of text, or code. This ensures each agent’s output is well-defined and can be used by subsequent agents.
- **Clarifications**: If the project description is ambiguous or missing crucial information, identify those gaps. **Before** finalizing the agent plan, list any **clarifying_questions** you would ask the user in order to proceed. (If there are clarifying questions, the JSON output should include them and you may hold off on providing the full agent list until answers are given.)

**Output Format**:
Provide the workflow plan as a **JSON object** with the following structure and fields:
```json
{
  "clarifying_questions": [
    /* If any ambiguities are detected, list your clarifying questions here as strings.
       If this field is present, you might omit the rest of the structure pending answers. */
  ],
  "entry_agent": "<name of the agent that should start the workflow>",

  "agents": [
    {
      "name": "<Agent Identifier or Name>",
      "role": "<Short description of the agent's role>",
      "instructions": "<Detailed instructions for this agent (system prompt)>",
      "tools": [
        /* list of tool names or identifiers this agent can use, e.g. "web_search", "python_repl".
           Include only the tool names (the implementation will be handled in code).
           Omit or use an empty array if no tools needed for this agent. */
      ],
      "output_format": "<Expected output format for this agent's result (e.g. 'markdown', 'JSON with fields x,y', 'plain text explanation')>",
      "handoffs_to": [
        /* list of agent names that this agent can hand off to after completing its task, if any.
           For a simple linear flow, this might be a single next agent.
           For a branching scenario, this could include multiple agents (the decision logic should be in the handing-off agent's instructions).
           Omit if this agent is final or does not delegate further. */
      ]
    },
    /* ... more agents as needed ... */
  ],

  "handoffs": [
    /* (Optional) You can include a separate structure for handoffs if the relationships are complex.
       Each entry could detail a handoff scenario, e.g.:
       { "from": "<Agent Name>", "to": "<Agent Name>", "condition": "<when or why this handoff happens>" }.
       This can be omitted if the handoff logic is already clear from the agents' definitions above. */
  ]
}
```

**Additional notes**:
- Ensure the JSON is well-formed. All agent instructions and strings should be properly quoted.
- Do not include any explanatory text outside the JSON. **Only output the JSON object** as the answer.
- If no clarifications are needed, do not include the "clarifying_questions" field at all (or include it as an empty list). If included with questions, stop after listing them (the assumption is that the user will answer and then the full plan will be generated).
- The configuration should be directly usable with the OpenAI Agents SDK, meaning someone could parse this JSON and create the agents, tools, and handoffs as specified to run the multi-agent workflow.

Now, using the above guidelines, generate the JSON configuration for the multi-agent workflow based on the user's project description.
````

This meta-prompt first instructs the AI about its role (as a workflow planner), then enumerates all required aspects (steps, agents, tools, handoffs, output format, clarifications). It provides a template JSON with comments as a guide. In practice, the AI will fill in this structure with concrete values for a given project description. The emphasis on outputting *only* JSON helps ensure the result is machine-readable. The inclusion of an `"entry_agent"` field identifies which agent to start with, and each agent’s `handoffs_to` list (or the separate `"handoffs"` section) defines the collaboration logic. The clarifying questions mechanism is also embedded to handle ambiguities: the AI will populate that if needed instead of guessing details.

## Python Script to Parse and Instantiate the Agents

Once the meta-prompt produces the JSON configuration, you can use a Python script to parse this JSON and instantiate the agents, tools, and handoffs using the OpenAI Agents SDK. The script below assumes you have the JSON output (either as a string or loaded into a Python dict) and the necessary tools implemented as Python functions. It then demonstrates how to create Agent objects, assign tools and handoffs, and run the multi-agent workflow. This configuration is meant to be directly deployable with OpenAI’s function-calling agent system (Agents SDK):

```python
import json
from agents import Agent, Runner  # assuming openai-agents SDK is installed
# (You would also import or define any tool functions that agents will use)

# Example: JSON output from the meta-prompt (in practice, load this from the actual output)
config_json = '''{
    "entry_agent": "Triage Agent",
    "agents": [
        {
            "name": "Triage Agent",
            "role": "Decider",
            "instructions": "Determine which specialized agent should handle the request based on its content.",
            "tools": [],
            "output_format": "Internal decision (no user output)",
            "handoffs_to": ["Research Agent", "Developer Agent"]
        },
        {
            "name": "Research Agent",
            "role": "Researcher",
            "instructions": "Gather information on the topic and provide a summary.",
            "tools": ["web_search"],
            "output_format": "JSON summary with key findings",
            "handoffs_to": ["Developer Agent"]
        },
        {
            "name": "Developer Agent",
            "role": "Coder",
            "instructions": "Use the research summary to implement the solution in code.",
            "tools": ["code_execution"],
            "output_format": "Python code",
            "handoffs_to": []
        }
    ]
}'''
config = json.loads(config_json)

# Suppose we have some predefined tool functions corresponding to tool names:
# (In a real scenario, these would perform actual actions or API calls)
def web_search(query: str) -> str:
    # Dummy implementation of a web search tool
    return f"Search results for '{query}'..."

def code_execution(code: str) -> str:
    # Dummy implementation of a code execution tool
    try:
        exec_globals = {}
        exec(code, exec_globals)
        return str(exec_globals.get('result', ''))  # assume code defines 'result'
    except Exception as e:
        return f"Error executing code: {e}"

available_tools = {
    "web_search": web_search,
    "code_execution": code_execution
}

# Instantiate agents based on the config
agents = {}
for agent_conf in config["agents"]:
    name = agent_conf["name"]
    instructions = agent_conf.get("instructions", "")
    # Map tool names to actual function objects
    tool_funcs = []
    for tool_name in agent_conf.get("tools", []):
        if tool_name in available_tools:
            tool_funcs.append(available_tools[tool_name])
    # Handle output format/schema if needed (Agents SDK uses output_type for structured output)
    output_type = None
    if agent_conf.get("output_format"):
        # In a real setup, you might define a Pydantic model or schema based on output_format.
        # Here we just note it; actual enforcement would require defining output_type class.
        output_type = None  # placeholder: implement schema if needed
    # Create the Agent instance
    agent_obj = Agent(name=name, instructions=instructions, tools=tool_funcs, output_type=output_type)
    agents[name] = agent_obj

# Set up handoffs between agents according to the config
for agent_conf in config["agents"]:
    if "handoffs_to" in agent_conf:
        agent_name = agent_conf["name"]
        handoff_targets = agent_conf["handoffs_to"]
        if handoff_targets:  # non-empty list
            # Link agent to each target agent object
            agents[agent_name].handoffs = [agents[target] for target in handoff_targets]

# Identify the entry point agent to start the workflow
entry_agent_name = config.get("entry_agent") or config["agents"][0]["name"]
entry_agent = agents[entry_agent_name]

# (Optional) Provide the initial user input (the project description or query to solve)
user_input = "<<<user's project description or question>>>"

# Run the multi-agent workflow using the runner
result = Runner.run_sync(entry_agent, input=user_input)
print("Final output:", result.final_output)
```

**How this works:** We load the JSON configuration produced by the meta-prompt. For each agent in the JSON, we create an `Agent` object with its name, instructions (system prompt), and attach any tools by looking up predefined functions (in the `available_tools` map). We also prepare for structured outputs: if an agent has a specified `output_format` or schema, we could define an `output_type` (using Pydantic models or a JSON schema) to enforce that format ([GitHub - openai/openai-agents-python: A lightweight, powerful framework for multi-agent workflows](https://github.com/openai/openai-agents-python#:~:text=Final%20output%20is%20the%20last,agent%20produces%20in%20the%20loop)) – in the script above this is left as a placeholder, but in a real implementation you would create a class matching the schema and pass it to `Agent(..., output_type=YourSchemaClass)`.

Next, we configure handoffs. In the JSON, each agent may list `handoffs_to` targets. Using that, we set the `.handoffs` property of the agent to the list of corresponding Agent objects. This mirrors how the Agents SDK allows an agent to delegate to others by name ([GitHub - openai/openai-agents-python: A lightweight, powerful framework for multi-agent workflows](https://github.com/openai/openai-agents-python#:~:text=triage_agent%20%3D%20Agent%28%20name%3D,handoffs%3D%5Bspanish_agent%2C%20english_agent%5D%2C)). If the JSON had a separate `"handoffs"` section, you would similarly loop through it and link the agents accordingly.

Finally, we determine the entry point agent (the first agent to invoke). The JSON includes an `"entry_agent"` field for convenience; otherwise we could just pick the first agent in the list or a specific one designated to start. We then call `Runner.run_sync` (a synchronous helper to run the agent loop) with the entry agent and the initial user input. The Agents SDK will handle the agent’s internal loop: calling the LLM with its instructions, using tools, handing off to other agents as directed, and so on ([GitHub - openai/openai-agents-python: A lightweight, powerful framework for multi-agent workflows](https://github.com/openai/openai-agents-python#:~:text=Final%20output%20is%20the%20last,agent%20produces%20in%20the%20loop)). When the workflow completes, `result.final_output` will contain the final result produced by the multi-agent system, which we print or return.

This script, combined with the JSON from the meta-prompt, creates a deployable multi-agent setup. By following the configuration, the Agents SDK will ensure each agent operates with the given role and tools, and that the handoff logic is respected. The structured JSON output from the meta-prompt and the corresponding parser script together enable a seamless transition from a high-level task description to an orchestrated multi-agent execution in an OpenAI function-calling environment.