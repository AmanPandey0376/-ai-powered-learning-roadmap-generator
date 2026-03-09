"""
Utility helper functions for the Learning Roadmap Backend API.

This module provides common utilities for JSON file operations, input validation,
and error handling to ensure consistent behavior across the application.
"""

import json
import os
import re
import logging
from typing import Dict, Any, Optional, Union
from flask import jsonify


def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load and parse a JSON file with proper error handling.
    
    Args:
        file_path (str): Path to the JSON file to load
        
    Returns:
        Optional[Dict[str, Any]]: Parsed JSON data or None if error occurs
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        if not os.path.exists(file_path):
            logging.error(f"JSON file not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logging.info(f"Successfully loaded JSON file: {file_path}")
            return data
            
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in file {file_path}: {str(e)}")
        raise json.JSONDecodeError(f"Invalid JSON format in {file_path}", e.doc, e.pos)
    except Exception as e:
        logging.error(f"Unexpected error loading JSON file {file_path}: {str(e)}")
        raise


def sanitize_skill_input(skill: str) -> str:
    """
    Sanitize and normalize skill input for consistent processing.
    
    Args:
        skill (str): Raw skill input from user
        
    Returns:
        str: Sanitized and normalized skill name
    """
    if not skill or not isinstance(skill, str):
        return ""
    
    # Remove extra whitespace and convert to lowercase
    sanitized = skill.strip().lower()
    
    # Remove special characters except spaces, hyphens, and plus signs
    sanitized = re.sub(r'[^\w\s\-\+]', '', sanitized)
    
    # Replace multiple spaces with single space
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Limit length to prevent abuse
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized


def validate_skill_input(skill: Union[str, None]) -> tuple[bool, str]:
    """
    Validate skill input and return validation result.
    
    Args:
        skill (Union[str, None]): Skill input to validate
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if skill is None:
        return False, "Skill parameter is required"
    
    if not isinstance(skill, str):
        return False, "Skill must be a string"
    
    sanitized_skill = sanitize_skill_input(skill)
    
    if not sanitized_skill:
        return False, "Skill cannot be empty or contain only special characters"
    
    if len(sanitized_skill) < 2:
        return False, "Skill must be at least 2 characters long"
    
    return True, ""


def create_error_response(error_message: str, status_code: int = 400, error_type: str = "ValidationError") -> tuple:
    """
    Create a standardized error response for API endpoints.
    
    Args:
        error_message (str): Human-readable error message
        status_code (int): HTTP status code (default: 400)
        error_type (str): Type of error (default: "ValidationError")
        
    Returns:
        tuple: (response_object, status_code)
    """
    error_response = {
        "error": error_type,
        "message": error_message,
        "status": status_code
    }
    
    logging.warning(f"API Error Response: {error_type} - {error_message} (Status: {status_code})")
    
    return jsonify(error_response), status_code


def create_success_response(data: Dict[str, Any], status_code: int = 200) -> tuple:
    """
    Create a standardized success response for API endpoints.
    
    Args:
        data (Dict[str, Any]): Response data
        status_code (int): HTTP status code (default: 200)
        
    Returns:
        tuple: (response_object, status_code)
    """
    logging.info(f"API Success Response: Status {status_code}")
    return jsonify(data), status_code


def get_data_file_path(filename: str) -> str:
    """
    Get the full path to a data file in the data directory.
    
    Args:
        filename (str): Name of the data file
        
    Returns:
        str: Full path to the data file
    """
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to backend directory, then into data directory
    backend_dir = os.path.dirname(current_dir)
    data_path = os.path.join(backend_dir, 'data', filename)
    
    return data_path


def normalize_skill_name(skill: str) -> str:
    """
    Normalize skill name for consistent lookup in data files.
    
    Args:
        skill (str): Raw skill name
        
    Returns:
        str: Normalized skill name for data lookup
    """
    if not skill:
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized = skill.strip().lower()
    
    # Handle common variations and synonyms
    skill_mappings = {
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'react.js': 'react',
        'reactjs': 'react',
        'vue.js': 'vue',
        'vuejs': 'vue',
        'node.js': 'nodejs',
        'node': 'nodejs',
        'frontend': 'frontend development',
        'backend': 'backend development',
        'fullstack': 'full stack development',
        'full-stack': 'full stack development',
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'devops': 'devops',
        'dev ops': 'devops'
    }
    
    # Check for exact matches first
    if normalized in skill_mappings:
        return skill_mappings[normalized]
    
    # Check for partial matches (e.g., "react developer" -> "react")
    for key, value in skill_mappings.items():
        if key in normalized:
            return value
    
    return normalized


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('backend.log')
        ]
    )
    
    logging.info(f"Logging initialized with level: {log_level}")