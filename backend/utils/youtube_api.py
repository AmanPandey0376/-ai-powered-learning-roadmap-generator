#!/usr/bin/env python3
"""
YouTube Data API integration for fetching learning playlists and videos.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from config import Config

class YouTubeAPI:
    """YouTube Data API client for fetching educational content."""
    
    def __init__(self):
        """Initialize YouTube API client."""
        self.api_key = Config.YOUTUBE_API_KEY
        self.base_url = Config.YOUTUBE_API_BASE
        self.timeout = Config.REQUEST_TIMEOUT
        self.api_available = self._check_api_availability()
        logging.info(f"YouTube API client initialized - API available: {self.api_available}")
    
    def _check_api_availability(self) -> bool:
        """Check if the YouTube API is available and working."""
        try:
            if not self.api_key or self.api_key == "your-youtube-api-key-here":
                logging.warning("YouTube API key not configured")
                return False
            
            # Test API with a simple request
            test_url = f"{self.base_url}/search"
            test_params = {
                'key': self.api_key,
                'part': 'snippet',
                'type': 'video',
                'q': 'test',
                'maxResults': 1
            }
            
            response = requests.get(test_url, params=test_params, timeout=5)
            if response.status_code == 200:
                return True
            else:
                logging.warning(f"YouTube API test failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            logging.warning(f"YouTube API availability check failed: {str(e)}")
            return False
    
    def search_playlists(self, skill: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for educational playlists related to a skill.
        
        Args:
            skill: The skill to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of playlist information
        """
        try:
            # Check if API is available
            if not self.api_available:
                logging.warning("YouTube API not available, returning empty results")
                return []
            # Search for playlists
            search_url = f"{self.base_url}/search"
            search_params = {
                'key': self.api_key,
                'part': 'snippet',
                'type': 'playlist',
                'q': f"{skill} tutorial course complete",
                'maxResults': max_results,
                'order': 'relevance'
            }
            
            response = requests.get(search_url, params=search_params, timeout=self.timeout)
            response.raise_for_status()
            
            search_data = response.json()
            playlists = []
            
            for item in search_data.get('items', []):
                playlist_info = self._extract_playlist_info(item)
                if playlist_info:
                    # Get additional playlist details
                    detailed_info = self._get_playlist_details(playlist_info['id'])
                    if detailed_info:
                        playlist_info.update(detailed_info)
                        playlists.append(playlist_info)
            
            logging.info(f"Found {len(playlists)} YouTube playlists for: {skill}")
            return playlists
            
        except Exception as e:
            logging.error(f"Error searching YouTube playlists for {skill}: {str(e)}")
            return []
    
    def _extract_playlist_info(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract basic playlist information from search result."""
        try:
            snippet = item.get('snippet', {})
            playlist_id = item.get('id', {}).get('playlistId')
            
            if not playlist_id:
                return None
            
            return {
                'id': playlist_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'channel_id': snippet.get('channelId', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'url': f"https://www.youtube.com/playlist?list={playlist_id}",
                'platform': 'YouTube'
            }
        except Exception as e:
            logging.error(f"Error extracting playlist info: {str(e)}")
            return None
    
    def _get_playlist_details(self, playlist_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a playlist."""
        try:
            # Get playlist details
            details_url = f"{self.base_url}/playlists"
            details_params = {
                'key': self.api_key,
                'part': 'snippet,contentDetails',
                'id': playlist_id
            }
            
            response = requests.get(details_url, params=details_params, timeout=self.timeout)
            response.raise_for_status()
            
            details_data = response.json()
            items = details_data.get('items', [])
            
            if not items:
                return None
            
            item = items[0]
            content_details = item.get('contentDetails', {})
            
            # Get playlist items to calculate duration
            items_info = self._get_playlist_items(playlist_id)
            
            return {
                'video_count': content_details.get('itemCount', 0),
                'total_duration_minutes': items_info.get('total_duration', 0),
                'video_titles': items_info.get('video_titles', [])
            }
            
        except Exception as e:
            logging.error(f"Error getting playlist details for {playlist_id}: {str(e)}")
            return None
    
    def _get_playlist_items(self, playlist_id: str, max_results: int = 50) -> Dict[str, Any]:
        """Get items from a playlist and calculate total duration."""
        try:
            items_url = f"{self.base_url}/playlistItems"
            items_params = {
                'key': self.api_key,
                'part': 'snippet',
                'playlistId': playlist_id,
                'maxResults': max_results
            }
            
            response = requests.get(items_url, params=items_params, timeout=self.timeout)
            response.raise_for_status()
            
            items_data = response.json()
            video_ids = []
            video_titles = []
            
            for item in items_data.get('items', []):
                video_id = item.get('snippet', {}).get('resourceId', {}).get('videoId')
                video_title = item.get('snippet', {}).get('title', '')
                
                if video_id:
                    video_ids.append(video_id)
                    video_titles.append(video_title)
            
            # Get video durations
            total_duration = self._get_videos_duration(video_ids)
            
            return {
                'total_duration': total_duration,
                'video_titles': video_titles[:10]  # First 10 video titles
            }
            
        except Exception as e:
            logging.error(f"Error getting playlist items: {str(e)}")
            return {'total_duration': 0, 'video_titles': []}
    
    def _get_videos_duration(self, video_ids: List[str]) -> int:
        """Get total duration of videos in minutes."""
        try:
            if not video_ids:
                return 0
            
            # YouTube API allows up to 50 video IDs per request
            video_ids_str = ','.join(video_ids[:50])
            
            videos_url = f"{self.base_url}/videos"
            videos_params = {
                'key': self.api_key,
                'part': 'contentDetails',
                'id': video_ids_str
            }
            
            response = requests.get(videos_url, params=videos_params, timeout=self.timeout)
            response.raise_for_status()
            
            videos_data = response.json()
            total_minutes = 0
            
            for video in videos_data.get('items', []):
                duration = video.get('contentDetails', {}).get('duration', '')
                minutes = self._parse_duration(duration)
                total_minutes += minutes
            
            return total_minutes
            
        except Exception as e:
            logging.error(f"Error getting video durations: {str(e)}")
            return 0
    
    def _parse_duration(self, duration: str) -> int:
        """Parse YouTube duration format (PT4M13S) to minutes."""
        try:
            if not duration.startswith('PT'):
                return 0
            
            duration = duration[2:]  # Remove 'PT'
            minutes = 0
            
            # Parse hours
            if 'H' in duration:
                hours_part = duration.split('H')[0]
                minutes += int(hours_part) * 60
                duration = duration.split('H')[1]
            
            # Parse minutes
            if 'M' in duration:
                minutes_part = duration.split('M')[0]
                minutes += int(minutes_part)
                duration = duration.split('M')[1]
            
            # Parse seconds (convert to minutes)
            if 'S' in duration:
                seconds_part = duration.split('S')[0]
                minutes += int(seconds_part) / 60
            
            return int(minutes)
            
        except Exception as e:
            logging.error(f"Error parsing duration {duration}: {str(e)}")
            return 0

# Create singleton instance
youtube_api = YouTubeAPI()

def get_youtube_courses(skill: str) -> List[Dict[str, Any]]:
    """
    Get YouTube courses for a specific skill.
    
    Args:
        skill: The skill to search for
        
    Returns:
        List of YouTube course information
    """
    try:
        results = youtube_api.search_playlists(skill)
        if results:
            logging.info(f"YouTube API returned {len(results)} courses for: {skill}")
        else:
            logging.warning(f"YouTube API returned no results for: {skill}")
        return results
    except Exception as e:
        logging.error(f"Error getting YouTube courses for {skill}: {str(e)}")
        return []