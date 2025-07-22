#!/usr/bin/env python3
"""
Model access client for CLASSICS-EMR benchmark.

This module provides a unified interface for accessing different LLMs
via the Together AI API, with rate limiting, error handling, and cost tracking.
"""

import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import asyncio
from datetime import datetime



try:
    from together import Together
    TOGETHER_AVAILABLE = True
except ImportError:
    TOGETHER_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class GenerationConfig:
    """Configuration for text generation parameters."""
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int = 150
    seed: Optional[int] = None
    stop_sequences: Optional[List[str]] = None

@dataclass
class GenerationResult:
    """Result from a model generation."""
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_seconds: float
    finish_reason: str
    timestamp: datetime
    error: Optional[str] = None

class ModelClient(ABC):
    """Abstract base class for model clients."""
    
    @abstractmethod
    def generate(self, prompt: str, config: GenerationConfig) -> GenerationResult:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model identifier."""
        pass
    
    @abstractmethod
    def get_cost_per_token(self) -> Dict[str, float]:
        """Get cost per token for input and output."""
        pass

class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        if len(self.requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.requests.append(now)

class TogetherAIClient(ModelClient):
    """Client for Together AI models (DeepSeek V3, Llama 3.1)."""
    
    # Model configurations
    MODEL_CONFIGS = {
        "deepseek-v3": {
            "model_id": "deepseek-ai/DeepSeek-V3",
            "input_cost_per_1k": 0.27,  # $0.27 per 1K input tokens
            "output_cost_per_1k": 1.10,  # $1.10 per 1K output tokens
            "rpm": 60  # requests per minute
        },
        "llama-3.1-70b": {
            "model_id": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "input_cost_per_1k": 0.88,  # $0.88 per 1K input tokens
            "output_cost_per_1k": 0.88,  # $0.88 per 1K output tokens
            "rpm": 60
        },
        "kimi-k2-instruct": {
            "model_id": "moonshotai/Kimi-K2-Instruct",
            "input_cost_per_1k": 1.00,  # $1.00 per 1K input tokens
            "output_cost_per_1k": 3.00,  # $3.00 per 1K output tokens
            "rpm": 60
        },
        "llama-4-maverick": {
            "model_id": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "input_cost_per_1k": 1.50,  # Estimated pricing - update when official pricing available
            "output_cost_per_1k": 1.50,
            "rpm": 60
        },
        "qwen3-235b": {
            "model_id": "Qwen/Qwen3-235B-A22B",
            "input_cost_per_1k": 2.00,  # Estimated pricing - update when official pricing available
            "output_cost_per_1k": 2.00,
            "rpm": 60
        }
    }
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        if not TOGETHER_AVAILABLE:
            raise ImportError("together package not available. Install with: pip install together")
        
        if model_name not in self.MODEL_CONFIGS:
            raise ValueError(f"Unsupported model: {model_name}. Available: {list(self.MODEL_CONFIGS.keys())}")
        
        self.model_name = model_name
        self.config = self.MODEL_CONFIGS[model_name]
        
        # Initialize client
        api_key = api_key or os.getenv('TOGETHER_API_KEY')
        if not api_key:
            raise ValueError("Together AI API key required. Set TOGETHER_API_KEY environment variable.")
        
        self.client = Together(api_key=api_key)
        self.rate_limiter = RateLimiter(self.config["rpm"])
        
        logger.info(f"Initialized Together AI client for {model_name}")
    
    def generate(self, prompt: str, config: GenerationConfig) -> GenerationResult:
        """Generate text using Together AI API."""
        start_time = time.time()
        
        try:
            # Rate limiting
            self.rate_limiter.wait_if_needed()
            
            # Prepare request
            messages = [{"role": "user", "content": prompt}]
            
            # Build request parameters
            request_params = {
                "model": self.config["model_id"],
                "messages": messages,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "max_tokens": config.max_tokens,
            }
            
            if config.seed is not None:
                request_params["seed"] = config.seed
            
            if config.stop_sequences:
                request_params["stop"] = config.stop_sequences
            
            # Make API call
            response = self.client.chat.completions.create(**request_params)
            
            # Extract response data
            choice = response.choices[0]
            text = choice.message.content or ""
            finish_reason = choice.finish_reason or "unknown"
            
            # Token usage
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens
            
            # Calculate cost
            cost_usd = self._calculate_cost(prompt_tokens, completion_tokens)
            
            latency_seconds = time.time() - start_time
            
            return GenerationResult(
                text=text,
                model=self.get_model_name(),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                latency_seconds=latency_seconds,
                finish_reason=finish_reason,
                timestamp=datetime.now(),
                error=None
            )
            
        except Exception as e:
            latency_seconds = time.time() - start_time
            logger.error(f"Together AI generation failed: {e}")
            
            return GenerationResult(
                text="",
                model=self.get_model_name(),
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                latency_seconds=latency_seconds,
                finish_reason="error",
                timestamp=datetime.now(),
                error=str(e)
            )
    
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost in USD for token usage."""
        input_cost = (prompt_tokens / 1000) * self.config["input_cost_per_1k"]
        output_cost = (completion_tokens / 1000) * self.config["output_cost_per_1k"]
        return input_cost + output_cost
    
    def get_model_name(self) -> str:
        return f"together-ai/{self.model_name}"
    
    def get_cost_per_token(self) -> Dict[str, float]:
        return {
            "input_per_1k": self.config["input_cost_per_1k"],
            "output_per_1k": self.config["output_cost_per_1k"]
        }



