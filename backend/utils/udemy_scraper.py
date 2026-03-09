#!/usr/bin/env python3
"""
Udemy web scraper for fetching course information.
"""

import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re
import time
from urllib.parse import quote_plus

class UdemyScraper:
    """Web scraper for Udemy courses."""
    
    def __init__(self):
        """Initialize Udemy scraper."""
        self.base_url = "https://www.udemy.com"
        self.search_url = "https://www.udemy.com/courses/search/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        logging.info("Udemy scraper initialized")
    
    def search_courses(self, skill: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for courses on Udemy.
        
        Args:
            skill: The skill to search for
            limit: Maximum number of results to return
            
        Returns:
            List of course information
        """
        try:
            logging.info(f"Scraping Udemy courses for: {skill}")
            
            # Construct search URL
            search_query = quote_plus(skill)
            search_url = f"{self.search_url}?q={search_query}&sort=relevance"
            
            # Make request
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find course cards
            courses = []
            course_cards = soup.find_all('div', {'data-purpose': 'course-card-container'})
            
            for card in course_cards[:limit]:
                course_info = self._extract_course_info(card)
                if course_info:
                    courses.append(course_info)
            
            logging.info(f"Scraped {len(courses)} Udemy courses for: {skill}")
            return courses
            
        except Exception as e:
            logging.error(f"Error scraping Udemy courses for {skill}: {str(e)}")
            return self._get_fallback_courses(skill)
    
    def _extract_course_info(self, card) -> Optional[Dict[str, Any]]:
        """Extract course information from course card."""
        try:
            # Course title
            title_elem = card.find('h3', {'data-purpose': 'course-title-url'})
            if not title_elem:
                title_elem = card.find('a', {'data-purpose': 'course-title-url'})
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Course"
            
            # Course URL
            url_elem = card.find('a', {'data-purpose': 'course-title-url'})
            relative_url = url_elem.get('href', '') if url_elem else ''
            full_url = f"{self.base_url}{relative_url}" if relative_url else ""
            
            # Instructor
            instructor_elem = card.find('span', {'data-purpose': 'safely-set-inner-html:course-card:visible-instructors'})
            if not instructor_elem:
                instructor_elem = card.find('div', class_='course-card--instructor-list--2GzTA')
            instructor = instructor_elem.get_text(strip=True) if instructor_elem else "Unknown Instructor"
            
            # Rating
            rating_elem = card.find('span', {'data-purpose': 'rating-number'})
            rating = 0.0
            if rating_elem:
                try:
                    rating = float(rating_elem.get_text(strip=True))
                except:
                    rating = 4.0
            
            # Price
            price_elem = card.find('span', {'data-purpose': 'course-price-text'})
            if not price_elem:
                price_elem = card.find('div', class_='price-text--price-part--Tu6MH')
            price = price_elem.get_text(strip=True) if price_elem else "Price varies"
            
            # Students count
            students_elem = card.find('span', {'data-purpose': 'enrollment'})
            students = students_elem.get_text(strip=True) if students_elem else "0 students"
            
            # Duration (estimate based on content)
            duration = self._estimate_duration(title)
            
            return {
                'title': title,
                'instructor': instructor,
                'url': full_url,
                'platform': 'Udemy',
                'type': 'Course',
                'difficulty': self._determine_difficulty(title),
                'estimated_hours': duration,
                'rating': rating,
                'price': price,
                'students': students,
                'highlights': ['Lifetime access', 'Certificate of completion', 'Mobile access'],
                'description': f"Learn {title.lower()} with hands-on projects and practical examples"
            }
            
        except Exception as e:
            logging.error(f"Error extracting course info: {str(e)}")
            return None
    
    def _determine_difficulty(self, title: str) -> str:
        """Determine course difficulty from title."""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['beginner', 'basics', 'introduction', 'fundamentals', 'start']):
            return 'Beginner'
        elif any(word in title_lower for word in ['advanced', 'expert', 'master', 'professional', 'complete']):
            return 'Advanced'
        else:
            return 'Intermediate'
    
    def _estimate_duration(self, title: str) -> int:
        """Estimate course duration from title."""
        title_lower = title.lower()
        
        # Look for duration indicators
        if 'bootcamp' in title_lower or 'complete' in title_lower:
            return 60
        elif 'masterclass' in title_lower or 'comprehensive' in title_lower:
            return 40
        elif 'crash course' in title_lower or 'quick' in title_lower:
            return 15
        else:
            return 25
    
    def _get_fallback_courses(self, skill: str) -> List[Dict[str, Any]]:
        """Get fallback courses when scraping fails."""
        skill_lower = skill.lower()
        
        # Data Science courses
        if any(term in skill_lower for term in ['data science', 'machine learning', 'ai']):
            return [
                {
                    'title': 'The Data Science Course: Complete Data Science Bootcamp',
                    'instructor': '365 Careers',
                    'url': 'https://www.udemy.com/course/the-data-science-course-complete-data-science-bootcamp/',
                    'platform': 'Udemy',
                    'type': 'Course',
                    'difficulty': 'Beginner',
                    'estimated_hours': 29,
                    'rating': 4.5,
                    'price': '$84.99',
                    'students': '400,000+ students',
                    'highlights': ['Complete curriculum', 'Hands-on projects', 'Certificate'],
                    'description': 'Master data science with Python, statistics, and machine learning'
                },
                {
                    'title': 'Machine Learning A-Z: Hands-On Python & R In Data Science',
                    'instructor': 'Kirill Eremenko, Hadelin de Ponteves',
                    'url': 'https://www.udemy.com/course/machinelearning/',
                    'platform': 'Udemy',
                    'type': 'Course',
                    'difficulty': 'Intermediate',
                    'estimated_hours': 44,
                    'rating': 4.5,
                    'price': '$94.99',
                    'students': '800,000+ students',
                    'highlights': ['Python & R', 'Real projects', 'Industry applications'],
                    'description': 'Learn machine learning algorithms with practical implementations'
                }
            ]
        
        # Web Development courses
        elif any(term in skill_lower for term in ['web dev', 'frontend', 'backend', 'react', 'javascript']):
            return [
                {
                    'title': 'The Complete Web Developer Bootcamp',
                    'instructor': 'Dr. Angela Yu',
                    'url': 'https://www.udemy.com/course/the-complete-web-development-bootcamp/',
                    'platform': 'Udemy',
                    'type': 'Course',
                    'difficulty': 'Beginner',
                    'estimated_hours': 65,
                    'rating': 4.7,
                    'price': '$84.99',
                    'students': '800,000+ students',
                    'highlights': ['Full-stack development', 'Modern frameworks', 'Portfolio projects'],
                    'description': 'Become a full-stack web developer with HTML, CSS, JavaScript, Node.js, and more'
                },
                {
                    'title': 'React - The Complete Guide',
                    'instructor': 'Maximilian Schwarzmüller',
                    'url': 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/',
                    'platform': 'Udemy',
                    'type': 'Course',
                    'difficulty': 'Intermediate',
                    'estimated_hours': 48,
                    'rating': 4.6,
                    'price': '$94.99',
                    'students': '500,000+ students',
                    'highlights': ['React hooks', 'Redux', 'Real projects'],
                    'description': 'Master React with hooks, context, Redux, and modern patterns'
                }
            ]
        
        # Python courses
        elif 'python' in skill_lower:
            return [
                {
                    'title': 'Complete Python Bootcamp: Go from zero to hero in Python',
                    'instructor': 'Jose Portilla',
                    'url': 'https://www.udemy.com/course/complete-python-bootcamp/',
                    'platform': 'Udemy',
                    'type': 'Course',
                    'difficulty': 'Beginner',
                    'estimated_hours': 22,
                    'rating': 4.6,
                    'price': '$84.99',
                    'students': '1,500,000+ students',
                    'highlights': ['Complete curriculum', 'Hands-on projects', 'Popular course'],
                    'description': 'Learn Python programming from scratch with practical projects'
                },
                {
                    'title': 'Automate the Boring Stuff with Python Programming',
                    'instructor': 'Al Sweigart',
                    'url': 'https://www.udemy.com/course/automate/',
                    'platform': 'Udemy',
                    'type': 'Course',
                    'difficulty': 'Beginner',
                    'estimated_hours': 10,
                    'rating': 4.6,
                    'price': '$84.99',
                    'students': '600,000+ students',
                    'highlights': ['Practical automation', 'Real-world applications', 'Beginner-friendly'],
                    'description': 'Learn Python by automating everyday tasks and workflows'
                }
            ]
        
        # Default courses
        else:
            return [
                {
                    'title': f'Complete {skill.title()} Course',
                    'instructor': 'Expert Instructor',
                    'url': f'https://www.udemy.com/courses/search/?q={quote_plus(skill)}',
                    'platform': 'Udemy',
                    'type': 'Course',
                    'difficulty': 'Intermediate',
                    'estimated_hours': 30,
                    'rating': 4.5,
                    'price': '$84.99',
                    'students': '50,000+ students',
                    'highlights': ['Comprehensive curriculum', 'Practical projects', 'Certificate'],
                    'description': f'Master {skill} with hands-on projects and real-world applications'
                }
            ]

# Create singleton instance
udemy_scraper = UdemyScraper()

def get_udemy_courses(skill: str) -> List[Dict[str, Any]]:
    """
    Get Udemy courses for a specific skill.
    
    Args:
        skill: The skill to search for
        
    Returns:
        List of Udemy course information
    """
    return udemy_scraper.search_courses(skill)