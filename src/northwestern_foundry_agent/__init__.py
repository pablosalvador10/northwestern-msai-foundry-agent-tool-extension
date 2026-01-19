"""Northwestern Foundry Agent - Azure AI Foundry Agent Integrations.

This package provides tools and utilities for building Azure AI Foundry agents
with Azure Functions and Logic Apps integrations for Northwestern MSAI students.
"""

from northwestern_foundry_agent.config.settings import Settings
from northwestern_foundry_agent.foundry.agent import FoundryAgent
from northwestern_foundry_agent.utils.errors import FoundryAgentError

__version__ = "0.1.0"
__all__ = ["FoundryAgent", "FoundryAgentError", "Settings", "__version__"]
