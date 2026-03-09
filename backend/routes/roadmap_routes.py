"""
Roadmap API Routes

This module implements Flask Blueprint for roadmap-related endpoints.
Provides POST /api/roadmap endpoint with input validation and error handling.
"""

from flask import Blueprint, request, jsonify
import json
import logging
from services.roadmap_generator import get_roadmap_for_skill
from services.ai_roadmap_generator import get_ai_roadmap_for_skill
from services.groq_ai_generator import get_groq_roadmap_for_skill
from utils.helpers import validate_skill_input, create_error_response, create_success_response


# Create Blueprint for roadmap routes
roadmap_bp = Blueprint('roadmap', __name__, url_prefix='/api')


@roadmap_bp.route('/roadmap', methods=['POST'])
def generate_roadmap():
    """
    Generate learning roadmap for specified skill.
    
    Expected JSON payload:
    {
        "skill": "string (required)"
    }
    
    Returns:
        JSON response with roadmap data or error message
        
    Status Codes:
        200: Success - roadmap generated
        400: Bad Request - invalid input
        500: Internal Server Error - server error
    """
    try:
        logging.info("Received roadmap generation request")
        
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
        
        # Generate roadmap using Groq AI (with multiple fallbacks)
        try:
            # Primary: Groq AI generation
            roadmap_data = get_groq_roadmap_for_skill(skill.strip())
            logging.info(f"Generated Groq AI roadmap for: {skill.strip()}")
        except Exception as e:
            logging.warning(f"Groq AI generation failed, trying enhanced AI method: {e}")
            try:
                # Secondary: Enhanced AI with APIs
                roadmap_data = get_ai_roadmap_for_skill(skill.strip())
                logging.info(f"Generated enhanced AI roadmap for: {skill.strip()}")
            except Exception as e2:
                logging.warning(f"Enhanced AI failed, falling back to traditional method: {e2}")
                # Tertiary: Traditional method
                roadmap_data = get_roadmap_for_skill(skill.strip())
        
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
                    from services.groq_resources_generator import get_groq_resources_for_skill
                    resources_data = get_groq_resources_for_skill(skill.strip())
                    logging.info(f"Generated Groq AI resources for: {skill.strip()}")
                except Exception as e3:
                    logging.warning(f"Groq AI failed, using manual fallback: {e3}")
                    # Final fallback: Manual resources fallback
                    from services.resource_service import get_resources_for_skill
                    resources_data = get_resources_for_skill(skill.strip())
        
        # Format response to match frontend expectations
        response_data = {
            'roadmap': roadmap_data,
            'resources': {
                'free': resources_data.get('freeResources', []),
                'paid': resources_data.get('paidResources', [])
            }
        }
        
        logging.info(f"Successfully generated roadmap for skill: {skill.strip()}")
        return create_success_response(response_data, 200)
        
    except ValueError as e:
        # Handle validation errors from service
        logging.warning(f"Validation error in roadmap generation: {str(e)}")
        return create_error_response(str(e), 400, "ValidationError")
        
    except FileNotFoundError as e:
        # Handle missing data files
        logging.error(f"Data file not found: {str(e)}")
        return create_error_response(
            "Sample roadmap data file not found", 
            500, 
            "DataFileError"
        )
        
    except json.JSONDecodeError as e:
        # Handle malformed JSON data files
        logging.error(f"JSON decode error: {str(e)}")
        return create_error_response(
            "Sample roadmap data file is malformed", 
            500, 
            "DataFormatError"
        )
        
    except Exception as e:
        # Handle unexpected errors
        logging.error(f"Unexpected error in roadmap generation: {str(e)}")
        return create_error_response(
            "An unexpected error occurred while generating the roadmap", 
            500, 
            "InternalServerError"
        )


@roadmap_bp.route('/roadmap', methods=['GET'])
def roadmap_info():
    """
    Provide information about the roadmap endpoint.
    
    Returns:
        JSON response with endpoint usage information
    """
    return jsonify({
        'endpoint': '/api/roadmap',
        'method': 'POST',
        'description': 'Generate learning roadmap for a specific skill',
        'required_parameters': {
            'skill': 'string - The skill name to generate roadmap for'
        },
        'example_request': {
            'skill': 'react developer'
        },
        'response_format': {
            'roadmap': {
                'skill': 'string',
                'title': 'string', 
                'modules': 'array of learning modules',
                'majorProject': 'object with capstone project details'
            },
            'resources': {
                'skill': 'string',
                'freeResources': 'array of free learning resources',
                'paidResources': 'array of paid learning resources'
            }
        }
    }), 200


# Error handlers for the blueprint
@roadmap_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors for roadmap routes."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested roadmap endpoint was not found',
        'status': 404
    }), 404


@roadmap_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors for roadmap routes."""
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'The HTTP method is not allowed for this endpoint',
        'status': 405
    }), 405