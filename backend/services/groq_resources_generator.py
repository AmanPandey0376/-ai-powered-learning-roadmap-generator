#!/usr/bin/env python3
"""
Groq AI-Powered Learning Resources Generator
Uses Groq's fast LLM API to generate intelligent, curated learning resources.
"""

import json
import logging
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

class GroqResourcesGenerator:
    """
    Generates intelligent learning resources using Groq AI API.
    """
    
    def __init__(self):
        """Initialize the Groq AI resources generator."""
        self.api_key = os.getenv('GROQ_API_KEY', '')
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.1-8b-instant"  # Current fast Groq model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logging.info("Groq AI Resources Generator initialized")
    
    def generate_learning_resources(self, skill: str) -> Dict[str, Any]:
        """
        Generate intelligent learning resources using Groq AI.
        
        Args:
            skill: The skill to generate resources for
            
        Returns:
            Comprehensive resources with AI-generated content
        """
        try:
            logging.info(f"Generating Groq AI resources for: {skill}")
            
            # Create the prompt for resources generation
            prompt = self.create_resources_prompt(skill)
            
            # Get AI response
            ai_response = self.call_groq_api(prompt)
            
            # Parse and structure the response
            resources = self.parse_ai_resources(ai_response, skill)
            
            logging.info(f"Successfully generated Groq AI resources for: {skill}")
            return resources
            
        except Exception as e:
            logging.error(f"Groq AI resources generation failed: {e}")
            # Fallback to basic resources
            return self.generate_fallback_resources(skill)
    
    def create_resources_prompt(self, skill: str) -> str:
        """
        Create a comprehensive prompt for resources generation.
        """
        current_year = datetime.now().year
        
        prompt = f"""
You are an expert learning resource curator. Create a list of VERIFIED, WORKING learning resources for "{skill}" in {current_year}.

CRITICAL REQUIREMENTS:
1. ONLY include resources that are CONFIRMED to exist and be accessible
2. Use REAL, WORKING URLs that are currently active
3. Focus on well-established, reputable platforms and resources
4. Prioritize resources that have been consistently available for years
5. Include only resources you are 100% certain about

RESPONSE FORMAT (JSON):
{{
  "skill": "{skill}",
  "freeResources": [
    {{
      "name": "Resource Name",
      "type": "Course|Tutorial|Documentation|Practice Platform|YouTube Channel",
      "url": "https://verified-working-url.com",
      "description": "Clear description of what this resource provides",
      "difficulty": "Beginner|Intermediate|Advanced",
      "estimatedHours": 25,
      "rating": 4.8,
      "provider": "Platform/Author Name",
      "lastUpdated": "2024",
      "highlights": ["Key benefit 1", "Key benefit 2", "Key benefit 3"]
    }}
  ],
  "paidResources": [
    {{
      "name": "Resource Name",
      "type": "Course|Platform Subscription|Book",
      "url": "https://verified-working-url.com",
      "description": "Clear description of what this resource provides",
      "difficulty": "Beginner|Intermediate|Advanced",
      "estimatedHours": 40,
      "price": "$X-Y",
      "rating": 4.9,
      "provider": "Platform Name",
      "lastUpdated": "2024",
      "highlights": ["Key benefit 1", "Key benefit 2", "Key benefit 3"],
      "certificateOffered": true
    }}
  ]
}}

ONLY USE THESE ULTRA-BASIC URLS:

NEVER create platform-specific URLs. ONLY use these guaranteed working URLs:

ALLOWED URLS:
- Google Search: https://www.google.com/search?q=[search-terms]
- YouTube: https://youtube.com
- Wikipedia: https://en.wikipedia.org/wiki/[topic]

ABSOLUTE RULES:
- NEVER use platform-specific URLs (no udemy.com, coursera.org, etc.)
- ONLY use Google search URLs, YouTube, and Wikipedia
- These are the ONLY 3 types of URLs allowed
- For paid resources, use Google search to find courses
- For free resources, use Google search, YouTube, or Wikipedia
- Users will find current courses through search results

Generate the resources now:
"""
        return prompt
    
    def call_groq_api(self, prompt: str) -> str:
        """
        Call Groq AI API to generate content.
        """
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert learning resource curator who creates comprehensive, up-to-date resource lists. Always respond with valid JSON format and include only real, existing resources."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000,
                "top_p": 0.9
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Clean up the response (remove markdown formatting if present)
                content = content.strip()
                
                # Handle various markdown formats
                if '```json' in content:
                    start_idx = content.find('```json') + 7
                    end_idx = content.rfind('```')
                    if end_idx > start_idx:
                        content = content[start_idx:end_idx]
                elif '```' in content:
                    start_idx = content.find('```') + 3
                    end_idx = content.rfind('```')
                    if end_idx > start_idx:
                        content = content[start_idx:end_idx]
                
                # Remove any leading/trailing whitespace and newlines
                content = content.strip()
                
                # Try to find JSON object if there's extra text
                if not content.startswith('{'):
                    json_start = content.find('{')
                    if json_start != -1:
                        content = content[json_start:]
                
                if not content.endswith('}'):
                    json_end = content.rfind('}')
                    if json_end != -1:
                        content = content[:json_end + 1]
                
                return content
            else:
                logging.error(f"Groq API error: {response.status_code} - {response.text}")
                raise Exception(f"Groq API returned {response.status_code}")
                
        except Exception as e:
            logging.error(f"Groq API call failed: {e}")
            raise
    
    def parse_ai_resources(self, ai_response: str, skill: str) -> Dict[str, Any]:
        """
        Parse and validate the AI-generated resources.
        """
        try:
            # Parse JSON response
            resources_data = json.loads(ai_response)
            
            # Validate required fields
            if not resources_data.get('freeResources'):
                resources_data['freeResources'] = []
            if not resources_data.get('paidResources'):
                resources_data['paidResources'] = []
            
            # Add metadata
            resources_data['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'generation_method': 'groq_ai',
                'model_used': self.model,
                'ai_generated': True
            }
            
            # Ensure skill is set correctly
            resources_data['skill'] = skill
            
            # Validate and clean up resource entries
            resources_data['freeResources'] = self.validate_resources(resources_data.get('freeResources', []))
            resources_data['paidResources'] = self.validate_resources(resources_data.get('paidResources', []))
            
            return resources_data
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse AI JSON response: {e}")
            logging.error(f"AI Response: {ai_response[:500]}...")
            raise ValueError("Invalid JSON from AI")
        except Exception as e:
            logging.error(f"Error parsing AI resources: {e}")
            raise
    
    def validate_resources(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean up resource entries.
        """
        validated_resources = []
        
        for resource in resources:
            # Ensure required fields
            if not resource.get('name'):
                continue
                
            # Set defaults for missing fields
            resource.setdefault('type', 'Course')
            resource.setdefault('description', 'Learning resource')
            resource.setdefault('difficulty', 'Intermediate')
            resource.setdefault('estimatedHours', 20)
            resource.setdefault('rating', 4.5)
            resource.setdefault('provider', 'Various')
            resource.setdefault('lastUpdated', '2024')
            resource.setdefault('highlights', [])
            
            # Clean up URL if present
            if resource.get('url') and not resource['url'].startswith('http'):
                resource['url'] = f"https://{resource['url']}"
            
            validated_resources.append(resource)
        
        return validated_resources
    
    def generate_fallback_resources(self, skill: str) -> Dict[str, Any]:
        """
        Generate fallback resources when Groq AI fails.
        """
        logging.info(f"Generating fallback resources for: {skill}")
        
        # First try to get verified resources with URL validation
        try:
            from services.verified_resources_service import get_verified_resources_for_skill
            verified_resources = get_verified_resources_for_skill(skill, validate_urls=True)
            
            # If we got resources with working URLs, use them
            if (verified_resources.get('freeResources') or verified_resources.get('paidResources')):
                logging.info(f"Using verified resources for: {skill}")
                return verified_resources
        except Exception as e:
            logging.warning(f"Failed to get verified resources: {e}")
        
        # Fallback to ultra-minimal resources
        logging.info(f"Using ultra-minimal fallback for: {skill}")
        
        # Use skill-specific templates
        if any(term in skill.lower() for term in ['data science', 'machine learning', 'ai']):
            return self.create_data_science_resources()
        elif any(term in skill.lower() for term in ['web dev', 'frontend', 'backend', 'react', 'javascript']):
            return self.create_web_dev_resources(skill)
        elif any(term in skill.lower() for term in ['python']):
            return self.create_python_resources()
        else:
            return self.create_generic_resources(skill)
    
    def create_data_science_resources(self) -> Dict[str, Any]:
        """Create ultra-minimal data science resources with only the most basic URLs."""
        return {
            "skill": "data science",
            "freeResources": [
                {
                    "name": "Google Search - Data Science Courses",
                    "type": "Search",
                    "url": "https://www.google.com/search?q=free+data+science+courses",
                    "description": "Search for free data science courses and tutorials",
                    "difficulty": "Beginner",
                    "estimatedHours": 0,
                    "rating": 4.5,
                    "provider": "Google",
                    "lastUpdated": "2024",
                    "highlights": ["Always current", "Multiple options", "Free access"]
                },
                {
                    "name": "YouTube",
                    "type": "Video Platform",
                    "url": "https://youtube.com",
                    "description": "Search for data science tutorials and courses on YouTube",
                    "difficulty": "Beginner",
                    "estimatedHours": 50,
                    "rating": 4.5,
                    "provider": "YouTube",
                    "lastUpdated": "2024",
                    "highlights": ["Video format", "Visual learning", "Free access"]
                },
                {
                    "name": "Wikipedia - Data Science",
                    "type": "Reference",
                    "url": "https://en.wikipedia.org/wiki/Data_science",
                    "description": "Learn about data science fundamentals and concepts",
                    "difficulty": "Beginner",
                    "estimatedHours": 2,
                    "rating": 4.3,
                    "provider": "Wikipedia",
                    "lastUpdated": "2024",
                    "highlights": ["Comprehensive overview", "Free access", "Reliable information"]
                }
            ],
            "paidResources": [
                {
                    "name": "Google Search - Paid Data Science Courses",
                    "type": "Search",
                    "url": "https://www.google.com/search?q=paid+data+science+courses+udemy+coursera",
                    "description": "Search for premium data science courses on major platforms",
                    "difficulty": "Beginner",
                    "estimatedHours": 0,
                    "price": "Varies",
                    "rating": 4.5,
                    "provider": "Google",
                    "lastUpdated": "2024",
                    "highlights": ["Current options", "Compare prices", "Multiple platforms"],
                    "certificateOffered": True
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_method": "groq_fallback",
                "ai_generated": False
            }
        }
    
    def create_web_dev_resources(self, skill: str) -> Dict[str, Any]:
        """Create ultra-minimal web development resources with only the most basic URLs."""
        return {
            "skill": skill,
            "freeResources": [
                {
                    "name": "Google Search - Web Development Courses",
                    "type": "Search",
                    "url": "https://www.google.com/search?q=free+web+development+courses",
                    "description": "Search for free web development courses and tutorials",
                    "difficulty": "Beginner",
                    "estimatedHours": 0,
                    "rating": 4.5,
                    "provider": "Google",
                    "lastUpdated": "2024",
                    "highlights": ["Always current", "Multiple options", "Free access"]
                },
                {
                    "name": "YouTube",
                    "type": "Video Platform",
                    "url": "https://youtube.com",
                    "description": "Search for web development tutorials and courses on YouTube",
                    "difficulty": "Beginner",
                    "estimatedHours": 50,
                    "rating": 4.6,
                    "provider": "YouTube",
                    "lastUpdated": "2024",
                    "highlights": ["Video format", "Visual learning", "Free access"]
                },
                {
                    "name": "Wikipedia - Web Development",
                    "type": "Reference",
                    "url": "https://en.wikipedia.org/wiki/Web_development",
                    "description": "Learn about web development fundamentals and concepts",
                    "difficulty": "Beginner",
                    "estimatedHours": 2,
                    "rating": 4.3,
                    "provider": "Wikipedia",
                    "lastUpdated": "2024",
                    "highlights": ["Comprehensive overview", "Free access", "Reliable information"]
                }
            ],
            "paidResources": [
                {
                    "name": "Google Search - Paid Web Development Courses",
                    "type": "Search",
                    "url": "https://www.google.com/search?q=paid+web+development+courses+udemy+coursera",
                    "description": "Search for premium web development courses on major platforms",
                    "difficulty": "Beginner",
                    "estimatedHours": 0,
                    "price": "Varies",
                    "rating": 4.5,
                    "provider": "Google",
                    "lastUpdated": "2024",
                    "highlights": ["Current options", "Compare prices", "Multiple platforms"],
                    "certificateOffered": True
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_method": "groq_fallback",
                "ai_generated": False
            }
        }
    
    def create_python_resources(self) -> Dict[str, Any]:
        """Create ultra-minimal Python-specific resources with only the most basic URLs."""
        return {
            "skill": "python",
            "freeResources": [
                {
                    "name": "Google Search - Python Courses",
                    "type": "Search",
                    "url": "https://www.google.com/search?q=free+python+programming+courses",
                    "description": "Search for free Python programming courses and tutorials",
                    "difficulty": "Beginner",
                    "estimatedHours": 0,
                    "rating": 4.5,
                    "provider": "Google",
                    "lastUpdated": "2024",
                    "highlights": ["Always current", "Multiple options", "Free access"]
                },
                {
                    "name": "YouTube",
                    "type": "Video Platform",
                    "url": "https://youtube.com",
                    "description": "Search for Python tutorials and courses on YouTube",
                    "difficulty": "Beginner",
                    "estimatedHours": 40,
                    "rating": 4.6,
                    "provider": "YouTube",
                    "lastUpdated": "2024",
                    "highlights": ["Video format", "Visual learning", "Free access"]
                },
                {
                    "name": "Wikipedia - Python Programming",
                    "type": "Reference",
                    "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
                    "description": "Learn about Python programming language fundamentals",
                    "difficulty": "Beginner",
                    "estimatedHours": 2,
                    "rating": 4.3,
                    "provider": "Wikipedia",
                    "lastUpdated": "2024",
                    "highlights": ["Comprehensive overview", "Free access", "Reliable information"]
                }
            ],
            "paidResources": [
                {
                    "name": "Google Search - Paid Python Courses",
                    "type": "Search",
                    "url": "https://www.google.com/search?q=paid+python+courses+udemy+coursera+datacamp",
                    "description": "Search for premium Python courses on major platforms",
                    "difficulty": "Beginner",
                    "estimatedHours": 0,
                    "price": "Varies",
                    "rating": 4.5,
                    "provider": "Google",
                    "lastUpdated": "2024",
                    "highlights": ["Current options", "Compare prices", "Multiple platforms"],
                    "certificateOffered": True
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_method": "groq_fallback",
                "ai_generated": False
            }
        }
    
    def create_generic_resources(self, skill: str) -> Dict[str, Any]:
        """Create ultra-minimal generic resources with only the most basic URLs."""
        return {
            "skill": skill,
            "freeResources": [
                {
                    "name": f"Google Search - {skill.title()} Courses",
                    "type": "Search",
                    "url": f"https://www.google.com/search?q=free+{skill.replace(' ', '+')}+courses",
                    "description": f"Search for free {skill} courses and tutorials",
                    "difficulty": "Beginner",
                    "estimatedHours": 0,
                    "rating": 4.5,
                    "provider": "Google",
                    "lastUpdated": "2024",
                    "highlights": ["Always current", "Multiple options", "Free access"]
                },
                {
                    "name": "YouTube",
                    "type": "Video Platform",
                    "url": "https://youtube.com",
                    "description": f"Search for {skill} tutorials and courses on YouTube",
                    "difficulty": "Beginner",
                    "estimatedHours": 30,
                    "rating": 4.3,
                    "provider": "YouTube",
                    "lastUpdated": "2024",
                    "highlights": ["Video format", "Visual learning", "Free access"]
                },
                {
                    "name": f"Wikipedia - {skill.title()}",
                    "type": "Reference",
                    "url": f"https://en.wikipedia.org/wiki/{skill.replace(' ', '_')}",
                    "description": f"Learn about {skill} fundamentals and concepts",
                    "difficulty": "Beginner",
                    "estimatedHours": 2,
                    "rating": 4.3,
                    "provider": "Wikipedia",
                    "lastUpdated": "2024",
                    "highlights": ["Comprehensive overview", "Free access", "Reliable information"]
                }
            ],
            "paidResources": [
                {
                    "name": f"Google Search - Paid {skill.title()} Courses",
                    "type": "Search",
                    "url": f"https://www.google.com/search?q=paid+{skill.replace(' ', '+')}+courses+udemy+coursera",
                    "description": f"Search for premium {skill} courses on major platforms",
                    "difficulty": "Beginner",
                    "estimatedHours": 0,
                    "price": "Varies",
                    "rating": 4.5,
                    "provider": "Google",
                    "lastUpdated": "2024",
                    "highlights": ["Current options", "Compare prices", "Multiple platforms"],
                    "certificateOffered": True
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_method": "groq_fallback",
                "ai_generated": False
            }
        }

# Convenience function for the main application
def get_groq_resources_for_skill(skill: str) -> Dict[str, Any]:
    """
    Generate Groq AI-powered resources for the specified skill.
    
    Args:
        skill: The skill to generate resources for
        
    Returns:
        Complete resources dictionary
    """
    generator = GroqResourcesGenerator()
    return generator.generate_learning_resources(skill)