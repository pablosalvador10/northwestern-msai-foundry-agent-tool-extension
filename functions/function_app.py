"""Azure Functions for Northwestern Foundry Agent Lab.

This module contains HTTP-triggered Azure Functions for demonstrating
Azure AI Foundry agent integrations.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

import azure.functions as func

# Create the Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# Deterministic quotes for testing (no external calls)
QUOTES = {
    "motivation": [
        {
            "quote": "The only way to do great work is to love what you do.",
            "author": "Steve Jobs",
        },
        {
            "quote": "Innovation distinguishes between a leader and a follower.",
            "author": "Steve Jobs",
        },
        {
            "quote": "Stay hungry, stay foolish.",
            "author": "Steve Jobs",
        },
    ],
    "wisdom": [
        {
            "quote": "The only true wisdom is in knowing you know nothing.",
            "author": "Socrates",
        },
        {
            "quote": "In the middle of difficulty lies opportunity.",
            "author": "Albert Einstein",
        },
        {
            "quote": "Knowledge speaks, but wisdom listens.",
            "author": "Jimi Hendrix",
        },
    ],
    "humor": [
        {
            "quote": "I'm not superstitious, but I am a little stitious.",
            "author": "Michael Scott",
        },
        {
            "quote": "I used to think I was indecisive. Now I'm not so sure.",
            "author": "Unknown",
        },
        {
            "quote": "I'm on a seafood diet. I see food and I eat it.",
            "author": "Unknown",
        },
    ],
}


def get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def create_response(data: dict[str, Any], status_code: int = 200) -> func.HttpResponse:
    """Create a JSON HTTP response.

    Args:
        data: Response data dictionary.
        status_code: HTTP status code.

    Returns:
        Formatted HttpResponse with JSON content.
    """
    return func.HttpResponse(
        body=json.dumps(data, default=str),
        status_code=status_code,
        mimetype="application/json",
    )


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint.

    Returns the health status of the Azure Functions backend,
    including service information and timestamp.

    Args:
        req: The HTTP request object.

    Returns:
        JSON response with health status information.

    Example response:
        {
            "status": "healthy",
            "service_name": "northwestern-foundry-functions",
            "version": "1.0.0",
            "timestamp": "2024-01-15T10:30:00.000000+00:00",
            "details": {
                "python_version": "3.11.0",
                "function_app": "running"
            }
        }
    """
    import sys

    response_data = {
        "status": "healthy",
        "service_name": "northwestern-foundry-functions",
        "version": "1.0.0",
        "timestamp": get_current_timestamp(),
        "details": {
            "python_version": sys.version.split()[0],
            "function_app": "running",
        },
    }

    return create_response(response_data)


@app.route(route="quote", methods=["GET"])
def quote_of_the_day(req: func.HttpRequest) -> func.HttpResponse:
    """Quote of the day endpoint.

    Returns a deterministic quote based on the current day and
    requested category. No external API calls are made.

    Args:
        req: The HTTP request object.

    Query Parameters:
        category: Quote category (motivation, wisdom, humor).
                  Defaults to "motivation".

    Returns:
        JSON response with quote data.

    Example response:
        {
            "quote": "The only way to do great work is to love what you do.",
            "author": "Steve Jobs",
            "category": "motivation",
            "timestamp": "2024-01-15T10:30:00.000000+00:00"
        }
    """
    # Get category from query params
    category = req.params.get("category", "motivation").lower()

    # Validate category
    if category not in QUOTES:
        return create_response(
            {
                "error": f"Invalid category: {category}",
                "valid_categories": list(QUOTES.keys()),
            },
            status_code=400,
        )

    # Get deterministic quote based on day of year
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    quote_list = QUOTES[category]
    quote_index = day_of_year % len(quote_list)
    selected_quote = quote_list[quote_index]

    response_data = {
        "quote": selected_quote["quote"],
        "author": selected_quote["author"],
        "category": category,
        "timestamp": get_current_timestamp(),
    }

    return create_response(response_data)
