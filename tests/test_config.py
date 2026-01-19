"""Tests for configuration settings."""

from __future__ import annotations

from northwestern_foundry_agent.config.settings import Settings, get_settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.log_level == "INFO"
        assert settings.log_format == "json"
        assert settings.debug is False
        assert settings.azure_openai_deployment == "gpt-4o"

    def test_settings_from_env_vars(self, monkeypatch):
        """Test settings loaded from environment variables."""
        monkeypatch.setenv("AZURE_AI_PROJECT_CONNECTION_STRING", "test-conn-string")
        monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "test-sub-id")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("DEBUG", "true")

        settings = Settings()

        assert settings.azure_ai_project_connection_string == "test-conn-string"
        assert settings.azure_subscription_id == "test-sub-id"
        assert settings.log_level == "DEBUG"
        assert settings.debug is True

    def test_is_configured_property(self):
        """Test is_configured property."""
        settings = Settings(azure_ai_project_connection_string="")
        assert settings.is_configured is False

        settings = Settings(azure_ai_project_connection_string="test-string")
        assert settings.is_configured is True

    def test_functions_configured_property(self):
        """Test functions_configured property."""
        settings = Settings(azure_function_app_url="")
        assert settings.functions_configured is False

        settings = Settings(azure_function_app_url="https://test.azurewebsites.net")
        assert settings.functions_configured is True

    def test_logic_apps_configured_property(self):
        """Test logic_apps_configured property."""
        settings = Settings(logic_app_trigger_url="")
        assert settings.logic_apps_configured is False

        settings = Settings(logic_app_trigger_url="https://test-logic.azurewebsites.net")
        assert settings.logic_apps_configured is True

    def test_url_validation_adds_https(self):
        """Test URL validator adds https:// prefix."""
        settings = Settings(
            azure_openai_endpoint="test.openai.azure.com",
            azure_function_app_url="test.azurewebsites.net",
        )

        assert settings.azure_openai_endpoint == "https://test.openai.azure.com"
        assert settings.azure_function_app_url == "https://test.azurewebsites.net"

    def test_url_validation_preserves_existing_scheme(self):
        """Test URL validator preserves existing http/https scheme."""
        settings = Settings(
            azure_openai_endpoint="https://test.openai.azure.com/",
        )

        assert settings.azure_openai_endpoint == "https://test.openai.azure.com/"

    def test_settings_from_env_file(self, tmp_path):
        """Test settings loaded from .env file."""
        env_content = """
AZURE_AI_PROJECT_CONNECTION_STRING=file-conn-string
LOG_LEVEL=WARNING
DEBUG=false
"""
        env_file = tmp_path / ".env"
        env_file.write_text(env_content)

        settings = Settings(_env_file=env_file)

        assert settings.azure_ai_project_connection_string == "file-conn-string"
        assert settings.log_level == "WARNING"
        assert settings.debug is False


class TestGetSettings:
    """Test cases for get_settings function."""

    def test_get_settings_caching(self):
        """Test that get_settings returns cached instance."""
        # Clear the cache first
        get_settings.cache_clear()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_get_settings_with_env_file(self, tmp_path):
        """Test get_settings with custom env file."""
        env_content = "LOG_LEVEL=ERROR\n"
        env_file = tmp_path / "custom.env"
        env_file.write_text(env_content)

        # Clear cache to get fresh settings
        get_settings.cache_clear()

        settings = get_settings(env_file=env_file)

        assert settings.log_level == "ERROR"