class ModelFactory:
    """Factory for creating model clients."""
    
    @staticmethod
    def create_client(model_name: str, **kwargs) -> ModelClient:
        """Create a model client by name."""
        
        # Together AI models
        if model_name in ["deepseek-v3", "deepseek"]:
            return TogetherAIClient("deepseek-v3", **kwargs)
        elif model_name in ["llama-3.1-70b", "llama-70b", "llama"]:
            return TogetherAIClient("llama-3.1-70b", **kwargs)
        elif model_name in ["kimi-k2-instruct", "kimi-k2", "kimi"]:
            return TogetherAIClient("kimi-k2-instruct", **kwargs)
        elif model_name in ["llama-4-maverick", "llama4-maverick", "maverick"]:
            return TogetherAIClient("llama-4-maverick", **kwargs)

        elif model_name in ["qwen3-235b", "qwen3", "qwen"]:
            return TogetherAIClient("qwen3-235b", **kwargs)
        
        else:
            available_models = [
                "deepseek-v3", "llama-3.1-70b", "kimi-k2-instruct", 
                "llama-4-maverick", "qwen3-235b"
            ]
            raise ValueError(f"Unknown model: {model_name}. Available: {', '.join(available_models)}")
    
    @staticmethod
    def get_all_models() -> List[str]:
        """Get list of all supported models."""
        return ["deepseek-v3", "llama-3.1-70b", "kimi-k2-instruct", "llama-4-maverick", "qwen3-235b"]

class ModelAccessManager:
    """Manager for coordinating multiple model clients with shared rate limiting."""
    
    def __init__(self):
        self.clients: Dict[str, ModelClient] = {}
        self.total_cost = 0.0
        self.total_requests = 0
        
    def add_model(self, model_name: str, **kwargs) -> None:
        """Add a model client."""
        client = ModelFactory.create_client(model_name, **kwargs)
        self.clients[model_name] = client
        logger.info(f"Added model client: {model_name}")
    
    def generate(self, model_name: str, prompt: str, config: GenerationConfig) -> GenerationResult:
        """Generate text using specified model."""
        if model_name not in self.clients:
            raise ValueError(f"Model not initialized: {model_name}")
        
        result = self.clients[model_name].generate(prompt, config)
        
        # Track costs and requests
        self.total_cost += result.cost_usd
        self.total_requests += 1
        
        logger.info(f"Generated {result.completion_tokens} tokens with {model_name}, cost: ${result.cost_usd:.4f}")
        
        return result
    
    def get_cost_summary(self) -> Dict[str, Any]:
        """Get summary of costs and usage."""
        return {
            "total_cost_usd": self.total_cost,
            "total_requests": self.total_requests,
            "average_cost_per_request": self.total_cost / max(1, self.total_requests),
            "models": list(self.clients.keys())
        }

# Convenience functions
def create_model_client(model_name: str, **kwargs) -> ModelClient:
    """Create a single model client."""
    return ModelFactory.create_client(model_name, **kwargs)

def create_model_manager(models: List[str], **kwargs) -> ModelAccessManager:
    """Create a model manager with multiple models."""
    manager = ModelAccessManager()
    for model in models:
        manager.add_model(model, **kwargs)
    return manager 