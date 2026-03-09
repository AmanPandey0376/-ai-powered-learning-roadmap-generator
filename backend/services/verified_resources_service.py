#!/usr/bin/env python3
"""
Verified Resources Service
Manages a curated list of verified learning resources with working URLs.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
from services.url_validator import validate_resource_urls

class VerifiedResourcesService:
    """
    Service for managing verified learning resources.
    """
    
    def __init__(self):
        """Initialize the verified resources service."""
        self.resources_data = None
        self.data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'verified_resources.json')
        logging.info("Verified Resources Service initialized")
    
    def load_verified_resources(self) -> Dict[str, Any]:
        """
        Load verified resources from JSON file.
        
        Returns:
            Dictionary containing verified resources
        """
        if self.resources_data is None:
            try:
                with open(self.data_file_path, 'r', encoding='utf-8') as file:
                    self.resources_data = json.load(file)
                logging.info(f"Loaded verified resources for {len(self.resources_data)} skills")
            except FileNotFoundError:
                logging.error(f"Verified resources file not found: {self.data_file_path}")
                self.resources_data = {}
            except json.JSONDecodeError as e:
                logging.error(f"Error parsing verified resources JSON: {str(e)}")
                self.resources_data = {}
            except Exception as e:
                logging.error(f"Unexpected error loading verified resources: {str(e)}")
                self.resources_data = {}
        
        return self.resources_data
    
    def get_skill_key(self, skill: str) -> str:
        """
        Convert skill name to resource key format.
        
        Args:
            skill: The skill name
            
        Returns:
            Normalized skill key
        """
        skill_lower = skill.lower().strip()
        
        # Map common skill variations to resource keys
        skill_mappings = {
            'data science': 'data_science',
            'data scientist': 'data_science',
            'machine learning': 'data_science',
            'ml': 'data_science',
            'ai': 'data_science',
            'artificial intelligence': 'data_science',
            
            'web development': 'web_development',
            'web developer': 'web_development',
            'frontend': 'web_development',
            'frontend developer': 'web_development',
            'backend': 'web_development',
            'backend developer': 'web_development',
            'full stack': 'web_development',
            'fullstack': 'web_development',
            'full stack developer': 'web_development',
            'react': 'web_development',
            'react developer': 'web_development',
            'javascript': 'web_development',
            'js': 'web_development',
            'html': 'web_development',
            'css': 'web_development',
            'node.js': 'web_development',
            'nodejs': 'web_development',
            
            'python': 'python',
            'python developer': 'python',
            'python programming': 'python',
        }
        
        return skill_mappings.get(skill_lower, 'python')  # Default to python if not found
    
    def get_verified_resources(self, skill: str, validate_urls: bool = True) -> Dict[str, Any]:
        """
        Get verified resources for a specific skill.
        
        Args:
            skill: The skill to get resources for
            validate_urls: Whether to validate URLs before returning
            
        Returns:
            Dictionary with verified resources
        """
        try:
            # Load verified resources
            all_resources = self.load_verified_resources()
            
            # Get skill key
            skill_key = self.get_skill_key(skill)
            
            # Get resources for the skill
            skill_resources = all_resources.get(skill_key, {})
            
            if not skill_resources:
                logging.warning(f"No verified resources found for skill: {skill} (key: {skill_key})")
                return {
                    "skill": skill,
                    "freeResources": [],
                    "paidResources": [],
                    "metadata": {
                        "source": "verified_resources",
                        "validated": False,
                        "skill_key": skill_key
                    }
                }
            
            # Format response
            resources_response = {
                "skill": skill,
                "freeResources": skill_resources.get("freeResources", []),
                "paidResources": skill_resources.get("paidResources", []),
                "metadata": {
                    "source": "verified_resources",
                    "validated": validate_urls,
                    "skill_key": skill_key
                }
            }
            
            # Validate URLs if requested
            if validate_urls:
                logging.info(f"Validating URLs for {skill} resources...")
                resources_response = validate_resource_urls(resources_response)
            
            logging.info(f"Retrieved {len(resources_response['freeResources'])} free and {len(resources_response['paidResources'])} paid resources for: {skill}")
            return resources_response
            
        except Exception as e:
            logging.error(f"Error getting verified resources for {skill}: {str(e)}")
            return {
                "skill": skill,
                "freeResources": [],
                "paidResources": [],
                "metadata": {
                    "source": "verified_resources",
                    "validated": False,
                    "error": str(e)
                }
            }
    
    def get_all_skills(self) -> List[str]:
        """
        Get list of all available skills.
        
        Returns:
            List of skill names
        """
        try:
            all_resources = self.load_verified_resources()
            return list(all_resources.keys())
        except Exception as e:
            logging.error(f"Error getting skill list: {str(e)}")
            return []

# Create singleton instance
verified_resources_service = VerifiedResourcesService()

def get_verified_resources_for_skill(skill: str, validate_urls: bool = True) -> Dict[str, Any]:
    """
    Convenience function to get verified resources for a skill.
    
    Args:
        skill: The skill to get resources for
        validate_urls: Whether to validate URLs
        
    Returns:
        Dictionary with verified resources
    """
    return verified_resources_service.get_verified_resources(skill, validate_urls)