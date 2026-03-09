#!/usr/bin/env python3
"""
Real-time roadmap API route that fetches resources from multiple platforms.
"""

from flask import Blueprint, request, jsonify
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any

from utils.youtube_api import get_youtube_courses
from utils.coursera_api import get_coursera_courses
from utils.github_api import get_github_resources
from utils.ai_ranker import rank_learning_resources
from utils.helpers import validate_skill_input, create_error_response, create_success_response

# Create Blueprint for real-time roadmap routes
realtime_roadmap_bp = Blueprint('realtime_roadmap', __name__, url_prefix='/api')

class RealTimeRoadmapGenerator:
    """Real-time roadmap generator that fetches from multiple APIs."""
    
    def __init__(self):
        """Initialize the real-time roadmap generator."""
        self.max_workers = 3  # Number of concurrent API calls
        logging.info("Real-time roadmap generator initialized")
    
    def fetch_all_resources(self, skill: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch resources from all platforms concurrently.
        
        Args:
            skill: The skill to fetch resources for
            
        Returns:
            Dictionary containing resources from all platforms
        """
        try:
            logging.info(f"Fetching resources from all platforms for: {skill}")
            
            all_resources = {
                "YouTube": [],
                "Coursera": [],
                "GitHub": []
            }
            
            # Define API fetch functions
            fetch_functions = [
                ("YouTube", lambda: get_youtube_courses(skill)),
                ("Coursera", lambda: get_coursera_courses(skill)),
                ("GitHub", lambda: get_github_resources(skill))
            ]
            
            # Execute API calls concurrently
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_platform = {
                    executor.submit(func): platform 
                    for platform, func in fetch_functions
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_platform):
                    platform = future_to_platform[future]
                    try:
                        resources = future.result()
                        all_resources[platform] = resources
                        logging.info(f"Fetched {len(resources)} resources from {platform}")
                    except Exception as e:
                        logging.error(f"Error fetching from {platform}: {str(e)}")
                        all_resources[platform] = []
            
            # Log summary
            total_resources = sum(len(resources) for resources in all_resources.values())
            logging.info(f"Total resources fetched: {total_resources}")
            
            return all_resources
            
        except Exception as e:
            logging.error(f"Error fetching resources for {skill}: {str(e)}")
            return {"YouTube": [], "Coursera": [], "GitHub": []}
    
    def generate_roadmap(self, skill: str) -> Dict[str, Any]:
        """
        Generate a complete roadmap with AI-ranked resources.
        
        Args:
            skill: The skill to generate roadmap for
            
        Returns:
            Complete roadmap with best free and paid resources
        """
        try:
            logging.info(f"Generating real-time roadmap for: {skill}")
            
            # Fetch resources from all platforms
            all_resources = self.fetch_all_resources(skill)
            
            # Check if we got any resources
            total_resources = sum(len(resources) for resources in all_resources.values())
            if total_resources == 0:
                logging.warning(f"No resources found for skill: {skill}")
                return self._create_empty_roadmap(skill)
            
            # Use AI to rank and select best resources
            try:
                recommendations = rank_learning_resources(skill, all_resources)
                recommendations["skill"] = skill
                
                # Add metadata
                recommendations["metadata"] = {
                    "generation_method": "realtime_api",
                    "total_resources_found": total_resources,
                    "platforms_used": list(all_resources.keys()),
                    "ai_ranked": True
                }
                
                logging.info(f"Successfully generated real-time roadmap for: {skill}")
                return recommendations
                
            except Exception as e:
                logging.error(f"AI ranking failed, using fallback: {str(e)}")
                return self._create_fallback_roadmap(skill, all_resources)
            
        except Exception as e:
            logging.error(f"Error generating roadmap for {skill}: {str(e)}")
            return self._create_empty_roadmap(skill)
    
    def _create_empty_roadmap(self, skill: str) -> Dict[str, Any]:
        """Create an empty roadmap when no resources are found."""
        return {
            "skill": skill,
            "free": None,
            "paid": None,
            "metadata": {
                "generation_method": "realtime_api",
                "total_resources_found": 0,
                "ai_ranked": False,
                "error": "No resources found"
            }
        }
    
    def _create_fallback_roadmap(self, skill: str, all_resources: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Create a fallback roadmap when AI ranking fails."""
        roadmap = {
            "skill": skill,
            "free": None,
            "paid": None,
            "metadata": {
                "generation_method": "realtime_api_fallback",
                "total_resources_found": sum(len(resources) for resources in all_resources.values()),
                "ai_ranked": False
            }
        }
        
        # Find best free resource (prioritize YouTube)
        for platform in ["YouTube", "GitHub"]:
            if platform in all_resources and all_resources[platform]:
                best_resource = all_resources[platform][0]  # Take first (usually best)
                roadmap["free"] = {
                    "platform": best_resource.get("platform", platform),
                    "title": best_resource.get("title", ""),
                    "instructor": best_resource.get("instructor", best_resource.get("owner", "")),
                    "url": best_resource.get("url", ""),
                    "hours": best_resource.get("estimated_hours", 0),
                    "rating": best_resource.get("rating", 0),
                    "description": best_resource.get("description", "")
                }
                break
        
        # Find best paid resource (prioritize Coursera)
        for platform in ["Coursera"]:
            if platform in all_resources and all_resources[platform]:
                best_resource = all_resources[platform][0]  # Take first (usually best)
                roadmap["paid"] = {
                    "platform": best_resource.get("platform", platform),
                    "title": best_resource.get("title", ""),
                    "instructor": best_resource.get("instructor", ""),
                    "url": best_resource.get("url", ""),
                    "hours": best_resource.get("estimated_hours", 0),
                    "rating": best_resource.get("rating", 0),
                    "description": best_resource.get("description", ""),
                    "cost": best_resource.get("price", "")
                }
                break
        
        return roadmap

# Create singleton instance
roadmap_generator = RealTimeRoadmapGenerator()

@realtime_roadmap_bp.route('/roadmap/realtime', methods=['POST'])
def generate_realtime_roadmap():
    """
    Generate real-time roadmap by fetching from multiple APIs.
    
    Expected JSON payload:
    {
        "skill": "string (required)"
    }
    
    Returns:
        JSON response with AI-ranked roadmap recommendations
    """
    try:
        logging.info("Received real-time roadmap generation request")
        
        # Validate request has JSON content
        if not request.is_json:
            return create_error_response(
                "Request must contain JSON data", 
                400, 
                "Invalid Content-Type"
            )
        
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required skill parameter
        if not data:
            return create_error_response(
                "Request body must contain JSON data", 
                400, 
                "Missing JSON data"
            )
        
        if 'skill' not in data:
            return create_error_response(
                'The "skill" parameter is required', 
                400, 
                "Missing required parameter"
            )
        
        skill = data['skill']
        
        # Validate skill input using helper function
        is_valid, error_message = validate_skill_input(skill)
        if not is_valid:
            return create_error_response(error_message, 400, "ValidationError")
        
        # Generate real-time roadmap
        roadmap_data = roadmap_generator.generate_roadmap(skill.strip())
        
        logging.info(f"Successfully generated real-time roadmap for skill: {skill.strip()}")
        return create_success_response(roadmap_data, 200)
        
    except ValueError as e:
        logging.warning(f"Validation error in real-time roadmap generation: {str(e)}")
        return create_error_response(str(e), 400, "ValidationError")
        
    except Exception as e:
        logging.error(f"Unexpected error in real-time roadmap generation: {str(e)}")
        return create_error_response(
            "An unexpected error occurred while generating the roadmap", 
            500, 
            "InternalServerError"
        )

@realtime_roadmap_bp.route('/roadmap/realtime', methods=['GET'])
def realtime_roadmap_info():
    """
    Provide information about the real-time roadmap endpoint.
    
    Returns:
        JSON response with endpoint usage information
    """
    return jsonify({
        'endpoint': '/api/roadmap/realtime',
        'method': 'POST',
        'description': 'Generate real-time roadmap by fetching from multiple APIs',
        'required_parameters': {
            'skill': 'string - The skill name to generate roadmap for'
        },
        'example_request': {
            'skill': 'data science'
        },
        'response_format': {
            'skill': 'string',
            'free': {
                'platform': 'string',
                'title': 'string',
                'instructor': 'string',
                'url': 'string',
                'hours': 'number',
                'rating': 'number',
                'description': 'string'
            },
            'paid': {
                'platform': 'string',
                'title': 'string',
                'instructor': 'string',
                'url': 'string',
                'hours': 'number',
                'rating': 'number',
                'description': 'string',
                'cost': 'string'
            },
            'metadata': {
                'generation_method': 'string',
                'total_resources_found': 'number',
                'ai_ranked': 'boolean'
            }
        },
        'platforms_integrated': [
            'YouTube Data API',
            'Coursera Public API',
            'GitHub API',
            'Groq AI (for ranking)'
        ]
    }), 200