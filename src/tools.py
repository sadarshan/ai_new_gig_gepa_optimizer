from typing import Dict, Any, List


def get_available_tools() -> List[Dict[str, Any]]:
    """
    Returns the list of available tools for the sourcing concierge AI.
    """
    return [
        {
            "name": "submit_request",
            "description": "Submit a sourcing request for a product or service to suppliers",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_description": {
                        "type": "string", 
                        "description": "Detailed description of the product/service needed"
                    },
                    "quantity": {
                        "type": "integer", 
                        "description": "Quantity required"
                    },
                    "budget": {
                        "type": "number", 
                        "description": "Budget range or maximum budget"
                    },
                    "timeline": {
                        "type": "string", 
                        "description": "When the product/service is needed"
                    },
                    "specifications": {
                        "type": "object", 
                        "description": "Additional specifications or requirements"
                    }
                },
                "required": ["product_description", "quantity"]
            }
        },
        {
            "name": "cancel_request",
            "description": "Cancel an existing sourcing request",
            "parameters": {
                "type": "object",
                "properties": {
                    "request_id": {
                        "type": "string", 
                        "description": "ID of the request to cancel"
                    },
                    "reason": {
                        "type": "string", 
                        "description": "Reason for cancellation"
                    }
                },
                "required": ["request_id"]
            }
        },
        {
            "name": "reply_to_buyer",
            "description": "Send a message back to the buyer with information, questions, or updates",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string", 
                        "description": "Message to send to the buyer"
                    },
                    "message_type": {
                        "type": "string", 
                        "enum": ["question", "information", "update", "clarification"], 
                        "description": "Type of message being sent"
                    },
                    "requires_response": {
                        "type": "boolean", 
                        "description": "Whether this message requires a response from the buyer"
                    }
                },
                "required": ["message", "message_type"]
            }
        }
    ]


def get_tool_names() -> List[str]:
    """
    Returns just the names of available tools.
    """
    return [tool["name"] for tool in get_available_tools()]