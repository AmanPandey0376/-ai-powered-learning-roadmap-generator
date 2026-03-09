#!/usr/bin/env python3
"""
GitHub API integration for fetching awesome lists and learning repositories.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from config import Config

class GitHubAPI:
    """GitHub API client for fetching learning repositories."""
    
    def __init__(self):
        """Initialize GitHub API client."""
        self.base_url = Config.GITHUB_API_BASE
        self.timeout = Config.REQUEST_TIMEOUT
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Learning-Roadmap-Generator'
        }
        logging.info("GitHub API client initialized")
    
    def search_awesome_lists(self, skill: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for awesome lists related to a skill.
        
        Args:
            skill: The skill to search for
            limit: Maximum number of results to return
            
        Returns:
            List of repository information
        """
        try:
            # Search for awesome lists
            search_queries = [
                f"awesome-{skill.replace(' ', '-')}",
                f"awesome {skill}",
                f"{skill} resources",
                f"{skill} learning"
            ]
            
            all_repos = []
            
            for query in search_queries:
                repos = self._search_repositories(query, limit=2)
                all_repos.extend(repos)
                
                if len(all_repos) >= limit:
                    break
            
            # Remove duplicates and sort by stars
            unique_repos = self._deduplicate_repos(all_repos)
            sorted_repos = sorted(unique_repos, key=lambda x: x.get('stars', 0), reverse=True)
            
            result = sorted_repos[:limit]
            logging.info(f"Found {len(result)} GitHub repositories for: {skill}")
            return result
            
        except Exception as e:
            logging.error(f"Error searching GitHub repositories for {skill}: {str(e)}")
            return self._get_fallback_repos(skill)
    
    def _search_repositories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search repositories using GitHub API."""
        try:
            search_url = f"{self.base_url}/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': limit
            }
            
            response = requests.get(search_url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            repos = []
            
            for item in data.get('items', []):
                repo_info = self._extract_repo_info(item)
                if repo_info:
                    repos.append(repo_info)
            
            return repos
            
        except Exception as e:
            logging.error(f"Error searching repositories for {query}: {str(e)}")
            return []
    
    def _extract_repo_info(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract repository information from GitHub API response."""
        try:
            return {
                'id': item.get('id', ''),
                'title': item.get('name', ''),
                'description': item.get('description', ''),
                'url': item.get('html_url', ''),
                'stars': item.get('stargazers_count', 0),
                'forks': item.get('forks_count', 0),
                'language': item.get('language', ''),
                'owner': item.get('owner', {}).get('login', ''),
                'updated_at': item.get('updated_at', ''),
                'platform': 'GitHub',
                'type': 'Repository',
                'difficulty': 'Intermediate',
                'estimated_hours': 10,
                'rating': min(5.0, 3.0 + (item.get('stargazers_count', 0) / 10000)),  # Scale stars to rating
                'highlights': ['Open source', 'Community-driven', 'Free access']
            }
            
        except Exception as e:
            logging.error(f"Error extracting repo info: {str(e)}")
            return None
    
    def _deduplicate_repos(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate repositories based on URL."""
        seen_urls = set()
        unique_repos = []
        
        for repo in repos:
            url = repo.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_repos.append(repo)
        
        return unique_repos
    
    def _get_fallback_repos(self, skill: str) -> List[Dict[str, Any]]:
        """Get fallback repositories when API fails."""
        skill_lower = skill.lower()
        
        # Data Science repositories
        if any(term in skill_lower for term in ['data science', 'machine learning', 'ai']):
            return [
                {
                    'id': 'awesome-datascience',
                    'title': 'awesome-datascience',
                    'description': 'An awesome Data Science repository to learn and apply for real world problems',
                    'url': 'https://github.com/academic/awesome-datascience',
                    'stars': 23000,
                    'platform': 'GitHub',
                    'type': 'Repository',
                    'difficulty': 'Intermediate',
                    'estimated_hours': 20,
                    'rating': 4.8,
                    'highlights': ['Comprehensive resources', 'Community curated', 'Regular updates']
                },
                {
                    'id': 'ml-for-beginners',
                    'title': 'ML-For-Beginners',
                    'description': '12 weeks, 26 lessons, 52 quizzes, classic Machine Learning for all',
                    'url': 'https://github.com/microsoft/ML-For-Beginners',
                    'stars': 69000,
                    'platform': 'GitHub',
                    'type': 'Repository',
                    'difficulty': 'Beginner',
                    'estimated_hours': 50,
                    'rating': 4.9,
                    'highlights': ['Microsoft curriculum', 'Beginner-friendly', 'Structured learning']
                }
            ]
        
        # Web Development repositories
        elif any(term in skill_lower for term in ['web dev', 'frontend', 'backend', 'react', 'javascript']):
            return [
                {
                    'id': 'awesome-javascript',
                    'title': 'awesome-javascript',
                    'description': 'A collection of awesome browser-side JavaScript libraries, resources and shiny things',
                    'url': 'https://github.com/sorrycc/awesome-javascript',
                    'stars': 33000,
                    'platform': 'GitHub',
                    'type': 'Repository',
                    'difficulty': 'Intermediate',
                    'estimated_hours': 15,
                    'rating': 4.7,
                    'highlights': ['Comprehensive JS resources', 'Library recommendations', 'Community curated']
                },
                {
                    'id': 'web-dev-for-beginners',
                    'title': 'Web-Dev-For-Beginners',
                    'description': '24 Lessons, 12 Weeks, Get Started as a Web Developer',
                    'url': 'https://github.com/microsoft/Web-Dev-For-Beginners',
                    'stars': 83000,
                    'platform': 'GitHub',
                    'type': 'Repository',
                    'difficulty': 'Beginner',
                    'estimated_hours': 60,
                    'rating': 4.9,
                    'highlights': ['Microsoft curriculum', 'Structured course', 'Hands-on projects']
                }
            ]
        
        # Python repositories
        elif 'python' in skill_lower:
            return [
                {
                    'id': 'awesome-python',
                    'title': 'awesome-python',
                    'description': 'A curated list of awesome Python frameworks, libraries, software and resources',
                    'url': 'https://github.com/vinta/awesome-python',
                    'stars': 221000,
                    'platform': 'GitHub',
                    'type': 'Repository',
                    'difficulty': 'Intermediate',
                    'estimated_hours': 20,
                    'rating': 4.9,
                    'highlights': ['Most comprehensive', 'Regularly updated', 'Community favorite']
                },
                {
                    'id': 'python-for-beginners',
                    'title': 'Python-For-Beginners',
                    'description': 'A Python course for beginners with hands-on projects',
                    'url': 'https://github.com/microsoft/c9-python-getting-started',
                    'stars': 15000,
                    'platform': 'GitHub',
                    'type': 'Repository',
                    'difficulty': 'Beginner',
                    'estimated_hours': 30,
                    'rating': 4.6,
                    'highlights': ['Microsoft course', 'Beginner-friendly', 'Practical examples']
                }
            ]
        
        # Default repositories
        else:
            return [
                {
                    'id': 'free-programming-books',
                    'title': 'free-programming-books',
                    'description': 'Freely available programming books',
                    'url': 'https://github.com/EbookFoundation/free-programming-books',
                    'stars': 335000,
                    'platform': 'GitHub',
                    'type': 'Repository',
                    'difficulty': 'Beginner',
                    'estimated_hours': 10,
                    'rating': 4.9,
                    'highlights': ['Largest collection', 'Multiple languages', 'Free resources']
                }
            ]

# Create singleton instance
github_api = GitHubAPI()

def get_github_resources(skill: str) -> List[Dict[str, Any]]:
    """
    Get GitHub resources for a specific skill.
    
    Args:
        skill: The skill to search for
        
    Returns:
        List of GitHub repository information
    """
    return github_api.search_awesome_lists(skill)