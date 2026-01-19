"""Tool definitions for Azure AI Foundry Agent.

This module provides abstractions for defining tools that can be registered
with Azure AI Foundry agents, including Azure Functions and Logic Apps.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolParameter:
    """Definition of a tool parameter.

    Attributes:
        name: Parameter name.
        param_type: Parameter type (string, integer, boolean, object, array).
        description: Human-readable description of the parameter.
        required: Whether the parameter is required.
        enum: Optional list of allowed values.
        default: Optional default value.
    """

    name: str
    param_type: str
    description: str
    required: bool = True
    enum: list[str] | None = None
    default: Any = None

    def to_schema(self) -> dict[str, Any]:
        """Convert parameter to JSON Schema format.

        Returns:
            Dictionary representing the parameter in JSON Schema format.
        """
        schema: dict[str, Any] = {
            "type": self.param_type,
            "description": self.description,
        }

        if self.enum:
            schema["enum"] = self.enum

        if self.default is not None:
            schema["default"] = self.default

        return schema


@dataclass
class ToolDefinition(ABC):
    """Base class for tool definitions.

    Defines the interface for tools that can be registered with
    Azure AI Foundry agents.

    Attributes:
        name: Unique identifier for the tool.
        description: Human-readable description of what the tool does.
        parameters: List of tool parameters.
    """

    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)

    @abstractmethod
    def to_function_definition(self) -> dict[str, Any]:
        """Convert tool to Azure AI Foundry function definition format.

        Returns:
            Dictionary representing the function definition.
        """

    def get_parameters_schema(self) -> dict[str, Any]:
        """Generate JSON Schema for tool parameters.

        Returns:
            Dictionary representing the parameters JSON Schema.
        """
        properties: dict[str, Any] = {}
        required: list[str] = []

        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)

        schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }

        if required:
            schema["required"] = required

        return schema


@dataclass
class AzureFunctionTool(ToolDefinition):
    """Tool definition for an Azure Function.

    Represents an Azure Function that can be called as a tool
    by the AI agent.

    Attributes:
        name: Unique identifier for the function.
        description: Human-readable description of the function.
        parameters: List of function parameters.
        endpoint: The HTTP endpoint URL for the function.
        http_method: HTTP method to use (GET, POST, etc.).
    """

    endpoint: str = ""
    http_method: str = "GET"

    def to_function_definition(self) -> dict[str, Any]:
        """Convert to Azure AI Foundry function definition format.

        Returns:
            Dictionary representing the function definition.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema(),
            },
        }


@dataclass
class LogicAppTool(ToolDefinition):
    """Tool definition for a Logic App workflow.

    Represents a Logic App HTTP trigger that can be called as a tool
    by the AI agent.

    Attributes:
        name: Unique identifier for the workflow.
        description: Human-readable description of the workflow.
        parameters: List of workflow parameters.
        trigger_url: The HTTP trigger URL for the Logic App.
    """

    trigger_url: str = ""

    def to_function_definition(self) -> dict[str, Any]:
        """Convert to Azure AI Foundry function definition format.

        Returns:
            Dictionary representing the function definition.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_schema(),
            },
        }


def create_health_check_tool(endpoint: str) -> AzureFunctionTool:
    """Create a tool definition for the health check Azure Function.

    Args:
        endpoint: The function endpoint URL.

    Returns:
        AzureFunctionTool configured for health check.

    Example:
        >>> tool = create_health_check_tool("https://func.azurewebsites.net/api/health")
        >>> print(tool.name)
        health_check
    """
    return AzureFunctionTool(
        name="health_check",
        description="Check the health status of the Azure Functions backend. "
        "Returns status information and timestamp.",
        parameters=[],
        endpoint=endpoint,
        http_method="GET",
    )


def create_quote_tool(endpoint: str) -> AzureFunctionTool:
    """Create a tool definition for the quote of the day Azure Function.

    Args:
        endpoint: The function endpoint URL.

    Returns:
        AzureFunctionTool configured for quote retrieval.

    Example:
        >>> tool = create_quote_tool("https://func.azurewebsites.net/api/quote")
        >>> print(tool.name)
        quote_of_the_day
    """
    return AzureFunctionTool(
        name="quote_of_the_day",
        description="Get an inspirational quote of the day. "
        "Returns a deterministic quote for testing purposes.",
        parameters=[
            ToolParameter(
                name="category",
                param_type="string",
                description="Category of quote to retrieve",
                required=False,
                enum=["motivation", "wisdom", "humor"],
                default="motivation",
            ),
        ],
        endpoint=endpoint,
        http_method="GET",
    )


def create_logic_app_tool(trigger_url: str, workflow_name: str) -> LogicAppTool:
    """Create a tool definition for a Logic App workflow.

    Args:
        trigger_url: The Logic App HTTP trigger URL.
        workflow_name: Name of the workflow for identification.

    Returns:
        LogicAppTool configured for the workflow.

    Example:
        >>> tool = create_logic_app_tool(
        ...     "https://logic-app.azurewebsites.net/api/trigger",
        ...     "process_request"
        ... )
        >>> print(tool.name)
        process_request
    """
    return LogicAppTool(
        name=workflow_name,
        description=f"Trigger the {workflow_name} Logic App workflow. "
        "Processes input data and returns the workflow result.",
        parameters=[
            ToolParameter(
                name="input_data",
                param_type="object",
                description="Input data to send to the Logic App workflow",
                required=True,
            ),
        ],
        trigger_url=trigger_url,
    )
