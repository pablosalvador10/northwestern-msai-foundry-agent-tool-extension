"""Azure AI Foundry Agent implementation using Microsoft Agent Framework SDK.

This module provides a high-level abstraction for creating and managing
Azure AI Foundry agents with cloud-deployed tool integrations (Azure Functions
and Logic Apps) using the azure-ai-projects SDK.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from northwestern_foundry_agent.config.settings import Settings, get_settings
from northwestern_foundry_agent.utils.errors import (
    ConfigurationError,
    ToolRegistrationError,
)
from northwestern_foundry_agent.utils.logging import get_logger

if TYPE_CHECKING:
    from azure.ai.projects import AIProjectClient

# Agent type is Any since the SDK types are still evolving
Agent = Any

logger = get_logger(__name__)


class FoundryAgent:
    """High-level interface for Azure AI Foundry Agent operations.

    This class provides methods to create, configure, and run Azure AI
    Foundry agents with cloud-deployed tool integrations using the
    Microsoft Agent Framework SDK (azure-ai-projects).

    Supports:
    - OpenAPI tools for Azure Functions HTTP endpoints
    - OpenAPI tools for Logic Apps HTTP triggers
    - Custom function tools with local handlers

    Attributes:
        settings: Application settings instance.
        client: Azure AI Project client instance.
        agent: The created/loaded Azure AI agent.

    Example:
        >>> from northwestern_foundry_agent import FoundryAgent, Settings
        >>> settings = Settings()
        >>> agent = FoundryAgent(settings)
        >>>
        >>> # Add Azure Function as OpenAPI tool
        >>> agent.add_azure_function_tool(
        ...     name="health_check",
        ...     description="Check system health status",
        ...     endpoint_url="https://myfunc.azurewebsites.net/api/health",
        ...     openapi_spec_url="https://myfunc.azurewebsites.net/api/openapi.json"
        ... )
        >>>
        >>> # Create agent with tools
        >>> agent.create_agent("my-assistant", "A helpful assistant")
        >>> response = agent.run("Check the system health")
    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the FoundryAgent.

        Args:
            settings: Optional Settings instance. If None, loads from environment.

        Raises:
            ConfigurationError: If required configuration is missing.
        """
        self.settings = settings or get_settings()
        self._client: AIProjectClient | None = None
        self._agent: Agent | None = None
        self._tools: list[Any] = []
        self._tool_handlers: dict[str, Any] = {}
        self._thread_id: str | None = None

        logger.info("FoundryAgent initialized with Microsoft Agent Framework SDK")

    @property
    def client(self) -> AIProjectClient:
        """Get or create the Azure AI Project client.

        Returns:
            Configured AIProjectClient instance.

        Raises:
            ConfigurationError: If connection string is not configured.
        """
        if self._client is None:
            self._client = self._create_client()
        return self._client

    @property
    def agent(self) -> Agent | None:
        """Get the current agent instance."""
        return self._agent

    @property
    def tools(self) -> list[Any]:
        """Get registered tools list."""
        return self._tools.copy()

    def _create_client(self) -> AIProjectClient:
        """Create Azure AI Project client.

        Returns:
            Configured AIProjectClient instance.

        Raises:
            ConfigurationError: If connection string is not configured.
        """
        if not self.settings.azure_ai_project_connection_string:
            raise ConfigurationError(
                "Azure AI Project connection string is not configured",
                details={"setting": "azure_ai_project_connection_string"},
            )

        try:
            from azure.ai.projects import AIProjectClient
            from azure.identity import DefaultAzureCredential

            credential = DefaultAzureCredential()

            # The SDK supports from_connection_string for easy setup
            client = AIProjectClient.from_connection_string(  # type: ignore[attr-defined]
                credential=credential,
                conn_str=self.settings.azure_ai_project_connection_string,
            )

            logger.info("Azure AI Project client created successfully")
            return client  # type: ignore[no-any-return]

        except ImportError as e:
            raise ConfigurationError(
                "Azure AI Projects SDK not installed. "
                "Install with: pip install azure-ai-projects azure-identity",
                details={"import_error": str(e)},
            ) from e

    def add_openapi_tool(
        self,
        name: str,
        description: str,
        openapi_spec: dict[str, Any] | str,
        auth_type: str = "anonymous",
    ) -> None:
        """Add an OpenAPI-based tool for cloud-deployed services.

        This method allows you to register Azure Functions or Logic Apps
        endpoints as tools using their OpenAPI specifications.

        Args:
            name: Unique name for the tool.
            description: Human-readable description of what the tool does.
            openapi_spec: OpenAPI specification as a dict or URL string.
            auth_type: Authentication type (currently only 'anonymous' is supported).

        Raises:
            ToolRegistrationError: If tool registration fails.

        Example:
            >>> agent.add_openapi_tool(
            ...     name="health_check",
            ...     description="Check Azure Function health status",
            ...     openapi_spec="https://myfunc.azurewebsites.net/api/openapi.json"
            ... )
        """
        try:
            from azure.ai.projects.models import (
                OpenApiAgentTool,
                OpenApiAnonymousAuthDetails,
                OpenApiFunctionDefinition,
            )

            # Use anonymous auth for simplicity - Azure Functions/Logic Apps
            # typically use key-based auth embedded in URLs or headers
            auth = OpenApiAnonymousAuthDetails()

            # Create OpenAPI function definition
            openapi_def = OpenApiFunctionDefinition(
                name=name,
                description=description,
                spec=openapi_spec if isinstance(openapi_spec, dict) else {"url": openapi_spec},
                auth=auth,
            )

            # Create the tool
            tool = OpenApiAgentTool(openapi=openapi_def)
            self._tools.append(tool)

            logger.info(
                "OpenAPI tool registered: name=%s, auth_type=%s",
                name,
                auth_type,
            )

        except ImportError as e:
            raise ToolRegistrationError(
                f"Failed to import Azure AI Projects models: {e}",
                tool_name=name,
            ) from e
        except Exception as e:
            raise ToolRegistrationError(
                f"Failed to register OpenAPI tool: {e}",
                tool_name=name,
            ) from e

    def add_azure_function_tool(
        self,
        name: str,
        description: str,
        function_url: str,
        parameters: dict[str, Any] | None = None,
        method: str = "GET",
        function_key: str | None = None,
    ) -> None:
        """Add an Azure Function as a tool using inline OpenAPI spec.

        This is a convenience method that creates an OpenAPI specification
        for a simple Azure Function HTTP endpoint.

        Args:
            name: Unique name for the tool (used as operation ID).
            description: Human-readable description of the function.
            function_url: Full URL to the Azure Function endpoint.
            parameters: Optional dict of query parameters with their types.
            method: HTTP method (GET, POST, etc.). Defaults to GET.
            function_key: Optional function key for authentication.

        Example:
            >>> agent.add_azure_function_tool(
            ...     name="health_check",
            ...     description="Check the health status of the system",
            ...     function_url="https://myfunc.azurewebsites.net/api/health"
            ... )
            >>>
            >>> agent.add_azure_function_tool(
            ...     name="get_quote",
            ...     description="Get a quote by category",
            ...     function_url="https://myfunc.azurewebsites.net/api/quote",
            ...     parameters={"category": {"type": "string", "description": "Quote category"}}
            ... )
        """
        # Build inline OpenAPI spec for the function
        openapi_spec = self._build_function_openapi_spec(
            name=name,
            description=description,
            function_url=function_url,
            parameters=parameters,
            method=method,
        )

        # Determine auth type based on function key
        auth_type = "anonymous"  # Azure Functions support anonymous or key-based auth

        self.add_openapi_tool(
            name=name,
            description=description,
            openapi_spec=openapi_spec,
            auth_type=auth_type,
        )

        # Store function key if provided (for custom handling)
        if function_key:
            self._tool_handlers[f"{name}_key"] = function_key

        logger.info("Azure Function tool added: name=%s, url=%s", name, function_url)

    def add_logic_app_tool(
        self,
        name: str,
        description: str,
        trigger_url: str,
        request_schema: dict[str, Any] | None = None,
        sas_token: str | None = None,
    ) -> None:
        """Add a Logic App HTTP trigger as a tool.

        This method registers a Logic App workflow that can be triggered
        via HTTP as an agent tool.

        Args:
            name: Unique name for the tool.
            description: Human-readable description of the Logic App workflow.
            trigger_url: HTTP trigger URL for the Logic App.
            request_schema: Optional JSON schema for the request body.
            sas_token: Optional SAS token for authentication.

        Example:
            >>> agent.add_logic_app_tool(
            ...     name="process_document",
            ...     description="Process a document through the workflow",
            ...     trigger_url="https://prod-00.eastus.logic.azure.com/workflows/...",
            ...     request_schema={
            ...         "type": "object",
            ...         "properties": {
            ...             "action": {"type": "string"},
            ...             "data": {"type": "object"}
            ...         }
            ...     }
            ... )
        """
        # Build OpenAPI spec for Logic App
        openapi_spec = self._build_logic_app_openapi_spec(
            name=name,
            description=description,
            trigger_url=trigger_url,
            request_schema=request_schema,
        )

        self.add_openapi_tool(
            name=name,
            description=description,
            openapi_spec=openapi_spec,
            auth_type="anonymous",  # SAS token is in URL for Logic Apps
        )

        # Store SAS token if provided separately
        if sas_token:
            self._tool_handlers[f"{name}_sas"] = sas_token

        logger.info("Logic App tool added: name=%s", name)

    def add_function_tool(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Any,
    ) -> None:
        """Add a custom function tool with a local handler.

        This method registers a function tool that will be handled locally
        by the provided handler function when the agent calls it.

        Args:
            name: Unique name for the function.
            description: Human-readable description.
            parameters: JSON Schema for the function parameters.
            handler: Callable to handle function invocations.

        Example:
            >>> def my_handler(query: str) -> dict:
            ...     return {"result": f"Processed: {query}"}
            >>>
            >>> agent.add_function_tool(
            ...     name="process_query",
            ...     description="Process a user query",
            ...     parameters={
            ...         "type": "object",
            ...         "properties": {
            ...             "query": {"type": "string", "description": "The query to process"}
            ...         },
            ...         "required": ["query"]
            ...     },
            ...     handler=my_handler
            ... )
        """
        try:
            from azure.ai.projects.models import FunctionTool

            # FunctionTool requires: name, parameters, strict, optional description
            tool = FunctionTool(
                name=name,
                parameters=parameters,
                strict=True,
                description=description,
            )
            self._tools.append(tool)
            self._tool_handlers[name] = handler

            logger.info("Function tool registered: name=%s", name)

        except ImportError as e:
            raise ToolRegistrationError(
                f"Failed to import FunctionTool: {e}",
                tool_name=name,
            ) from e

    def _build_function_openapi_spec(
        self,
        name: str,
        description: str,
        function_url: str,
        parameters: dict[str, Any] | None = None,
        method: str = "GET",
    ) -> dict[str, Any]:
        """Build an OpenAPI specification for an Azure Function.

        Args:
            name: Operation ID / function name.
            description: Function description.
            function_url: Full URL to the function.
            parameters: Query parameters specification.
            method: HTTP method.

        Returns:
            OpenAPI specification dictionary.
        """
        # Parse URL to get base and path
        from urllib.parse import urlparse

        parsed = urlparse(function_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path or f"/api/{name}"

        # Build parameters list
        param_list = []
        if parameters:
            for param_name, param_spec in parameters.items():
                param_list.append(
                    {
                        "name": param_name,
                        "in": "query",
                        "required": param_spec.get("required", False),
                        "schema": {
                            "type": param_spec.get("type", "string"),
                        },
                        "description": param_spec.get("description", ""),
                    }
                )

        spec: dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{name} Azure Function",
                "version": "1.0.0",
                "description": description,
            },
            "servers": [{"url": base_url}],
            "paths": {
                path: {
                    method.lower(): {
                        "operationId": name,
                        "summary": description,
                        "parameters": param_list,
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object"},
                                    }
                                },
                            }
                        },
                    }
                }
            },
        }

        return spec

    def _build_logic_app_openapi_spec(
        self,
        name: str,
        description: str,
        trigger_url: str,
        request_schema: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build an OpenAPI specification for a Logic App HTTP trigger.

        Args:
            name: Operation ID / workflow name.
            description: Workflow description.
            trigger_url: Full trigger URL.
            request_schema: JSON schema for request body.

        Returns:
            OpenAPI specification dictionary.
        """
        from urllib.parse import urlparse

        parsed = urlparse(trigger_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path

        request_body = None
        if request_schema:
            request_body = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": request_schema,
                    }
                },
            }

        spec: dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{name} Logic App",
                "version": "1.0.0",
                "description": description,
            },
            "servers": [{"url": base_url}],
            "paths": {
                path: {
                    "post": {
                        "operationId": name,
                        "summary": description,
                        "requestBody": request_body,
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object"},
                                    }
                                },
                            },
                            "202": {
                                "description": "Accepted - workflow started",
                            },
                        },
                    }
                }
            },
        }

        return spec

    def create_agent(
        self,
        name: str,
        instructions: str,
        model: str | None = None,
    ) -> Agent:
        """Create a new Azure AI Foundry agent with registered tools.

        Args:
            name: Name for the agent.
            instructions: System instructions for the agent.
            model: Model deployment name. Defaults to settings value.

        Returns:
            Created Agent instance.

        Raises:
            ConfigurationError: If agent creation fails.

        Example:
            >>> agent.add_azure_function_tool(...)
            >>> agent.create_agent(
            ...     "my-assistant",
            ...     "You are a helpful assistant that can check system health."
            ... )
        """
        model = model or self.settings.azure_openai_deployment

        try:
            # Create agent with tools
            create_kwargs: dict[str, Any] = {
                "model": model,
                "name": name,
                "instructions": instructions,
            }

            # Add tools if any are registered
            if self._tools:
                create_kwargs["tools"] = self._tools

            self._agent = self.client.agents.create_agent(**create_kwargs)  # type: ignore[attr-defined]

            logger.info(
                "Agent created: name=%s, model=%s, tools=%d",
                name,
                model,
                len(self._tools),
            )
            return self._agent

        except Exception as e:
            logger.error("Failed to create agent: %s", str(e))
            raise ConfigurationError(
                f"Failed to create agent: {e}",
                details={"name": name, "model": model},
            ) from e

    def load_agent(self, agent_id: str) -> Agent:
        """Load an existing Azure AI Foundry agent.

        Args:
            agent_id: The ID of the agent to load.

        Returns:
            Loaded Agent instance.

        Raises:
            ConfigurationError: If agent loading fails.

        Example:
            >>> agent.load_agent("asst_abc123")
        """
        try:
            self._agent = self.client.agents.get_agent(agent_id)  # type: ignore[attr-defined]
            logger.info("Agent loaded: id=%s", agent_id)
            return self._agent

        except Exception as e:
            logger.error("Failed to load agent: %s", str(e))
            raise ConfigurationError(
                f"Failed to load agent: {e}",
                details={"agent_id": agent_id},
            ) from e

    def run(
        self,
        message: str,
        thread_id: str | None = None,
    ) -> str:
        """Run the agent with a user message.

        This method sends a message to the agent. For OpenAPI tools (Azure
        Functions, Logic Apps), the agent will automatically call the
        cloud endpoints. For function tools with local handlers, this
        method handles the tool calls.

        Args:
            message: User message to send to the agent.
            thread_id: Optional existing thread ID to continue conversation.

        Returns:
            Agent's response text.

        Raises:
            ConfigurationError: If agent is not created/loaded.

        Example:
            >>> response = agent.run("What is the system health status?")
            >>> print(response)
        """
        if self._agent is None:
            raise ConfigurationError(
                "No agent created or loaded. Call create_agent() or load_agent() first."
            )

        try:
            # Create or get thread
            if thread_id:
                thread = self.client.agents.get_thread(thread_id)  # type: ignore[attr-defined]
            else:
                thread = self.client.agents.create_thread()  # type: ignore[attr-defined]

            self._thread_id = thread.id

            # Add user message
            self.client.agents.create_message(  # type: ignore[attr-defined]
                thread_id=thread.id,
                role="user",
                content=message,
            )

            # Run the agent - this handles OpenAPI tool calls automatically
            run = self.client.agents.create_and_process_run(  # type: ignore[attr-defined]
                thread_id=thread.id,
                assistant_id=self._agent.id,
            )

            # Handle function tool calls if needed (local handlers)
            while run.status == "requires_action":
                run = self._handle_tool_calls(thread.id, run)

            # Check for errors
            if run.status == "failed":
                error_msg = getattr(run, "last_error", "Unknown error")
                logger.error("Agent run failed: %s", error_msg)
                return f"Agent run failed: {error_msg}"

            # Get the response
            messages = self.client.agents.list_messages(thread_id=thread.id)  # type: ignore[attr-defined]

            # Return the last assistant message
            for msg in messages.data:
                if msg.role == "assistant":
                    for content in msg.content:
                        if hasattr(content, "text"):
                            return str(content.text.value)

            return "No response from agent"

        except Exception as e:
            logger.error("Agent run failed: %s", str(e))
            raise ConfigurationError(
                f"Agent run failed: {e}",
                details={"message": message[:100]},
            ) from e

    def _handle_tool_calls(self, thread_id: str, run: Any) -> Any:
        """Handle function tool calls from the agent (local handlers only).

        OpenAPI tools (Azure Functions, Logic Apps) are handled automatically
        by the Azure AI service. This method handles FunctionTool calls that
        have local handlers registered.

        Args:
            thread_id: The thread ID.
            run: The current run object.

        Returns:
            Updated run object after submitting tool outputs.
        """
        tool_outputs = []

        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            logger.info("Handling tool call: name=%s, args=%s", tool_name, tool_args)

            # Get handler and execute
            handler = self._tool_handlers.get(tool_name)
            if handler and callable(handler):
                try:
                    result = handler(**tool_args)
                    output = json.dumps(result) if isinstance(result, dict) else str(result)
                except Exception as e:
                    logger.error("Tool execution failed: %s", str(e))
                    output = json.dumps({"error": str(e)})
            else:
                # No local handler - this shouldn't happen for properly configured tools
                output = json.dumps({"error": f"No handler registered for tool: {tool_name}"})

            tool_outputs.append({"tool_call_id": tool_call.id, "output": output})

        # Submit tool outputs
        return self.client.agents.submit_tool_outputs_and_poll(  # type: ignore[attr-defined]
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=tool_outputs,
        )

    def delete_agent(self) -> None:
        """Delete the current agent.

        Raises:
            ConfigurationError: If no agent is loaded.
        """
        if self._agent is None:
            raise ConfigurationError("No agent to delete")

        try:
            self.client.agents.delete_agent(self._agent.id)  # type: ignore[attr-defined]
            logger.info("Agent deleted: id=%s", self._agent.id)
            self._agent = None
            self._tools.clear()
            self._tool_handlers.clear()

        except Exception as e:
            logger.error("Failed to delete agent: %s", str(e))
            raise ConfigurationError(
                f"Failed to delete agent: {e}",
            ) from e

    def get_thread_id(self) -> str | None:
        """Get the current thread ID for continuing conversations.

        Returns:
            The current thread ID or None if no conversation started.
        """
        return self._thread_id
