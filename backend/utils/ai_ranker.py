#!/usr/bin/env python3
"""
AI-powered ranking and filtering of learning resources using Groq API.
"""

import json
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple
from config import Config

class AIRanker:
    """AI-powered resource ranker using Groq API."""
    
    def __init__(self):
        """Initialize AI ranker."""
        self.api_key = Config.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = Config.GROQ_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logging.info("AI Ranker initialized")
    
    def rank_and_select_resources(self, skill: str, all_resources: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Rank and select the best free and paid resources for a skill.
        
        Args:
            skill: The skill to rank resources for
            all_resources: Dictionary containing resources from different platforms
            
        Returns:
            Dictionary with best free and paid resource recommendations
        """
        try:
            logging.info(f"Ranking resources for: {skill}")
            
            # Create prompt for AI ranking
            prompt = self._create_ranking_prompt(skill, all_resources)
            
            # Get AI response
            ai_response = self._call_groq_api(prompt)
            
            # Parse AI response
            recommendations = self._parse_ai_response(ai_response, all_resources)
            
            logging.info(f"Successfully ranked resources for: {skill}")
            return recommendations
            
        except Exception as e:
            logging.error(f"Error ranking resources for {skill}: {str(e)}")
            return self._create_fallback_recommendations(skill, all_resources)
    
    def _create_ranking_prompt(self, skill: str, all_resources: Dict[str, List[Dict[str, Any]]]) -> str:
        """Create a prompt for AI ranking."""
        
        # Summarize available resources
        resource_summary = []
        
        for platform, resources in all_resources.items():
            for i, resource in enumerate(resources[:3]):  # Limit to top 3 per platform
                summary = f"{platform}_{i+1}: {resource.get('title', 'Unknown')} by {resource.get('instructor', resource.get('owner', 'Unknown'))}"
                if resource.get('estimated_hours'):
                    summary += f" ({resource['estimated_hours']} hours)"
                if resource.get('rating'):
                    summary += f" - Rating: {resource['rating']}/5"
                resource_summary.append(summary)
        
        resources_text = "\n".join(resource_summary)
        
        prompt = f"""
You are an expert learning advisor. Analyze these learning resources for "{skill}" and recommend the BEST single resource for each category.

AVAILABLE RESOURCES:
{resources_text}

SELECTION CRITERIA:
1. Quality and reputation of instructor/platform
2. Comprehensive coverage of the skill
3. Practical, hands-on approach
4. Good ratings and reviews
5. Appropriate difficulty progression
6. For FREE: Completely free access to core content
7. For PAID: Best value for money with certificates/credentials

RESPONSE FORMAT (JSON):
{{
  "free_recommendation": {{
    "platform": "platform_name",
    "resource_index": 0,
    "reason": "Why this is the best free option"
  }},
  "paid_recommendation": {{
    "platform": "platform_name", 
    "resource_index": 0,
    "reason": "Why this is the best paid option"
  }}
}}

IMPORTANT:
- Choose only ONE resource for free and ONE for paid
- Use the exact platform names and resource indices from the list above
- Focus on resources that provide complete learning paths, not just reference materials
- Prioritize resources with proven track records and good instructor reputation
- For free resources, prefer comprehensive courses over just documentation
- For paid resources, consider certification value and career impact

Analyze and recommend now:
"""
        return prompt
    
    def _call_groq_api(self, prompt: str) -> str:
        """Call Groq AI API."""
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert learning advisor who recommends the best educational resources. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": Config.GROQ_TEMPERATURE,
                "max_tokens": Config.GROQ_MAX_TOKENS,
                "top_p": 0.9
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=Config.REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Clean up the response
                content = content.strip()
                
                # Handle markdown formatting
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
                
                content = content.strip()
                
                # Find JSON object
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
            logging.error(f"Groq API call failed: {str(e)}")
            raise
    
    def _parse_ai_response(self, ai_response: str, all_resources: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Parse AI response and extract recommendations."""
        try:
            # Parse JSON response
            recommendations = json.loads(ai_response)
            
            result = {
                "skill": "",
                "free": None,
                "paid": None,
                "metadata": {
                    "ai_generated": True,
                    "ranking_method": "groq_ai"
                }
            }
            
            # Extract free recommendation
            if "free_recommendation" in recommendations:
                free_rec = recommendations["free_recommendation"]
                platform = free_rec.get("platform", "")
                index = free_rec.get("resource_index", 0)
                
                if platform in all_resources and index < len(all_resources[platform]):
                    resource = all_resources[platform][index]
                    result["free"] = {
                        "platform": resource.get("platform", platform),
                        "title": resource.get("title", ""),
                        "instructor": resource.get("instructor", resource.get("owner", "")),
                        "url": resource.get("url", ""),
                        "hours": resource.get("estimated_hours", 0),
                        "rating": resource.get("rating", 0),
                        "description": resource.get("description", ""),
                        "reason": free_rec.get("reason", "")
                    }
            
            # Extract paid recommendation
            if "paid_recommendation" in recommendations:
                paid_rec = recommendations["paid_recommendation"]
                platform = paid_rec.get("platform", "")
                index = paid_rec.get("resource_index", 0)
                
                if platform in all_resources and index < len(all_resources[platform]):
                    resource = all_resources[platform][index]
                    result["paid"] = {
                        "platform": resource.get("platform", platform),
                        "title": resource.get("title", ""),
                        "instructor": resource.get("instructor", resource.get("owner", "")),
                        "url": resource.get("url", ""),
                        "hours": resource.get("estimated_hours", 0),
                        "rating": resource.get("rating", 0),
                        "description": resource.get("description", ""),
                        "cost": resource.get("price", ""),
                        "reason": paid_rec.get("reason", "")
                    }
            
            return result
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse AI JSON response: {e}")
            logging.error(f"AI Response: {ai_response[:500]}...")
            raise ValueError("Invalid JSON from AI")
        except Exception as e:
            logging.error(f"Error parsing AI recommendations: {e}")
            raise
    
    def _create_fallback_recommendations(self, skill: str, all_resources: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Create fallback recommendations when AI fails."""
        logging.info(f"Creating fallback recommendations for: {skill}")
        
        result = {
            "skill": skill,
            "free": None,
            "paid": None,
            "metadata": {
                "ai_generated": False,
                "ranking_method": "fallback"
            }
        }
        
        # Find best free resource (prioritize YouTube and GitHub)
        free_candidates = []
        for platform in ["YouTube", "GitHub"]:
            if platform in all_resources and all_resources[platform]:
                free_candidates.extend(all_resources[platform])
        
        if free_candidates:
            # Sort by rating and stars
            best_free = max(free_candidates, key=lambda x: (x.get("rating", 0), x.get("stars", 0)))
            result["free"] = {
                "platform": best_free.get("platform", ""),
                "title": best_free.get("title", ""),
                "instructor": best_free.get("instructor", best_free.get("owner", "")),
                "url": best_free.get("url", ""),
                "hours": best_free.get("estimated_hours", 0),
                "rating": best_free.get("rating", 0),
                "description": best_free.get("description", ""),
                "reason": "Highest rated free resource available"
            }
        
        # Find best paid resource (prioritize Coursera)
        paid_candidates = []
        for platform in ["Coursera"]:
            if platform in all_resources and all_resources[platform]:
                paid_candidates.extend(all_resources[platform])
        
        if paid_candidates:
            # Sort by rating and estimated hours
            best_paid = max(paid_candidates, key=lambda x: (x.get("rating", 0), x.get("estimated_hours", 0)))
            result["paid"] = {
                "platform": best_paid.get("platform", ""),
                "title": best_paid.get("title", ""),
                "instructor": best_paid.get("instructor", ""),
                "url": best_paid.get("url", ""),
                "hours": best_paid.get("estimated_hours", 0),
                "rating": best_paid.get("rating", 0),
                "description": best_paid.get("description", ""),
                "cost": best_paid.get("price", ""),
                "reason": "Highest rated comprehensive paid course"
            }
        
        return result

# Create singleton instance
ai_ranker = AIRanker()

def rank_learning_resources(skill: str, all_resources: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Rank and select the best learning resources for a skill.
    
    Args:
        skill: The skill to rank resources for
        all_resources: Dictionary containing resources from different platforms
        
    Returns:
        Dictionary with best free and paid resource recommendations
    """
    return ai_ranker.rank_and_select_resources(skill, all_resources)