#!/usr/bin/env python3
"""
Property Image Service for InvestorIQ
Fetches actual property images from multiple sources
"""

import requests
import os
import urllib.parse
from typing import List, Dict, Optional
import json
import time

class PropertyImageService:
    def __init__(self):
        self.google_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
        self.cache_dir = 'static/property_images'
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def get_property_images(self, address: str, city: str, state: str = 'IL') -> List[str]:
        """Get multiple property images from various sources"""
        images = []
        
        # 1. Street View Static API (Google) - Best quality
        street_view = self.get_street_view_image(address, city, state)
        if street_view:
            images.append(street_view)
        
        # 2. Satellite view
        satellite = self.get_satellite_image(address, city, state)
        if satellite:
            images.append(satellite)
            
        # 3. Multiple angles street view
        angles = [0, 90, 180, 270]  # N, E, S, W
        for angle in angles[:2]:  # Just get 2 angles to avoid too many images
            angled_view = self.get_street_view_image(address, city, state, heading=angle)
            if angled_view and angled_view not in images:
                images.append(angled_view)
        
        # 4. Fallback to enhanced placeholder if no real images
        if not images:
            images.append(self.create_enhanced_placeholder(address, city))
            
        return images[:4]  # Limit to 4 images max
    
    def get_street_view_image(self, address: str, city: str, state: str, 
                            heading: int = 0, pitch: int = 0) -> Optional[str]:
        """Get Street View image using Google API"""
        if not self.google_api_key or self.google_api_key == 'demo_key':
            return None
            
        full_address = f"{address}, {city}, {state}"
        encoded_address = urllib.parse.quote(full_address)
        
        # High quality Street View Static API call
        url = (f"https://maps.googleapis.com/maps/api/streetview?"
               f"size=640x640&"
               f"location={encoded_address}&"
               f"heading={heading}&"
               f"pitch={pitch}&"
               f"fov=80&"
               f"key={self.google_api_key}")
        
        return url
    
    def get_satellite_image(self, address: str, city: str, state: str) -> Optional[str]:
        """Get satellite/aerial view of property"""
        if not self.google_api_key or self.google_api_key == 'demo_key':
            return None
            
        full_address = f"{address}, {city}, {state}"
        encoded_address = urllib.parse.quote(full_address)
        
        # Static Maps API for satellite view
        url = (f"https://maps.googleapis.com/maps/api/staticmap?"
               f"center={encoded_address}&"
               f"zoom=19&"
               f"size=640x640&"
               f"maptype=satellite&"
               f"key={self.google_api_key}")
        
        return url
    
    def create_enhanced_placeholder(self, address: str, city: str) -> str:
        """Create enhanced placeholder with property info"""
        # Create a more informative placeholder
        address_short = address[:25] + "..." if len(address) > 25 else address
        location_text = f"{address_short}, {city}"
        encoded_text = urllib.parse.quote(location_text)
        
        # Use a property-themed placeholder
        return f"https://via.placeholder.com/640x640/2196F3/ffffff?text=🏠+{encoded_text}"
    
    def get_property_image_gallery(self, property_data: Dict) -> Dict:
        """Get complete image gallery for a property"""
        address = property_data.get('property_address', '')
        city = property_data.get('city', '')
        state = property_data.get('state', 'IL')
        
        images = self.get_property_images(address, city, state)
        
        return {
            'primary_image': images[0] if images else None,
            'all_images': images,
            'street_view_url': self.get_street_view_embed_url(address, city, state),
            'maps_url': f"https://www.google.com/maps/search/{urllib.parse.quote(address + ', ' + city + ', ' + state)}"
        }
    
    def get_street_view_embed_url(self, address: str, city: str, state: str) -> str:
        """Get embeddable Street View URL for iframe"""
        full_address = f"{address}, {city}, {state}"
        encoded_address = urllib.parse.quote(full_address)
        
        if self.google_api_key and self.google_api_key != 'demo_key':
            return f"https://www.google.com/maps/embed/v1/streetview?key={self.google_api_key}&location={encoded_address}"
        else:
            # Fallback to regular Google Maps
            return f"https://www.google.com/maps/embed/v1/place?q={encoded_address}&key=demo"

def get_free_street_view_alternatives():
    """List of free alternatives to Google Street View"""
    return [
        {
            'name': 'Mapillary',
            'url': 'https://www.mapillary.com/app/',
            'description': 'Open street-level imagery',
            'api': True
        },
        {
            'name': 'OpenStreetCam',
            'url': 'https://openstreetcam.org/',
            'description': 'Open source street view',
            'api': True
        },
        {
            'name': 'Bing Maps',
            'url': 'https://www.bing.com/maps/streetside',
            'description': 'Microsoft Streetside imagery',
            'api': True
        }
    ]

# Usage examples:
def example_usage():
    """Examples of how to use the PropertyImageService"""
    service = PropertyImageService()
    
    # Example property
    property_data = {
        'property_address': '123 Main St',
        'city': 'Moline',
        'state': 'IL'
    }
    
    # Get image gallery
    gallery = service.get_property_image_gallery(property_data)
    
    print("Primary Image:", gallery['primary_image'])
    print("All Images:", gallery['all_images'])
    print("Street View Embed:", gallery['street_view_url'])