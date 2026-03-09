#!/usr/bin/env python3
"""
Groq AI-Powered Resource Generator
Uses Groq's fast LLM API to generate intelligent, personalized learning resources.
"""

import json
import logging
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

class GroqResourceGenerator:
    """
    Generates intelligent learning resources using Groq AI API.
    """
    
    def __init__(self):
        """Initialize the Groq AI resource generator."""
        self.api_key = os.getenv('GROQ_API_KEY', '')
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.1-8b-instant"  # Current fast Groq model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logging.info("Groq AI Resource Generator initialized")
    
    def generate_intelligent_resources(self, skill: str) -> Dict[str, Any]:
        """
        Generate intelligent learning resources using Groq AI.
        
        Args:
            skill: The skill to find resources for
            
        Returns:
            Dictionary with AI-generated free and paid resources
        """
        try:
            logging.info(f"Generating Groq AI resources for: {skill}")
            
            # Create the prompt for resource generation
            prompt = self.create_resource_prompt(skill)
            
            # Get AI response
            ai_response = self.call_groq_api(prompt)
            
            # Parse and structure the response
            resources = self.parse_ai_resources(ai_response, skill)
            
            logging.info(f"Successfully generated Groq AI resources for: {skill}")
            return resources
            
        except Exception as e:
            logging.error(f"Groq AI resource generation failed: {e}")
            # Fallback to curated resources
            return self.generate_fallback_resources(skill)
    
    def create_resource_prompt(self, skill: str) -> str:
        """
        Create a comprehensive prompt for resource generation.
        """
        current_year = datetime.now().year
        
        prompt = f"""
You are an expert learning resource curator and educational consultant. Create a comprehensive list of the BEST learning resources for "{skill}" that are current, high-quality, and effective in {current_year}.

REQUIREMENTS:
1. Provide 8-10 FREE resources (YouTube channels, documentation, free courses, GitHub repos)
2. Provide 5-7 PAID resources (premium courses, books, certifications)
3. Focus on resources that are:
   - Currently available and active
   - High quality with good reviews/ratings
   - Practical and hands-on
   - From reputable creators/platforms
   - Cover different learning styles (video, text, interactive)
4. Include realistic details like duration, difficulty level, and what makes each resource special
5. Prioritize resources that teach modern, industry-relevant skills

RESPONSE FORMAT (JSON):
{{
  "skill": "{skill}",
  "freeResources": [
    {{
      "id": 1,
      "title": "Resource Title",
      "platform": "YouTube/GitHub/Documentation/etc",
      "creator": "Creator Name or Organization",
      "link": "https://example.com",
      "type": "Video Course/Documentation/Repository/Article Series",
      "duration": "X hours" or "Self-paced",
      "difficulty": "Beginner/Intermediate/Advanced",
      "description": "Detailed description of what this resource covers and why it's valuable",
      "highlights": ["Key feature 1", "Key feature 2", "Key feature 3"],
      "rating": 4.8,
      "learners": "500K+" or "Popular"
    }}
  ],
  "paidResources": [
    {{
      "id": 1,
      "title": "Course/Book Title",
      "platform": "Udemy/Coursera/Pluralsight/Amazon/etc",
      "creator": "Instructor Name",
      "link": "https://example.com",
      "type": "Video Course/Book/Certification/Bootcamp",
      "price": "$XX.XX" or "$$$ range",
      "duration": "X hours",
      "difficulty": "Beginner/Intermediate/Advanced",
      "description": "Detailed description of the course content and learning outcomes",
      "highlights": ["Key benefit 1", "Key benefit 2", "Key benefit 3"],
      "rating": 4.7,
      "students": "100K+",
      "certificate": true
    }}
  ]
}}

SPECIFIC GUIDELINES BY SKILL:

For Data Science:
- FREE: Python.org docs, Kaggle Learn, YouTube (3Blue1Brown, StatQuest), GitHub awesome lists, Google Colab tutorials
- PAID: Coursera Data Science Specialization, Udemy courses by Jose Portilla, DataCamp, "Hands-On Machine Learning" book

For Web Development:
- FREE: MDN Web Docs, freeCodeCamp, YouTube (Traversy Media, The Net Ninja), GitHub repos, W3Schools
- PAID: Udemy courses by Brad Traversy/Maximilian, Frontend Masters, "You Don't Know JS" book series

For Machine Learning/AI:
- FREE: Andrew Ng's ML course (YouTube), Papers with Code, Hugging Face docs, Fast.ai
- PAID: Coursera ML Specialization, Udacity AI Nanodegree, "Pattern Recognition and Machine Learning" book

For Cybersecurity:
- FREE: OWASP documentation, Cybrary free courses, YouTube (John Hammond, LiveOverflow), Kali Linux docs
- PAID: Offensive Security courses, SANS training, CompTIA Security+ materials

Always include:
- Mix of beginner to advanced resources
- Different formats (video, text, interactive)
- Both theoretical and practical resources
- Community-recommended and industry-standard materials
- Current and actively maintained resources

Generate the resource list now:
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
                        "content": "You are an expert educational resource curator who creates comprehensive, high-quality learning resource lists. Always respond with valid JSON format and include only real, accessible resources."
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
            if not resources_data.get('freeResources') and not resources_data.get('paidResources'):
                raise ValueError("No resources in AI response")
            
            # Add metadata
            resources_data['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'generation_method': 'groq_ai_resources',
                'model_used': self.model,
                'ai_generated': True
            }
            
            # Ensure skill is set correctly
            resources_data['skill'] = skill
            
            # Validate and clean up resources
            free_resources = resources_data.get('freeResources', [])
            paid_resources = resources_data.get('paidResources', [])
            
            # Ensure each resource has required fields
            for i, resource in enumerate(free_resources):
                if not resource.get('id'):
                    resource['id'] = i + 1
                if not resource.get('title'):
                    resource['title'] = f"Free {skill.title()} Resource {i+1}"
                if not resource.get('platform'):
                    resource['platform'] = "Online"
                if not resource.get('creator'):
                    resource['creator'] = "Community"
                if not resource.get('description'):
                    resource['description'] = f"Quality learning resource for {skill}"
            
            for i, resource in enumerate(paid_resources):
                if not resource.get('id'):
                    resource['id'] = i + 1
                if not resource.get('title'):
                    resource['title'] = f"Premium {skill.title()} Course {i+1}"
                if not resource.get('platform'):
                    resource['platform'] = "Online Course Platform"
                if not resource.get('creator'):
                    resource['creator'] = "Expert Instructor"
                if not resource.get('description'):
                    resource['description'] = f"Comprehensive {skill} course with certification"
            
            return resources_data
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse AI JSON response: {e}")
            logging.error(f"AI Response: {ai_response[:500]}...")
            raise ValueError("Invalid JSON from AI")
        except Exception as e:
            logging.error(f"Error parsing AI resources: {e}")
            raise
    
    def generate_fallback_resources(self, skill: str) -> Dict[str, Any]:
        """
        Generate fallback resources when Groq AI fails.
        """
        logging.info(f"Generating fallback resources for: {skill}")
        
        # Use skill-specific templates
        if any(term in skill.lower() for term in ['data science', 'machine learning', 'ai']):
            return self.create_data_science_resources()
        elif any(term in skill.lower() for term in ['web dev', 'frontend', 'backend', 'react', 'javascript']):
            return self.create_web_dev_resources()
        else:
            return self.create_generic_resources(skill)
    
    def create_data_science_resources(self) -> Dict[str, Any]:
        """Create comprehensive data science resources."""
        return {
            "skill": "data science",
            "freeResources": [
                {
                    "id": 1,
                    "title": "Python for Data Science Handbook",
                    "platform": "GitHub",
                    "creator": "Jake VanderPlas",
                    "link": "https://github.com/jakevdp/PythonDataScienceHandbook",
                    "type": "Interactive Book",
                    "duration": "Self-paced",
                    "difficulty": "Beginner to Intermediate",
                    "description": "Complete handbook covering essential tools for data science in Python including NumPy, Pandas, Matplotlib, and Scikit-Learn",
                    "highlights": ["Jupyter notebooks", "Practical examples", "Comprehensive coverage"],
                    "rating": 4.8,
                    "learners": "50K+ stars"
                },
                {
                    "id": 2,
                    "title": "Kaggle Learn",
                    "platform": "Kaggle",
                    "creator": "Kaggle Team",
                    "link": "https://www.kaggle.com/learn",
                    "type": "Interactive Courses",
                    "duration": "2-4 hours per course",
                    "difficulty": "Beginner to Advanced",
                    "description": "Free micro-courses on Python, Machine Learning, Data Visualization, and more with hands-on exercises",
                    "highlights": ["Hands-on coding", "Certificates", "Real datasets"],
                    "rating": 4.7,
                    "learners": "1M+"
                },
                {
                    "id": 3,
                    "title": "3Blue1Brown - Neural Networks",
                    "platform": "YouTube",
                    "creator": "Grant Sanderson",
                    "link": "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi",
                    "type": "Video Series",
                    "duration": "4 hours",
                    "difficulty": "Intermediate",
                    "description": "Intuitive visual explanations of neural networks and deep learning concepts",
                    "highlights": ["Visual learning", "Mathematical intuition", "Clear explanations"],
                    "rating": 4.9,
                    "learners": "10M+ views"
                },
                {
                    "id": 4,
                    "title": "StatQuest with Josh Starmer",
                    "platform": "YouTube",
                    "creator": "Josh Starmer",
                    "link": "https://www.youtube.com/c/joshstarmer",
                    "type": "Video Channel",
                    "duration": "Various",
                    "difficulty": "Beginner to Advanced",
                    "description": "Statistics and machine learning concepts explained clearly with memorable examples",
                    "highlights": ["Clear explanations", "Statistics focus", "Memorable examples"],
                    "rating": 4.8,
                    "learners": "1M+ subscribers"
                },
                {
                    "id": 5,
                    "title": "Fast.ai Practical Deep Learning",
                    "platform": "Fast.ai",
                    "creator": "Jeremy Howard",
                    "link": "https://course.fast.ai/",
                    "type": "Free Course",
                    "duration": "7 weeks",
                    "difficulty": "Intermediate",
                    "description": "Practical deep learning course focusing on real-world applications and state-of-the-art techniques",
                    "highlights": ["Top-down approach", "Practical focus", "Latest techniques"],
                    "rating": 4.8,
                    "learners": "500K+"
                }
            ],
            "paidResources": [
                {
                    "id": 1,
                    "title": "Machine Learning Specialization",
                    "platform": "Coursera",
                    "creator": "Andrew Ng",
                    "link": "https://www.coursera.org/specializations/machine-learning-introduction",
                    "type": "Specialization",
                    "price": "$49/month",
                    "duration": "3 months",
                    "difficulty": "Beginner to Intermediate",
                    "description": "Comprehensive machine learning course covering supervised learning, unsupervised learning, and best practices",
                    "highlights": ["Industry standard", "Hands-on projects", "University certificate"],
                    "rating": 4.9,
                    "students": "5M+",
                    "certificate": True
                },
                {
                    "id": 2,
                    "title": "Python for Data Science and Machine Learning Bootcamp",
                    "platform": "Udemy",
                    "creator": "Jose Portilla",
                    "link": "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/",
                    "type": "Video Course",
                    "price": "$84.99",
                    "duration": "25 hours",
                    "difficulty": "Beginner to Intermediate",
                    "description": "Complete data science bootcamp covering Python, pandas, NumPy, matplotlib, seaborn, plotly, scikit-learn, and more",
                    "highlights": ["Comprehensive coverage", "Hands-on projects", "Lifetime access"],
                    "rating": 4.6,
                    "students": "500K+",
                    "certificate": True
                },
                {
                    "id": 3,
                    "title": "Hands-On Machine Learning (Book)",
                    "platform": "O'Reilly",
                    "creator": "Aurélien Géron",
                    "link": "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/",
                    "type": "Technical Book",
                    "price": "$59.99",
                    "duration": "Self-paced",
                    "difficulty": "Intermediate to Advanced",
                    "description": "Practical guide to machine learning with scikit-learn, Keras, and TensorFlow including real-world examples",
                    "highlights": ["Practical approach", "Latest techniques", "Code examples"],
                    "rating": 4.7,
                    "students": "Industry standard",
                    "certificate": False
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_method": "groq_fallback_resources",
                "ai_generated": False
            }
        }
    
    def create_web_dev_resources(self) -> Dict[str, Any]:
        """Create web development resources."""
        return {
            "skill": "web development",
            "freeResources": [
                {
                    "id": 1,
                    "title": "MDN Web Docs",
                    "platform": "Mozilla",
                    "creator": "Mozilla Foundation",
                    "link": "https://developer.mozilla.org/",
                    "type": "Documentation",
                    "duration": "Self-paced",
                    "difficulty": "All levels",
                    "description": "Comprehensive documentation for web technologies including HTML, CSS, JavaScript, and Web APIs",
                    "highlights": ["Authoritative source", "Interactive examples", "Regular updates"],
                    "rating": 4.9,
                    "learners": "Millions"
                },
                {
                    "id": 2,
                    "title": "freeCodeCamp",
                    "platform": "freeCodeCamp",
                    "creator": "freeCodeCamp.org",
                    "link": "https://www.freecodecamp.org/",
                    "type": "Interactive Course",
                    "duration": "300+ hours",
                    "difficulty": "Beginner to Advanced",
                    "description": "Complete web development curriculum with certifications and real projects for nonprofits",
                    "highlights": ["Hands-on projects", "Certifications", "Community support"],
                    "rating": 4.8,
                    "learners": "400K+ graduates"
                }
            ],
            "paidResources": [
                {
                    "id": 1,
                    "title": "The Complete Web Developer Course",
                    "platform": "Udemy",
                    "creator": "Rob Percival",
                    "link": "https://www.udemy.com/course/the-complete-web-development-bootcamp/",
                    "type": "Video Course",
                    "price": "$94.99",
                    "duration": "65 hours",
                    "difficulty": "Beginner to Advanced",
                    "description": "Complete web development bootcamp covering HTML, CSS, JavaScript, Node.js, React, MongoDB, and more",
                    "highlights": ["Full-stack coverage", "Real projects", "Job preparation"],
                    "rating": 4.7,
                    "students": "1M+",
                    "certificate": True
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_method": "groq_fallback_resources",
                "ai_generated": False
            }
        }
    
    def create_generic_resources(self, skill: str) -> Dict[str, Any]:
        """Create generic resources for any skill."""
        return {
            "skill": skill,
            "freeResources": [
                {
                    "id": 1,
                    "title": f"{skill.title()} Documentation",
                    "platform": "Official Docs",
                    "creator": "Official Team",
                    "link": f"https://www.google.com/search?q={skill.replace(' ', '+')}+official+documentation",
                    "type": "Documentation",
                    "duration": "Self-paced",
                    "difficulty": "All levels",
                    "description": f"Official documentation and guides for {skill}",
                    "highlights": ["Authoritative", "Up-to-date", "Comprehensive"],
                    "rating": 4.5,
                    "learners": "Community"
                }
            ],
            "paidResources": [
                {
                    "id": 1,
                    "title": f"Complete {skill.title()} Course",
                    "platform": "Udemy",
                    "creator": "Expert Instructor",
                    "link": f"https://www.udemy.com/courses/search/?q={skill.replace(' ', '+')}",
                    "type": "Video Course",
                    "price": "$79.99",
                    "duration": "20+ hours",
                    "difficulty": "Beginner to Advanced",
                    "description": f"Comprehensive {skill} course with practical projects and real-world applications",
                    "highlights": ["Comprehensive", "Practical projects", "Certificate"],
                    "rating": 4.5,
                    "students": "10K+",
                    "certificate": True
                }
            ],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_method": "groq_fallback_resources",
                "ai_generated": False
            }
        }

# Convenience function for the main application
def get_groq_resources_for_skill(skill: str) -> Dict[str, Any]:
    """
    Generate Groq AI-powered resources for the specified skill.
    
    Args:
        skill: The skill to find resources for
        
    Returns:
        Dictionary with AI-generated free and paid resources
    """
    generator = GroqResourceGenerator()
    return generator.generate_intelligent_resources(skill)