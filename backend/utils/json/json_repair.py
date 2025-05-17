"""
JSON repair utilities for fixing malformed JSON from LLM responses.

This module provides functions to repair and validate JSON data from LLM responses,
particularly focusing on common issues with Gemini's JSON output.
"""

import json
import re
import logging
from typing import Any, Dict, List, Union, Optional

logger = logging.getLogger(__name__)

def repair_json(json_str: str) -> str:
    """
    Repair common JSON formatting issues in LLM responses, with special handling for truncated responses.

    Args:
        json_str: The potentially malformed JSON string

    Returns:
        A repaired JSON string that should be parseable
    """
    if not json_str or not isinstance(json_str, str):
        return "{}"

    logger.info(f"Attempting to repair JSON (first 100 chars): {json_str[:100]}...")

    # Step 1: Remove any markdown code block markers
    json_str = re.sub(r'```(?:json)?\s*([\s\S]*?)\s*```', r'\1', json_str)

    # Step 2: Extract JSON if it's embedded in other text
    json_match = re.search(r'({[\s\S]*}|\[[\s\S]*\])', json_str)
    if json_match:
        json_str = json_match.group(1)

    # Step 3: Handle truncated JSON arrays
    if json_str.strip().startswith('[') and not json_str.strip().endswith(']'):
        logger.warning("Detected truncated JSON array. Attempting to close the array.")
        # Count open and close brackets to determine nesting level
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        missing_close_brackets = open_brackets - close_brackets

        # Add missing closing brackets
        if missing_close_brackets > 0:
            # First check if we're in the middle of an object
            last_open_brace = json_str.rfind('{')
            last_close_brace = json_str.rfind('}')

            if last_open_brace > last_close_brace:
                # We're in the middle of an object, close it first
                json_str += '}'

            # Now close any array brackets
            json_str += ']' * missing_close_brackets
            logger.info(f"Added {missing_close_brackets} closing brackets to truncated array")

    # Step 4: Handle truncated JSON objects
    if json_str.strip().startswith('{') and not json_str.strip().endswith('}'):
        logger.warning("Detected truncated JSON object. Attempting to close the object.")
        # Count open and close braces to determine nesting level
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        missing_close_braces = open_braces - close_braces

        # Add missing closing braces
        if missing_close_braces > 0:
            json_str += '}' * missing_close_braces
            logger.info(f"Added {missing_close_braces} closing braces to truncated object")

    # Step 5: Fix truncated array elements
    # Look for array elements that might be cut off
    if '",' in json_str[-5:] or '},' in json_str[-5:]:
        logger.warning("Detected truncated array element. Removing trailing comma.")
        json_str = re.sub(r'[",}],\s*$', r'\1', json_str)

    # Step 6: Fix truncated property names or values
    # If the string ends with a colon or a colon and some whitespace, it's likely a truncated property
    if re.search(r':\s*$', json_str):
        logger.warning("Detected truncated property. Adding empty string value.")
        json_str += '""'

    # Step 7: Fix trailing commas in objects and arrays
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*\]', ']', json_str)

    # Step 8: Fix missing quotes around property names
    json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)

    # Step 9: Fix single quotes used instead of double quotes
    # This is more complex as we need to avoid replacing single quotes within strings
    in_string = False
    in_escape = False
    result = []

    for char in json_str:
        if char == '\\' and not in_escape:
            in_escape = True
            result.append(char)
        elif in_escape:
            in_escape = False
            result.append(char)
        elif char == '"' and not in_escape:
            in_string = not in_string
            result.append(char)
        elif char == "'" and not in_string and not in_escape:
            # Replace single quotes with double quotes when not in a string
            result.append('"')
        else:
            result.append(char)

    json_str = ''.join(result)

    # Step 10: Fix unquoted string values
    # This is a heuristic and may not catch all cases
    json_str = re.sub(r':\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*([,}])', r':"\1"\2', json_str)

    # Step 11: Fix missing commas between array elements
    json_str = re.sub(r'}\s*{', '},{', json_str)
    json_str = re.sub(r'"\s*{', '",{', json_str)
    json_str = re.sub(r'}\s*"', '},"', json_str)
    json_str = re.sub(r'"\s*"', '","', json_str)

    # Step 12: Fix missing commas between object properties
    json_str = re.sub(r'"\s*"', '","', json_str)

    # Step 13: Fix boolean and null values
    json_str = re.sub(r':\s*True\s*([,}])', r':true\1', json_str)
    json_str = re.sub(r':\s*False\s*([,}])', r':false\1', json_str)
    json_str = re.sub(r':\s*None\s*([,}])', r':null\1', json_str)

    # Step 14: Fix numeric values
    # This is a heuristic and may not catch all cases
    json_str = re.sub(r':\s*([0-9]+\.[0-9]+)\s*([,}])', r':\1\2', json_str)
    json_str = re.sub(r':\s*([0-9]+)\s*([,}])', r':\1\2', json_str)

    # Final validation check - try to parse and fix if still invalid
    try:
        json.loads(json_str)
        logger.info("JSON repair successful - valid JSON produced")
    except json.JSONDecodeError as e:
        logger.warning(f"JSON still invalid after repair: {e}. Attempting last-resort fixes.")

        # Last resort: if it's supposed to be an array but still broken,
        # create a minimal valid array with whatever complete elements we can extract
        if json_str.strip().startswith('['):
            try:
                # Try to extract valid array elements
                elements = re.findall(r'({[^{}]*}|"[^"]*"|\[[^\[\]]*\]|true|false|null|-?\d+(?:\.\d+)?)', json_str)
                if elements:
                    json_str = '[' + ','.join(elements) + ']'
                    logger.info(f"Created minimal valid array with {len(elements)} elements")
                else:
                    json_str = '[]'
                    logger.warning("Could not extract any valid elements, returning empty array")
            except Exception as ex:
                logger.error(f"Error during last-resort array repair: {ex}")
                json_str = '[]'

        # If it's supposed to be an object but still broken, create a minimal valid object
        elif json_str.strip().startswith('{'):
            try:
                # Try to extract valid key-value pairs
                # This regex looks for "key": value patterns
                pairs = re.findall(r'"([^"]+)"\s*:\s*({[^{}]*}|"[^"]*"|\[[^\[\]]*\]|true|false|null|-?\d+(?:\.\d+)?)', json_str)
                if pairs:
                    json_str = '{' + ','.join([f'"{k}": {v}' for k, v in pairs]) + '}'
                    logger.info(f"Created minimal valid object with {len(pairs)} properties")
                else:
                    json_str = '{}'
                    logger.warning("Could not extract any valid key-value pairs, returning empty object")
            except Exception as ex:
                logger.error(f"Error during last-resort object repair: {ex}")
                json_str = '{}'

    return json_str

