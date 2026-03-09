"""
Roadmap Generator Service

This module provides core business logic for generating learning roadmaps.
It handles loading sample roadmaps from JSON files, skill name normalization,
and default roadmap generation for unknown skills.
"""

import json
import os
import re
import logging
from typing import Dict, List, Optional, Any
from utils.helpers import load_json_file, get_data_file_path, normalize_skill_name


class RoadmapGenerator:
    """
    Service class for generating and managing learning roadmaps.
    
    Handles both pre-defined roadmaps from JSON data and dynamic generation
    of default roadmaps for skills not in the sample data.
    """
    
    def __init__(self):
        """Initialize the roadmap generator with empty cache."""
        self._sample_roadmaps: Optional[Dict[str, Any]] = None
        self._data_file_path = get_data_file_path('sample_roadmaps.json')
        logging.info("RoadmapGenerator initialized")
    
    def load_sample_roadmaps(self) -> Dict[str, Any]:
        """
        Load sample roadmaps from JSON file with caching.
        
        Returns:
            Dict containing all sample roadmaps keyed by skill name
            
        Raises:
            FileNotFoundError: If the sample roadmaps file doesn't exist
            json.JSONDecodeError: If the JSON file is malformed
        """
        if self._sample_roadmaps is None:
            try:
                logging.info(f"Loading sample roadmaps from: {self._data_file_path}")
                self._sample_roadmaps = load_json_file(self._data_file_path)
                logging.info(f"Successfully loaded {len(self._sample_roadmaps)} sample roadmaps")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logging.error(f"Failed to load sample roadmaps: {str(e)}")
                raise
            except Exception as e:
                logging.error(f"Unexpected error loading sample roadmaps: {str(e)}")
                raise
        
        return self._sample_roadmaps
    
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
    
    def get_roadmap(self, skill: str) -> Dict[str, Any]:
        """
        Get roadmap for specified skill.
        
        First attempts to find a pre-defined roadmap in sample data.
        If not found, generates a default roadmap structure.
        
        Args:
            skill: The skill name to generate roadmap for
            
        Returns:
            Complete roadmap dictionary with skill, title, modules, and majorProject
            
        Raises:
            ValueError: If skill parameter is empty or invalid
        """
        try:
            if not skill or not isinstance(skill, str):
                raise ValueError("Skill parameter must be a non-empty string")
            
            normalized_skill = self.normalize_skill_name(skill)
            
            if not normalized_skill:
                raise ValueError("Skill name cannot be empty after normalization")
            
            logging.info(f"Generating roadmap for skill: {skill} (normalized: {normalized_skill})")
            
            # Load sample roadmaps
            sample_roadmaps = self.load_sample_roadmaps()
            
            # Check if we have a pre-defined roadmap (exact match first)
            if normalized_skill in sample_roadmaps:
                logging.info(f"Found pre-defined roadmap for: {normalized_skill}")
                roadmap = sample_roadmaps[normalized_skill].copy()
                roadmap['skill'] = skill  # Use original skill name in response
                return roadmap
            
            # Try fuzzy matching for similar skills
            matched_skill = self.find_similar_skill(normalized_skill, sample_roadmaps)
            if matched_skill:
                logging.info(f"Found similar roadmap '{matched_skill}' for: {normalized_skill}")
                roadmap = sample_roadmaps[matched_skill].copy()
                roadmap['skill'] = skill  # Use original skill name in response
                return roadmap
            
            # Generate default roadmap for unknown skill
            logging.info(f"Generating default roadmap for unknown skill: {skill}")
            return self.generate_default_roadmap(skill)
            
        except ValueError as e:
            logging.warning(f"Validation error in get_roadmap: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error in get_roadmap for skill '{skill}': {str(e)}")
            raise
    
    def find_similar_skill(self, skill: str, available_skills: Dict[str, Any]) -> Optional[str]:
        """
        Find similar skill using fuzzy matching and synonyms.
        
        Args:
            skill: The normalized skill to match
            available_skills: Dictionary of available skills
            
        Returns:
            Matching skill name or None if no match found
        """
        # Define skill synonyms and variations
        skill_synonyms = {
            'data science': ['data scientist', 'data analytics', 'data analysis'],
            'data scientist': ['data science', 'data analytics', 'data analysis'],
            'machine learning': ['ml', 'machine learning engineer', 'ai engineer'],
            'artificial intelligence': ['ai', 'machine learning', 'ai engineer'],
            'web development': ['web developer', 'frontend developer', 'backend developer'],
            'full stack': ['full stack developer', 'fullstack developer', 'web developer'],
            'react': ['react developer', 'react js', 'reactjs'],
            'python': ['python developer', 'python programming'],
            'javascript': ['js', 'javascript developer', 'js developer'],
        }
        
        # Check direct synonyms
        for available_skill in available_skills.keys():
            # Check if current skill is a synonym of available skill
            if skill in skill_synonyms.get(available_skill, []):
                return available_skill
            
            # Check if available skill is a synonym of current skill
            if available_skill in skill_synonyms.get(skill, []):
                return available_skill
        
        # Check partial matches (contains)
        for available_skill in available_skills.keys():
            # Check if skill contains available skill or vice versa
            if skill in available_skill or available_skill in skill:
                # Prefer longer matches (more specific)
                if len(available_skill) >= 3:  # Avoid matching very short terms
                    return available_skill
        
        return None
    
    def generate_default_roadmap(self, skill: str) -> Dict[str, Any]:
        """
        Generate a default roadmap structure for unknown skills.
        
        Creates a progressive learning path with 4 modules, each containing
        relevant mini-projects, plus a comprehensive capstone project.
        
        Args:
            skill: The skill name to generate roadmap for
            
        Returns:
            Complete default roadmap dictionary
        """
        try:
            logging.info(f"Generating default roadmap for: {skill}")
            
            # Capitalize skill name for title
            skill_title = skill.title()
            
            # Generate 4 progressive learning modules
            modules = [
            {
                "id": 1,
                "name": f"{skill_title} Fundamentals",
                "description": f"Learn the core concepts and basics of {skill}",
                "miniProjects": [
                    {
                        "name": f"Basic {skill_title} Project",
                        "description": f"Build a simple project to practice {skill} fundamentals",
                        "estimatedHours": 8
                    },
                    {
                        "name": f"{skill_title} Exercise Collection",
                        "description": f"Complete a series of exercises to reinforce {skill} concepts",
                        "estimatedHours": 6
                    }
                ]
            },
            {
                "id": 2,
                "name": f"Intermediate {skill_title}",
                "description": f"Build on fundamentals with more advanced {skill} techniques",
                "miniProjects": [
                    {
                        "name": f"{skill_title} Application",
                        "description": f"Create a functional application using intermediate {skill} concepts",
                        "estimatedHours": 12
                    },
                    {
                        "name": f"Problem-Solving with {skill_title}",
                        "description": f"Solve real-world problems using {skill} methodologies",
                        "estimatedHours": 10
                    }
                ]
            },
            {
                "id": 3,
                "name": f"Advanced {skill_title} Techniques",
                "description": f"Master advanced patterns and best practices in {skill}",
                "miniProjects": [
                    {
                        "name": f"Complex {skill_title} System",
                        "description": f"Build a complex system demonstrating advanced {skill} concepts",
                        "estimatedHours": 16
                    },
                    {
                        "name": f"{skill_title} Optimization Project",
                        "description": f"Focus on performance and optimization in {skill}",
                        "estimatedHours": 14
                    }
                ]
            },
            {
                "id": 4,
                "name": f"Professional {skill_title} Development",
                "description": f"Learn industry standards, testing, and deployment for {skill}",
                "miniProjects": [
                    {
                        "name": f"{skill_title} Testing Suite",
                        "description": f"Implement comprehensive testing for {skill} projects",
                        "estimatedHours": 12
                    },
                    {
                        "name": f"Production-Ready {skill_title} App",
                        "description": f"Deploy a production-ready application using {skill}",
                        "estimatedHours": 18
                    }
                ]
            }
            ]
            
            # Generate major capstone project
            major_project = {
                "name": f"Complete {skill_title} Portfolio Project",
                "description": f"Build a comprehensive project that demonstrates mastery of {skill} concepts and best practices",
                "requirements": [
                    f"Implement core {skill} functionality",
                    f"Follow {skill} best practices and design patterns",
                    "Include comprehensive documentation",
                    "Add testing and quality assurance",
                    "Deploy to production environment",
                    "Demonstrate problem-solving skills"
                ],
                "estimatedHours": 50
            }
            
            roadmap = {
                "skill": skill,
                "title": f"Complete {skill_title} Learning Roadmap",
                "modules": modules,
                "majorProject": major_project
            }
            
            logging.info(f"Successfully generated default roadmap for: {skill}")
            return roadmap
            
        except Exception as e:
            logging.error(f"Error generating default roadmap for '{skill}': {str(e)}")
            raise


# Create a singleton instance for use across the application
roadmap_generator = RoadmapGenerator()


def get_roadmap_for_skill(skill: str) -> Dict[str, Any]:
    """
    Convenience function to get roadmap for a skill.
    
    Args:
        skill: The skill name to generate roadmap for
        
    Returns:
        Complete roadmap dictionary
        
    Raises:
        ValueError: If skill parameter is invalid
        FileNotFoundError: If sample data file is missing
        json.JSONDecodeError: If sample data file is malformed
    """
    return roadmap_generator.get_roadmap(skill)


def load_sample_roadmaps() -> Dict[str, Any]:
    """
    Convenience function to load sample roadmaps.
    
    Returns:
        Dictionary of all sample roadmaps
        
    Raises:
        FileNotFoundError: If sample data file is missing
        json.JSONDecodeError: If sample data file is malformed
    """
    return roadmap_generator.load_sample_roadmaps()