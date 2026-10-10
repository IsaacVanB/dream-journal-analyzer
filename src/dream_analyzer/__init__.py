"""Reusable services for the dream-analyzer project."""

from dream_analyzer.analysis import SingleDreamAnalysisService
from dream_analyzer.agent import (
    AgentEmptyResponseError,
    AgentResponse,
    AgentTraceError,
    AgentTurnTrace,
    AgentToolLimitError,
    DreamRagAgent,
    ToolExecution,
    ToolRequest,
)
from dream_analyzer.artifacts import write_json_atomic, write_text_atomic
from dream_analyzer.bm25 import Bm25SearchResult, DreamBm25Index, tokenize_english
from dream_analyzer.characters import CharacterLookupService
from dream_analyzer.config import Settings
from dream_analyzer.dates import (
    filter_records_by_date,
    filter_dreams_by_date,
    format_period_label,
    parse_date_bound,
    period_start,
    record_date,
    validate_date_range,
)
from dream_analyzer.index import DreamIndex, EmbeddingModelMismatchError
from dream_analyzer.models import Dream, DreamValidationError, RelatedDream, SearchResult
from dream_analyzer.ollama_client import OllamaGateway
from dream_analyzer.parser import JournalParser
from dream_analyzer.rag import DirectRagService
from dream_analyzer.repository import (
    CharacterDictionaryRepository,
    DreamNotFoundError,
    DreamRepository,
    StructuredDreamRepository,
    load_jsonl_objects,
)
from dream_analyzer.statistics import DreamStatisticsService
from dream_analyzer.structuring import DreamStructuringService
from dream_analyzer.trends import TagTrendService
from dream_analyzer.tools import (
    AgentTool,
    AnalyticalToolResult,
    CharacterContextTool,
    CharacterMentionsTool,
    DreamByIdTool,
    DreamDateRangeTool,
    DreamKeywordSearchTool,
    DreamSearchTool,
    DreamStatisticsTool,
    DreamTagTool,
    TagTrendTool,
)

__all__ = [
    "Dream",
    "DreamRagAgent",
    "DreamBm25Index",
    "DreamKeywordSearchTool",
    "DreamSearchTool",
    "DreamStatisticsTool",
    "DreamTagTool",
    "TagTrendTool",
    "DreamByIdTool",
    "DreamDateRangeTool",
    "AgentTool",
    "AnalyticalToolResult",
    "CharacterContextTool",
    "CharacterMentionsTool",
    "CharacterDictionaryRepository",
    "Bm25SearchResult",
    "DreamIndex",
    "DreamNotFoundError",
    "DreamRepository",
    "StructuredDreamRepository",
    "DreamValidationError",
    "DreamStatisticsService",
    "DreamStructuringService",
    "DirectRagService",
    "EmbeddingModelMismatchError",
    "filter_records_by_date",
    "filter_dreams_by_date",
    "format_period_label",
    "load_jsonl_objects",
    "OllamaGateway",
    "JournalParser",
    "parse_date_bound",
    "period_start",
    "RelatedDream",
    "record_date",
    "SearchResult",
    "Settings",
    "SingleDreamAnalysisService",
    "TagTrendService",
    "AgentResponse",
    "AgentEmptyResponseError",
    "AgentTraceError",
    "AgentTurnTrace",
    "AgentToolLimitError",
    "ToolExecution",
    "ToolRequest",
    "tokenize_english",
    "validate_date_range",
    "CharacterLookupService",
    "write_json_atomic",
    "write_text_atomic",
]
