
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import streamlit as st
import time
import json

class WebSearcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_duckduckgo(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search using DuckDuckGo (free alternative)"""
        try:
            # DuckDuckGo instant answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Abstract (direct answer)
            if data.get('Abstract'):
                results.append({
                    'title': 'Direct Answer',
                    'snippet': data['Abstract'],
                    'url': data.get('AbstractURL', ''),
                    'source': 'DuckDuckGo'
                })
            
            # Answer from Infobox
            if data.get('Answer'):
                results.append({
                    'title': 'Quick Answer',
                    'snippet': data['Answer'],
                    'url': data.get('AnswerURL', ''),
                    'source': 'DuckDuckGo'
                })
            
            # Related topics
            for topic in data.get('RelatedTopics', [])[:max_results-len(results)]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' ').title(),
                        'snippet': topic['Text'],
                        'url': topic.get('FirstURL', ''),
                        'source': 'Wikipedia'
                    })
            
            # If no results, try web scraping as fallback
            if not results:
                results = self.search_web_scraping(query, max_results)
            
            return results
            
        except Exception as e:
            st.warning(f"DuckDuckGo search error: {str(e)}. Trying alternative method...")
            return self.search_web_scraping(query, max_results)
    
    def search_web_scraping(self, query: str, max_results: int = 3) -> List[Dict]:
        """Backup search using web scraping"""
        try:
            # Search using a different approach
            search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            search_results = soup.find_all('div', class_='result')[:max_results]
            
            for result in search_results:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem and snippet_elem:
                    results.append({
                        'title': title_elem.get_text().strip(),
                        'snippet': snippet_elem.get_text().strip(),
                        'url': title_elem.get('href', ''),
                        'source': 'Web Search'
                    })
            
            return results
            
        except Exception as e:
            st.error(f"Web scraping error: {str(e)}")
            return []
    
    def search_multiple_sources(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search multiple sources and combine results"""
        all_results = []
        
        # Try DuckDuckGo first
        ddg_results = self.search_duckduckgo(query, max_results)
        all_results.extend(ddg_results)
        
        # Remove duplicates based on title similarity
        unique_results = []
        seen_titles = set()
        
        for result in all_results:
            title_lower = result['title'].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_results.append(result)
        
        return unique_results[:max_results]
