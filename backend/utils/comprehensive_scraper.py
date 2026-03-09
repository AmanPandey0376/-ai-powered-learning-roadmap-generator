#!/usr/bin/env python3
"""
Comprehensive scraper that orchestrates all platform scrapers.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any
import time

from utils.youtube_api import get_youtube_courses
from utils.youtube_scraper import get_youtube_courses_scraper
from utils.coursera_api import get_coursera_courses
from utils.github_api import get_github_resources
from utils.udemy_scraper import get_udemy_courses
from utils.kaggle_scraper import get_kaggle_courses

class ComprehensiveScraper:
    """Orchestrates scraping from all learning platforms."""
    
    def __init__(self):
        """Initialize comprehensive scraper."""
        self.max_workers = 5  # Number of platforms
        self.timeout = 30  # Timeout per platform
        logging.info("Comprehensive scraper initialized")
    
    def scrape_all_platforms(self, skill: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape resources from all platforms concurrently.
        
        Args:
            skill: The skill to search for
            
        Returns:
            Dictionary containing resources from all platforms
        """
        try:
            logging.info(f"Starting comprehensive scraping for: {skill}")
            start_time = time.time()
            
            all_resources = {
                "YouTube": [],
                "Coursera": [],
                "GitHub": [],
                "Udemy": [],
                "Kaggle": []
            }
            
            # Define scraping functions with YouTube fallback
            def get_youtube_with_fallback(skill):
                try:
                    # Try API first
                    results = get_youtube_courses(skill)
                    if results:
                        logging.info(f"YouTube API returned {len(results)} results")
                        return results
                    else:
                        logging.warning("YouTube API returned no results, trying scraper")
                        return get_youtube_courses_scraper(skill)
                except Exception as e:
                    logging.warning(f"YouTube API failed: {e}, trying scraper")
                    return get_youtube_courses_scraper(skill)
            
            scraping_functions = [
                ("YouTube", lambda: get_youtube_with_fallback(skill)),
                ("Coursera", lambda: get_coursera_courses(skill)),
                ("GitHub", lambda: get_github_resources(skill)),
                ("Udemy", lambda: get_udemy_courses(skill)),
                ("Kaggle", lambda: get_kaggle_courses(skill))
            ]
            
            # Execute scraping concurrently
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all scraping tasks
                future_to_platform = {
                    executor.submit(func): platform 
                    for platform, func in scraping_functions
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_platform, timeout=self.timeout):
                    platform = future_to_platform[future]
                    try:
                        resources = future.result(timeout=10)  # Individual timeout
                        all_resources[platform] = resources
                        logging.info(f"SUCCESS {platform}: {len(resources)} resources scraped")
                    except Exception as e:
                        logging.error(f"FAILED {platform} scraping failed: {str(e)}")
                        all_resources[platform] = []
            
            # Log summary
            total_resources = sum(len(resources) for resources in all_resources.values())
            elapsed_time = time.time() - start_time
            
            logging.info(f"COMPLETE Comprehensive scraping completed in {elapsed_time:.2f}s")
            logging.info(f"TOTAL Total resources found: {total_resources}")
            
            # Log per-platform results
            for platform, resources in all_resources.items():
                status = "SUCCESS" if resources else "FAILED"
                logging.info(f"   {status} {platform}: {len(resources)} resources")
            
            return all_resources
            
        except Exception as e:
            logging.error(f"Error in comprehensive scraping for {skill}: {str(e)}")
            return self._get_emergency_fallback(skill)
    
    def get_categorized_resources(self, skill: str) -> Dict[str, Any]:
        """
        Get resources categorized by free and paid.
        
        Args:
            skill: The skill to search for
            
        Returns:
            Dictionary with categorized resources
        """
        try:
            # Scrape all platforms
            all_platform_resources = self.scrape_all_platforms(skill)
            
            # Categorize resources
            free_resources = []
            paid_resources = []
            
            for platform, resources in all_platform_resources.items():
                for resource in resources:
                    # Determine if resource is free or paid
                    price = resource.get('price', '').lower()
                    is_free = (
                        price == 'free' or 
                        'free' in price or 
                        price == '' or
                        'audit' in price or
                        platform in ['YouTube', 'GitHub', 'Kaggle']
                    )
                    
                    if is_free:
                        free_resources.append(resource)
                    else:
                        paid_resources.append(resource)
            
            # Sort by rating and popularity
            free_resources.sort(key=lambda x: (x.get('rating', 0), x.get('stars', 0)), reverse=True)
            paid_resources.sort(key=lambda x: (x.get('rating', 0), x.get('estimated_hours', 0)), reverse=True)
            
            result = {
                'skill': skill,
                'freeResources': free_resources,
                'paidResources': paid_resources,
                'metadata': {
                    'total_free': len(free_resources),
                    'total_paid': len(paid_resources),
                    'platforms_scraped': list(all_platform_resources.keys()),
                    'scraping_method': 'comprehensive_multi_platform'
                }
            }
            
            logging.info(f"CATEGORIZED Categorized resources: {len(free_resources)} free, {len(paid_resources)} paid")
            return result
            
        except Exception as e:
            logging.error(f"Error categorizing resources for {skill}: {str(e)}")
            return self._get_emergency_fallback(skill)
    
    def _get_emergency_fallback(self, skill: str) -> Dict[str, Any]:
        """Emergency fallback when all scraping fails."""
        logging.warning(f"Using emergency fallback for: {skill}")
        
        skill_lower = skill.lower()
        
        # Basic fallback resources
        if any(term in skill_lower for term in ['data science', 'machine learning', 'ai']):
            free_resources = [
                {
                    'title': 'Kaggle Learn - Data Science',
                    'instructor': 'Kaggle',
                    'url': 'https://www.kaggle.com/learn',
                    'platform': 'Kaggle',
                    'type': 'Micro-Course',
                    'difficulty': 'Beginner',
                    'estimated_hours': 20,
                    'rating': 4.7,
                    'price': 'Free',
                    'description': 'Learn data science with hands-on exercises',
                    'highlights': ['Interactive', 'Free certificates', 'Real datasets']
                }
            ]
            paid_resources = [
                {
                    'title': 'Data Science Bootcamp',
                    'instructor': 'Udemy',
                    'url': 'https://www.udemy.com',
                    'platform': 'Udemy',
                    'type': 'Course',
                    'difficulty': 'Beginner',
                    'estimated_hours': 50,
                    'rating': 4.5,
                    'price': '$84.99',
                    'description': 'Complete data science bootcamp',
                    'highlights': ['Comprehensive', 'Lifetime access', 'Certificate']
                }
            ]
        else:
            # Generic fallback
            free_resources = [
                {
                    'title': f'{skill.title()} Tutorials',
                    'instructor': 'YouTube',
                    'url': 'https://www.youtube.com',
                    'platform': 'YouTube',
                    'type': 'Video',
                    'difficulty': 'Beginner',
                    'estimated_hours': 10,
                    'rating': 4.3,
                    'price': 'Free',
                    'description': f'Learn {skill} through video tutorials',
                    'highlights': ['Video format', 'Free access', 'Visual learning']
                }
            ]
            paid_resources = [
                {
                    'title': f'{skill.title()} Course',
                    'instructor': 'Udemy',
                    'url': 'https://www.udemy.com',
                    'platform': 'Udemy',
                    'type': 'Course',
                    'difficulty': 'Intermediate',
                    'estimated_hours': 30,
                    'rating': 4.4,
                    'price': '$84.99',
                    'description': f'Master {skill} with practical projects',
                    'highlights': ['Hands-on projects', 'Certificate', 'Lifetime access']
                }
            ]
        
        return {
            'skill': skill,
            'freeResources': free_resources,
            'paidResources': paid_resources,
            'metadata': {
                'total_free': len(free_resources),
                'total_paid': len(paid_resources),
                'platforms_scraped': ['Emergency Fallback'],
                'scraping_method': 'emergency_fallback'
            }
        }

# Create singleton instance
comprehensive_scraper = ComprehensiveScraper()

def scrape_all_learning_resources(skill: str) -> Dict[str, Any]:
    """
    Scrape learning resources from all platforms.
    
    Args:
        skill: The skill to search for
        
    Returns:
        Categorized resources from all platforms
    """
    return comprehensive_scraper.get_categorized_resources(skill)

def scrape_platform_resources(skill: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Scrape resources organized by platform.
    
    Args:
        skill: The skill to search for
        
    Returns:
        Resources organized by platform
    """
    return comprehensive_scraper.scrape_all_platforms(skill)