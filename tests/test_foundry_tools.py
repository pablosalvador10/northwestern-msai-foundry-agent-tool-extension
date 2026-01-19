"""Tests for Foundry tools and agent."""

from __future__ import annotations

from northwestern_foundry_agent.foundry.tools import (
    AzureFunctionTool,
    LogicAppTool,
    ToolParameter,
    create_health_check_tool,
    create_logic_app_tool,
    create_quote_tool,
)


class TestToolParameter:
    """Test cases for ToolParameter."""

    def test_basic_parameter(self):
        """Test basic parameter creation."""
        param = ToolParameter(
            name="query",
            param_type="string",
            description="Search query",
        )

        assert param.name == "query"
        assert param.param_type == "string"
        assert param.required is True

    def test_optional_parameter(self):
        """Test optional parameter with default."""
        param = ToolParameter(
            name="limit",
            param_type="integer",
            description="Result limit",
            required=False,
            default=10,
        )

        assert param.required is False
        assert param.default == 10

    def test_enum_parameter(self):
        """Test parameter with enum values."""
        param = ToolParameter(
            name="category",
            param_type="string",
            description="Category selection",
            enum=["a", "b", "c"],
        )

        assert param.enum == ["a", "b", "c"]

    def test_to_schema(self):
        """Test conversion to JSON Schema."""
        param = ToolParameter(
            name="category",
            param_type="string",
            description="Category selection",
            enum=["motivation", "wisdom"],
            default="motivation",
        )

        schema = param.to_schema()

        assert schema["type"] == "string"
        assert schema["description"] == "Category selection"
        assert schema["enum"] == ["motivation", "wisdom"]
        assert schema["default"] == "motivation"


class TestAzureFunctionTool:
    """Test cases for AzureFunctionTool."""

    def test_basic_tool(self):
        """Test basic function tool creation."""
        tool = AzureFunctionTool(
            name="my_function",
            description="My test function",
            endpoint="https://func.azurewebsites.net/api/my_function",
            http_method="GET",
        )

        assert tool.name == "my_function"
        assert tool.http_method == "GET"

    def test_to_function_definition(self):
        """Test conversion to function definition."""
        tool = AzureFunctionTool(
            name="search",
            description="Search for items",
            parameters=[
                ToolParameter(
                    name="query",
                    param_type="string",
                    description="Search query",
                ),
            ],
        )

        definition = tool.to_function_definition()

        assert definition["type"] == "function"
        assert definition["function"]["name"] == "search"
        assert definition["function"]["description"] == "Search for items"
        assert "parameters" in definition["function"]

    def test_get_parameters_schema(self):
        """Test parameters schema generation."""
        tool = AzureFunctionTool(
            name="test",
            description="Test function",
            parameters=[
                ToolParameter(
                    name="required_param",
                    param_type="string",
                    description="Required param",
                    required=True,
                ),
                ToolParameter(
                    name="optional_param",
                    param_type="integer",
                    description="Optional param",
                    required=False,
                ),
            ],
        )

        schema = tool.get_parameters_schema()

        assert schema["type"] == "object"
        assert "required_param" in schema["properties"]
        assert "optional_param" in schema["properties"]
        assert schema["required"] == ["required_param"]


class TestLogicAppTool:
    """Test cases for LogicAppTool."""

    def test_basic_tool(self):
        """Test basic Logic App tool creation."""
        tool = LogicAppTool(
            name="my_workflow",
            description="My workflow",
            trigger_url="https://logic.azurewebsites.net/trigger",
        )

        assert tool.name == "my_workflow"
        assert tool.trigger_url == "https://logic.azurewebsites.net/trigger"

    def test_to_function_definition(self):
        """Test conversion to function definition."""
        tool = LogicAppTool(
            name="process_data",
            description="Process input data",
            parameters=[
                ToolParameter(
                    name="input_data",
                    param_type="object",
                    description="Input data",
                ),
            ],
        )

        definition = tool.to_function_definition()

        assert definition["type"] == "function"
        assert definition["function"]["name"] == "process_data"


class TestToolFactories:
    """Test cases for tool factory functions."""

    def test_create_health_check_tool(self):
        """Test health check tool creation."""
        tool = create_health_check_tool("https://func.azurewebsites.net/api/health")

        assert tool.name == "health_check"
        assert tool.http_method == "GET"
        assert tool.endpoint == "https://func.azurewebsites.net/api/health"
        assert len(tool.parameters) == 0

    def test_create_quote_tool(self):
        """Test quote tool creation."""
        tool = create_quote_tool("https://func.azurewebsites.net/api/quote")

        assert tool.name == "quote_of_the_day"
        assert tool.http_method == "GET"
        assert len(tool.parameters) == 1
        assert tool.parameters[0].name == "category"
        assert tool.parameters[0].enum == ["motivation", "wisdom", "humor"]

    def test_create_logic_app_tool(self):
        """Test Logic App tool creation."""
        tool = create_logic_app_tool(
            "https://logic.azurewebsites.net/trigger",
            "my_workflow",
        )

        assert tool.name == "my_workflow"
        assert tool.trigger_url == "https://logic.azurewebsites.net/trigger"
        assert len(tool.parameters) == 1
        assert tool.parameters[0].name == "input_data"
