"""
Azure Functions client abstraction for AI Foundry agent integration.

This module provides a client for invoking Azure Functions as tools
within an AI Foundry agent workflow.
"""

import logging
from typing import Any, Dict, Optional

import aiohttp
import requests
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel, Field, field_validator


logger = logging.getLogger(__name__)


class FunctionConfig(BaseModel):
    """Configuration for an Azure Function.
    
    Attributes:
        function_url: The HTTP endpoint URL for the Azure Function.
        function_key: Optional function key for authentication.
        use_managed_identity: Whether to use Azure Managed Identity for authentication.
        timeout: Request timeout in seconds.
    """
    
    function_url: str = Field(..., description="Azure Function HTTP endpoint URL")
    function_key: Optional[str] = Field(None, description="Function key for authentication")
    use_managed_identity: bool = Field(
        False, 
        description="Use Azure Managed Identity for authentication"
    )
    timeout: int = Field(30, ge=1, le=300, description="Request timeout in seconds")
    
    @field_validator("function_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that the URL is properly formatted."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("function_url must start with http:// or https://")
        return v


class AzureFunctionsClient:
    """Client for interacting with Azure Functions.
    
    This client provides both synchronous and asynchronous methods for
    invoking Azure Functions, with support for function keys and managed
    identity authentication.
    
    Example:
        >>> config = FunctionConfig(
        ...     function_url="https://myapp.azurewebsites.net/api/myfunction",
        ...     function_key="abc123"
        ... )
        >>> client = AzureFunctionsClient(config)
        >>> result = client.invoke_function({"data": "test"})
    """
    
    def __init__(self, config: FunctionConfig) -> None:
        """Initialize the Azure Functions client.
        
        Args:
            config: Configuration for the Azure Function.
        """
        self.config = config
        self._credential: Optional[DefaultAzureCredential] = None
        
        if self.config.use_managed_identity:
            self._credential = DefaultAzureCredential()
            logger.info("Initialized Azure Functions client with managed identity")
        else:
            logger.info("Initialized Azure Functions client with function key")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for the request.
        
        Returns:
            Dictionary of HTTP headers including authentication.
        """
        headers = {"Content-Type": "application/json"}
        
        if self.config.function_key:
            headers["x-functions-key"] = self.config.function_key
            logger.debug("Added function key to request headers")
        
        return headers
    
    def invoke_function(
        self, 
        payload: Dict[str, Any],
        method: str = "POST"
    ) -> Dict[str, Any]:
        """Invoke an Azure Function synchronously.
        
        Args:
            payload: JSON payload to send to the function.
            method: HTTP method (GET, POST, PUT, etc.).
            
        Returns:
            The JSON response from the function.
            
        Raises:
            requests.RequestException: If the request fails.
            ValueError: If the response is not valid JSON.
        """
        logger.info(f"Invoking Azure Function: {self.config.function_url}")
        logger.debug(f"Request method: {method}, payload keys: {list(payload.keys())}")
        
        try:
            response = requests.request(
                method=method,
                url=self.config.function_url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Function invocation successful. Status: {response.status_code}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Failed to invoke Azure Function: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Invalid JSON response from function: {str(e)}")
            raise
    
    async def invoke_function_async(
        self,
        payload: Dict[str, Any],
        method: str = "POST"
    ) -> Dict[str, Any]:
        """Invoke an Azure Function asynchronously.
        
        Args:
            payload: JSON payload to send to the function.
            method: HTTP method (GET, POST, PUT, etc.).
            
        Returns:
            The JSON response from the function.
            
        Raises:
            aiohttp.ClientError: If the request fails.
            ValueError: If the response is not valid JSON.
        """
        logger.info(f"Invoking Azure Function asynchronously: {self.config.function_url}")
        logger.debug(f"Request method: {method}, payload keys: {list(payload.keys())}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=self.config.function_url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    logger.info(f"Async function invocation successful. Status: {response.status}")
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error(f"Failed to invoke Azure Function asynchronously: {str(e)}")
            raise
        except ValueError as e:
            logger.error(f"Invalid JSON response from function: {str(e)}")
            raise


class DataProcessorFunction:
    """Sample Azure Function tool for data processing.
    
    This class demonstrates how to wrap an Azure Function as a tool
    that can be used by an AI Foundry agent.
    
    Example:
        >>> config = FunctionConfig(
        ...     function_url="https://myapp.azurewebsites.net/api/process-data",
        ...     function_key="key123"
        ... )
        >>> processor = DataProcessorFunction(config)
        >>> result = processor.process_data({"values": [1, 2, 3]})
    """
    
    def __init__(self, config: FunctionConfig) -> None:
        """Initialize the data processor function.
        
        Args:
            config: Configuration for the Azure Function.
        """
        self.client = AzureFunctionsClient(config)
        logger.info("Initialized DataProcessorFunction")
    
    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data using the Azure Function.
        
        Args:
            data: Input data to process.
            
        Returns:
            Processed data from the function.
        """
        logger.info("Processing data through Azure Function")
        
        try:
            result = self.client.invoke_function({
                "operation": "process",
                "data": data
            })
            logger.info("Data processing completed successfully")
            return result
        except Exception as e:
            logger.error(f"Data processing failed: {str(e)}")
            raise


class IntegrationFunction:
    """Sample Azure Function tool for system integration.
    
    This class demonstrates a second Azure Function that performs
    integration tasks, such as calling external APIs or services.
    
    Example:
        >>> config = FunctionConfig(
        ...     function_url="https://myapp.azurewebsites.net/api/integrate",
        ...     function_key="key123"
        ... )
        >>> integration = IntegrationFunction(config)
        >>> result = integration.call_external_service(
        ...     service="weather-api",
        ...     params={"location": "Chicago"}
        ... )
    """
    
    def __init__(self, config: FunctionConfig) -> None:
        """Initialize the integration function.
        
        Args:
            config: Configuration for the Azure Function.
        """
        self.client = AzureFunctionsClient(config)
        logger.info("Initialized IntegrationFunction")
    
    def call_external_service(
        self,
        service: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call an external service through the Azure Function.
        
        Args:
            service: Name of the external service to call.
            params: Parameters to pass to the service.
            
        Returns:
            Response from the external service.
        """
        logger.info(f"Calling external service '{service}' through Azure Function")
        
        try:
            result = self.client.invoke_function({
                "service": service,
                "parameters": params
            })
            logger.info(f"External service call to '{service}' completed successfully")
            return result
        except Exception as e:
            logger.error(f"External service call to '{service}' failed: {str(e)}")
            raise
