#!/usr/bin/env python3
"""
Groq AI-Powered Learning Roadmap Generator
Uses Groq's fast LLM API to generate intelligent, personalized learning roadmaps.
"""

import json
import logging
import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class GroqAIGenerator:
    """
    Generates intelligent roadmaps using Groq AI API.
    """
    
    def __init__(self):
        """Initialize the Groq AI generator."""
        self.api_key = os.getenv('GROQ_API_KEY', '')
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.1-8b-instant"  # Current fast Groq model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logging.info("Groq AI Generator initialized")
    
    def generate_intelligent_roadmap(self, skill: str) -> Dict[str, Any]:
        """
        Generate an intelligent roadmap using Groq AI.
        
        Args:
            skill: The skill to generate roadmap for
            
        Returns:
            Comprehensive roadmap with AI-generated content
        """
        try:
            logging.info(f"Generating Groq AI roadmap for: {skill}")
            
            # Create the prompt for roadmap generation
            prompt = self.create_roadmap_prompt(skill)
            
            # Get AI response
            ai_response = self.call_groq_api(prompt)
            
            # Parse and structure the response
            roadmap = self.parse_ai_roadmap(ai_response, skill)
            
            logging.info(f"Successfully generated Groq AI roadmap for: {skill}")
            return roadmap
            
        except Exception as e:
            logging.error(f"Groq AI generation failed: {e}")
            # Fallback to enhanced template
            return self.generate_fallback_roadmap(skill)
    
    def create_roadmap_prompt(self, skill: str) -> str:
        """
        Create a comprehensive prompt for roadmap generation.
        """
        current_year = datetime.now().year
        
        prompt = f"""
You are an expert learning curriculum designer and industry professional. Create a comprehensive, modern learning roadmap for "{skill}" that reflects current industry standards and trends in {current_year}.

REQUIREMENTS:
1. Create 6-8 progressive learning modules
2. Each module should have 2-3 hands-on mini-projects
3. Include a major capstone project
4. Focus on practical, industry-relevant skills
5. Include modern tools, frameworks, and technologies
6. Provide realistic time estimates
7. Ensure proper learning progression (beginner → advanced)

RESPONSE FORMAT (JSON):
{{
  "skill": "{skill}",
  "title": "Complete [Skill] Learning Roadmap",
  "modules": [
    {{
      "id": 1,
      "name": "Module Name",
      "description": "Detailed description of what students will learn",
      "miniProjects": [
        {{
          "name": "Project Name",
          "description": "Specific project description with technologies used",
          "estimatedHours": 15,
          "technologies": ["Tech1", "Tech2", "Tech3"]
        }}
      ]
    }}
  ],
  "majorProject": {{
    "name": "Capstone Project Name",
    "description": "Comprehensive final project description",
    "requirements": [
      "Specific requirement 1",
      "Specific requirement 2"
    ],
    "estimatedHours": 80,
    "technologies": ["Tech1", "Tech2"]
  }}
}}

IMPORTANT GUIDELINES:
- For Data Science: Include Python, Statistics, ML, Deep Learning, NLP, Computer Vision, GenAI, MLOps
- For Web Development: Include HTML/CSS, JavaScript, React/Vue, Backend (Node.js/Python), Databases, DevOps
- For Mobile Development: Include native (Swift/Kotlin) or cross-platform (React Native/Flutter)
- For DevOps: Include Docker, Kubernetes, CI/CD, Cloud platforms, Infrastructure as Code
- For Cybersecurity: Include Network Security, Ethical Hacking, Penetration Testing, Security Tools
- Always include current industry trends and modern tools
- Make projects practical and portfolio-worthy
- Ensure realistic time estimates based on complexity

Generate the roadmap now:
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
                        "content": "You are an expert curriculum designer who creates detailed, practical learning roadmaps. Always respond with valid JSON format."
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
    
    def parse_ai_roadmap(self, ai_response: str, skill: str) -> Dict[str, Any]:
        """
        Parse and validate the AI-generated roadmap.
        """
        try:
            # Parse JSON response
            roadmap_data = json.loads(ai_response)
            
            # Validate required fields
            if not roadmap_data.get('modules'):
                raise ValueError("No modules in AI response")
            
            # Add metadata
            roadmap_data['metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'generation_method': 'groq_ai',
                'model_used': self.model,
                'ai_generated': True
            }
            
            # Ensure skill is set correctly
            roadmap_data['skill'] = skill
            
            # Validate modules structure
            for i, module in enumerate(roadmap_data.get('modules', [])):
                if not module.get('name'):
                    module['name'] = f"Module {i+1}"
                if not module.get('id'):
                    module['id'] = i + 1
                if not module.get('miniProjects'):
                    module['miniProjects'] = []
            
            # Validate major project
            if not roadmap_data.get('majorProject'):
                roadmap_data['majorProject'] = self.create_default_major_project(skill)
            
            return roadmap_data
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse AI JSON response: {e}")
            logging.error(f"AI Response: {ai_response[:500]}...")
            raise ValueError("Invalid JSON from AI")
        except Exception as e:
            logging.error(f"Error parsing AI roadmap: {e}")
            raise
    
    def create_default_major_project(self, skill: str) -> Dict[str, Any]:
        """Create a default major project if AI doesn't provide one."""
        return {
            "name": f"Comprehensive {skill.title()} Portfolio Project",
            "description": f"Build an end-to-end project that demonstrates mastery of {skill} concepts and industry best practices",
            "requirements": [
                f"Implement core {skill} functionality",
                "Follow industry best practices and design patterns",
                "Include comprehensive documentation",
                "Add thorough testing and quality assurance",
                "Deploy to production environment",
                "Demonstrate problem-solving skills"
            ],
            "estimatedHours": 80,
            "technologies": []
        }
    
    def generate_fallback_roadmap(self, skill: str) -> Dict[str, Any]:
        """
        Generate a fallback roadmap when Groq AI fails.
        """
        logging.info(f"Generating fallback roadmap for: {skill}")
        
        # Use skill-specific templates
        if any(term in skill.lower() for term in ['data science', 'machine learning', 'ai']):
            return self.create_data_science_fallback()
        elif any(term in skill.lower() for term in ['web dev', 'frontend', 'backend', 'react', 'javascript']):
            return self.create_web_dev_fallback(skill)
        else:
            return self.create_generic_fallback(skill)
    
    def create_data_science_fallback(self) -> Dict[str, Any]:
        """Create a comprehensive data science fallback roadmap."""
        return {
            "skill": "data science",
            "title": "Complete Data Science Learning Roadmap",
            "modules": [
                {
                    "id": 1,
                    "name": "Python Programming & Data Fundamentals",
                    "description": "Master Python programming with focus on data manipulation and analysis libraries",
                    "miniProjects": [
                        {
                            "name": "COVID-19 Data Analysis Dashboard",
                            "description": "Analyze real COVID-19 data using pandas, numpy, and create interactive visualizations with plotly",
                            "estimatedHours": 15,
                            "technologies": ["Python", "Pandas", "NumPy", "Matplotlib", "Plotly"]
                        },
                        {
                            "name": "Financial Market Data Pipeline",
                            "description": "Build automated data collection and analysis pipeline for stock market data",
                            "estimatedHours": 18,
                            "technologies": ["Python", "yfinance", "Pandas", "SQLite", "Jupyter"]
                        }
                    ]
                },
                {
                    "id": 2,
                    "name": "Statistics & Probability for Data Science",
                    "description": "Build strong foundation in statistical concepts, hypothesis testing, and probability theory",
                    "miniProjects": [
                        {
                            "name": "A/B Testing Platform",
                            "description": "Create complete A/B testing framework with statistical significance calculations and power analysis",
                            "estimatedHours": 20,
                            "technologies": ["SciPy", "Statsmodels", "Seaborn", "Jupyter", "Statistical Tests"]
                        },
                        {
                            "name": "Customer Analytics Dashboard",
                            "description": "Perform comprehensive exploratory data analysis on customer data with statistical insights",
                            "estimatedHours": 16,
                            "technologies": ["Pandas", "Seaborn", "Plotly Dash", "Statistical Analysis"]
                        }
                    ]
                },
                {
                    "id": 3,
                    "name": "Machine Learning & Predictive Analytics",
                    "description": "Learn supervised and unsupervised ML algorithms with hands-on implementation and evaluation",
                    "miniProjects": [
                        {
                            "name": "House Price Prediction with Advanced Feature Engineering",
                            "description": "Build end-to-end ML pipeline with feature engineering, model selection, and hyperparameter tuning",
                            "estimatedHours": 25,
                            "technologies": ["Scikit-learn", "XGBoost", "Feature Engineering", "Cross-validation", "GridSearch"]
                        },
                        {
                            "name": "Customer Churn Prediction System",
                            "description": "Develop complete churn prediction system with model interpretability and business insights",
                            "estimatedHours": 22,
                            "technologies": ["Random Forest", "SHAP", "LIME", "Model Deployment", "Business Intelligence"]
                        }
                    ]
                },
                {
                    "id": 4,
                    "name": "Deep Learning & Neural Networks",
                    "description": "Master neural networks, CNNs, RNNs, and modern deep learning frameworks",
                    "miniProjects": [
                        {
                            "name": "Medical Image Classification with Transfer Learning",
                            "description": "Build CNN models using transfer learning for medical image diagnosis",
                            "estimatedHours": 30,
                            "technologies": ["TensorFlow", "Keras", "Transfer Learning", "CNN", "Data Augmentation"]
                        },
                        {
                            "name": "Stock Price Forecasting with LSTM Networks",
                            "description": "Create LSTM networks for multi-step time series forecasting with attention mechanisms",
                            "estimatedHours": 28,
                            "technologies": ["LSTM", "GRU", "Attention", "Time Series", "PyTorch"]
                        }
                    ]
                },
                {
                    "id": 5,
                    "name": "Natural Language Processing & Text Analytics",
                    "description": "Learn text processing, sentiment analysis, and modern NLP techniques including transformers",
                    "miniProjects": [
                        {
                            "name": "Multi-language Sentiment Analysis API",
                            "description": "Build production-ready sentiment analysis API supporting multiple languages and domains",
                            "estimatedHours": 26,
                            "technologies": ["NLTK", "spaCy", "Transformers", "BERT", "FastAPI", "Docker"]
                        },
                        {
                            "name": "Intelligent Document Processing System",
                            "description": "Create document summarization and question-answering system using transformer models",
                            "estimatedHours": 32,
                            "technologies": ["Transformers", "BERT", "GPT", "Hugging Face", "Vector Databases", "LangChain"]
                        }
                    ]
                },
                {
                    "id": 6,
                    "name": "Computer Vision & Image Processing",
                    "description": "Master image processing, object detection, and computer vision applications",
                    "miniProjects": [
                        {
                            "name": "Real-time Object Detection System",
                            "description": "Implement YOLO-based object detection for real-time video processing and analysis",
                            "estimatedHours": 35,
                            "technologies": ["YOLO", "OpenCV", "Object Detection", "Real-time Processing", "Edge Computing"]
                        },
                        {
                            "name": "Face Recognition & Emotion Detection Platform",
                            "description": "Build comprehensive face analysis system with recognition, emotion detection, and age estimation",
                            "estimatedHours": 30,
                            "technologies": ["Face Recognition", "Emotion Detection", "OpenCV", "Deep Learning", "API Development"]
                        }
                    ]
                }
            ],
            "majorProject": {
                "name": "AI-Powered Business Intelligence & Analytics Platform",
                "description": "Build a comprehensive AI platform that combines multiple data science techniques to solve real business problems across different domains",
                "requirements": [
                    "Multi-source data ingestion pipeline (APIs, databases, files, streaming)",
                    "Real-time data processing and streaming analytics with Apache Kafka",
                    "Advanced statistical analysis and hypothesis testing framework",
                    "Machine learning models for prediction, classification, and clustering",
                    "Deep learning models for image and text analysis",
                    "Natural language processing for document analysis and chatbot functionality",
                    "Computer vision for image/video content analysis and insights",
                    "Interactive dashboard with real-time visualizations using Plotly Dash",
                    "RESTful APIs for all ML models with proper versioning and documentation",
                    "Comprehensive testing, monitoring, and alerting system",
                    "Cloud deployment with auto-scaling and load balancing on AWS/GCP",
                    "Complete CI/CD pipeline with Docker and Kubernetes"
                ],
                "estimatedHours": 120,
                "technologies": ["Python", "TensorFlow", "PyTorch", "FastAPI", "Docker", "Kubernetes", "AWS", "Apache Kafka", "PostgreSQL", "Redis"]
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_method": "groq_fallback",
                "ai_generated": False
            }
        }
    
    def create_web_dev_fallback(self, skill: str) -> Dict[str, Any]:
        """Create a web development fallback roadmap."""
        return {
            "skill": skill,
            "title": f"Complete {skill.title()} Learning Roadmap",
            "modules": [
                {
                    "id": 1,
                    "name": "HTML, CSS & Responsive Design Fundamentals",
                    "description": "Master modern HTML5, CSS3, and responsive design principles for all devices",
                    "miniProjects": [
                        {
                            "name": "Portfolio Website with Advanced CSS",
                            "description": "Build a fully responsive portfolio website using CSS Grid, Flexbox, and animations",
                            "estimatedHours": 12,
                            "technologies": ["HTML5", "CSS3", "CSS Grid", "Flexbox", "Responsive Design"]
                        },
                        {
                            "name": "E-commerce Landing Page",
                            "description": "Create a modern e-commerce landing page with advanced CSS techniques and animations",
                            "estimatedHours": 15,
                            "technologies": ["HTML5", "CSS3", "SASS", "CSS Animations", "Mobile-First Design"]
                        }
                    ]
                },
                {
                    "id": 2,
                    "name": "JavaScript & Modern ES6+ Features",
                    "description": "Learn modern JavaScript, DOM manipulation, and asynchronous programming",
                    "miniProjects": [
                        {
                            "name": "Interactive Task Management App",
                            "description": "Build a feature-rich todo application with local storage and advanced JavaScript",
                            "estimatedHours": 18,
                            "technologies": ["JavaScript ES6+", "DOM Manipulation", "Local Storage", "Event Handling"]
                        },
                        {
                            "name": "Weather Dashboard with API Integration",
                            "description": "Create a weather dashboard that fetches data from multiple APIs and displays interactive charts",
                            "estimatedHours": 20,
                            "technologies": ["JavaScript", "Fetch API", "Async/Await", "Chart.js", "Geolocation API"]
                        }
                    ]
                }
            ],
            "majorProject": {
                "name": "Full-Stack Social Media Platform",
                "description": "Build a complete social media platform with real-time features and modern web technologies",
                "requirements": [
                    "User authentication and authorization system",
                    "Real-time messaging and notifications",
                    "Image and video upload with processing",
                    "Responsive design for all devices",
                    "RESTful API with proper documentation",
                    "Database design and optimization",
                    "Deployment with CI/CD pipeline"
                ],
                "estimatedHours": 100,
                "technologies": ["React", "Node.js", "Express", "MongoDB", "Socket.io", "AWS S3", "Docker"]
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_method": "groq_fallback",
                "ai_generated": False
            }
        }
    
    def create_generic_fallback(self, skill: str) -> Dict[str, Any]:
        """Create a generic fallback roadmap for any skill."""
        return {
            "skill": skill,
            "title": f"Complete {skill.title()} Learning Roadmap",
            "modules": [
                {
                    "id": 1,
                    "name": f"{skill.title()} Fundamentals & Core Concepts",
                    "description": f"Build a strong foundation in {skill} with essential concepts and practical applications",
                    "miniProjects": [
                        {
                            "name": f"Basic {skill.title()} Project",
                            "description": f"Create a foundational project to practice core {skill} concepts and workflows",
                            "estimatedHours": 12,
                            "technologies": [skill.title(), "Best Practices"]
                        }
                    ]
                }
            ],
            "majorProject": self.create_default_major_project(skill),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generation_method": "groq_fallback",
                "ai_generated": False
            }
        }

# Convenience function for the main application
def get_groq_roadmap_for_skill(skill: str) -> Dict[str, Any]:
    """
    Generate a Groq AI-powered roadmap for the specified skill.
    
    Args:
        skill: The skill to generate roadmap for
        
    Returns:
        Complete roadmap dictionary
    """
    generator = GroqAIGenerator()
    return generator.generate_intelligent_roadmap(skill)