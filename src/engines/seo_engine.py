import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import Dict, List, Any
import json

class SEOAnalysisEngine:
    """
    Engine for analyzing on-page SEO factors that affect search engine
    visibility and ranking potential.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; GSC-Scanner/1.0; +https://example.com/bot)'
        })
        self.timeout = 30

    def analyze(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive SEO analysis
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary containing SEO analysis results and recommendations
        """
        start_time = time.time()
        results = {
            'url': url,
            'timestamp': time.time(),
            'on_page': {},
            'content': {},
            'technical_seo': {},
            'recommendations': [],
            'errors': []
        }
        
        try:
            # Fetch page content
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code != 200:
                results['errors'].append(f"Could not fetch page: HTTP {response.status_code}")
                return results
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # On-page SEO analysis
            results['on_page'] = self._analyze_on_page_elements(soup, url)
            
            # Content analysis
            results['content'] = self._analyze_content_quality(soup, response.text)
            
            # Technical SEO analysis
            results['technical_seo'] = self._analyze_technical_seo(soup, url, response)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
        except Exception as e:
            results['errors'].append(f"SEO analysis failed: {str(e)}")
        
        results['execution_time'] = time.time() - start_time
        return results

    def _analyze_on_page_elements(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analyze on-page SEO elements"""
        on_page = {}
        
        # Title tag analysis
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text().strip()
            on_page['title'] = {
                'text': title_text,
                'length': len(title_text),
                'is_optimal_length': 30 <= len(title_text) <= 60,
                'is_unique': True,  # Would need database check for uniqueness
                'has_keywords': self._has_relevant_keywords(title_text, url)
            }
        else:
            on_page['title'] = {
                'text': None,
                'length': 0,
                'is_optimal_length': False,
                'exists': False
            }
        
        # Meta description analysis
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc_text = meta_desc['content'].strip()
            on_page['meta_description'] = {
                'text': desc_text,
                'length': len(desc_text),
                'is_optimal_length': 120 <= len(desc_text) <= 160,
                'has_call_to_action': self._has_call_to_action(desc_text),
                'has_keywords': self._has_relevant_keywords(desc_text, url)
            }
        else:
            on_page['meta_description'] = {
                'text': None,
                'length': 0,
                'is_optimal_length': False,
                'exists': False
            }
        
        # Header structure analysis
        on_page['headers'] = self._analyze_header_structure(soup)
        
        # URL analysis
        on_page['url_structure'] = self._analyze_url_structure(url)
        
        # Image optimization
        on_page['images'] = self._analyze_images(soup, url)
        
        # Internal linking
        on_page['internal_links'] = self._analyze_internal_links(soup, url)
        
        return on_page

    def _analyze_content_quality(self, soup: BeautifulSoup, html_content: str) -> Dict[str, Any]:
        """Analyze content quality and structure"""
        content = {}
        
        # Extract main content
        main_content = self._extract_main_content(soup)
        
        # Word count analysis
        word_count = len(main_content.split())
        content['word_count'] = {
            'total': word_count,
            'is_sufficient': word_count >= 300,
            'is_comprehensive': word_count >= 1000
        }
        
        # Content structure
        content['structure'] = {
            'has_paragraphs': len(soup.find_all('p')) > 0,
            'has_lists': len(soup.find_all(['ul', 'ol'])) > 0,
            'has_headings': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])) > 0
        }
        
        # Readability analysis (basic)
        content['readability'] = self._analyze_readability(main_content)
        
        # Keyword analysis
        content['keywords'] = self._analyze_keyword_usage(main_content, soup)
        
        # Content uniqueness (basic check)
        content['uniqueness'] = {
            'estimated_unique': True,  # Would need external service for real check
            'duplicate_content_risk': self._check_duplicate_content_risk(soup)
        }
        
        return content

    def _analyze_technical_seo(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """Analyze technical SEO factors"""
        technical = {}
        
        # Meta tags
        technical['meta_tags'] = self._analyze_meta_tags(soup)
        
        # Structured data
        technical['structured_data'] = self._analyze_structured_data(soup)
        
        # Canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        technical['canonical'] = {
            'exists': canonical is not None,
            'url': canonical.get('href') if canonical else None,
            'is_self_referencing': canonical.get('href') == url if canonical else False
        }
        
        # Open Graph tags
        technical['open_graph'] = self._analyze_open_graph(soup)
        
        # Schema markup
        technical['schema'] = self._find_schema_markup(soup)
        
        return technical

    def _analyze_header_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze header tag structure and hierarchy"""
        headers = {}
        
        for level in range(1, 7):
            header_tags = soup.find_all(f'h{level}')
            headers[f'h{level}'] = {
                'count': len(header_tags),
                'texts': [h.get_text().strip() for h in header_tags[:5]]  # First 5 only
            }
        
        # Check for proper hierarchy
        h1_count = len(soup.find_all('h1'))
        headers['hierarchy'] = {
            'has_single_h1': h1_count == 1,
            'h1_count': h1_count,
            'proper_structure': self._check_header_hierarchy(soup)
        }
        
        return headers

    def _analyze_url_structure(self, url: str) -> Dict[str, Any]:
        """Analyze URL structure and SEO-friendliness"""
        parsed = urlparse(url)
        path = parsed.path
        
        return {
            'length': len(url),
            'is_descriptive': self._is_descriptive_url(path),
            'has_keywords': self._url_has_keywords(path),
            'uses_hyphens': '-' in path,
            'uses_underscores': '_' in path,
            'depth': len([p for p in path.split('/') if p]),
            'has_parameters': bool(parsed.query),
            'is_https': parsed.scheme == 'https'
        }

    def _analyze_images(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Analyze image optimization"""
        images = soup.find_all('img')
        
        total_images = len(images)
        images_with_alt = len([img for img in images if img.get('alt')])
        images_with_title = len([img for img in images if img.get('title')])
        
        return {
            'total_count': total_images,
            'with_alt_text': images_with_alt,
            'with_title': images_with_title,
            'alt_text_percentage': (images_with_alt / total_images * 100) if total_images > 0 else 0,
            'optimization_score': (images_with_alt / total_images * 100) if total_images > 0 else 100
        }

    def _analyze_internal_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Analyze internal linking structure"""
        all_links = soup.find_all('a', href=True)
        parsed_base = urlparse(base_url)
        
        internal_links = []
        external_links = []
        
        for link in all_links:
            href = link['href']
            parsed_href = urlparse(href)
            
            if not parsed_href.netloc or parsed_href.netloc == parsed_base.netloc:
                internal_links.append(href)
            else:
                external_links.append(href)
        
        return {
            'total_links': len(all_links),
            'internal_count': len(internal_links),
            'external_count': len(external_links),
            'internal_ratio': len(internal_links) / len(all_links) if all_links else 0
        }

    def _analyze_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze various meta tags"""
        meta_tags = {}
        
        # Viewport
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        meta_tags['viewport'] = {
            'exists': viewport is not None,
            'content': viewport.get('content') if viewport else None
        }
        
        # Robots
        robots = soup.find('meta', attrs={'name': 'robots'})
        meta_tags['robots'] = {
            'exists': robots is not None,
            'content': robots.get('content') if robots else None
        }
        
        # Language
        lang_attr = soup.find('html', attrs={'lang': True})
        meta_tags['language'] = {
            'html_lang': lang_attr.get('lang') if lang_attr else None,
            'exists': lang_attr is not None
        }
        
        return meta_tags

    def _analyze_structured_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze structured data implementation"""
        structured_data = {
            'json_ld': [],
            'microdata': False,
            'rdfa': False
        }
        
        # JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                structured_data['json_ld'].append(data)
            except:
                pass
        
        # Microdata (basic check)
        if soup.find(attrs={'itemscope': True}):
            structured_data['microdata'] = True
        
        # RDFa (basic check)
        if soup.find(attrs={'typeof': True}) or soup.find(attrs={'property': True}):
            structured_data['rdfa'] = True
        
        return structured_data

    def _analyze_open_graph(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze Open Graph meta tags"""
        og_tags = {}
        
        og_properties = ['title', 'description', 'image', 'url', 'type', 'site_name']
        
        for prop in og_properties:
            tag = soup.find('meta', attrs={'property': f'og:{prop}'})
            og_tags[prop] = {
                'exists': tag is not None,
                'content': tag.get('content') if tag else None
            }
        
        return og_tags

    def _find_schema_markup(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Find and analyze schema markup"""
        schema_types = []
        
        # JSON-LD schemas
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and '@type' in data:
                    schema_types.append(data['@type'])
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and '@type' in item:
                            schema_types.append(item['@type'])
            except:
                pass
        
        return {
            'types_found': list(set(schema_types)),
            'count': len(schema_types),
            'has_schema': len(schema_types) > 0
        }

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content text from page"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main'))
        
        if main_content:
            return main_content.get_text()
        else:
            return soup.get_text()

    def _analyze_readability(self, text: str) -> Dict[str, Any]:
        """Basic readability analysis"""
        sentences = text.split('.')
        words = text.split()
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        return {
            'average_sentence_length': avg_sentence_length,
            'is_readable': avg_sentence_length < 20,
            'total_sentences': len(sentences),
            'total_words': len(words)
        }

    def _analyze_keyword_usage(self, content: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze keyword usage and density"""
        # This is a simplified keyword analysis
        words = content.lower().split()
        word_count = {}
        
        for word in words:
            if len(word) > 3:  # Only count words longer than 3 characters
                word_count[word] = word_count.get(word, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'top_keywords': top_keywords,
            'keyword_density': {kw: (count / len(words) * 100) for kw, count in top_keywords[:5]}
        }

    def _has_relevant_keywords(self, text: str, url: str) -> bool:
        """Check if text contains relevant keywords (simplified)"""
        # Extract potential keywords from URL
        parsed = urlparse(url)
        path_words = re.findall(r'[a-zA-Z]+', parsed.path.lower())
        
        text_lower = text.lower()
        return any(word in text_lower for word in path_words if len(word) > 3)

    def _has_call_to_action(self, text: str) -> bool:
        """Check if text contains call-to-action phrases"""
        cta_phrases = ['learn more', 'read more', 'click here', 'get started', 'sign up', 'download', 'buy now', 'contact us']
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in cta_phrases)

    def _is_descriptive_url(self, path: str) -> bool:
        """Check if URL path is descriptive"""
        # Check for meaningful words vs random characters/numbers
        words = re.findall(r'[a-zA-Z]+', path)
        numbers = re.findall(r'\d+', path)
        
        return len(words) > len(numbers) and len(words) > 0

    def _url_has_keywords(self, path: str) -> bool:
        """Check if URL contains keyword-like terms"""
        words = re.findall(r'[a-zA-Z]{3,}', path.lower())
        return len(words) > 0

    def _check_header_hierarchy(self, soup: BeautifulSoup) -> bool:
        """Check if header hierarchy is properly structured"""
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if not headers:
            return False
        
        # Simple check: should start with h1 and not skip levels
        current_level = 0
        for header in headers:
            level = int(header.name[1])
            if current_level == 0:
                if level != 1:
                    return False
            elif level > current_level + 1:
                return False
            current_level = level
        
        return True

    def _check_duplicate_content_risk(self, soup: BeautifulSoup) -> bool:
        """Check for potential duplicate content issues"""
        # Basic check for boilerplate content
        content_length = len(soup.get_text())
        unique_content_length = len(set(soup.get_text().split()))
        
        # If unique words are less than 50% of total, might be duplicate
        return (unique_content_length / content_length) < 0.5 if content_length > 0 else False

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate SEO optimization recommendations"""
        recommendations = []
        
        on_page = results.get('on_page', {})
        content = results.get('content', {})
        technical = results.get('technical_seo', {})
        
        # Title tag recommendations
        title = on_page.get('title', {})
        if not title.get('exists', True):
            recommendations.append({
                'priority': 'high',
                'category': 'on_page',
                'issue': 'Missing Title Tag',
                'description': 'Page does not have a title tag',
                'recommendation': 'Add a descriptive title tag between 30-60 characters',
                'impact': 'Title tags are crucial for search rankings and click-through rates'
            })
        elif not title.get('is_optimal_length', False):
            recommendations.append({
                'priority': 'medium',
                'category': 'on_page',
                'issue': 'Title Tag Length',
                'description': f"Title tag is {title.get('length', 0)} characters",
                'recommendation': 'Optimize title tag length to 30-60 characters for best display',
                'impact': 'Proper title length ensures full display in search results'
            })
        
        # Meta description recommendations
        meta_desc = on_page.get('meta_description', {})
        if not meta_desc.get('exists', True):
            recommendations.append({
                'priority': 'medium',
                'category': 'on_page',
                'issue': 'Missing Meta Description',
                'description': 'Page does not have a meta description',
                'recommendation': 'Add a compelling meta description between 120-160 characters',
                'impact': 'Meta descriptions influence click-through rates from search results'
            })
        
        # Header structure recommendations
        headers = on_page.get('headers', {})
        hierarchy = headers.get('hierarchy', {})
        if not hierarchy.get('has_single_h1', False):
            recommendations.append({
                'priority': 'medium',
                'category': 'on_page',
                'issue': 'H1 Tag Issues',
                'description': f"Page has {hierarchy.get('h1_count', 0)} H1 tags",
                'recommendation': 'Use exactly one H1 tag per page for proper content hierarchy',
                'impact': 'Proper header structure helps search engines understand content organization'
            })
        
        # Content recommendations
        word_count = content.get('word_count', {})
        if not word_count.get('is_sufficient', False):
            recommendations.append({
                'priority': 'medium',
                'category': 'content',
                'issue': 'Insufficient Content',
                'description': f"Page has only {word_count.get('total', 0)} words",
                'recommendation': 'Expand content to at least 300 words for better search visibility',
                'impact': 'Comprehensive content typically ranks better in search results'
            })
        
        # Image optimization recommendations
        images = on_page.get('images', {})
        if images.get('alt_text_percentage', 0) < 90:
            recommendations.append({
                'priority': 'medium',
                'category': 'accessibility',
                'issue': 'Missing Alt Text',
                'description': f"Only {images.get('alt_text_percentage', 0):.1f}% of images have alt text",
                'recommendation': 'Add descriptive alt text to all images',
                'impact': 'Alt text improves accessibility and helps search engines understand images'
            })
        
        return recommendations

    def get_metrics_for_scoring(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics for score calculation"""
        on_page = results.get('on_page', {})
        content = results.get('content', {})
        technical = results.get('technical_seo', {})
        
        return {
            'title_optimized': on_page.get('title', {}).get('is_optimal_length', False),
            'meta_description_ok': on_page.get('meta_description', {}).get('exists', False),
            'headers_structured': on_page.get('headers', {}).get('hierarchy', {}).get('has_single_h1', False),
            'url_optimized': on_page.get('url_structure', {}).get('is_descriptive', False),
            'content_quality_ok': content.get('word_count', {}).get('is_sufficient', False),
            'images_optimized': on_page.get('images', {}).get('alt_text_percentage', 0) > 80,
            'has_structured_data': technical.get('structured_data', {}).get('json_ld', []) != []
        }

