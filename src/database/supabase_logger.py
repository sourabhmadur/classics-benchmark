#!/usr/bin/env python3
"""
Supabase logging client for CLASSICS-EMR benchmark.

This module provides a unified interface for logging experiment results
to Supabase, including experiment runs, generation results, and metrics.
"""

import os
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import logging

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

logger = logging.getLogger(__name__)

class SupabaseLogger:
    """
    Logger for CLASSICS-EMR experiment results using Supabase.
    
    Handles experiment runs, generation results, and evaluation metrics.
    Gracefully handles missing Supabase configuration for development.
    """
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialize Supabase logger.
        
        Args:
            supabase_url: Supabase project URL (defaults to SUPABASE_URL env var)
            supabase_key: Supabase anon key (defaults to SUPABASE_ANON_KEY env var)
        """
        self.client: Optional[Client] = None
        self.enabled = False
        
        # Get credentials
        self.url = supabase_url or os.getenv('SUPABASE_URL')
        self.key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        
        # Initialize client if possible
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize Supabase client with error handling."""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase package not available. Install with: pip install supabase>=2.0.0")
            return
            
        if not self.url or not self.key:
            logger.warning("Supabase credentials not found. Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables.")
            return
            
        try:
            self.client = create_client(self.url, self.key)
            self.enabled = True
            logger.info("Supabase client initialized successfully")
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.enabled = False
    
    def _test_connection(self) -> bool:
        """Test Supabase connection and table access."""
        if not self.enabled:
            return False
            
        try:
            # Try to query experiment_runs table
            result = self.client.table('experiment_runs').select('id').limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.warning(f"Supabase connection test failed: {e}")
            logger.warning("Make sure database tables are created. See docs/supabase_setup_guide.md")
            return False
    
    def create_experiment_run(
        self, 
        experiment_name: str, 
        description: str = "", 
        config: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a new experiment run entry.
        
        Args:
            experiment_name: Name of the experiment
            description: Optional description
            config: Configuration parameters as JSON
            
        Returns:
            Experiment run ID if successful, None if failed
        """
        if not self.enabled:
            logger.warning("Supabase not enabled, skipping experiment run creation")
            return None
            
        try:
            data = {
                'experiment_name': experiment_name,
                'description': description,
                'config': config or {},
                'status': 'running'
            }
            
            result = self.client.table('experiment_runs').insert(data).execute()
            
            if result.data and len(result.data) > 0:
                experiment_id = result.data[0]['id']
                logger.info(f"Created experiment run: {experiment_id}")
                return experiment_id
            else:
                logger.error("Failed to create experiment run: no data returned")
                return None
                
        except Exception as e:
            logger.error(f"Error creating experiment run: {e}")
            return None
    
    def update_experiment_status(self, experiment_id: str, status: str) -> bool:
        """
        Update experiment run status.
        
        Args:
            experiment_id: Experiment run ID
            status: New status ('running', 'completed', 'failed')
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
            
        try:
            result = self.client.table('experiment_runs').update({
                'status': status
            }).eq('id', experiment_id).execute()
            
            logger.info(f"Updated experiment {experiment_id} status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating experiment status: {e}")
            return False
    
    def log_generation_result(
        self,
        experiment_run_id: Optional[str],
        novel_key: str,
        snippet_id: int,
        snippet_text: str,
        first_sentence: str,
        model_key: str,
        model_name: str,
        model_provider: str,
        is_open_source: bool,
        prompt_strategy: str,
        prompt_text: str,
        temperature: float,
        top_p: float,
        seed: Optional[int],
        max_tokens: int,
        generated_text: Optional[str],
        generation_time: float,
        success: bool,
        error: Optional[str] = None,
        exact_match_recall: Optional[float] = None,
        partial_overlap_score: Optional[float] = None,
        word_overlap_score: Optional[float] = None,
        semantic_similarity_score: Optional[float] = None
    ) -> Optional[str]:
        """
        Log a generation result with all parameters and metrics.
        
        Returns:
            Generation result ID if successful, None if failed
        """
        if not self.enabled:
            logger.debug(f"Supabase not enabled, skipping log for {model_key} on {novel_key} snippet {snippet_id}")
            return None
            
        try:
            data = {
                'experiment_run_id': experiment_run_id,
                'novel_key': novel_key,
                'snippet_id': snippet_id,
                'snippet_type': 'target',  # vs 'control' for future paraphrased snippets
                'original_text': snippet_text,
                'first_sentence': first_sentence,
                'model_key': model_key,
                'model_name': model_name,
                'model_id': model_key,  # For backwards compatibility
                'provider': model_provider,
                'is_open_source': is_open_source,
                'prompt_strategy': prompt_strategy,
                'prompt_text': prompt_text,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'top_p': top_p,
                'seed': seed,
                'generated_text': generated_text,
                'generation_time': generation_time,
                'success': success,
                'error': error,
                'exact_match_recall': exact_match_recall,
                'partial_overlap_score': partial_overlap_score,
                'word_overlap_score': word_overlap_score,
                'semantic_similarity_score': semantic_similarity_score
            }
            
            result = self.client.table('generation_results').insert(data).execute()
            
            if result.data and len(result.data) > 0:
                generation_id = result.data[0]['id']
                logger.debug(f"Logged generation result: {generation_id}")
                return generation_id
            else:
                logger.error("Failed to log generation result: no data returned")
                return None
                
        except Exception as e:
            logger.error(f"Error logging generation result: {e}")
            return None
    
    def get_experiment_results(self, experiment_id: str) -> List[Dict[str, Any]]:
        """
        Get all generation results for an experiment.
        
        Args:
            experiment_id: Experiment run ID
            
        Returns:
            List of generation result records
        """
        if not self.enabled:
            return []
            
        try:
            result = self.client.table('generation_results').select('*').eq(
                'experiment_run_id', experiment_id
            ).execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting experiment results: {e}")
            return []
    
    def get_model_statistics(self, model_key: str) -> Dict[str, Any]:
        """
        Get statistics for a specific model across all experiments.
        
        Args:
            model_key: Model identifier
            
        Returns:
            Dictionary with model statistics
        """
        if not self.enabled:
            return {}
            
        try:
            # Get all results for this model
            result = self.client.table('generation_results').select('*').eq(
                'model_key', model_key
            ).eq('success', True).execute()
            
            if not result.data:
                return {}
            
            results = result.data
            
            # Calculate statistics
            stats = {
                'total_generations': len(results),
                'successful_generations': len([r for r in results if r['success']]),
                'avg_generation_time': sum(r['generation_time'] for r in results) / len(results),
                'emr_results': [r['exact_match_recall'] for r in results if r['exact_match_recall'] is not None],
                'partial_overlap_results': [r['partial_overlap_score'] for r in results if r['partial_overlap_score'] is not None],
                'word_overlap_results': [r['word_overlap_score'] for r in results if r['word_overlap_score'] is not None],
                'semantic_similarity_results': [r['semantic_similarity_score'] for r in results if r['semantic_similarity_score'] is not None]
            }
            
            # Calculate averages for metrics
            if stats['emr_results']:
                stats['avg_emr'] = sum(stats['emr_results']) / len(stats['emr_results'])
                stats['emr_positive_rate'] = len([x for x in stats['emr_results'] if x >= 0.9]) / len(stats['emr_results'])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting model statistics: {e}")
            return {}
    
    def create_database_tables(self) -> bool:
        """
        Create database tables if they don't exist.
        Note: This requires service role key, not anon key.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.error("Supabase not enabled")
            return False
            
        # SQL for creating tables
        create_tables_sql = """
        -- Create experiment_runs table
        CREATE TABLE IF NOT EXISTS experiment_runs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            experiment_name TEXT NOT NULL,
            description TEXT,
            config JSONB,
            status TEXT DEFAULT 'running'
        );

        -- Create generation_results table
        CREATE TABLE IF NOT EXISTS generation_results (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            experiment_run_id UUID REFERENCES experiment_runs(id),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            
            -- Snippet information
            novel_key TEXT NOT NULL,
            snippet_id INTEGER NOT NULL,
            snippet_type TEXT NOT NULL,
            original_text TEXT NOT NULL,
            first_sentence TEXT,
            
            -- Model information
            model_key TEXT NOT NULL,
            model_name TEXT NOT NULL,
            model_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            is_open_source BOOLEAN NOT NULL,
            
            -- Generation parameters
            prompt_strategy TEXT NOT NULL,
            prompt_text TEXT NOT NULL,
            max_tokens INTEGER NOT NULL,
            temperature FLOAT NOT NULL,
            top_p FLOAT NOT NULL,
            seed INTEGER,
            
            -- Generation results
            generated_text TEXT,
            generation_time FLOAT NOT NULL,
            success BOOLEAN NOT NULL,
            error TEXT,
            
            -- Evaluation metrics
            exact_match_recall FLOAT,
            partial_overlap_score FLOAT,
            word_overlap_score FLOAT,
            semantic_similarity_score FLOAT
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_generation_results_experiment_run ON generation_results(experiment_run_id);
        CREATE INDEX IF NOT EXISTS idx_generation_results_model ON generation_results(model_key);
        CREATE INDEX IF NOT EXISTS idx_generation_results_novel ON generation_results(novel_key);
        CREATE INDEX IF NOT EXISTS idx_generation_results_strategy ON generation_results(prompt_strategy);
        CREATE INDEX IF NOT EXISTS idx_generation_results_success ON generation_results(success);
        """
        
        try:
            # Note: This may fail with anon key - tables should be created via SQL Editor
            result = self.client.rpc('exec_sql', {'sql': create_tables_sql}).execute()
            logger.info("Database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            logger.info("Please create tables manually using the SQL Editor in Supabase dashboard")
            logger.info("See docs/supabase_setup_guide.md for instructions")
            return False

# Global logger instance
_supabase_logger: Optional[SupabaseLogger] = None

def get_supabase_logger() -> SupabaseLogger:
    """Get the global Supabase logger instance."""
    global _supabase_logger
    if _supabase_logger is None:
        _supabase_logger = SupabaseLogger()
    return _supabase_logger

def set_supabase_logger(logger_instance: SupabaseLogger) -> None:
    """Set the global Supabase logger instance."""
    global _supabase_logger
    _supabase_logger = logger_instance 