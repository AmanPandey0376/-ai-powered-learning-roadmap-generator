"""
Resource Service

This module provides core business logic for managing learning resources.
It handles loading resources from JSON files, filtering by skill,
and formatting responses for the API endpoints.
"""

import json
import os
import re
import logging
from typing import Dict, List, Optional, Any
from utils.helpers import load_json_file, get_data_file_path, normalize_skill_name


class ResourceService:
    """
    Service class for managing and retrieving learning resources.
    
    Handles loading resources from JSON data, filtering by skill,
    and formatting responses for both free and paid resources.
    """
    
    def __init__(self):
        """Initialize the resource service with empty cache."""
        self._resources_data: Optional[Dict[str, Any]] = None
        self._data_file_path = get_data_file_path('resources.json')
        logging.info("ResourceService initialized")
    
    def load_resources_data(self) -> Dict[str, Any]:
        """
        Load resources from JSON file with caching.
        
        Returns:
            Dict containing all resources keyed by skill name
            
        Raises:
            FileNotFoundError: If the resources file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
        """
        if self._resources_data is None:
            try:
                logging.info(f"Loading resources data from: {self._data_file_path}")
                self._resources_data = load_json_file(self._data_file_path)
                logging.info(f"Successfully loaded resources for {len(self._resources_data)} skills")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logging.error(f"Failed to load resources data: {str(e)}")
                raise
            except Exception as e:
                logging.error(f"Unexpected error loading resources data: {str(e)}")
                raise
        
        return self._resources_data
    
    def normalize_skill_name(self, skill: str) -> str:
        """
        Normalize skill name for consistent lookup.
        
        Uses the centralized normalize_skill_name function from helpers.
        
        Args:
            skill: Raw skill name from user input
            
        Returns:
            Normalized skill name for lookup
        """
        try:
            normalized = normalize_skill_name(skill)
            logging.debug(f"Normalized skill '{skill}' to '{normalized}'")
            return normalized
        except Exception as e:
            logging.error(f"Error normalizing skill name '{skill}': {str(e)}")
            return ""
    
    def filter_resources_by_skill(self, skill: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Filter and retrieve resources for a specific skill.
        
        Args:
            skill: The skill name to filter resources for
            
        Returns:
            Dictionary with 'freeResources' and 'paidResources' arrays
            Returns empty arrays if no resources found for the skill
        """
        try:
            normalized_skill = self.normalize_skill_name(skill)
            
            if not normalized_skill:
                logging.warning(f"Empty skill name after normalization: {skill}")
                return {"freeResources": [], "paidResources": []}
            
            logging.info(f"Filtering resources for skill: {skill} (normalized: {normalized_skill})")
            
            # Load resources data
            resources_data = self.load_resources_data()
            
            # Check if we have resources for this skill
            if normalized_skill in resources_data:
                skill_resources = resources_data[normalized_skill]
                result = {
                    "freeResources": skill_resources.get("freeResources", []),
                    "paidResources": skill_resources.get("paidResources", [])
                }
                logging.info(f"Found {len(result['freeResources'])} free and {len(result['paidResources'])} paid resources for: {normalized_skill}")
                return result
            
            # Return empty arrays if no resources found
            logging.info(f"No resources found for skill: {normalized_skill}")
            return {"freeResources": [], "paidResources": []}
            
        except Exception as e:
            logging.error(f"Error filtering resources for skill '{skill}': {str(e)}")
            return {"freeResources": [], "paidResources": []}
    
    def get_resources(self, skill: str) -> Dict[str, Any]:
        """
        Get formatted resources for specified skill.
        
        Retrieves both free and paid resources for the skill and formats
        them according to the API response specification.
        
        Args:
            skill: The skill name to get resources for
            
        Returns:
            Complete resources dictionary with skill, freeResources, and paidResources
            
        Raises:
            ValueError: If skill parameter is empty or invalid
        """
        try:
            if not skill or not isinstance(skill, str):
                raise ValueError("Skill parameter must be a non-empty string")
            
            normalized_skill = self.normalize_skill_name(skill)
            
            if not normalized_skill:
                raise ValueError("Skill name cannot be empty after normalization")
            
            logging.info(f"Getting resources for skill: {skill}")
            
            # Get filtered resources
            resources = self.filter_resources_by_skill(skill)
            
            # Format response according to API specification
            result = self.format_resource_response(skill, resources)
            logging.info(f"Successfully retrieved resources for: {skill}")
            return result
            
        except ValueError as e:
            logging.warning(f"Validation error in get_resources: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in get_resources for skill '{skill}': {str(e)}")
            raise
    
    def format_resource_response(self, skill: str, resources: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Format resource data for API response.
        
        Ensures the response matches the expected API format with proper
        field names and structure.
        
        Args:
            skill: Original skill name from request
            resources: Dictionary containing freeResources and paidResources arrays
            
        Returns:
            Formatted response dictionary ready for JSON serialization
        """
        return {
            "skill": skill,
            "freeResources": resources.get("freeResources", []),
            "paidResources": resources.get("paidResources", [])
        }


# Create a singleton instance for use across the application
resource_service = ResourceService()


def get_resources_for_skill(skill: str) -> Dict[str, Any]:
    """
    Convenience function to get resources for a skill.
    
    Args:
        skill: The skill name to get resources for
        
    Returns:
        Complete resources dictionary
        
    Raises:
        ValueError: If skill parameter is invalid
        FileNotFoundError: If resources data file is missing
        json.JSONDecodeError: If resources data file is malformed
    """
    return resource_service.get_resources(skill)


def load_resources_data() -> Dict[str, Any]:
    """
    Convenience function to load resources data.
    
    Returns:
        Dictionary of all resources data
        
    Raises:
        FileNotFoundError: If resources data file is missing
        json.JSONDecodeError: If resources data file is malformed
    """
    return resource_service.load_resources_data()