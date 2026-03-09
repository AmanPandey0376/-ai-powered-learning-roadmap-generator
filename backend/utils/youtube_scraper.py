#!/usr/bin/env python3
"""
YouTube web scraper for educational content (fallback when API fails).
"""

import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re
import time
import random
from urllib.parse import quote_plus, urljoin

class YouTubeScraper:
    """Web scraper for YouTube educational content."""
    
    def __init__(self):
        """Initialize YouTube scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 15
        self.delay_range = (1, 3)
        logging.info("YouTube scraper initialized")
    
    def search_courses(self, skill: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for YouTube courses/playlists related to a skill.
        
        Args:
            skill: The skill to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of course information
        """
        try:
            logging.info(f"Searching YouTube for: {skill}")
            
            # Create search queries for better results
            search_queries = [
                f"{skill} complete course tutorial",
                f"{skill} full tutorial playlist",
                f"learn {skill} step by step",
                f"{skill} beginner to advanced"
            ]
            
            all_courses = []
            
            for query in search_queries:
                courses = self._search_single_query(query, max_results // len(search_queries))
                all_courses.extend(courses)
                
                # Add delay between searches
                time.sleep(random.uniform(*self.delay_range))
            
            # Remove duplicates and sort by relevance
            unique_courses = self._remove_duplicates(all_courses)
            sorted_courses = self._sort_by_relevance(unique_courses, skill)
            
            result = sorted_courses[:max_results]
            logging.info(f"Found {len(result)} YouTube courses for: {skill}")
            return result
            
        except Exception as e:
            logging.error(f"Error searching YouTube for {skill}: {str(e)}")
            return self._get_youtube_fallback(skill)
    
    def _search_single_query(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search YouTube for a single query."""
        try:
            # YouTube search URL
            search_url = "https://www.youtube.com/results"
            params = {
                'search_query': query,
                'sp': 'EgIQAw%253D%253D'  # Filter for playlists
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse the response
            soup = BeautifulSoup(response.content, 'html.parser')
            courses = []
            
            # Find script tag with initial data
            script_tags = soup.find_all('script')
            for script in script_tags:
                if script.string and 'var ytInitialData' in script.string:
                    # Extract JSON data from script
                    courses = self._extract_courses_from_script(script.string, max_results)
                    break
            
            if not courses:
                # Fallback: try to extract from HTML structure
                courses = self._extract_courses_from_html(soup, max_results)
            
            return courses
            
        except Exception as e:
            logging.error(f"Error in single query search: {str(e)}")
            return []
    
    def _extract_courses_from_script(self, script_content: str, max_results: int) -> List[Dict[str, Any]]:
        """Extract course data from YouTube's initial data script."""
        try:
            # This is a simplified extraction - YouTube's structure is complex
            # In practice, you'd need more sophisticated parsing
            courses = []
            
            # Look for playlist patterns in the script
            playlist_pattern = r'"playlistId":"([^"]+)".*?"title":{"runs":\[{"text":"([^"]+)"}\]}'
            matches = re.findall(playlist_pattern, script_content)
            
            for playlist_id, title in matches[:max_results]:
                # Skip personal playlists and invalid IDs
                if self._is_valid_educational_playlist(playlist_id, title):
                    course = {
                        'title': title,
                        'url': f"https://www.youtube.com/playlist?list={playlist_id}",
                        'instructor': 'YouTube Creator',
                        'platform': 'YouTube',
                        'type': 'Playlist',
                        'difficulty': 'Beginner',
                        'estimated_hours': 10,
                        'rating': 4.5,
                        'price': 'Free',
                        'description': f'Learn {title} through this comprehensive playlist',
                        'highlights': ['Video tutorials', 'Free access', 'Self-paced learning'],
                        'certificateOffered': False
                    }
                    courses.append(course)
            
            return courses
            
        except Exception as e:
            logging.error(f"Error extracting from script: {str(e)}")
            return []
    
    def _extract_courses_from_html(self, soup: BeautifulSoup, max_results: int) -> List[Dict[str, Any]]:
        """Fallback extraction from HTML structure."""
        try:
            courses = []
            
            # Look for video/playlist containers
            containers = soup.find_all('div', {'class': re.compile(r'ytd-video-renderer|ytd-playlist-renderer')})
            
            for container in containers[:max_results]:
                title_elem = container.find('a', {'id': 'video-title'}) or container.find('h3')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                
                if url and not url.startswith('http'):
                    url = f"https://www.youtube.com{url}"
                
                # Extract channel name
                channel_elem = container.find('a', {'class': re.compile(r'channel-name|ytd-channel-name')})
                channel = channel_elem.get_text(strip=True) if channel_elem else 'YouTube Creator'
                
                # Validate the content before adding
                if self._is_valid_youtube_content(title, url):
                    course = {
                        'title': title,
                        'url': url,
                        'instructor': channel,
                        'platform': 'YouTube',
                        'type': 'Video/Playlist',
                        'difficulty': 'Beginner',
                        'estimated_hours': 8,
                        'rating': 4.3,
                        'price': 'Free',
                        'description': f'Learn through this YouTube content: {title}',
                        'highlights': ['Video format', 'Free access', 'Visual learning'],
                        'certificateOffered': False
                    }
                    courses.append(course)
            
            return courses
            
        except Exception as e:
            logging.error(f"Error extracting from HTML: {str(e)}")
            return []
    
    def _remove_duplicates(self, courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate courses based on title similarity."""
        unique_courses = []
        seen_titles = set()
        
        for course in courses:
            title = course.get('title', '').lower()
            # Simple deduplication based on title
            title_key = re.sub(r'[^a-z0-9]', '', title)
            
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_courses.append(course)
        
        return unique_courses
    
    def _is_valid_educational_playlist(self, playlist_id: str, title: str) -> bool:
        """Check if a playlist is valid for educational content."""
        # Skip personal playlists and system playlists
        invalid_playlist_ids = [
            'WL',  # Watch Later
            'LL',  # Liked Videos
            'UL',  # Uploads
            'FL',  # Favorites
            'PL',  # Personal playlists (sometimes)
        ]
        
        # Skip if playlist ID is in invalid list
        if playlist_id in invalid_playlist_ids:
            logging.debug(f"Skipping invalid playlist: {playlist_id} - {title}")
            return False
        
        # Skip if playlist ID is too short (likely system playlist)
        if len(playlist_id) < 10:
            logging.debug(f"Skipping short playlist ID: {playlist_id} - {title}")
            return False
        
        # Skip if title is empty or too generic
        if not title or len(title.strip()) < 3:
            logging.debug(f"Skipping playlist with invalid title: {playlist_id} - {title}")
            return False
        
        # Skip titles that are clearly personal
        personal_keywords = ['my playlist', 'watch later', 'liked videos', 'favorites', 'personal']
        title_lower = title.lower()
        for keyword in personal_keywords:
            if keyword in title_lower:
                logging.debug(f"Skipping personal playlist: {playlist_id} - {title}")
                return False
        
        return True
    
    def _is_valid_youtube_content(self, title: str, url: str) -> bool:
        """Check if YouTube content is valid for educational purposes."""
        # Skip if title is empty or too short
        if not title or len(title.strip()) < 3:
            return False
        
        # Skip personal playlists by URL
        if 'list=WL' in url or 'list=LL' in url or 'list=FL' in url:
            logging.debug(f"Skipping personal playlist URL: {url}")
            return False
        
        # Skip titles that are clearly personal or non-educational
        personal_keywords = ['my playlist', 'watch later', 'liked videos', 'favorites', 'personal']
        title_lower = title.lower()
        for keyword in personal_keywords:
            if keyword in title_lower:
                logging.debug(f"Skipping personal content: {title}")
                return False
        
        return True
    
    def _sort_by_relevance(self, courses: List[Dict[str, Any]], skill: str) -> List[Dict[str, Any]]:
        """Sort courses by relevance to the skill."""
        skill_words = skill.lower().split()
        
        def relevance_score(course):
            title = course.get('title', '').lower()
            score = 0
            
            # Score based on skill words in title
            for word in skill_words:
                if word in title:
                    score += 2
            
            # Bonus for educational keywords
            educational_keywords = ['tutorial', 'course', 'complete', 'learn', 'beginner', 'guide']
            for keyword in educational_keywords:
                if keyword in title:
                    score += 1
            
            return score
        
        return sorted(courses, key=relevance_score, reverse=True)
    
    def _get_youtube_fallback(self, skill: str) -> List[Dict[str, Any]]:
        """Fallback YouTube courses when scraping fails."""
        skill_lower = skill.lower()
        
        # Create generic YouTube courses based on skill
        fallback_courses = []
        
        # Common educational channels and course types
        course_templates = [
            {
                'title': f'{skill.title()} Complete Tutorial',
                'instructor': 'Programming with Mosh',
                'description': f'Complete {skill} tutorial for beginners',
                'estimated_hours': 12
            },
            {
                'title': f'Learn {skill.title()} in 2024',
                'instructor': 'freeCodeCamp.org',
                'description': f'Comprehensive {skill} course',
                'estimated_hours': 8
            },
            {
                'title': f'{skill.title()} Crash Course',
                'instructor': 'Traversy Media',
                'description': f'Quick start guide to {skill}',
                'estimated_hours': 4
            }
        ]
        
        for template in course_templates:
            course = {
                'title': template['title'],
                'url': f'https://www.youtube.com/results?search_query={quote_plus(template["title"])}',
                'instructor': template['instructor'],
                'platform': 'YouTube',
                'type': 'Video',
                'difficulty': 'Beginner',
                'estimated_hours': template['estimated_hours'],
                'rating': 4.5,
                'price': 'Free',
                'description': template['description'],
                'highlights': ['Free content', 'Video tutorials', 'Popular creators'],
                'certificateOffered': False
            }
            fallback_courses.append(course)
        
        logging.info(f"Using fallback YouTube courses for: {skill}")
        return fallback_courses

# Create singleton instance
youtube_scraper = YouTubeScraper()

def get_youtube_courses_scraper(skill: str) -> List[Dict[str, Any]]:
    """
    Get YouTube courses using web scraping (fallback method).
    
    Args:
        skill: The skill to search for
        
    Returns:
        List of YouTube course information
    """
    return youtube_scraper.search_courses(skill)