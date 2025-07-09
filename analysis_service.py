import asyncio
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from src.engines.technical_engine import TechnicalAccessibilityEngine
from src.engines.performance_engine import PerformanceEngine
from src.engines.seo_engine import SEOAnalysisEngine
from src.engines.mobile_engine import MobileFriendlinessEngine
from src.models.url_analysis import UrlAnalysis, db
from src.models.analysis_result import AnalysisResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Service for orchestrating URL analysis across multiple engines
    and managing the analysis workflow.
    """
    
    def __init__(self, pagespeed_api_key: str = None):
        self.engines = {
            'technical': TechnicalAccessibilityEngine(),
            'performance': PerformanceEngine(pagespeed_api_key),
            'seo': SEOAnalysisEngine(),
            'mobile': MobileFriendlinessEngine()
        }
        self.max_workers = 4  # Number of engines that can run in parallel

    def analyze_url(self, analysis_id: str, url: str, engines: List[str], 
                   client_id: str = None) -> Dict[str, Any]:
        """
        Perform comprehensive URL analysis using specified engines
        
        Args:
            analysis_id: Unique identifier for this analysis
            url: The URL to analyze
            engines: List of engine names to run
            client_id: Client identifier for multi-tenant support
            
        Returns:
            Dictionary containing overall analysis results
        """
        start_time = time.time()
        
        # Update analysis status to running
        analysis = UrlAnalysis.query.get(analysis_id)
        if analysis:
            analysis.mark_running()
            db.session.commit()
        
        results = {
            'analysis_id': analysis_id,
            'url': url,
            'engines_run': [],
            'engines_failed': [],
            'overall_score': 0,
            'category_scores': {},
            'recommendations': [],
            'execution_time': 0,
            'timestamp': time.time()
        }
        
        try:
            # Run engines in parallel
            engine_results = self._run_engines_parallel(url, engines)
            
            # Process results and save to database
            for engine_name, engine_result in engine_results.items():
                if 'error' not in engine_result:
                    results['engines_run'].append(engine_name)
                    
                    # Create and save analysis result
                    analysis_result = AnalysisResult(
                        analysis_id=analysis_id,
                        engine=engine_name,
                        execution_time=engine_result.get('execution_time', 0)
                    )
                    
                    # Set results data
                    analysis_result.set_results(engine_result)
                    
                    # Calculate score based on engine metrics
                    metrics = self._extract_metrics_for_engine(engine_name, engine_result)
                    score = analysis_result.calculate_score(metrics)
                    analysis_result.score = score
                    
                    # Set recommendations
                    recommendations = engine_result.get('recommendations', [])
                    analysis_result.set_recommendations(recommendations)
                    
                    # Add to session
                    db.session.add(analysis_result)
                    
                    # Update results summary
                    results['category_scores'][engine_name] = score
                    results['recommendations'].extend(recommendations)
                    
                else:
                    results['engines_failed'].append({
                        'engine': engine_name,
                        'error': engine_result['error']
                    })
                    logger.error(f"Engine {engine_name} failed: {engine_result['error']}")
            
            # Calculate overall score
            if results['category_scores']:
                results['overall_score'] = sum(results['category_scores'].values()) / len(results['category_scores'])
            
            # Sort recommendations by priority
            results['recommendations'] = self._sort_recommendations(results['recommendations'])
            
            # Update analysis status
            if analysis:
                analysis.mark_completed()
                db.session.commit()
            
            logger.info(f"Analysis {analysis_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {str(e)}")
            results['error'] = str(e)
            
            # Mark analysis as failed
            if analysis:
                analysis.mark_failed(str(e))
                db.session.commit()
        
        results['execution_time'] = time.time() - start_time
        return results

    def _run_engines_parallel(self, url: str, engines: List[str]) -> Dict[str, Any]:
        """Run multiple engines in parallel for faster analysis"""
        engine_results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all engine tasks
            future_to_engine = {}
            for engine_name in engines:
                if engine_name in self.engines:
                    future = executor.submit(self._run_single_engine, engine_name, url)
                    future_to_engine[future] = engine_name
                else:
                    logger.warning(f"Unknown engine: {engine_name}")
            
            # Collect results as they complete
            for future in as_completed(future_to_engine):
                engine_name = future_to_engine[future]
                try:
                    result = future.result(timeout=120)  # 2 minute timeout per engine
                    engine_results[engine_name] = result
                    logger.info(f"Engine {engine_name} completed in {result.get('execution_time', 0):.2f}s")
                except Exception as e:
                    engine_results[engine_name] = {'error': str(e)}
                    logger.error(f"Engine {engine_name} failed: {str(e)}")
        
        return engine_results

    def _run_single_engine(self, engine_name: str, url: str) -> Dict[str, Any]:
        """Run a single analysis engine"""
        try:
            engine = self.engines[engine_name]
            result = engine.analyze(url)
            return result
        except Exception as e:
            return {'error': str(e)}

    def _extract_metrics_for_engine(self, engine_name: str, engine_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics for score calculation from engine results"""
        try:
            engine = self.engines[engine_name]
            if hasattr(engine, 'get_metrics_for_scoring'):
                return engine.get_metrics_for_scoring(engine_result)
            else:
                return {}
        except Exception as e:
            logger.error(f"Failed to extract metrics for {engine_name}: {str(e)}")
            return {}

    def _sort_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort recommendations by priority and impact"""
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        
        return sorted(recommendations, key=lambda x: (
            priority_order.get(x.get('priority', 'low'), 2),
            x.get('category', ''),
            x.get('issue', '')
        ))

    def get_analysis_summary(self, analysis_id: str) -> Dict[str, Any]:
        """Get a summary of analysis results"""
        analysis = UrlAnalysis.query.get(analysis_id)
        if not analysis:
            return {'error': 'Analysis not found'}
        
        results = AnalysisResult.get_analysis_results(analysis_id)
        
        summary = {
            'analysis_id': analysis_id,
            'url': analysis.url,
            'status': analysis.status,
            'started_at': analysis.started_at.isoformat() if analysis.started_at else None,
            'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None,
            'engines_requested': analysis.get_engines_requested(),
            'engines_completed': [r.engine for r in results],
            'category_scores': {r.engine: r.score for r in results if r.score is not None},
            'overall_score': 0,
            'total_recommendations': sum(len(r.get_recommendations()) for r in results)
        }
        
        # Calculate overall score
        scores = [r.score for r in results if r.score is not None]
        if scores:
            summary['overall_score'] = sum(scores) / len(scores)
        
        return summary

    def get_detailed_results(self, analysis_id: str) -> Dict[str, Any]:
        """Get detailed analysis results including all engine data"""
        analysis = UrlAnalysis.query.get(analysis_id)
        if not analysis:
            return {'error': 'Analysis not found'}
        
        results = AnalysisResult.get_analysis_results(analysis_id)
        
        detailed = {
            'analysis': analysis.to_dict(),
            'results': {},
            'recommendations': [],
            'summary': self.get_analysis_summary(analysis_id)
        }
        
        for result in results:
            detailed['results'][result.engine] = {
                'score': result.score,
                'execution_time': result.execution_time,
                'data': result.get_results(),
                'recommendations': result.get_recommendations()
            }
            detailed['recommendations'].extend(result.get_recommendations())
        
        # Sort recommendations
        detailed['recommendations'] = self._sort_recommendations(detailed['recommendations'])
        
        return detailed

    def check_cache(self, client_id: str, url: str, max_age_hours: int = 24) -> Optional[str]:
        """Check if there's a recent analysis for the same URL"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        recent_analysis = UrlAnalysis.query.filter(
            UrlAnalysis.client_id == client_id,
            UrlAnalysis.url == url,
            UrlAnalysis.status == 'completed',
            UrlAnalysis.created_at > cutoff_time
        ).order_by(UrlAnalysis.created_at.desc()).first()
        
        return recent_analysis.id if recent_analysis else None

    def get_client_history(self, client_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get analysis history for a client"""
        analyses = UrlAnalysis.get_client_analyses(client_id, limit)
        
        history = []
        for analysis in analyses:
            summary = self.get_analysis_summary(analysis.id)
            history.append(summary)
        
        return history

    def delete_analysis(self, analysis_id: str, client_id: str = None) -> bool:
        """Delete an analysis and all its results"""
        analysis = UrlAnalysis.query.get(analysis_id)
        
        if not analysis:
            return False
        
        # Check client ownership if specified
        if client_id and analysis.client_id != client_id:
            return False
        
        try:
            # Delete analysis (results will be deleted via cascade)
            db.session.delete(analysis)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete analysis {analysis_id}: {str(e)}")
            db.session.rollback()
            return False

    def get_engine_status(self) -> Dict[str, Any]:
        """Get status of all analysis engines"""
        status = {
            'engines': {},
            'total_engines': len(self.engines),
            'healthy_engines': 0
        }
        
        for engine_name, engine in self.engines.items():
            try:
                # Simple health check - try to create engine instance
                engine_status = {
                    'name': engine_name,
                    'status': 'healthy',
                    'class': engine.__class__.__name__
                }
                status['healthy_engines'] += 1
            except Exception as e:
                engine_status = {
                    'name': engine_name,
                    'status': 'unhealthy',
                    'error': str(e)
                }
            
            status['engines'][engine_name] = engine_status
        
        return status

