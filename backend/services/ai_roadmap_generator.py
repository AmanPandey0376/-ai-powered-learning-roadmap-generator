#!/usr/bin/env python3
"""
AI-Powered Roadmap Generator
Uses multiple approaches to generate intelligent, detailed learning roadmaps.
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class AIRoadmapGenerator:
    """
    Generates intelligent roadmaps using AI and real-world data sources.
    """
    
    def __init__(self):
        """Initialize the AI roadmap generator."""
        self.github_api_base = "https://api.github.com"
        self.roadmap_sh_api = "https://roadmap.sh/api"
        self.free_apis = {
            'github_trending': 'https://api.github.com/search/repositories',
            'dev_to': 'https://dev.to/api/articles',
            'hackernews': 'https://hacker-news.firebaseio.com/v0',
        }
        logging.info("AI Roadmap Generator initialized")
    
    def generate_intelligent_roadmap(self, skill: str) -> Dict[str, Any]:
        """
        Generate an intelligent roadmap using multiple data sources.
        
        Args:
            skill: The skill to generate roadmap for
            
        Returns:
            Comprehensive roadmap with real-world insights
        """
        try:
            logging.info(f"Generating intelligent roadmap for: {skill}")
            
            # Step 1: Get industry trends and popular technologies
            trends = self.get_industry_trends(skill)
            
            # Step 2: Get learning resources from multiple sources
            resources = self.gather_learning_resources(skill)
            
            # Step 3: Generate structured roadmap
            roadmap = self.create_structured_roadmap(skill, trends, resources)
            
            # Step 4: Add real projects and practical applications (optional enhancement)
            # roadmap = self.enhance_with_real_projects(roadmap, skill, trends)
            
            logging.info(f"Successfully generated intelligent roadmap for: {skill}")
            return roadmap
            
        except Exception as e:
            logging.error(f"Error generating intelligent roadmap: {e}")
            # Fallback to enhanced template-based generation
            return self.generate_enhanced_template_roadmap(skill)
    
    def get_industry_trends(self, skill: str) -> Dict[str, Any]:
        """
        Get current industry trends and popular technologies.
        
        Args:
            skill: The skill to analyze
            
        Returns:
            Dictionary with trending technologies, frameworks, and tools
        """
        trends = {
            'popular_repos': [],
            'trending_topics': [],
            'hot_technologies': [],
            'job_market_insights': []
        }
        
        try:
            # Get trending GitHub repositories
            github_trends = self.get_github_trends(skill)
            trends['popular_repos'] = github_trends
            
            # Get trending topics from Dev.to
            dev_trends = self.get_dev_to_trends(skill)
            trends['trending_topics'] = dev_trends
            
            # Extract hot technologies
            trends['hot_technologies'] = self.extract_technologies(github_trends, dev_trends)
            
        except Exception as e:
            logging.warning(f"Could not fetch trends for {skill}: {e}")
        
        return trends
    
    def get_github_trends(self, skill: str) -> List[Dict[str, Any]]:
        """Get trending repositories from GitHub."""
        try:
            # Search for popular repositories related to the skill
            params = {
                'q': f'{skill} language:python OR language:javascript OR language:java',
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            response = requests.get(
                f"{self.github_api_base}/search/repositories",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                repos = []
                
                for repo in data.get('items', [])[:5]:
                    repos.append({
                        'name': repo.get('name'),
                        'description': repo.get('description', ''),
                        'stars': repo.get('stargazers_count', 0),
                        'language': repo.get('language'),
                        'topics': repo.get('topics', [])
                    })
                
                return repos
            
        except Exception as e:
            logging.warning(f"GitHub API error: {e}")
        
        return []
    
    def get_dev_to_trends(self, skill: str) -> List[Dict[str, Any]]:
        """Get trending articles from Dev.to."""
        try:
            params = {
                'tag': skill.replace(' ', ''),
                'top': 7,  # Last 7 days
                'per_page': 5
            }
            
            response = requests.get(
                "https://dev.to/api/articles",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                articles = response.json()
                trends = []
                
                for article in articles[:5]:
                    trends.append({
                        'title': article.get('title'),
                        'tags': article.get('tag_list', []),
                        'reactions': article.get('public_reactions_count', 0)
                    })
                
                return trends
            
        except Exception as e:
            logging.warning(f"Dev.to API error: {e}")
        
        return []
    
    def extract_technologies(self, github_trends: List, dev_trends: List) -> List[str]:
        """Extract popular technologies from trends data."""
        technologies = set()
        
        # Extract from GitHub topics
        for repo in github_trends:
            technologies.update(repo.get('topics', []))
        
        # Extract from Dev.to tags
        for article in dev_trends:
            technologies.update(article.get('tags', []))
        
        # Filter and return relevant technologies
        relevant_techs = [tech for tech in technologies if len(tech) > 2 and tech.isalpha()]
        return list(relevant_techs)[:10]
    
    def create_structured_roadmap(self, skill: str, trends: Dict, resources: Dict) -> Dict[str, Any]:
        """
        Create a structured roadmap based on skill analysis and trends.
        """
        # Define skill-specific learning paths
        skill_paths = self.get_skill_learning_path(skill, trends)
        
        roadmap = {
            'skill': skill,
            'title': f"Complete {skill.title()} Learning Roadmap",
            'modules': skill_paths['modules'],
            'majorProject': skill_paths['major_project'],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'trending_technologies': trends.get('hot_technologies', []),
                'data_sources': ['GitHub API', 'Dev.to API', 'Industry Analysis']
            }
        }
        
        return roadmap
    
    def get_skill_learning_path(self, skill: str, trends: Dict) -> Dict[str, Any]:
        """
        Generate skill-specific learning path with current industry trends.
        """
        skill_lower = skill.lower()
        
        # Data Science Path - Use the detailed roadmap from JSON first
        if any(term in skill_lower for term in ['data science', 'data scientist']):
            # Try to get the detailed roadmap from our JSON data first
            try:
                from services.roadmap_generator import get_roadmap_for_skill
                detailed_roadmap = get_roadmap_for_skill(skill)
                if detailed_roadmap and len(detailed_roadmap.get('modules', [])) > 4:
                    # We have a detailed roadmap, enhance it with trends
                    return {
                        'modules': detailed_roadmap['modules'],
                        'major_project': detailed_roadmap.get('majorProject', self.create_generic_major_project(skill))
                    }
            except:
                pass
            # Fallback to AI-generated path
            return self.create_data_science_path(trends)
        
        # Machine Learning Path
        elif any(term in skill_lower for term in ['machine learning', 'ai', 'artificial intelligence']):
            return self.create_data_science_path(trends)
        
        # Web Development Path
        elif any(term in skill_lower for term in ['web dev', 'frontend', 'backend', 'full stack', 'react', 'javascript']):
            return self.create_generic_intelligent_path(skill, trends)
        
        # Mobile Development Path
        elif any(term in skill_lower for term in ['mobile', 'android', 'ios', 'flutter', 'react native']):
            return self.create_generic_intelligent_path(skill, trends)
        
        # DevOps Path
        elif any(term in skill_lower for term in ['devops', 'cloud', 'aws', 'docker', 'kubernetes']):
            return self.create_generic_intelligent_path(skill, trends)
        
        # Cybersecurity Path
        elif any(term in skill_lower for term in ['security', 'cybersecurity', 'ethical hacking', 'penetration testing']):
            return self.create_generic_intelligent_path(skill, trends)
        
        # Default: Generate based on trends and common patterns
        else:
            return self.create_generic_intelligent_path(skill, trends)
    
    def create_data_science_path(self, trends: Dict) -> Dict[str, Any]:
        """Create comprehensive data science learning path."""
        hot_techs = trends.get('hot_technologies', [])
        
        modules = [
            {
                "id": 1,
                "name": "Python Programming & Data Fundamentals",
                "description": "Master Python programming with focus on data manipulation, analysis libraries, and scientific computing",
                "miniProjects": [
                    {
                        "name": "COVID-19 Data Analysis Dashboard",
                        "description": "Analyze real COVID-19 data using pandas, numpy, and create interactive visualizations",
                        "estimatedHours": 15,
                        "technologies": ["Python", "Pandas", "NumPy", "Matplotlib", "Plotly"]
                    },
                    {
                        "name": "Financial Market Data Scraper",
                        "description": "Build a web scraper to collect stock market data and perform basic financial analysis",
                        "estimatedHours": 12,
                        "technologies": ["BeautifulSoup", "Requests", "yfinance", "Pandas"]
                    }
                ]
            },
            {
                "id": 2,
                "name": "Statistics, Probability & Exploratory Data Analysis",
                "description": "Build strong foundation in statistical concepts, hypothesis testing, and data exploration techniques",
                "miniProjects": [
                    {
                        "name": "A/B Testing Platform",
                        "description": "Create a complete A/B testing framework with statistical significance calculations",
                        "estimatedHours": 18,
                        "technologies": ["SciPy", "Statsmodels", "Seaborn", "Jupyter"]
                    },
                    {
                        "name": "Customer Analytics Dashboard",
                        "description": "Perform comprehensive EDA on customer data with statistical insights and recommendations",
                        "estimatedHours": 20,
                        "technologies": ["Pandas", "Seaborn", "Plotly Dash", "Statistical Tests"]
                    }
                ]
            },
            {
                "id": 3,
                "name": "Machine Learning Algorithms & Implementation",
                "description": "Learn supervised and unsupervised ML algorithms with hands-on implementation and evaluation",
                "miniProjects": [
                    {
                        "name": "House Price Prediction with Feature Engineering",
                        "description": "Build end-to-end ML pipeline with advanced feature engineering and model selection",
                        "estimatedHours": 25,
                        "technologies": ["Scikit-learn", "XGBoost", "Feature Engineering", "Cross-validation"]
                    },
                    {
                        "name": "Customer Churn Prediction System",
                        "description": "Develop a complete churn prediction system with model interpretability and business insights",
                        "estimatedHours": 22,
                        "technologies": ["Random Forest", "SHAP", "LIME", "Model Deployment"]
                    }
                ]
            },
            {
                "id": 4,
                "name": "Deep Learning & Neural Networks",
                "description": "Master neural networks, CNNs, RNNs, and modern deep learning frameworks for complex problems",
                "miniProjects": [
                    {
                        "name": "Image Classification with Transfer Learning",
                        "description": "Build CNN models using transfer learning for medical image classification",
                        "estimatedHours": 30,
                        "technologies": ["TensorFlow", "Keras", "Transfer Learning", "CNN", "Data Augmentation"]
                    },
                    {
                        "name": "Time Series Forecasting with LSTM",
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
                        "description": "Build a production-ready sentiment analysis API supporting multiple languages",
                        "estimatedHours": 26,
                        "technologies": ["NLTK", "spaCy", "Transformers", "BERT", "FastAPI"]
                    },
                    {
                        "name": "Document Summarization & QA System",
                        "description": "Create an intelligent document processing system with summarization and question-answering",
                        "estimatedHours": 32,
                        "technologies": ["Transformers", "BERT", "GPT", "Hugging Face", "Vector Databases"]
                    }
                ]
            },
            {
                "id": 6,
                "name": "Computer Vision & Image Processing",
                "description": "Master image processing, object detection, and computer vision applications using deep learning",
                "miniProjects": [
                    {
                        "name": "Real-time Object Detection System",
                        "description": "Implement YOLO-based object detection for real-time video processing",
                        "estimatedHours": 35,
                        "technologies": ["YOLO", "OpenCV", "Object Detection", "Real-time Processing"]
                    },
                    {
                        "name": "Face Recognition & Emotion Detection",
                        "description": "Build a comprehensive face analysis system with recognition and emotion detection",
                        "estimatedHours": 30,
                        "technologies": ["Face Recognition", "Emotion Detection", "OpenCV", "Deep Learning"]
                    }
                ]
            },
            {
                "id": 7,
                "name": "Generative AI & Large Language Models",
                "description": "Learn transformer architecture, work with LLMs, and build generative AI applications",
                "miniProjects": [
                    {
                        "name": "Custom ChatGPT Clone with RAG",
                        "description": "Build a domain-specific chatbot using retrieval-augmented generation",
                        "estimatedHours": 40,
                        "technologies": ["OpenAI API", "LangChain", "Vector Databases", "RAG", "Streamlit"]
                    },
                    {
                        "name": "AI Content Generation Platform",
                        "description": "Create a multi-modal AI platform for text, image, and code generation",
                        "estimatedHours": 45,
                        "technologies": ["GPT-4", "DALL-E", "Stable Diffusion", "Multi-modal AI"]
                    }
                ]
            },
            {
                "id": 8,
                "name": "MLOps, Deployment & Production Systems",
                "description": "Learn to deploy, monitor, and maintain ML systems in production environments",
                "miniProjects": [
                    {
                        "name": "End-to-End MLOps Pipeline",
                        "description": "Build complete MLOps pipeline with CI/CD, model versioning, and monitoring",
                        "estimatedHours": 38,
                        "technologies": ["MLflow", "Docker", "Kubernetes", "CI/CD", "Model Monitoring"]
                    },
                    {
                        "name": "Scalable ML Microservices Architecture",
                        "description": "Design and implement scalable ML services with load balancing and auto-scaling",
                        "estimatedHours": 42,
                        "technologies": ["FastAPI", "Docker", "Kubernetes", "Load Balancing", "Auto-scaling"]
                    }
                ]
            }
        ]
        
        major_project = {
            "name": "AI-Powered Business Intelligence & Analytics Platform",
            "description": "Build a comprehensive AI platform that combines multiple data science techniques to solve real business problems across different domains",
            "requirements": [
                "Multi-source data ingestion pipeline (APIs, databases, files)",
                "Real-time data processing and streaming analytics",
                "Advanced statistical analysis and hypothesis testing framework",
                "Machine learning models for prediction, classification, and clustering",
                "Deep learning models for image and text analysis",
                "Natural language processing for document analysis and chatbot",
                "Computer vision for image/video content analysis",
                "Generative AI features for content creation and insights",
                "Interactive dashboard with real-time visualizations",
                "RESTful APIs for all ML models with proper versioning",
                "Comprehensive testing, monitoring, and alerting system",
                "Cloud deployment with auto-scaling and load balancing",
                "Complete documentation and user guides"
            ],
            "estimatedHours": 150,
            "technologies": hot_techs + ["Python", "TensorFlow", "PyTorch", "FastAPI", "Docker", "Kubernetes", "AWS/GCP"]
        }
        
        return {
            'modules': modules,
            'major_project': major_project
        }
    
    def create_web_development_path(self, skill: str, trends: Dict) -> Dict[str, Any]:
        """Create web development learning path based on specific focus."""
        # Implementation for web development paths
        # This would be similar to data science but focused on web technologies
        pass
    
    def generate_enhanced_template_roadmap(self, skill: str) -> Dict[str, Any]:
        """
        Fallback method that generates enhanced template-based roadmaps.
        Used when API calls fail or for unsupported skills.
        """
        return {
            'skill': skill,
            'title': f"Enhanced {skill.title()} Learning Path",
            'modules': self.create_generic_modules(skill),
            'majorProject': self.create_generic_major_project(skill),
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generation_method': 'enhanced_template',
                'note': 'This roadmap was generated using enhanced templates. For more detailed roadmaps, ensure internet connectivity for AI-powered generation.'
            }
        }
    
    def create_generic_modules(self, skill: str) -> List[Dict[str, Any]]:
        """Create generic but intelligent modules for any skill."""
        skill_title = skill.title()
        
        return [
            {
                "id": 1,
                "name": f"{skill_title} Fundamentals & Core Concepts",
                "description": f"Build a strong foundation in {skill} with essential concepts, terminology, and basic principles",
                "miniProjects": [
                    {
                        "name": f"Basic {skill_title} Project",
                        "description": f"Create a foundational project to practice core {skill} concepts and workflows",
                        "estimatedHours": 10
                    },
                    {
                        "name": f"{skill_title} Concept Explorer",
                        "description": f"Build an interactive tool to explore and demonstrate key {skill} principles",
                        "estimatedHours": 12
                    }
                ]
            },
            {
                "id": 2,
                "name": f"Intermediate {skill_title} Techniques",
                "description": f"Advance your {skill} skills with intermediate concepts, tools, and methodologies",
                "miniProjects": [
                    {
                        "name": f"Real-world {skill_title} Application",
                        "description": f"Develop a practical application that solves real problems using {skill}",
                        "estimatedHours": 18
                    },
                    {
                        "name": f"{skill_title} Automation Tool",
                        "description": f"Create tools to automate common {skill} tasks and workflows",
                        "estimatedHours": 15
                    }
                ]
            },
            {
                "id": 3,
                "name": f"Advanced {skill_title} & Best Practices",
                "description": f"Master advanced {skill} techniques, industry best practices, and optimization strategies",
                "miniProjects": [
                    {
                        "name": f"Enterprise-level {skill_title} System",
                        "description": f"Build a scalable, production-ready system demonstrating advanced {skill} concepts",
                        "estimatedHours": 25
                    },
                    {
                        "name": f"{skill_title} Performance Optimizer",
                        "description": f"Develop tools and techniques for optimizing {skill} performance and efficiency",
                        "estimatedHours": 20
                    }
                ]
            },
            {
                "id": 4,
                "name": f"Professional {skill_title} Development",
                "description": f"Learn industry standards, collaboration tools, and deployment strategies for {skill}",
                "miniProjects": [
                    {
                        "name": f"{skill_title} Testing & Quality Assurance Suite",
                        "description": f"Implement comprehensive testing and quality assurance for {skill} projects",
                        "estimatedHours": 16
                    },
                    {
                        "name": f"Production {skill_title} Deployment",
                        "description": f"Deploy and maintain {skill} applications in production environments",
                        "estimatedHours": 22
                    }
                ]
            }
        ]
    
    def create_generic_major_project(self, skill: str) -> Dict[str, Any]:
        """Create a comprehensive major project for any skill."""
        skill_title = skill.title()
        
        return {
            "name": f"Comprehensive {skill_title} Portfolio Project",
            "description": f"Build an end-to-end project that demonstrates mastery of {skill} concepts, best practices, and real-world application",
            "requirements": [
                f"Implement core {skill} functionality and features",
                f"Follow {skill} best practices and design patterns",
                "Include comprehensive documentation and user guides",
                "Add thorough testing and quality assurance",
                "Deploy to production environment with monitoring",
                "Demonstrate problem-solving and critical thinking skills",
                "Include performance optimization and scalability considerations",
                "Showcase integration with relevant tools and technologies"
            ],
            "estimatedHours": 60
        }
    
    def gather_learning_resources(self, skill: str) -> Dict[str, Any]:
        """
        Gather learning resources from multiple sources.
        This would be used to enhance the resources endpoint as well.
        """
        # This method would gather resources from various APIs
        # Implementation would be similar to the roadmap generation
        return {
            'free_resources': [],
            'paid_resources': [],
            'trending_courses': [],
            'popular_tutorials': []
        }

# Convenience function for the main application
def get_ai_roadmap_for_skill(skill: str) -> Dict[str, Any]:
    """
    Generate an AI-powered roadmap for the specified skill.
    
    Args:
        skill: The skill to generate roadmap for
        
    Returns:
        Complete roadmap dictionary
    """
    generator = AIRoadmapGenerator()
    return generator.generate_intelligent_roadmap(skill)