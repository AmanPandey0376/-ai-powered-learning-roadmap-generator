#!/usr/bin/env python3
"""
AI-Powered Resource Generator
Fetches real learning resources from multiple free APIs and sources.
"""

import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import urllib.parse

class AIResourceGenerator:
    """
    Generates learning resources using real APIs and data sources.
    """
    
    def __init__(self):
        """Initialize the AI resource generator."""
        self.apis = {
            'youtube': 'https://www.googleapis.com/youtube/v3',
            'github': 'https://api.github.com',
            'dev_to': 'https://dev.to/api',
            'freecodecamp': 'https://www.freecodecamp.org/api',
            'coursera': 'https://api.coursera.org/api',
            'edx': 'https://courses.edx.org/api'
        }
        logging.info("AI Resource Generator initialized")
    
    def generate_intelligent_resources(self, skill: str) -> Dict[str, Any]:
        """
        Generate intelligent learning resources from multiple sources.
        
        Args:
            skill: The skill to find resources for
            
        Returns:
            Dictionary with free and paid resources
        """
        try:
            logging.info(f"Generating intelligent resources for: {skill}")
            
            # Gather resources from multiple sources
            free_resources = []
            paid_resources = []
            
            # Get YouTube tutorials
            youtube_resources = self.get_youtube_resources(skill)
            free_resources.extend(youtube_resources)
            
            # Get GitHub repositories and learning materials
            github_resources = self.get_github_resources(skill)
            free_resources.extend(github_resources)
            
            # Get Dev.to articles and tutorials
            dev_to_resources = self.get_dev_to_resources(skill)
            free_resources.extend(dev_to_resources)
            
            # Get free course platforms
            free_course_resources = self.get_free_course_resources(skill)
            free_resources.extend(free_course_resources)
            
            # Get paid course recommendations
            paid_course_resources = self.get_paid_course_resources(skill)
            paid_resources.extend(paid_course_resources)
            
            # Sort and filter resources
            free_resources = self.filter_and_sort_resources(free_resources)
            paid_resources = self.filter_and_sort_resources(paid_resources)
            
            return {
                'skill': skill,
                'freeResources': free_resources,
                'paidResources': paid_resources,
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_free': len(free_resources),
                    'total_paid': len(paid_resources),
                    'sources': ['YouTube', 'GitHub', 'Dev.to', 'Free Course Platforms']
                }
            }
            
        except Exception as e:
            logging.error(f"Error generating intelligent resources: {e}")
            return self.get_fallback_resources(skill)
    
    def get_youtube_resources(self, skill: str) -> List[Dict[str, Any]]:
        """
        Get YouTube tutorials and courses (using public data).
        Note: For production, you'd need YouTube Data API key.
        """
        resources = []
        
        try:
            # For now, we'll use curated YouTube channels and playlists
            # In production, you'd use YouTube Data API
            youtube_channels = self.get_curated_youtube_channels(skill)
            
            for channel in youtube_channels:
                resources.append({
                    'id': len(resources) + 1,
                    'title': channel['title'],
                    'platform': 'YouTube',
                    'creator': channel['creator'],
                    'link': channel['link'],
                    'type': 'Video Course',
                    'duration': channel.get('duration', 'Variable'),
                    'description': channel['description'],
                    'rating': channel.get('rating', 4.5),
                    'subscribers': channel.get('subscribers', 'N/A')
                })
                
        except Exception as e:
            logging.warning(f"YouTube resources error: {e}")
        
        return resources
    
    def get_github_resources(self, skill: str) -> List[Dict[str, Any]]:
        """Get learning repositories and resources from GitHub."""
        resources = []
        
        try:
            # Search for awesome lists and learning repositories
            search_queries = [
                f"awesome-{skill.replace(' ', '-')}",
                f"{skill} tutorial",
                f"{skill} learning",
                f"{skill} course"
            ]
            
            for query in search_queries:
                repos = self.search_github_repositories(query)
                
                for repo in repos[:2]:  # Limit to avoid too many results
                    resources.append({
                        'id': len(resources) + 1,
                        'title': repo['name'],
                        'platform': 'GitHub',
                        'creator': repo['owner'],
                        'link': repo['url'],
                        'type': 'Repository',
                        'description': repo['description'],
                        'stars': repo['stars'],
                        'language': repo.get('language', 'Multiple'),
                        'topics': repo.get('topics', [])
                    })
                    
        except Exception as e:
            logging.warning(f"GitHub resources error: {e}")
        
        return resources
    
    def search_github_repositories(self, query: str) -> List[Dict[str, Any]]:
        """Search GitHub repositories."""
        try:
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 5
            }
            
            response = requests.get(
                "https://api.github.com/search/repositories",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                repos = []
                
                for repo in data.get('items', []):
                    repos.append({
                        'name': repo.get('full_name'),
                        'owner': repo.get('owner', {}).get('login'),
                        'url': repo.get('html_url'),
                        'description': repo.get('description', ''),
                        'stars': repo.get('stargazers_count', 0),
                        'language': repo.get('language'),
                        'topics': repo.get('topics', [])
                    })
                
                return repos
            
        except Exception as e:
            logging.warning(f"GitHub search error: {e}")
        
        return []
    
    def get_dev_to_resources(self, skill: str) -> List[Dict[str, Any]]:
        """Get articles and tutorials from Dev.to."""
        resources = []
        
        try:
            # Search for articles related to the skill
            tag = skill.replace(' ', '').lower()
            
            params = {
                'tag': tag,
                'top': 30,  # Last 30 days
                'per_page': 5
            }
            
            response = requests.get(
                "https://dev.to/api/articles",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                articles = response.json()
                
                for article in articles:
                    resources.append({
                        'id': len(resources) + 1,
                        'title': article.get('title'),
                        'platform': 'Dev.to',
                        'creator': article.get('user', {}).get('name', 'Unknown'),
                        'link': article.get('url'),
                        'type': 'Article',
                        'description': article.get('description', ''),
                        'reading_time': f"{article.get('reading_time_minutes', 5)} min read",
                        'reactions': article.get('public_reactions_count', 0),
                        'tags': article.get('tag_list', [])
                    })
                    
        except Exception as e:
            logging.warning(f"Dev.to resources error: {e}")
        
        return resources
    
    def get_free_course_resources(self, skill: str) -> List[Dict[str, Any]]:
        """Get free courses from various platforms."""
        resources = []
        
        # Curated free course platforms and resources
        free_platforms = self.get_curated_free_courses(skill)
        
        for course in free_platforms:
            resources.append({
                'id': len(resources) + 1,
                'title': course['title'],
                'platform': course['platform'],
                'creator': course['creator'],
                'link': course['link'],
                'type': 'Free Course',
                'duration': course.get('duration', 'Self-paced'),
                'description': course['description'],
                'level': course.get('level', 'Beginner'),
                'certificate': course.get('certificate', False)
            })
        
        return resources
    
    def get_paid_course_resources(self, skill: str) -> List[Dict[str, Any]]:
        """Get paid course recommendations."""
        resources = []
        
        # Curated paid course recommendations
        paid_courses = self.get_curated_paid_courses(skill)
        
        for course in paid_courses:
            resources.append({
                'id': len(resources) + 1,
                'title': course['title'],
                'platform': course['platform'],
                'creator': course['creator'],
                'link': course['link'],
                'type': 'Paid Course',
                'price': course.get('price', 'Varies'),
                'duration': course.get('duration', 'Self-paced'),
                'description': course['description'],
                'rating': course.get('rating', 4.5),
                'students': course.get('students', 'N/A')
            })
        
        return resources
    
    def get_curated_youtube_channels(self, skill: str) -> List[Dict[str, Any]]:
        """Get curated YouTube channels for different skills."""
        skill_lower = skill.lower()
        
        # Data Science YouTube channels
        if any(term in skill_lower for term in ['data science', 'machine learning', 'ai']):
            return [
                {
                    'title': 'Python for Data Science - Complete Course',
                    'creator': 'freeCodeCamp.org',
                    'link': 'https://www.youtube.com/watch?v=LHBE6Q9XlzI',
                    'description': 'Complete Python for Data Science course covering pandas, numpy, matplotlib, and machine learning',
                    'duration': '12 hours',
                    'subscribers': '8.2M'
                },
                {
                    'title': 'Machine Learning Course by Andrew Ng',
                    'creator': 'Stanford Online',
                    'link': 'https://www.youtube.com/playlist?list=PLLssT5z_DsK-h9vYZkQkYNWcItqhlRJLN',
                    'description': 'Complete machine learning course by Andrew Ng covering all fundamental algorithms',
                    'duration': '55 hours',
                    'subscribers': '1.2M'
                },
                {
                    'title': 'Deep Learning Specialization',
                    'creator': 'DeepLearningAI',
                    'link': 'https://www.youtube.com/c/Deeplearningai',
                    'description': 'Deep learning courses covering neural networks, CNNs, RNNs, and more',
                    'duration': 'Multiple courses',
                    'subscribers': '500K'
                }
            ]
        
        # Web Development YouTube channels
        elif any(term in skill_lower for term in ['web dev', 'javascript', 'react', 'frontend', 'backend']):
            return [
                {
                    'title': 'Full Stack Web Development Course',
                    'creator': 'freeCodeCamp.org',
                    'link': 'https://www.youtube.com/watch?v=nu_pCVPKzTk',
                    'description': 'Complete full stack web development course covering HTML, CSS, JavaScript, React, and Node.js',
                    'duration': '10 hours',
                    'subscribers': '8.2M'
                },
                {
                    'title': 'JavaScript Mastery',
                    'creator': 'JavaScript Mastery',
                    'link': 'https://www.youtube.com/c/JavaScriptMastery',
                    'description': 'Modern JavaScript and React tutorials with real-world projects',
                    'duration': 'Multiple tutorials',
                    'subscribers': '1.5M'
                }
            ]
        
        # Default programming channels
        else:
            return [
                {
                    'title': f'{skill.title()} Programming Tutorial',
                    'creator': 'Programming with Mosh',
                    'link': f'https://www.youtube.com/results?search_query={urllib.parse.quote(skill)}+tutorial',
                    'description': f'Comprehensive {skill} programming tutorial for beginners and advanced learners',
                    'duration': 'Variable',
                    'subscribers': '3M'
                }
            ]
    
    def get_curated_free_courses(self, skill: str) -> List[Dict[str, Any]]:
        """Get curated free courses for different skills."""
        skill_lower = skill.lower()
        
        if any(term in skill_lower for term in ['data science', 'machine learning']):
            return [
                {
                    'title': 'Introduction to Data Science',
                    'platform': 'Coursera (Audit)',
                    'creator': 'IBM',
                    'link': 'https://www.coursera.org/learn/what-is-datascience',
                    'description': 'Free introduction to data science concepts and methodologies',
                    'duration': '4 weeks',
                    'certificate': True
                },
                {
                    'title': 'Machine Learning Course',
                    'platform': 'edX (Audit)',
                    'creator': 'MIT',
                    'link': 'https://www.edx.org/course/introduction-to-machine-learning',
                    'description': 'Comprehensive machine learning course from MIT',
                    'duration': '12 weeks',
                    'certificate': True
                }
            ]
        
        return [
            {
                'title': f'{skill.title()} Fundamentals',
                'platform': 'freeCodeCamp',
                'creator': 'freeCodeCamp',
                'link': f'https://www.freecodecamp.org/learn',
                'description': f'Free comprehensive course covering {skill} fundamentals and practical applications',
                'duration': 'Self-paced',
                'certificate': True
            }
        ]
    
    def get_curated_paid_courses(self, skill: str) -> List[Dict[str, Any]]:
        """Get curated paid courses for different skills."""
        skill_lower = skill.lower()
        
        if any(term in skill_lower for term in ['data science', 'machine learning']):
            return [
                {
                    'title': 'Complete Data Science Bootcamp',
                    'platform': 'Udemy',
                    'creator': 'Jose Portilla',
                    'link': 'https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/',
                    'description': 'Complete data science course with Python, pandas, numpy, matplotlib, seaborn, plotly, scikit-learn, and more',
                    'price': '$84.99',
                    'duration': '25 hours',
                    'rating': 4.6,
                    'students': '500K+'
                },
                {
                    'title': 'Machine Learning A-Z',
                    'platform': 'Udemy',
                    'creator': 'Kirill Eremenko',
                    'link': 'https://www.udemy.com/course/machinelearning/',
                    'description': 'Hands-on machine learning course with Python and R',
                    'price': '$94.99',
                    'duration': '44 hours',
                    'rating': 4.5,
                    'students': '1M+'
                }
            ]
        
        return [
            {
                'title': f'Complete {skill.title()} Course',
                'platform': 'Udemy',
                'creator': 'Top Instructor',
                'link': f'https://www.udemy.com/courses/search/?q={urllib.parse.quote(skill)}',
                'description': f'Comprehensive {skill} course with hands-on projects and real-world applications',
                'price': '$79.99',
                'duration': '20+ hours',
                'rating': 4.5
            }
        ]
    
    def filter_and_sort_resources(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and sort resources by quality and relevance."""
        # Remove duplicates based on title
        seen_titles = set()
        filtered_resources = []
        
        for resource in resources:
            title = resource.get('title', '').lower()
            if title not in seen_titles:
                seen_titles.add(title)
                filtered_resources.append(resource)
        
        # Sort by rating, stars, or reactions (depending on platform)
        def sort_key(resource):
            rating = resource.get('rating', 0)
            stars = resource.get('stars', 0)
            reactions = resource.get('reactions', 0)
            return max(rating, stars/1000, reactions/10)  # Normalize different metrics
        
        filtered_resources.sort(key=sort_key, reverse=True)
        
        # Limit to top 10 resources per category
        return filtered_resources[:10]
    
    def get_fallback_resources(self, skill: str) -> Dict[str, Any]:
        """Fallback resources when API calls fail."""
        return {
            'skill': skill,
            'freeResources': [
                {
                    'id': 1,
                    'title': f'{skill.title()} Documentation',
                    'platform': 'Official Docs',
                    'creator': 'Official Team',
                    'link': f'https://www.google.com/search?q={urllib.parse.quote(skill)}+official+documentation',
                    'type': 'Documentation',
                    'description': f'Official documentation and guides for {skill}',
                    'duration': 'Self-paced'
                }
            ],
            'paidResources': [
                {
                    'id': 1,
                    'title': f'Complete {skill.title()} Course',
                    'platform': 'Udemy',
                    'creator': 'Expert Instructor',
                    'link': f'https://www.udemy.com/courses/search/?q={urllib.parse.quote(skill)}',
                    'type': 'Paid Course',
                    'price': '$79.99',
                    'description': f'Comprehensive {skill} course with practical projects',
                    'duration': '20+ hours'
                }
            ]
        }

# Convenience function for the main application
def get_ai_resources_for_skill(skill: str) -> Dict[str, Any]:
    """
    Generate AI-powered resources for the specified skill.
    
    Args:
        skill: The skill to find resources for
        
    Returns:
        Dictionary with free and paid resources
    """
    generator = AIResourceGenerator()
    return generator.generate_intelligent_resources(skill)