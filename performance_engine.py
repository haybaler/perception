import requests
import time
import json
from typing import Dict, List, Any
from urllib.parse import urlparse

class PerformanceEngine:
    """
    Engine for analyzing Core Web Vitals and performance metrics that affect
    Google Search rankings and user experience.
    """
    
    def __init__(self, pagespeed_api_key: str = None):
        self.pagespeed_api_key = pagespeed_api_key
        self.session = requests.Session()
        self.timeout = 60  # PageSpeed API can be slow

    def analyze(self, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive performance analysis including Core Web Vitals
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary containing performance analysis results and recommendations
        """
        start_time = time.time()
        results = {
            'url': url,
            'timestamp': time.time(),
            'core_web_vitals': {},
            'performance_metrics': {},
            'recommendations': [],
            'errors': []
        }
        
        try:
            # Core Web Vitals Analysis
            if self.pagespeed_api_key:
                pagespeed_data = self._analyze_with_pagespeed_api(url)
                if pagespeed_data:
                    results['core_web_vitals'] = self._extract_core_web_vitals(pagespeed_data)
                    results['performance_metrics'] = self._extract_performance_metrics(pagespeed_data)
                    results['pagespeed_raw'] = pagespeed_data
            
            # Fallback performance analysis
            if not results['core_web_vitals']:
                results['core_web_vitals'] = self._basic_performance_analysis(url)
            
            # Mobile performance analysis
            results['mobile_performance'] = self._analyze_mobile_performance(url)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
        except Exception as e:
            results['errors'].append(f"Performance analysis failed: {str(e)}")
        
        results['execution_time'] = time.time() - start_time
        return results

    def _analyze_with_pagespeed_api(self, url: str) -> Dict[str, Any]:
        """Analyze URL using Google PageSpeed Insights API"""
        if not self.pagespeed_api_key:
            return None
        
        api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        
        # Analyze both mobile and desktop
        results = {}
        
        for strategy in ['mobile', 'desktop']:
            try:
                params = {
                    'url': url,
                    'key': self.pagespeed_api_key,
                    'strategy': strategy,
                    'category': ['PERFORMANCE', 'ACCESSIBILITY', 'BEST_PRACTICES', 'SEO']
                }
                
                response = self.session.get(api_url, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    results[strategy] = response.json()
                else:
                    results[strategy] = {'error': f"API returned {response.status_code}"}
                    
            except Exception as e:
                results[strategy] = {'error': str(e)}
        
        return results

    def _extract_core_web_vitals(self, pagespeed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Core Web Vitals metrics from PageSpeed data"""
        core_web_vitals = {}
        
        for strategy in ['mobile', 'desktop']:
            if strategy in pagespeed_data and 'error' not in pagespeed_data[strategy]:
                data = pagespeed_data[strategy]
                lighthouse_result = data.get('lighthouseResult', {})
                audits = lighthouse_result.get('audits', {})
                
                strategy_metrics = {}
                
                # Largest Contentful Paint (LCP)
                lcp_audit = audits.get('largest-contentful-paint', {})
                if 'numericValue' in lcp_audit:
                    lcp_seconds = lcp_audit['numericValue'] / 1000
                    strategy_metrics['lcp'] = {
                        'value': lcp_seconds,
                        'unit': 'seconds',
                        'rating': self._rate_lcp(lcp_seconds),
                        'displayValue': lcp_audit.get('displayValue', '')
                    }
                
                # Interaction to Next Paint (INP) or First Input Delay (FID)
                inp_audit = audits.get('interaction-to-next-paint', {})
                if 'numericValue' in inp_audit:
                    inp_ms = inp_audit['numericValue']
                    strategy_metrics['inp'] = {
                        'value': inp_ms,
                        'unit': 'milliseconds',
                        'rating': self._rate_inp(inp_ms),
                        'displayValue': inp_audit.get('displayValue', '')
                    }
                else:
                    # Fallback to FID if INP not available
                    fid_audit = audits.get('max-potential-fid', {})
                    if 'numericValue' in fid_audit:
                        fid_ms = fid_audit['numericValue']
                        strategy_metrics['fid'] = {
                            'value': fid_ms,
                            'unit': 'milliseconds',
                            'rating': self._rate_fid(fid_ms),
                            'displayValue': fid_audit.get('displayValue', '')
                        }
                
                # Cumulative Layout Shift (CLS)
                cls_audit = audits.get('cumulative-layout-shift', {})
                if 'numericValue' in cls_audit:
                    cls_value = cls_audit['numericValue']
                    strategy_metrics['cls'] = {
                        'value': cls_value,
                        'unit': 'score',
                        'rating': self._rate_cls(cls_value),
                        'displayValue': cls_audit.get('displayValue', '')
                    }
                
                core_web_vitals[strategy] = strategy_metrics
        
        return core_web_vitals

    def _extract_performance_metrics(self, pagespeed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional performance metrics from PageSpeed data"""
        performance_metrics = {}
        
        for strategy in ['mobile', 'desktop']:
            if strategy in pagespeed_data and 'error' not in pagespeed_data[strategy]:
                data = pagespeed_data[strategy]
                lighthouse_result = data.get('lighthouseResult', {})
                audits = lighthouse_result.get('audits', {})
                
                strategy_metrics = {}
                
                # Performance score
                categories = lighthouse_result.get('categories', {})
                performance_category = categories.get('performance', {})
                strategy_metrics['performance_score'] = performance_category.get('score', 0) * 100
                
                # First Contentful Paint
                fcp_audit = audits.get('first-contentful-paint', {})
                if 'numericValue' in fcp_audit:
                    strategy_metrics['fcp'] = fcp_audit['numericValue'] / 1000
                
                # Speed Index
                si_audit = audits.get('speed-index', {})
                if 'numericValue' in si_audit:
                    strategy_metrics['speed_index'] = si_audit['numericValue'] / 1000
                
                # Total Blocking Time
                tbt_audit = audits.get('total-blocking-time', {})
                if 'numericValue' in tbt_audit:
                    strategy_metrics['total_blocking_time'] = tbt_audit['numericValue']
                
                performance_metrics[strategy] = strategy_metrics
        
        return performance_metrics

    def _basic_performance_analysis(self, url: str) -> Dict[str, Any]:
        """Basic performance analysis when PageSpeed API is not available"""
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=self.timeout)
            load_time = time.time() - start_time
            
            # Basic metrics estimation
            return {
                'basic': {
                    'load_time': {
                        'value': load_time,
                        'unit': 'seconds',
                        'rating': 'good' if load_time < 3 else 'needs_improvement' if load_time < 5 else 'poor'
                    },
                    'response_size': {
                        'value': len(response.content),
                        'unit': 'bytes'
                    },
                    'status_code': response.status_code
                }
            }
        except Exception as e:
            return {'error': str(e)}

    def _analyze_mobile_performance(self, url: str) -> Dict[str, Any]:
        """Analyze mobile-specific performance factors"""
        # This would typically involve mobile-specific testing
        # For now, return basic mobile considerations
        return {
            'mobile_considerations': {
                'viewport_configured': self._check_viewport_meta(url),
                'touch_friendly': True,  # Would need deeper analysis
                'mobile_optimized': True  # Would need deeper analysis
            }
        }

    def _check_viewport_meta(self, url: str) -> bool:
        """Check if viewport meta tag is properly configured"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            content = response.text.lower()
            return 'viewport' in content and 'width=device-width' in content
        except:
            return False

    def _rate_lcp(self, lcp_seconds: float) -> str:
        """Rate LCP performance"""
        if lcp_seconds <= 2.5:
            return 'good'
        elif lcp_seconds <= 4.0:
            return 'needs_improvement'
        else:
            return 'poor'

    def _rate_inp(self, inp_ms: float) -> str:
        """Rate INP performance"""
        if inp_ms <= 200:
            return 'good'
        elif inp_ms <= 500:
            return 'needs_improvement'
        else:
            return 'poor'

    def _rate_fid(self, fid_ms: float) -> str:
        """Rate FID performance"""
        if fid_ms <= 100:
            return 'good'
        elif fid_ms <= 300:
            return 'needs_improvement'
        else:
            return 'poor'

    def _rate_cls(self, cls_value: float) -> str:
        """Rate CLS performance"""
        if cls_value <= 0.1:
            return 'good'
        elif cls_value <= 0.25:
            return 'needs_improvement'
        else:
            return 'poor'

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        core_web_vitals = results.get('core_web_vitals', {})
        
        # LCP recommendations
        for strategy, metrics in core_web_vitals.items():
            if 'lcp' in metrics and metrics['lcp']['rating'] != 'good':
                recommendations.append({
                    'priority': 'high',
                    'category': 'performance',
                    'issue': f'Poor Largest Contentful Paint ({strategy})',
                    'description': f"LCP is {metrics['lcp']['value']:.2f}s (target: ≤2.5s)",
                    'recommendation': 'Optimize server response times, remove render-blocking resources, and optimize images',
                    'impact': 'LCP directly affects Core Web Vitals score and user experience'
                })
            
            # INP/FID recommendations
            if 'inp' in metrics and metrics['inp']['rating'] != 'good':
                recommendations.append({
                    'priority': 'high',
                    'category': 'performance',
                    'issue': f'Poor Interaction to Next Paint ({strategy})',
                    'description': f"INP is {metrics['inp']['value']:.0f}ms (target: ≤200ms)",
                    'recommendation': 'Reduce JavaScript execution time and optimize event handlers',
                    'impact': 'INP affects user interaction responsiveness and Core Web Vitals'
                })
            
            # CLS recommendations
            if 'cls' in metrics and metrics['cls']['rating'] != 'good':
                recommendations.append({
                    'priority': 'medium',
                    'category': 'performance',
                    'issue': f'Poor Cumulative Layout Shift ({strategy})',
                    'description': f"CLS is {metrics['cls']['value']:.3f} (target: ≤0.1)",
                    'recommendation': 'Set size attributes for images and videos, avoid inserting content above existing content',
                    'impact': 'CLS affects visual stability and user experience'
                })
        
        return recommendations

    def get_metrics_for_scoring(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics for score calculation"""
        core_web_vitals = results.get('core_web_vitals', {})
        
        # Use mobile metrics as primary (mobile-first indexing)
        mobile_metrics = core_web_vitals.get('mobile', {})
        
        return {
            'lcp': mobile_metrics.get('lcp', {}).get('value', 0),
            'inp': mobile_metrics.get('inp', {}).get('value', 0),
            'cls': mobile_metrics.get('cls', {}).get('value', 0),
            'has_core_web_vitals': bool(mobile_metrics)
        }

