"""Azure AI Foundry Agent implementation.

This module provides a high-level abstraction for creating and managing
Azure AI Foundry agents with tool integrations.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from northwestern_foundry_agent.config.settings import Settings, get_settings
from northwestern_foundry_agent.utils.errors import (
    ConfigurationError,
)
from northwestern_foundry_agent.utils.logging import get_logger

if TYPE_CHECKING:
    from azure.ai.projects import AIProjectClient

    from northwestern_foundry_agent.foundry.tools import ToolDefinition

# Note: The Azure AI Projects SDK is in beta and types may not be fully available
# We use 'Any' for the Agent type to avoid type errors with the evolving SDK
Agent = Any

logger = get_logger(__name__)


class FoundryAgent:
    """High-level interface for Azure AI Foundry Agent operations.

    This class provides methods to create, configure, and run Azure AI
    Foundry agents with custom tool integrations.

    Attributes:
        settings: Application settings instance.
        client: Azure AI Project client instance.
        agent: The created/loaded Azure AI agent.
        tools: Dictionary of registered tools.

    Example:
        >>> from northwestern_foundry_agent import FoundryAgent, Settings
        >>> settings = Settings()
        >>> agent = FoundryAgent(settings)
        >>> agent.create_agent("my-assistant", "A helpful assistant")
        >>> agent.register_tool(health_check_tool)
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
        self._tools: dict[str, ToolDefinition] = {}
        self._tool_handlers: dict[str, Any] = {}

        logger.info("FoundryAgent initialized")

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
    def tools(self) -> dict[str, ToolDefinition]:
        """Get registered tools dictionary."""
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
            client: AIProjectClient = AIProjectClient.from_connection_string(  # type: ignore[attr-defined]
                credential=credential,
                conn_str=self.settings.azure_ai_project_connection_string,
            )

            logger.info("Azure AI Project client created successfully")
            return client

        except ImportError as e:
            raise ConfigurationError(
                "Azure AI Projects SDK not installed. "
                "Install with: pip install azure-ai-projects",
                details={"import_error": str(e)},
            ) from e

    def create_agent(
        self,
        name: str,
        instructions: str,
        model: str | None = None,
    ) -> Agent:
        """Create a new Azure AI Foundry agent.

        Args:
            name: Name for the agent.
            instructions: System instructions for the agent.
            model: Model deployment name. Defaults to settings value.

        Returns:
            Created Agent instance.

        Raises:
            ConfigurationError: If agent creation fails.

        Example:
            >>> agent.create_agent(
            ...     "assistant",
            ...     "You are a helpful assistant that can check system health."
            ... )
        """
        model = model or self.settings.azure_openai_deployment

        try:
            # Collect tool definitions
            tool_definitions = [tool.to_function_definition() for tool in self._tools.values()]

            self._agent = self.client.agents.create_agent(  # type: ignore[attr-defined]
                model=model,
                name=name,
                instructions=instructions,
                tools=tool_definitions if tool_definitions else None,
            )

            logger.info(
                "Agent created: name=%s, model=%s, tools=%d",
                name,
                model,
                len(tool_definitions),
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

    def register_tool(
        self,
        tool: ToolDefinition,
        handler: Any | None = None,
    ) -> None:
        """Register a tool with the agent.

        Args:
            tool: Tool definition to register.
            handler: Optional callable to handle tool invocations.

        Raises:
            ToolRegistrationError: If tool registration fails.

        Example:
            >>> from northwestern_foundry_agent.foundry.tools import create_health_check_tool
            >>> tool = create_health_check_tool("https://func.azurewebsites.net/api/health")
            >>> agent.register_tool(tool, health_check_handler)
        """
        if tool.name in self._tools:
            logger.warning("Tool '%s' already registered, overwriting", tool.name)

        self._tools[tool.name] = tool

        if handler is not None:
            self._tool_handlers[tool.name] = handler

        logger.info("Tool registered: name=%s, type=%s", tool.name, type(tool).__name__)

    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool from the agent.

        Args:
            tool_name: Name of the tool to unregister.
        """
        if tool_name in self._tools:
            del self._tools[tool_name]
            self._tool_handlers.pop(tool_name, None)
            logger.info("Tool unregistered: name=%s", tool_name)

    def run(
        self,
        message: str,
        thread_id: str | None = None,
    ) -> str:
        """Run the agent with a user message.

        This method sends a message to the agent and handles tool calls
        if any tools are registered.

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

            # Add user message
            self.client.agents.create_message(  # type: ignore[attr-defined]
                thread_id=thread.id,
                role="user",
                content=message,
            )

            # Run the agent
            run = self.client.agents.create_and_process_run(  # type: ignore[attr-defined]
                thread_id=thread.id,
                assistant_id=self._agent.id,
            )

            # Handle tool calls if needed
            while run.status == "requires_action":
                run = self._handle_tool_calls(thread.id, run)

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
        """Handle tool calls from the agent.

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

            logger.info("Handling tool call: name=%s", tool_name)

            # Get handler and execute
            handler = self._tool_handlers.get(tool_name)
            if handler:
                try:
                    result = handler(**tool_args)
                    output = json.dumps(result) if isinstance(result, dict) else str(result)
                except Exception as e:
                    logger.error("Tool execution failed: %s", str(e))
                    output = json.dumps({"error": str(e)})
            else:
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

        except Exception as e:
            logger.error("Failed to delete agent: %s", str(e))
            raise ConfigurationError(
                f"Failed to delete agent: {e}",
            ) from e
