#!/usr/bin/env python3
"""
Kaggle Learn web scraper for fetching course information.
"""

import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re
import json

class KaggleScraper:
    """Web scraper for Kaggle Learn courses."""
    
    def __init__(self):
        """Initialize Kaggle scraper."""
        self.base_url = "https://www.kaggle.com"
        self.learn_url = "https://www.kaggle.com/learn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        logging.info("Kaggle scraper initialized")
    
    def get_courses(self, skill: str = None) -> List[Dict[str, Any]]:
        """
        Get all available Kaggle Learn courses.
        
        Args:
            skill: Optional skill filter (not used as Kaggle has fixed courses)
            
        Returns:
            List of course information
        """
        try:
            logging.info("Scraping Kaggle Learn courses")
            
            # Get the main learn page
            response = self.session.get(self.learn_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            courses = []
            
            # Find course cards
            course_cards = soup.find_all('div', class_='sc-bZQynM')
            if not course_cards:
                course_cards = soup.find_all('a', href=re.compile(r'/learn/'))
            
            for card in course_cards:
                course_info = self._extract_course_info(card)
                if course_info:
                    courses.append(course_info)
            
            # If scraping fails, use fallback data
            if not courses:
                courses = self._get_all_kaggle_courses()
            
            # Filter by skill if provided
            if skill:
                courses = self._filter_by_skill(courses, skill)
            
            logging.info(f"Found {len(courses)} Kaggle Learn courses")
            return courses
            
        except Exception as e:
            logging.error(f"Error scraping Kaggle courses: {str(e)}")
            return self._get_all_kaggle_courses()
    
    def _extract_course_info(self, card) -> Optional[Dict[str, Any]]:
        """Extract course information from course card."""
        try:
            # Course title
            title_elem = card.find('h3') or card.find('h2') or card.find('span')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            if not title or len(title) < 3:
                return None
            
            # Course URL
            url = ""
            if card.name == 'a':
                url = card.get('href', '')
            else:
                link_elem = card.find('a')
                url = link_elem.get('href', '') if link_elem else ""
            
            if url and not url.startswith('http'):
                url = f"{self.base_url}{url}"
            
            # Description (try to find)
            desc_elem = card.find('p') or card.find('div', class_='description')
            description = desc_elem.get_text(strip=True) if desc_elem else f"Learn {title.lower()} with hands-on exercises"
            
            # Duration (try to extract)
            duration_elem = card.find('span', string=re.compile(r'\d+\s*(hour|hr)'))
            duration = 4  # Default
            if duration_elem:
                duration_text = duration_elem.get_text()
                duration_match = re.search(r'(\d+)', duration_text)
                if duration_match:
                    duration = int(duration_match.group(1))
            
            return {
                'title': title,
                'instructor': 'Kaggle',
                'url': url,
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Beginner',
                'estimated_hours': duration,
                'rating': 4.7,
                'price': 'Free',
                'description': description,
                'highlights': ['Hands-on exercises', 'Real datasets', 'Free certificate'],
                'format': 'Interactive notebooks'
            }
            
        except Exception as e:
            logging.error(f"Error extracting Kaggle course info: {str(e)}")
            return None
    
    def _filter_by_skill(self, courses: List[Dict[str, Any]], skill: str) -> List[Dict[str, Any]]:
        """Filter courses by skill relevance."""
        skill_lower = skill.lower()
        filtered_courses = []
        
        for course in courses:
            title_lower = course['title'].lower()
            description_lower = course['description'].lower()
            
            # Check if skill matches course content
            if (skill_lower in title_lower or 
                skill_lower in description_lower or
                any(term in title_lower for term in skill_lower.split())):
                filtered_courses.append(course)
        
        # If no direct matches, return data science related courses for most skills
        if not filtered_courses and any(term in skill_lower for term in ['data', 'machine', 'ai', 'python', 'analysis']):
            filtered_courses = [c for c in courses if any(term in c['title'].lower() for term in ['python', 'machine', 'data', 'pandas'])]
        
        return filtered_courses[:5]  # Limit to 5 most relevant
    
    def _get_all_kaggle_courses(self) -> List[Dict[str, Any]]:
        """Get all Kaggle Learn courses as fallback."""
        return [
            {
                'title': 'Python',
                'instructor': 'Kaggle',
                'url': 'https://www.kaggle.com/learn/python',
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Beginner',
                'estimated_hours': 5,
                'rating': 4.8,
                'price': 'Free',
                'description': 'Learn the most important language for data science',
                'highlights': ['Interactive coding', 'Immediate feedback', 'Free certificate'],
                'format': 'Interactive notebooks'
            },
            {
                'title': 'Intro to Machine Learning',
                'instructor': 'Kaggle',
                'url': 'https://www.kaggle.com/learn/intro-to-machine-learning',
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Beginner',
                'estimated_hours': 7,
                'rating': 4.7,
                'price': 'Free',
                'description': 'Learn the core ideas in machine learning, and build your first models',
                'highlights': ['Hands-on exercises', 'Real datasets', 'Practical focus'],
                'format': 'Interactive notebooks'
            },
            {
                'title': 'Pandas',
                'instructor': 'Kaggle',
                'url': 'https://www.kaggle.com/learn/pandas',
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Beginner',
                'estimated_hours': 4,
                'rating': 4.6,
                'price': 'Free',
                'description': 'Solve real-world data science tasks with Python Pandas',
                'highlights': ['Data manipulation', 'Real examples', 'Practical skills'],
                'format': 'Interactive notebooks'
            },
            {
                'title': 'Data Visualization',
                'instructor': 'Kaggle',
                'url': 'https://www.kaggle.com/learn/data-visualization',
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Beginner',
                'estimated_hours': 4,
                'rating': 4.5,
                'price': 'Free',
                'description': 'Make great data visualizations. A great way to see the power of coding!',
                'highlights': ['Visual storytelling', 'Multiple libraries', 'Beautiful charts'],
                'format': 'Interactive notebooks'
            },
            {
                'title': 'Feature Engineering',
                'instructor': 'Kaggle',
                'url': 'https://www.kaggle.com/learn/feature-engineering',
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Intermediate',
                'estimated_hours': 5,
                'rating': 4.6,
                'price': 'Free',
                'description': 'Discover the most effective way to improve your models',
                'highlights': ['Advanced techniques', 'Model improvement', 'Competition insights'],
                'format': 'Interactive notebooks'
            },
            {
                'title': 'Deep Learning',
                'instructor': 'Kaggle',
                'url': 'https://www.kaggle.com/learn/deep-learning',
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Intermediate',
                'estimated_hours': 6,
                'rating': 4.5,
                'price': 'Free',
                'description': 'Use TensorFlow and Keras to build and train neural networks',
                'highlights': ['TensorFlow', 'Neural networks', 'Modern techniques'],
                'format': 'Interactive notebooks'
            },
            {
                'title': 'SQL',
                'instructor': 'Kaggle',
                'url': 'https://www.kaggle.com/learn/intro-to-sql',
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Beginner',
                'estimated_hours': 4,
                'rating': 4.7,
                'price': 'Free',
                'description': 'Learn SQL for working with databases, using Google BigQuery',
                'highlights': ['Database skills', 'BigQuery', 'Real data'],
                'format': 'Interactive notebooks'
            },
            {
                'title': 'Natural Language Processing',
                'instructor': 'Kaggle',
                'url': 'https://www.kaggle.com/learn/natural-language-processing',
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Intermediate',
                'estimated_hours': 4,
                'rating': 4.4,
                'price': 'Free',
                'description': 'Build models to understand and generate text',
                'highlights': ['Text processing', 'Modern NLP', 'Practical applications'],
                'format': 'Interactive notebooks'
            },
            {
                'title': 'Computer Vision',
                'instructor': 'Kaggle',
                'url': 'https://www.kaggle.com/learn/computer-vision',
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Intermediate',
                'estimated_hours': 4,
                'rating': 4.3,
                'price': 'Free',
                'description': 'Build convolutional neural networks with TensorFlow and Keras',
                'highlights': ['Image processing', 'CNNs', 'TensorFlow'],
                'format': 'Interactive notebooks'
            },
            {
                'title': 'Time Series',
                'instructor': 'Kaggle',
                'url': 'https://www.kaggle.com/learn/time-series',
                'platform': 'Kaggle',
                'type': 'Micro-Course',
                'difficulty': 'Intermediate',
                'estimated_hours': 5,
                'rating': 4.4,
                'price': 'Free',
                'description': 'Apply machine learning to real-world forecasting tasks',
                'highlights': ['Forecasting', 'Time series analysis', 'Real applications'],
                'format': 'Interactive notebooks'
            }
        ]

# Create singleton instance
kaggle_scraper = KaggleScraper()

def get_kaggle_courses(skill: str) -> List[Dict[str, Any]]:
    """
    Get Kaggle Learn courses for a specific skill.
    
    Args:
        skill: The skill to search for
        
    Returns:
        List of Kaggle course information
    """
    return kaggle_scraper.get_courses(skill)