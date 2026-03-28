"""
Core components for Agentic Assistants.

This module contains the fundamental building blocks:
- OllamaManager: Manage Ollama server and models
- MLFlowTracker: Experiment tracking integration
- MLFlowManager: Enhanced model registry and deployment
- TelemetryManager: OpenTelemetry observability
- Base Models: Pydantic v2 base classes (AgenticEntity, mixins)
- Registry: Auto-registration via __init_subclass__
- DTO: Data Transfer Object system for API boundaries
- Repository / Service: Generic data access patterns
- State Machine: Graph-based workflow execution
- Serialization: Pluggable encode/decode backends
- Observability: Unified Logfire + OpenTelemetry wrapper
- Types: Canonical type aliases and protocols
- Trainer: Abstract training lifecycle with checkpointing and callbacks
- Skills: Skill-based agentic interface (Analyze/Decide/Act) with async support
- Security: Safety guardrails (prompt injection, PII, tool policy, output sanitization)
- Evaluation: Reliability metrics, RAGAS-aligned evaluation, golden datasets
- Patterns: GoF design pattern primitives for ML platforms
- Performance: Caching, retry, rate limiting, batch processing
- Meta: Singleton, plugin metaclasses, class decorators
- Data Utils: Text chunking, dict ops, token estimation
- Validators: Annotated constrained types for Pydantic models
"""

from agentic_assistants.core.ollama import OllamaManager
from agentic_assistants.core.mlflow_tracker import (
    MLFlowTracker,
    MLFlowManager,
    track_experiment,
    ModelStage,
    ModelVersion,
    DeploymentTarget,
    DeploymentInfo,
)
from agentic_assistants.core.telemetry import TelemetryManager, get_tracer

from agentic_assistants.core.base_models import (
    AgenticBaseModel,
    TimestampMixin,
    UUIDMixin,
    SlugMixin,
    SoftDeleteMixin,
    AuditMixin,
    TagsMixin,
    MetadataMixin,
    AgenticEntity,
    AgenticAuditEntity,
    AgenticSlugEntity,
    VersionedMixin,
    StatusMixin,
    EntityStatus,
    ErrorDetail,
    Envelope,
    PaginatedResponse,
    ErrorResponse,
    HealthCheck,
)

from agentic_assistants.core.registry import (
    AutoRegistry,
    ProviderRegistry,
    AdapterRegistry,
    PatternRegistry,
    DataSourceTypeRegistry,
    SerializerRegistry,
    NodeTypeRegistry,
)

from agentic_assistants.core.dto import (
    DTOConfig,
    BaseDTO,
    CreateDTO,
    ReadDTO,
    UpdateDTO,
)

from agentic_assistants.core.repository import (
    AbstractRepository,
    FilterSpec,
    SortSpec,
    PaginationSpec,
    InMemoryRepository,
    SQLAlchemyRepository,
)

from agentic_assistants.core.service import (
    BaseService,
    AuditedService,
    DomainEvent,
)

from agentic_assistants.core.state_machine import (
    START,
    END,
    StateNode,
    ConditionalEdge,
    Checkpointer,
    InMemoryCheckpointer,
    StateMachine,
    CompiledGraph,
)

from agentic_assistants.core.serialization import (
    Serializer,
    JsonSerializer,
    PydanticSerializer,
    MsgspecSerializer,
    get_serializer,
    register_serializer,
)

from agentic_assistants.core.observability import BackendType, ObservabilityManager

from agentic_assistants.core.types import (
    JSON,
    Embedding,
    ChatMessage,
    ChatHistory,
    ToolResult,
    ToolSpec,
    Metadata,
    NodeInputs,
    NodeOutputs,
    ModelName,
    ProviderName,
    CollectionName,
    RunID,
    TrainingState,
    EvalResult,
    SkillPayload,
    ExecutionStatus,
    ExecutionResult,
    DataCatalogProtocol,
    HookManagerProtocol,
    AdapterRunMetadata,
)

from agentic_assistants.core.foundation.types import (
    RunnableNodeProtocol,
    MutableStateProtocol,
    StateMapping,
)

from agentic_assistants.core.trainer import (
    TrainingConfig,
    TrainingMetrics,
    EarlyStopping,
    CheckpointManager,
    TrainerCallback,
    CallbackList,
    BaseTrainer,
)

from agentic_assistants.core.skills import (
    SkillConfig,
    SkillResult,
    SkillMiddleware,
    BaseSkill,
    AgentController,
)

from agentic_assistants.core.security import (
    SecurityConfig,
    PIIMatch,
    DisallowedActionGuard,
    check_prompt_injection,
    detect_pii,
    redact_pii,
    enforce_tool_policy,
    sanitize_output,
    validate_security,
)

from agentic_assistants.core.evaluation import (
    MetricValue,
    MetricTracker,
    TaskSuccessRate,
    LatencyMetric,
    HallucinationRate,
    HandoffEfficiency,
    ContextRelevance,
    ContextSufficiency,
    AnswerRelevance,
    CommunicationEfficiency,
    ResourceFootprint,
    EvaluationResult,
    EvaluationMixin,
    GoldenDataset,
)

from agentic_assistants.core.patterns import (
    ModelFactory,
    Pipeline,
    PipelineBuilder,
    AdapterBase,
    DecoratorBase,
    LazyProxy,
    ProxyBase,
    CachingProxy,
    LoggingDecorator,
    CachingDecorator,
    AlgorithmStrategy,
    StrategyContext,
    Observer,
    Subject,
    EventBus,
    Command,
    CommandQueue,
)

