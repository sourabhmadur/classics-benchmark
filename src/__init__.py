# CLASSICS-EMR Benchmark Package

from .model_access import (
    ModelClient,
    GenerationConfig,
    GenerationResult,
    ModelFactory,
    ModelAccessManager,
    create_model_client,
    create_model_manager
)

from .database import SupabaseLogger

__version__ = "0.1.0"
__all__ = [
    "ModelClient",
    "GenerationConfig", 
    "GenerationResult",
    "ModelFactory",
    "ModelAccessManager",
    "create_model_client",
    "create_model_manager",
    "SupabaseLogger"
] 