def parse_json_safely(json_str: str, default_type: str = "object") -> Union[Dict[str, Any], List[Any]]:
    """
    Parse JSON with repair attempts if initial parsing fails.

    Args:
        json_str: The JSON string to parse
        default_type: The default type to return if parsing fails ("object" or "array")

    Returns:
        The parsed JSON object/array or an empty dict/list if parsing fails
    """
    if not json_str:
        return {} if default_type == "object" else []

    # Log the first part of the JSON string for debugging
    logger.info(f"Attempting to parse JSON safely (first 100 chars): {json_str[:100]}...")

    try:
        # First attempt: direct parsing
        parsed = json.loads(json_str)
        logger.info(f"Successfully parsed JSON directly: {type(parsed).__name__}")
        return parsed
    except json.JSONDecodeError as e:
        logger.warning(f"Initial JSON parsing failed: {e}. Attempting repair.")

        # Second attempt: repair and parse
        try:
            repaired = repair_json(json_str)
            parsed = json.loads(repaired)
            logger.info(f"Successfully parsed JSON after repair: {type(parsed).__name__}")
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON even after repair: {e}")

            # Determine what type of structure we should return based on the content
            if json_str.strip().startswith('['):
                logger.warning("JSON appears to be an array. Returning empty array.")
                return []
            else:
                logger.warning("JSON appears to be an object. Returning empty object.")
                return {}
        except Exception as e:
            logger.error(f"Unexpected error during JSON repair: {e}")
            return {} if default_type == "object" else []


def parse_json_array_safely(json_str: str) -> List[Any]:
    """
    Parse JSON array with repair attempts if initial parsing fails.

    Args:
        json_str: The JSON string to parse

    Returns:
        The parsed JSON array or an empty list if parsing fails
    """
    result = parse_json_safely(json_str, default_type="array")

    # Ensure the result is a list
    if not isinstance(result, list):
        logger.warning(f"Expected array but got {type(result).__name__}. Converting to array.")
        if isinstance(result, dict):
            # If we got a dict, wrap it in a list
            return [result]
        else:
            # For any other type, return empty list
            return []

    return result
