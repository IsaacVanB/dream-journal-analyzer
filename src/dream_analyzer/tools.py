"""Public compatibility facade for dream-agent tools.

Implementations live in focused modules; imports from dream_analyzer.tools
remain supported.
"""

from dream_analyzer.analytics_tools import DreamStatisticsTool, TagTrendTool
from dream_analyzer.character_tools import (
    CharacterContextTool,
    CharacterMentionsTool,
)
from dream_analyzer.journal_tools import (
    DreamByIdTool,
    DreamDateRangeTool,
    DreamTagTool,
)
from dream_analyzer.retrieval_tools import DreamKeywordSearchTool, DreamSearchTool
from dream_analyzer.tool_protocols import (
    AgentTool,
    AnalyticalToolResult,
    CharacterRecordRepository,
    DatedDreamRepository,
    DreamByIdRepository,
    DreamCollectionRepository,
    SearchableDreamIndex,
    SearchableDreamKeywordIndex,
    StructuredDreamRecordRepository,
    TaggedDreamRepository,
)

__all__ = [
    "AgentTool",
    "AnalyticalToolResult",
    "CharacterContextTool",
    "CharacterMentionsTool",
    "CharacterRecordRepository",
    "DatedDreamRepository",
    "DreamByIdRepository",
    "DreamByIdTool",
    "DreamCollectionRepository",
    "DreamDateRangeTool",
    "DreamKeywordSearchTool",
    "DreamSearchTool",
    "DreamStatisticsTool",
    "DreamTagTool",
    "SearchableDreamIndex",
    "SearchableDreamKeywordIndex",
    "StructuredDreamRecordRepository",
    "TaggedDreamRepository",
    "TagTrendTool",
]
