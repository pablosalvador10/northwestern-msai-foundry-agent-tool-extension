"""Application settings and configuration management.

This module provides centralized configuration management using Pydantic settings,
supporting environment variables and .env files for secure credential management.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from pathlib import Path


class Settings(BaseSettings):
    """Application configuration settings.

    All settings can be configured via environment variables or .env file.
    Environment variables take precedence over .env file values.

    Attributes:
        azure_ai_project_connection_string: Connection string for Azure AI project.
        azure_subscription_id: Azure subscription identifier.
        azure_resource_group: Azure resource group name.
        azure_ai_project_name: Azure AI project name.
        azure_openai_endpoint: Azure OpenAI endpoint URL.
        azure_openai_deployment: Azure OpenAI model deployment name.
        azure_openai_api_version: Azure OpenAI API version.
        azure_function_app_url: Base URL for Azure Functions app.
        azure_function_key: Function key for authentication.
        logic_app_trigger_url: HTTP trigger URL for Logic App.
        logic_app_sas_token: Optional SAS token for Logic App authentication.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_format: Log output format (json or text).
        debug: Enable debug mode.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Azure AI Foundry Configuration
    azure_ai_project_connection_string: str = Field(
        default="",
        description="Connection string for Azure AI Foundry project",
    )
    azure_subscription_id: str = Field(
        default="",
        description="Azure subscription ID",
    )
    azure_resource_group: str = Field(
        default="",
        description="Azure resource group name",
    )
    azure_ai_project_name: str = Field(
        default="",
        description="Azure AI project name",
    )

    # Azure OpenAI Configuration
    azure_openai_endpoint: str = Field(
        default="",
        description="Azure OpenAI endpoint URL",
    )
    azure_openai_deployment: str = Field(
        default="gpt-4o",
        description="Azure OpenAI model deployment name",
    )
    azure_openai_api_version: str = Field(
        default="2024-08-01-preview",
        description="Azure OpenAI API version",
    )

    # Azure Functions Configuration
    azure_function_app_url: str = Field(
        default="",
        description="Base URL for Azure Functions app",
    )
    azure_function_key: str = Field(
        default="",
        description="Function key for authentication",
    )

    # Logic Apps Configuration
    logic_app_trigger_url: str = Field(
        default="",
        description="HTTP trigger URL for Logic App",
    )
    logic_app_sas_token: str = Field(
        default="",
        description="Optional SAS token for Logic App authentication",
    )

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log output format",
    )

    # Development Settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    @field_validator("azure_openai_endpoint", "azure_function_app_url", "logic_app_trigger_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL fields are properly formatted when provided."""
        if v and not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v

    @property
    def is_configured(self) -> bool:
        """Check if essential Azure AI configuration is provided."""
        return bool(self.azure_ai_project_connection_string)

    @property
    def functions_configured(self) -> bool:
        """Check if Azure Functions configuration is provided."""
        return bool(self.azure_function_app_url)

    @property
    def logic_apps_configured(self) -> bool:
        """Check if Logic Apps configuration is provided."""
        return bool(self.logic_app_trigger_url)


@lru_cache
def get_settings(env_file: Path | None = None) -> Settings:
    """Get cached application settings instance.

    Args:
        env_file: Optional path to .env file. Defaults to None (uses default .env).

    Returns:
        Cached Settings instance.

    Example:
        >>> settings = get_settings()
        >>> print(settings.log_level)
        INFO
    """
    if env_file:
        return Settings(_env_file=env_file)  # type: ignore[call-arg]
    return Settings()
