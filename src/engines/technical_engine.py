import requests
import time
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET
from typing import Dict, List, Any

class TechnicalAccessibilityEngine:
    """
    Engine for analyzing technical accessibility factors that affect Google's ability
    to crawl, index, and understand web pages.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GSC-Scanner/1.0; +https://example.com/bot)'
        })
        self.timeout = 30

    def analyze(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive technical accessibility analysis
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary containing analysis results and recommendations
        """
        start_time = time.time()
        results = {
            'url': url,
            'timestamp': time.time(),
            'checks': {},
            'recommendations': [],
            'errors': []
        }
        
        try:
            # HTTP Status Check
            results['checks']['http_status'] = self._check_http_status(url)
            
            # Robots.txt Analysis
            results['checks']['robots_txt'] = self._analyze_robots_txt(url)
            
            # Sitemap Discovery
            results['checks']['sitemap'] = self._discover_sitemap(url)
            
            # Resource Accessibility
            results['checks']['resources'] = self._check_resource_accessibility(url)
            
            # SSL/HTTPS Check
            results['checks']['ssl'] = self._check_ssl_security(url)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results['checks'])
            
        except Exception as e:
            results['errors'].append(f"Analysis failed: {str(e)}")
        
        results['execution_time'] = time.time() - start_time
        return results

    def _check_http_status(self, url: str) -> Dict[str, Any]:
        """Check HTTP status code and response headers"""
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            return {
                'status_code': response.status_code,
                'is_success': response.status_code == 200,
                'redirect_chain': [r.url for r in response.history] + [response.url],
                'final_url': response.url,
                'response_time': response.elapsed.total_seconds(),
                'headers': dict(response.headers),
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(response.content)
            }
        except requests.RequestException as e:
            return {
                'status_code': None,
                'is_success': False,
                'error': str(e),
                'redirect_chain': [],
                'final_url': url
            }

    def _analyze_robots_txt(self, url: str) -> Dict[str, Any]:
        """Analyze robots.txt file and check URL accessibility"""
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        try:
            # Fetch robots.txt
            response = self.session.get(robots_url, timeout=self.timeout)
            robots_exists = response.status_code == 200
            
            if robots_exists:
                # Parse robots.txt
                rp = RobotFileParser()
                rp.set_url(robots_url)
                rp.read()
                
                # Check if URL is allowed for Googlebot
                googlebot_allowed = rp.can_fetch('Googlebot', url)
                wildcard_allowed = rp.can_fetch('*', url)
                
                # Find sitemap declarations
                sitemaps = []
                for line in response.text.split('\n'):
                    if line.lower().startswith('sitemap:'):
                        sitemaps.append(line.split(':', 1)[1].strip())
                
                return {
                    'exists': True,
                    'content': response.text,
                    'googlebot_allowed': googlebot_allowed,
                    'wildcard_allowed': wildcard_allowed,
                    'sitemaps_declared': sitemaps,
                    'crawl_delay': rp.crawl_delay('Googlebot'),
                    'url_allowed': googlebot_allowed or wildcard_allowed
                }
            else:
                return {
                    'exists': False,
                    'url_allowed': True,  # No robots.txt means allowed
                    'googlebot_allowed': True,
                    'wildcard_allowed': True,
                    'sitemaps_declared': []
                }
                
        except Exception as e:
            return {
                'exists': False,
                'error': str(e),
                'url_allowed': True,  # Assume allowed if can't check
                'googlebot_allowed': True,
                'wildcard_allowed': True
            }

    def _discover_sitemap(self, url: str) -> Dict[str, Any]:
        """Discover and analyze XML sitemaps"""
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Common sitemap locations
        sitemap_urls = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_index.xml",
            f"{base_url}/sitemaps.xml"
        ]
        
        found_sitemaps = []
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=self.timeout)
                if response.status_code == 200:
                    sitemap_info = self._analyze_sitemap_content(response.text, sitemap_url)
                    if sitemap_info:
                        found_sitemaps.append(sitemap_info)
            except:
                continue
        
        return {
            'found': len(found_sitemaps) > 0,
            'sitemaps': found_sitemaps,
            'total_urls': sum(s.get('url_count', 0) for s in found_sitemaps)
        }

    def _analyze_sitemap_content(self, content: str, sitemap_url: str) -> Dict[str, Any]:
        """Analyze XML sitemap content"""
        try:
            root = ET.fromstring(content)
            
            # Handle different sitemap types
            if 'sitemapindex' in root.tag:
                # Sitemap index file
                sitemaps = []
                for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                    loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None:
                        sitemaps.append(loc.text)
                
                return {
                    'url': sitemap_url,
                    'type': 'index',
                    'sitemap_count': len(sitemaps),
                    'sitemaps': sitemaps
                }
            else:
                # Regular sitemap
                urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                
                return {
                    'url': sitemap_url,
                    'type': 'urlset',
                    'url_count': len(urls),
                    'last_modified': self._get_sitemap_lastmod(root)
                }
                
        except ET.ParseError:
            return None

    def _get_sitemap_lastmod(self, root) -> str:
        """Get the most recent lastmod date from sitemap"""
        lastmods = []
        for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            lastmod = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            if lastmod is not None:
                lastmods.append(lastmod.text)
        
        return max(lastmods) if lastmods else None

    def _check_resource_accessibility(self, url: str) -> Dict[str, Any]:
        """Check accessibility of CSS and JavaScript resources"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code != 200:
                return {'error': 'Could not fetch page content'}
            
            # Simple check for CSS and JS resources
            content = response.text.lower()
            
            css_count = content.count('<link') + content.count('.css')
            js_count = content.count('<script') + content.count('.js')
            
            return {
                'css_resources_found': css_count > 0,
                'js_resources_found': js_count > 0,
                'estimated_css_count': css_count,
                'estimated_js_count': js_count,
                'content_accessible': True
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'css_resources_found': False,
                'js_resources_found': False,
                'content_accessible': False
            }

    def _check_ssl_security(self, url: str) -> Dict[str, Any]:
        """Check SSL/HTTPS security implementation"""
        parsed_url = urlparse(url)
        
        return {
            'is_https': parsed_url.scheme == 'https',
            'ssl_enabled': parsed_url.scheme == 'https',
            'mixed_content_risk': parsed_url.scheme == 'https'  # Would need deeper analysis
        }

    def _generate_recommendations(self, checks: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis results"""
        recommendations = []
        
        # HTTP Status recommendations
        http_check = checks.get('http_status', {})
        if not http_check.get('is_success', False):
            recommendations.append({
                'priority': 'high',
                'category': 'accessibility',
                'issue': 'HTTP Status Error',
                'description': f"Page returns {http_check.get('status_code')} instead of 200",
                'recommendation': 'Fix server configuration to return proper HTTP 200 status code',
                'impact': 'Google cannot index pages that return error status codes'
            })
        
        # Robots.txt recommendations
        robots_check = checks.get('robots_txt', {})
        if not robots_check.get('url_allowed', True):
            recommendations.append({
                'priority': 'high',
                'category': 'crawling',
                'issue': 'Robots.txt Blocking',
                'description': 'URL is blocked by robots.txt directives',
                'recommendation': 'Update robots.txt to allow Googlebot access to this URL',
                'impact': 'Blocked URLs cannot be crawled or indexed by Google'
            })
        
        # Sitemap recommendations
        sitemap_check = checks.get('sitemap', {})
        if not sitemap_check.get('found', False):
            recommendations.append({
                'priority': 'medium',
                'category': 'discovery',
                'issue': 'No Sitemap Found',
                'description': 'No XML sitemap detected at common locations',
                'recommendation': 'Create and submit an XML sitemap to help Google discover your content',
                'impact': 'Sitemaps help Google discover and understand your site structure'
            })
        
        # HTTPS recommendations
        ssl_check = checks.get('ssl', {})
        if not ssl_check.get('is_https', False):
            recommendations.append({
                'priority': 'high',
                'category': 'security',
                'issue': 'No HTTPS',
                'description': 'Page is not served over HTTPS',
                'recommendation': 'Implement SSL certificate and redirect HTTP to HTTPS',
                'impact': 'HTTPS is a ranking factor and required for modern web security'
            })
        
        return recommendations

    def get_metrics_for_scoring(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics for score calculation"""
        checks = results.get('checks', {})
        
        return {
            'http_status_ok': checks.get('http_status', {}).get('is_success', False),
            'robots_txt_ok': checks.get('robots_txt', {}).get('url_allowed', True),
            'sitemap_found': checks.get('sitemap', {}).get('found', False),
            'css_accessible': checks.get('resources', {}).get('css_resources_found', False),
            'js_accessible': checks.get('resources', {}).get('js_resources_found', False),
            'https_enabled': checks.get('ssl', {}).get('is_https', False)
        }

