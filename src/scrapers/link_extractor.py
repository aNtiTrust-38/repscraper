import re
from typing import List, Dict

PLATFORM_PATTERNS = {
    'taobao': [r'https?://item\.taobao\.com/item\.htm\?id=\d+'],
    'weidian': [r'https?://weidian\.com/item\.html\?id=\d+'],
    '1688': [r'https?://detail\.1688\.com/offer/\d+\.html'],
    'yupoo': [r'https?://x\.yupoo\.com/albums/\d+'],
    'pandabuy': [r'https?://pandabuy\.com/item/\d+'],
}
PLATFORM_PRIORITY = {
    'taobao': 1,
    'weidian': 2,
    '1688': 3,
    'yupoo': 4,
    'pandabuy': 6,
}

class LinkExtractor:
    def extract_links(self, text: str) -> List[Dict]:
        found_links = []
        for platform, patterns in PLATFORM_PATTERNS.items():
            for pattern in patterns:
                for match in re.findall(pattern, text):
                    found_links.append({
                        'platform': platform,
                        'priority': PLATFORM_PRIORITY[platform],
                        'url': match
                    })
        # Sort by priority (lower number = higher priority)
        found_links.sort(key=lambda x: x['priority'])
        return found_links