from agentic_assistants.core.performance import (
    timed,
    TTLCache,
    cached,
    async_cached,
    retry,
    BatchProcessor,
    RateLimiter,
    LazyLoader,
)

from agentic_assistants.core.meta import (
    SingletonMeta,
    PluginMeta,
    frozen_attrs,
    validate_subclass,
)

from agentic_assistants.core.data_utils import (
    chunk_text,
    merge_dicts_deep,
    flatten_dict,
    unflatten_dict,
    estimate_tokens,
    truncate_text,
)

from agentic_assistants.core.validators import (
    NonEmptyStr,
    HttpUrl,
    JsonStr,
    SemVer,
    Slug,
    CronExpression,
    PositiveFloat,
    PositiveInt,
)

__all__ = [
    # Original core
    "OllamaManager",
    "MLFlowTracker",
    "MLFlowManager",
    "track_experiment",
    "ModelStage",
    "ModelVersion",
    "DeploymentTarget",
    "DeploymentInfo",
    "TelemetryManager",
    "get_tracer",
    # Base models
    "AgenticBaseModel",
    "TimestampMixin",
    "UUIDMixin",
    "SlugMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    "TagsMixin",
    "MetadataMixin",
    "AgenticEntity",
    "AgenticAuditEntity",
    "AgenticSlugEntity",
    "VersionedMixin",
    "StatusMixin",
    "EntityStatus",
    "ErrorDetail",
    "Envelope",
    "PaginatedResponse",
    "ErrorResponse",
    "HealthCheck",
    # Registry
    "AutoRegistry",
    "ProviderRegistry",
    "AdapterRegistry",
    "PatternRegistry",
    "DataSourceTypeRegistry",
    "SerializerRegistry",
    "NodeTypeRegistry",
    # DTO
    "DTOConfig",
    "BaseDTO",
    "CreateDTO",
    "ReadDTO",
    "UpdateDTO",
    # Repository / Service
    "AbstractRepository",
    "FilterSpec",
    "SortSpec",
    "PaginationSpec",
    "InMemoryRepository",
    "SQLAlchemyRepository",
    "BaseService",
    "AuditedService",
    "DomainEvent",
    # State Machine
    "START",
    "END",
    "StateNode",
    "ConditionalEdge",
    "Checkpointer",
    "InMemoryCheckpointer",
    "StateMachine",
    "CompiledGraph",
    # Serialization
    "Serializer",
    "JsonSerializer",
    "PydanticSerializer",
    "MsgspecSerializer",
    "get_serializer",
    "register_serializer",
    # Observability
    "BackendType",
    "ObservabilityManager",
    # Types
    "JSON",
    "Embedding",
    "ChatMessage",
    "ChatHistory",
    "ToolResult",
    "ToolSpec",
    "Metadata",
    "NodeInputs",
    "NodeOutputs",
    "ModelName",
    "ProviderName",
    "CollectionName",
    "RunID",
    "TrainingState",
    "EvalResult",
    "SkillPayload",
    "ExecutionStatus",
    "ExecutionResult",
    "DataCatalogProtocol",
    "HookManagerProtocol",
    "AdapterRunMetadata",
    "RunnableNodeProtocol",
    "MutableStateProtocol",
    "StateMapping",
    # Trainer
    "TrainingConfig",
    "TrainingMetrics",
    "EarlyStopping",
    "CheckpointManager",
    "TrainerCallback",
    "CallbackList",
    "BaseTrainer",
    # Skills
    "SkillConfig",
    "SkillResult",
    "SkillMiddleware",
    "BaseSkill",
    "AgentController",
    # Security
    "SecurityConfig",
    "PIIMatch",
    "DisallowedActionGuard",
    "check_prompt_injection",
    "detect_pii",
    "redact_pii",
    "enforce_tool_policy",
    "sanitize_output",
    "validate_security",
    # Evaluation
    "MetricValue",
    "MetricTracker",
    "TaskSuccessRate",
    "LatencyMetric",
    "HallucinationRate",
    "HandoffEfficiency",
    "ContextRelevance",
    "ContextSufficiency",
    "AnswerRelevance",
    "CommunicationEfficiency",
    "ResourceFootprint",
    "EvaluationResult",
    "EvaluationMixin",
    "GoldenDataset",
    # Design Patterns
    "ModelFactory",
    "Pipeline",
    "PipelineBuilder",
    "AdapterBase",
    "DecoratorBase",
    "LazyProxy",
    "ProxyBase",
    "CachingProxy",
    "LoggingDecorator",
    "CachingDecorator",
    "AlgorithmStrategy",
    "StrategyContext",
    "Observer",
    "Subject",
    "EventBus",
    "Command",
    "CommandQueue",
    # Performance
    "timed",
    "TTLCache",
    "cached",
    "async_cached",
    "retry",
    "BatchProcessor",
    "RateLimiter",
    "LazyLoader",
    # Meta
    "SingletonMeta",
    "PluginMeta",
    "frozen_attrs",
    "validate_subclass",
    # Data Utils
    "chunk_text",
    "merge_dicts_deep",
    "flatten_dict",
    "unflatten_dict",
    "estimate_tokens",
    "truncate_text",
    # Validators
    "NonEmptyStr",
    "HttpUrl",
    "JsonStr",
    "SemVer",
    "Slug",
    "CronExpression",
    "PositiveFloat",
    "PositiveInt",
]
