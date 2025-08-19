from typing import Dict, Any, List


def get_available_tools() -> List[Dict[str, Any]]:
    """
    Returns the list of available tools for the sourcing concierge AI.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "submit_request",
                "parameters": {
                "type": "object",
                "required": [
                    "product_or_service",
                    "quantity_or_scope",
                    "delivery_terms",
                    "origin",
                    "delivery_location",
                    "b2b_or_b2c"
                ],
                "properties": {
                    "origin": {
                    "type": "string",
                    "description": "The origin of the product or service - country/region. you can also fill this using the delivery location's country or region"
                    },
                    "documents": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "The documents of the product or service that the buyer wants to source. If documents not found then leave it empty array"
                    },
                    "b2b_or_b2c": {
                    "type": "string",
                    "description": "Based on the specifications(volume, distance between places for services, quantity, delivery timeframe) of the product or service, the type of the product or service can be b2b or b2c"
                    },
                    "delivery_terms": {
                    "type": "string",
                    "description": "The delivery terms of the product or service"
                    },
                    "specifications": {
                    "type": "object",
                    "description": "The specifications of the product or service in key value pairs"
                    },
                    "delivery_location": {
                    "type": "string",
                    "description": "The delivery location of the product or service - country/region [mandatory]"
                    },
                    "quantity_or_scope": {
                    "type": "string",
                    "description": "The quantity of the product or scope of the service"
                    },
                    "product_or_service": {
                    "type": "string",
                    "description": "The product or service buyer is sourcing"
                    }
                }
                },
                "description": "After collecting the information from the buyer, submit the request to proceed with the sourcing process. This returns a request ID that can be shared with the buyer"
            }
        },
        {
            "type": "function",
            "function": {
                "name": "cancel_request",
                "parameters": {
                    "type": "object",
                    "required": [
                        "request_id",
                        "content"
                    ],
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content that you want to send to the buyer. Remember the buyer is the one who puts request. So content should not contain 'The buyer has requested...'"
                        },
                        "request_id": {
                            "type": "string",
                            "description": "The request ID that the buyer wants to cancel"
                        }
                    }
                },
                "description": "Use this when you want to cancel the request"
            }
        },
        {
            "type": "function",
            "function": {
                "name": "reply_to_buyer",
                "parameters": {
                    "type": "object",
                    "required": [
                        "text"
                    ],
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text that you want to send to the buyer"
                        }
                    }
                },
                "description": "When you want to reply back to the buyer"
            }
        }
    ]


def get_tool_names() -> List[str]:
    """
    Returns just the names of available tools.
    """
    return [tool["function"]["name"] for tool in get_available_tools()]