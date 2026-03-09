#!/usr/bin/env python3
"""
URL Validator Service
Validates URLs to ensure they are active and working before including them in resources.
"""

import requests
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class URLValidator:
    """
    Service to validate URLs and ensure they are working.
    """
    
    def __init__(self):
        """Initialize the URL validator."""
        self.timeout = 10  # 10 seconds timeout
        self.max_workers = 5  # Maximum concurrent requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logging.info("URL Validator initialized")
    
    def validate_url(self, url: str) -> bool:
        """
        Validate a single URL to check if it's working.
        
        Args:
            url: The URL to validate
            
        Returns:
            True if URL is working, False otherwise
        """
        try:
            response = requests.head(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            # Consider 200-399 status codes as successful
            is_valid = 200 <= response.status_code < 400
            
            if is_valid:
                logging.info(f"URL validated successfully: {url}")
            else:
                logging.warning(f"URL returned status {response.status_code}: {url}")
                
            return is_valid
            
        except requests.exceptions.RequestException as e:
            logging.warning(f"URL validation failed for {url}: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error validating URL {url}: {str(e)}")
            return False
    
    def validate_urls_batch(self, urls: List[str]) -> Dict[str, bool]:
        """
        Validate multiple URLs concurrently.
        
        Args:
            urls: List of URLs to validate
            
        Returns:
            Dictionary mapping URLs to their validation status
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all URL validation tasks
            future_to_url = {executor.submit(self.validate_url, url): url for url in urls}
            
            # Collect results as they complete
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    logging.error(f"Error validating URL {url}: {str(e)}")
                    results[url] = False
        
        return results
    
    def filter_working_resources(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter resources to only include those with working URLs.
        
        Args:
            resources: List of resource dictionaries
            
        Returns:
            List of resources with working URLs only
        """
        if not resources:
            return []
        
        # Extract URLs from resources
        urls = [resource.get('url') for resource in resources if resource.get('url')]
        
        if not urls:
            return resources
        
        logging.info(f"Validating {len(urls)} URLs...")
        
        # Validate URLs
        validation_results = self.validate_urls_batch(urls)
        
        # Filter resources based on URL validation
        working_resources = []
        for resource in resources:
            url = resource.get('url')
            if not url or validation_results.get(url, False):
                working_resources.append(resource)
            else:
                logging.info(f"Filtered out resource with non-working URL: {resource.get('name', 'Unknown')} - {url}")
        
        logging.info(f"Filtered resources: {len(working_resources)} working out of {len(resources)} total")
        return working_resources

# Create a singleton instance
url_validator = URLValidator()

def validate_resource_urls(resources_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate URLs in resources data and filter out non-working ones.
    
    Args:
        resources_data: Dictionary containing freeResources and paidResources
        
    Returns:
        Filtered resources data with only working URLs
    """
    try:
        filtered_data = resources_data.copy()
        
        # Filter free resources
        if 'freeResources' in filtered_data:
            filtered_data['freeResources'] = url_validator.filter_working_resources(
                filtered_data['freeResources']
            )
        
        # Filter paid resources
        if 'paidResources' in filtered_data:
            filtered_data['paidResources'] = url_validator.filter_working_resources(
                filtered_data['paidResources']
            )
        
        return filtered_data
        
    except Exception as e:
        logging.error(f"Error validating resource URLs: {str(e)}")
        return resources_data  # Return original data if validation fails