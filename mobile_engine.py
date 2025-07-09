import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, List, Any
import re

class MobileFriendlinessEngine:
    """
    Engine for analyzing mobile-friendliness and user experience factors
    that affect Google's mobile-first indexing and page experience signals.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
        })
        self.timeout = 30

    def analyze(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive mobile-friendliness analysis
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary containing mobile analysis results and recommendations
        """
        start_time = time.time()
        results = {
            'url': url,
            'timestamp': time.time(),
            'mobile_friendly': {},
            'responsive_design': {},
            'user_experience': {},
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
            
            # Mobile-friendly checks
            results['mobile_friendly'] = self._analyze_mobile_friendly_factors(soup, response)
            
            # Responsive design analysis
            results['responsive_design'] = self._analyze_responsive_design(soup)
            
            # User experience analysis
            results['user_experience'] = self._analyze_user_experience(soup, url)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
        except Exception as e:
            results['errors'].append(f"Mobile analysis failed: {str(e)}")
        
        results['execution_time'] = time.time() - start_time
        return results

    def _analyze_mobile_friendly_factors(self, soup: BeautifulSoup, response) -> Dict[str, Any]:
        """Analyze core mobile-friendly factors"""
        mobile_factors = {}
        
        # Viewport configuration
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport and viewport.get('content'):
            viewport_content = viewport['content'].lower()
            mobile_factors['viewport'] = {
                'exists': True,
                'content': viewport['content'],
                'has_width_device': 'width=device-width' in viewport_content,
                'has_initial_scale': 'initial-scale' in viewport_content,
                'is_properly_configured': 'width=device-width' in viewport_content and 'initial-scale=1' in viewport_content
            }
        else:
            mobile_factors['viewport'] = {
                'exists': False,
                'is_properly_configured': False
            }
        
        # Text readability
        mobile_factors['text_readability'] = self._analyze_text_readability(soup)
        
        # Touch targets
        mobile_factors['touch_targets'] = self._analyze_touch_targets(soup)
        
        # Content sizing
        mobile_factors['content_sizing'] = self._analyze_content_sizing(soup)
        
        # Page loading
        mobile_factors['loading'] = {
            'response_size': len(response.content),
            'estimated_load_time': self._estimate_mobile_load_time(response),
            'has_compression': 'gzip' in response.headers.get('content-encoding', '').lower()
        }
        
        return mobile_factors

    def _analyze_responsive_design(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze responsive design implementation"""
        responsive = {}
        
        # CSS media queries detection
        responsive['media_queries'] = self._detect_media_queries(soup)
        
        # Flexible layouts
        responsive['flexible_layout'] = self._analyze_flexible_layout(soup)
        
        # Image responsiveness
        responsive['responsive_images'] = self._analyze_responsive_images(soup)
        
        # Font sizing
        responsive['font_sizing'] = self._analyze_font_sizing(soup)
        
        return responsive

    def _analyze_user_experience(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Analyze user experience factors"""
        ux = {}
        
        # Navigation usability
        ux['navigation'] = self._analyze_navigation_usability(soup)
        
        # Form usability
        ux['forms'] = self._analyze_form_usability(soup)
        
        # Intrusive interstitials
        ux['interstitials'] = self._detect_intrusive_interstitials(soup)
        
        # Content accessibility
        ux['accessibility'] = self._analyze_mobile_accessibility(soup)
        
        # Page structure
        ux['structure'] = self._analyze_page_structure(soup)
        
        return ux

    def _analyze_text_readability(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze text readability on mobile devices"""
        # Find all text elements
        text_elements = soup.find_all(['p', 'div', 'span', 'li'])
        
        # Check for font size specifications (simplified)
        small_text_count = 0
        total_text_elements = len(text_elements)
        
        for element in text_elements:
            style = element.get('style', '')
            if 'font-size' in style:
                # Extract font size (simplified regex)
                size_match = re.search(r'font-size:\s*(\d+)px', style)
                if size_match and int(size_match.group(1)) < 12:
                    small_text_count += 1
        
        return {
            'total_text_elements': total_text_elements,
            'small_text_elements': small_text_count,
            'readable_text_percentage': ((total_text_elements - small_text_count) / total_text_elements * 100) if total_text_elements > 0 else 100,
            'is_readable': small_text_count / total_text_elements < 0.1 if total_text_elements > 0 else True
        }

    def _analyze_touch_targets(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze touch target sizing and spacing"""
        # Find interactive elements
        interactive_elements = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        
        # Check for proper sizing (simplified analysis)
        properly_sized = 0
        total_interactive = len(interactive_elements)
        
        for element in interactive_elements:
            # Check if element has proper sizing attributes or classes
            style = element.get('style', '')
            class_names = ' '.join(element.get('class', []))
            
            # Simple heuristics for touch-friendly sizing
            if ('padding' in style or 'btn' in class_names.lower() or 
                element.name == 'button' or 'touch' in class_names.lower()):
                properly_sized += 1
        
        return {
            'total_interactive_elements': total_interactive,
            'properly_sized_elements': properly_sized,
            'touch_friendly_percentage': (properly_sized / total_interactive * 100) if total_interactive > 0 else 100,
            'is_touch_friendly': properly_sized / total_interactive > 0.8 if total_interactive > 0 else True
        }

    def _analyze_content_sizing(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content sizing for mobile devices"""
        # Check for horizontal scrolling issues
        content_elements = soup.find_all(['div', 'img', 'table', 'iframe'])
        
        fixed_width_elements = 0
        total_content_elements = len(content_elements)
        
        for element in content_elements:
            style = element.get('style', '')
            width = element.get('width', '')
            
            # Check for fixed widths that might cause horizontal scrolling
            if ('width:' in style and 'px' in style) or (width and width.isdigit() and int(width) > 320):
                fixed_width_elements += 1
        
        return {
            'total_content_elements': total_content_elements,
            'fixed_width_elements': fixed_width_elements,
            'flexible_content_percentage': ((total_content_elements - fixed_width_elements) / total_content_elements * 100) if total_content_elements > 0 else 100,
            'avoids_horizontal_scroll': fixed_width_elements / total_content_elements < 0.1 if total_content_elements > 0 else True
        }

    def _detect_media_queries(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Detect CSS media queries for responsive design"""
        media_queries_found = False
        responsive_breakpoints = []
        
        # Check inline styles and style tags
        style_tags = soup.find_all('style')
        for style in style_tags:
            content = style.get_text()
            if '@media' in content:
                media_queries_found = True
                # Extract breakpoints (simplified)
                breakpoints = re.findall(r'@media[^{]*\((?:max-width|min-width):\s*(\d+)px\)', content)
                responsive_breakpoints.extend(breakpoints)
        
        # Check linked stylesheets (would need to fetch them for full analysis)
        link_tags = soup.find_all('link', rel='stylesheet')
        has_external_css = len(link_tags) > 0
        
        return {
            'has_media_queries': media_queries_found,
            'breakpoints_found': list(set(responsive_breakpoints)),
            'has_external_css': has_external_css,
            'is_responsive': media_queries_found or has_external_css  # Assume external CSS might have media queries
        }

    def _analyze_flexible_layout(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze flexible layout implementation"""
        # Look for flexbox and grid usage
        elements_with_flex = soup.find_all(attrs={'style': re.compile(r'display:\s*flex|display:\s*grid')})
        elements_with_flex_classes = soup.find_all(attrs={'class': re.compile(r'flex|grid|col-|row-')})
        
        total_layout_elements = len(soup.find_all(['div', 'section', 'article', 'main', 'aside']))
        flexible_elements = len(elements_with_flex) + len(elements_with_flex_classes)
        
        return {
            'total_layout_elements': total_layout_elements,
            'flexible_elements': flexible_elements,
            'uses_modern_layout': flexible_elements > 0,
            'flexibility_score': min(100, (flexible_elements / total_layout_elements * 100)) if total_layout_elements > 0 else 0
        }

    def _analyze_responsive_images(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze responsive image implementation"""
        images = soup.find_all('img')
        total_images = len(images)
        
        responsive_images = 0
        for img in images:
            # Check for responsive image attributes
            if (img.get('srcset') or img.get('sizes') or 
                'responsive' in ' '.join(img.get('class', [])).lower() or
                'width: 100%' in img.get('style', '') or
                'max-width: 100%' in img.get('style', '')):
                responsive_images += 1
        
        return {
            'total_images': total_images,
            'responsive_images': responsive_images,
            'responsive_percentage': (responsive_images / total_images * 100) if total_images > 0 else 100,
            'uses_responsive_images': responsive_images > 0
        }

    def _analyze_font_sizing(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze font sizing for mobile readability"""
        # Check for relative font sizing
        elements_with_styles = soup.find_all(attrs={'style': True})
        
        relative_font_sizing = 0
        absolute_font_sizing = 0
        
        for element in elements_with_styles:
            style = element['style']
            if 'font-size' in style:
                if any(unit in style for unit in ['em', 'rem', '%', 'vw', 'vh']):
                    relative_font_sizing += 1
                elif 'px' in style:
                    absolute_font_sizing += 1
        
        total_font_declarations = relative_font_sizing + absolute_font_sizing
        
        return {
            'relative_font_sizing': relative_font_sizing,
            'absolute_font_sizing': absolute_font_sizing,
            'uses_relative_sizing': relative_font_sizing > absolute_font_sizing if total_font_declarations > 0 else True,
            'relative_sizing_percentage': (relative_font_sizing / total_font_declarations * 100) if total_font_declarations > 0 else 100
        }

    def _analyze_navigation_usability(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze navigation usability on mobile"""
        nav_elements = soup.find_all(['nav', 'menu']) + soup.find_all(attrs={'class': re.compile(r'nav|menu')})
        
        # Check for mobile-friendly navigation patterns
        has_hamburger_menu = bool(soup.find_all(attrs={'class': re.compile(r'hamburger|menu-toggle|nav-toggle')}))
        has_dropdown_menus = bool(soup.find_all(attrs={'class': re.compile(r'dropdown|submenu')}))
        
        return {
            'navigation_elements': len(nav_elements),
            'has_mobile_menu': has_hamburger_menu,
            'has_dropdown_menus': has_dropdown_menus,
            'is_mobile_optimized': has_hamburger_menu or len(nav_elements) > 0
        }

    def _analyze_form_usability(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze form usability on mobile devices"""
        forms = soup.find_all('form')
        inputs = soup.find_all(['input', 'textarea', 'select'])
        
        mobile_optimized_inputs = 0
        for input_elem in inputs:
            input_type = input_elem.get('type', 'text')
            # Check for mobile-optimized input types
            if input_type in ['email', 'tel', 'url', 'number', 'date', 'time']:
                mobile_optimized_inputs += 1
        
        return {
            'total_forms': len(forms),
            'total_inputs': len(inputs),
            'mobile_optimized_inputs': mobile_optimized_inputs,
            'mobile_input_percentage': (mobile_optimized_inputs / len(inputs) * 100) if inputs else 100,
            'has_mobile_optimized_forms': mobile_optimized_inputs > 0
        }

    def _detect_intrusive_interstitials(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Detect potentially intrusive interstitials"""
        # Look for modal, popup, or overlay elements
        modal_elements = soup.find_all(attrs={'class': re.compile(r'modal|popup|overlay|interstitial')})
        
        # Check for elements that might cover content
        covering_elements = soup.find_all(attrs={'style': re.compile(r'position:\s*fixed|position:\s*absolute')})
        
        return {
            'potential_modals': len(modal_elements),
            'covering_elements': len(covering_elements),
            'has_potential_interstitials': len(modal_elements) > 0 or len(covering_elements) > 3,
            'interstitial_risk': 'high' if len(modal_elements) > 2 else 'medium' if len(modal_elements) > 0 else 'low'
        }

    def _analyze_mobile_accessibility(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze mobile accessibility factors"""
        # Check for accessibility attributes
        elements_with_alt = len(soup.find_all('img', alt=True))
        total_images = len(soup.find_all('img'))
        
        elements_with_aria = len(soup.find_all(attrs={'aria-label': True}))
        interactive_elements = len(soup.find_all(['a', 'button', 'input']))
        
        return {
            'images_with_alt': elements_with_alt,
            'total_images': total_images,
            'alt_text_percentage': (elements_with_alt / total_images * 100) if total_images > 0 else 100,
            'elements_with_aria': elements_with_aria,
            'interactive_elements': interactive_elements,
            'accessibility_score': min(100, ((elements_with_alt + elements_with_aria) / (total_images + interactive_elements) * 100)) if (total_images + interactive_elements) > 0 else 100
        }

    def _analyze_page_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze page structure for mobile optimization"""
        # Check for semantic HTML5 elements
        semantic_elements = soup.find_all(['header', 'nav', 'main', 'article', 'section', 'aside', 'footer'])
        
        # Check for proper heading structure
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        return {
            'semantic_elements': len(semantic_elements),
            'uses_semantic_html': len(semantic_elements) > 0,
            'heading_elements': len(headings),
            'has_proper_structure': len(semantic_elements) > 2 and len(headings) > 0
        }

    def _estimate_mobile_load_time(self, response) -> float:
        """Estimate mobile load time based on response size"""
        # Simplified estimation based on 3G connection speed (~1.6 Mbps)
        size_mb = len(response.content) / (1024 * 1024)
        estimated_time = size_mb / 0.2  # Assuming 0.2 MB/s on 3G
        return round(estimated_time, 2)

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mobile optimization recommendations"""
        recommendations = []
        
        mobile_friendly = results.get('mobile_friendly', {})
        responsive_design = results.get('responsive_design', {})
        user_experience = results.get('user_experience', {})
        
        # Viewport recommendations
        viewport = mobile_friendly.get('viewport', {})
        if not viewport.get('is_properly_configured', False):
            recommendations.append({
                'priority': 'high',
                'category': 'mobile_friendly',
                'issue': 'Viewport Not Configured',
                'description': 'Page lacks proper viewport meta tag configuration',
                'recommendation': 'Add <meta name="viewport" content="width=device-width, initial-scale=1"> to the head section',
                'impact': 'Proper viewport configuration is essential for mobile-friendly display'
            })
        
        # Text readability recommendations
        text_readability = mobile_friendly.get('text_readability', {})
        if not text_readability.get('is_readable', True):
            recommendations.append({
                'priority': 'medium',
                'category': 'mobile_friendly',
                'issue': 'Small Text Size',
                'description': f"Text readability score: {text_readability.get('readable_text_percentage', 0):.1f}%",
                'recommendation': 'Increase font sizes to at least 12px for better mobile readability',
                'impact': 'Small text is difficult to read on mobile devices'
            })
        
        # Touch targets recommendations
        touch_targets = mobile_friendly.get('touch_targets', {})
        if not touch_targets.get('is_touch_friendly', True):
            recommendations.append({
                'priority': 'medium',
                'category': 'mobile_friendly',
                'issue': 'Small Touch Targets',
                'description': f"Touch-friendly elements: {touch_targets.get('touch_friendly_percentage', 0):.1f}%",
                'recommendation': 'Ensure interactive elements are at least 44px in height and width',
                'impact': 'Small touch targets are difficult to tap on mobile devices'
            })
        
        # Responsive design recommendations
        media_queries = responsive_design.get('media_queries', {})
        if not media_queries.get('is_responsive', False):
            recommendations.append({
                'priority': 'high',
                'category': 'responsive_design',
                'issue': 'Not Responsive',
                'description': 'Page does not appear to use responsive design',
                'recommendation': 'Implement CSS media queries and flexible layouts for different screen sizes',
                'impact': 'Non-responsive sites provide poor user experience on mobile devices'
            })
        
        # Content sizing recommendations
        content_sizing = mobile_friendly.get('content_sizing', {})
        if not content_sizing.get('avoids_horizontal_scroll', True):
            recommendations.append({
                'priority': 'medium',
                'category': 'mobile_friendly',
                'issue': 'Horizontal Scrolling',
                'description': 'Page content may require horizontal scrolling on mobile',
                'recommendation': 'Use flexible layouts and avoid fixed-width elements wider than viewport',
                'impact': 'Horizontal scrolling creates poor mobile user experience'
            })
        
        # Interstitials recommendations
        interstitials = user_experience.get('interstitials', {})
        if interstitials.get('interstitial_risk', 'low') == 'high':
            recommendations.append({
                'priority': 'medium',
                'category': 'user_experience',
                'issue': 'Intrusive Interstitials',
                'description': 'Page may have intrusive interstitials that block content',
                'recommendation': 'Avoid pop-ups and overlays that make content inaccessible on mobile',
                'impact': 'Intrusive interstitials can negatively affect mobile search rankings'
            })
        
        return recommendations

    def get_metrics_for_scoring(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics for score calculation"""
        mobile_friendly = results.get('mobile_friendly', {})
        responsive_design = results.get('responsive_design', {})
        user_experience = results.get('user_experience', {})
        
        return {
            'mobile_friendly': mobile_friendly.get('viewport', {}).get('is_properly_configured', False),
            'responsive_design': responsive_design.get('media_queries', {}).get('is_responsive', False),
            'touch_targets_ok': mobile_friendly.get('touch_targets', {}).get('is_touch_friendly', True),
            'viewport_configured': mobile_friendly.get('viewport', {}).get('exists', False),
            'text_readable': mobile_friendly.get('text_readability', {}).get('is_readable', True),
            'no_horizontal_scroll': mobile_friendly.get('content_sizing', {}).get('avoids_horizontal_scroll', True)
        }

