"""
Resources API Routes

This module implements Flask Blueprint for resource-related endpoints.
Provides GET /api/resources/<skill> endpoint with proper response formatting.
"""

from flask import Blueprint, jsonify
import json
import logging
from services.resource_service import get_resources_for_skill
from services.ai_resource_generator import get_ai_resources_for_skill
from services.groq_resources_generator import get_groq_resources_for_skill
from utils.helpers import validate_skill_input, create_error_response, create_success_response


# Create Blueprint for resources routes
resources_bp = Blueprint('resources', __name__, url_prefix='/api')


@resources_bp.route('/resources/<skill>', methods=['GET'])
def get_resources(skill):
    """
    Get learning resources for specified skill.
    
    URL Parameters:
        skill (string): The skill name to get resources for
    
    Returns:
        JSON response with resources data or error message
        
    Status Codes:
        200: Success - resources retrieved
        400: Bad Request - invalid skill parameter
        500: Internal Server Error - server error
    """
    try:
        logging.info(f"Received resources request for skill: {skill}")
        
        # Validate skill input using helper function
        is_valid, error_message = validate_skill_input(skill)
        if not is_valid:
            return create_error_response(error_message, 400, "ValidationError")
        
        # Get resources using comprehensive scraping with fallbacks
        try:
            # Primary: Comprehensive scraping from all platforms
            from utils.comprehensive_scraper import scrape_all_learning_resources
            resources_data = scrape_all_learning_resources(skill.strip())
            logging.info(f"Scraped comprehensive resources for: {skill.strip()}")
            
            # Check if we got resources
            if (resources_data.get('freeResources') or resources_data.get('paidResources')):
                logging.info(f"Using scraped resources: {resources_data['metadata']['total_free']} free, {resources_data['metadata']['total_paid']} paid")
            else:
                raise Exception("No scraped resources found")
                
        except Exception as e:
            logging.warning(f"Comprehensive scraping failed, trying verified resources: {e}")
            try:
                # Secondary: Verified resources with URL validation
                from services.verified_resources_service import get_verified_resources_for_skill
                resources_data = get_verified_resources_for_skill(skill.strip(), validate_urls=True)
                logging.info(f"Using verified resources for: {skill.strip()}")
            except Exception as e2:
                logging.warning(f"Verified resources failed, trying Groq AI: {e2}")
                try:
                    # Tertiary: Groq AI resource generation
                    resources_data = get_groq_resources_for_skill(skill.strip())
                    logging.info(f"Generated Groq AI resources for: {skill.strip()}")
                except Exception as e3:
                    logging.warning(f"Groq AI failed, using traditional fallback: {e3}")
                    # Final fallback: Traditional method
                    resources_data = get_resources_for_skill(skill.strip())
        
        # Return successful response
        logging.info(f"Successfully retrieved resources for skill: {skill.strip()}")
        return create_success_response(resources_data, 200)
        
    except ValueError as e:
        # Handle validation errors from service
        logging.warning(f"Validation error in resources retrieval: {str(e)}")
        return create_error_response(str(e), 400, "ValidationError")
        
    except FileNotFoundError as e:
        # Handle missing data files
        logging.error(f"Resources data file not found: {str(e)}")
        return create_error_response(
            "Resources data file not found", 
            500, 
            "DataFileError"
        )
        
    except json.JSONDecodeError as e:
        # Handle malformed JSON data files
        logging.error(f"JSON decode error in resources: {str(e)}")
        return create_error_response(
            "Resources data file is malformed", 
            500, 
            "DataFormatError"
        )
        
    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error in resources retrieval: {str(e)}")
        return create_error_response(
            "An unexpected error occurred while retrieving resources", 
            500, 
            "InternalServerError"
        )


@resources_bp.route('/resources', methods=['GET'])
def resources_info():
    """
    Provide information about the resources endpoint.
    
    Returns:
        JSON response with endpoint usage information
    """
    return jsonify({
        'endpoint': '/api/resources/<skill>',
        'method': 'GET',
        'description': 'Get learning resources for a specific skill',
        'url_parameters': {
            'skill': 'string - The skill name to get resources for'
        },
        'example_request': '/api/resources/react%20developer',
        'response_format': {
            'skill': 'string - The requested skill name',
            'freeResources': [
                {
                    'id': 'number',
                    'title': 'string',
                    'platform': 'string',
                    'creator': 'string',
                    'link': 'string',
                    'duration': 'string',
                    'description': 'string'
                }
            ],
            'paidResources': [
                {
                    'id': 'number',
                    'title': 'string',
                    'platform': 'string',
                    'creator': 'string',
                    'link': 'string',
                    'duration': 'string',
                    'price': 'string',
                    'description': 'string'
                }
            ]
        },
        'available_skills': [
            'react developer',
            'python developer',
            'machine learning engineer',
            'full stack developer',
            'data scientist'
        ]
    }), 200


# Error handlers for the blueprint
@resources_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors for resources routes."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resources endpoint was not found',
        'status': 404
    }), 404


@resources_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors for resources routes."""
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'The HTTP method is not allowed for this endpoint',
        'status': 405
    }), 405