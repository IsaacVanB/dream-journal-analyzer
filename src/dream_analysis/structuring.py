"""Reusable structured-feature extraction for dream journal entries."""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

from dream_analysis.ollama_client import OllamaGateway
from dream_analysis.imports import dream_text_hash
from dream_analysis.prompts import STRUCTURING_SYSTEM_PROMPT, structuring_user_prompt
from dream_analysis.repository import DreamRepository


DEFAULT_STRUCTURING_MODEL = "gemma3:12b"
SCHEMA_VERSION = 14
LEGACY_FEATURE_VERSION_SCHEMA = 13
EXTRACTION_VERSION = 1
LEGACY_EXTRACTION_VERSION = 1
MAX_VALIDATION_ATTEMPTS = 2
LEVELS = ["none", "low", "moderate", "high"]
ARRAY_SENTINELS = frozenset(
    {"none", "n/a", "not applicable", "unknown", "unclear"}
)
GENERIC_CHARACTER_ROLES = frozenset(
    {
        "aunt",
        "boss",
        "boyfriend",
        "brother",
        "cashier",
        "classmate",
        "colleague",
        "cop",
        "cops",
        "co-worker",
        "coworker",
        "debater",
        "dad",
        "doctor",
        "father",
        "friend",
        "girlfriend",
        "grandfather",
        "grandma",
        "grandmother",
        "grandpa",
        "husband",
        "manager",
        "mom",
        "mother",
        "neighbor",
        "nurse",
        "partner",
        "police",
        "police officer",
        "professor",
        "roommate",
        "sister",
        "stranger",
        "teacher",
        "therapist",
        "uncle",
        "waiter",
        "waitress",
        "wife",
    }
)

GENERIC_PERSON_NOUNS = frozenset(
    {
        "boy",
        "child",
        "girl",
        "guy",
        "kid",
        "lady",
        "man",
        "person",
        "woman",
    }
)
MAX_NAMED_CHARACTER_WORDS = 5
MAX_NAMED_CHARACTER_CHARS = 60

DREAM_FEATURE_SCHEMA = {
    "type": "object",
    "properties": {
        "setting": {"type": "array", "items": {"type": "string"}},
        "characters": {"type": "array", "items": {"type": "string"}},
        "named_characters": {"type": "array", "items": {"type": "string"}},
        "emotions": {"type": "array", "items": {"type": "string"}},
        "themes": {"type": "array", "items": {"type": "string"}},
        "objects": {"type": "array", "items": {"type": "string"}},
        "actions": {"type": "array", "items": {"type": "string"}},
        "sensory_details": {"type": "array", "items": {"type": "string"}},
        "dream_mechanics": {"type": "array", "items": {"type": "string"}},
        "tone": {"type": "string"},
        "lucidity": {"type": "boolean"},
        "lucidity_level": {
            "type": "string",
            "enum": ["none", "questioning", "lucid"],
        },
        "violence": {"type": "string", "enum": LEVELS},
        "sexual_content": {"type": "string", "enum": LEVELS},
        "social_conflict": {"type": "string", "enum": LEVELS},
        "threat_level": {"type": "string", "enum": LEVELS},
        "agency": {
            "type": "string",
            "enum": ["low", "moderate", "high", "unclear"],
        },
        "bizarreness": {"type": "string", "enum": LEVELS},
        "perspective": {
            "type": "string",
            "enum": ["first_person", "third_person", "mixed", "unclear"],
        },
        "ending": {
            "type": "string",
            "enum": ["resolved", "unresolved", "interrupted", "unclear"],
        },
        "memory_quality": {
            "type": "string",
            "enum": ["fragmentary", "partial", "detailed"],
        },
        "retrieval_quality": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": (
                "Query-independent estimate of how much specific, coherent, "
                "and distinctive evidence the report offers for retrieval."
            ),
        },
        "summary": {"type": "string"},
    },
    "required": [
        "setting",
        "characters",
        "named_characters",
        "emotions",
        "themes",
        "objects",
        "actions",
        "sensory_details",
        "dream_mechanics",
        "tone",
        "lucidity",
        "lucidity_level",
        "violence",
        "sexual_content",
        "social_conflict",
        "threat_level",
        "agency",
        "bizarreness",
        "perspective",
        "ending",
        "memory_quality",
        "retrieval_quality",
        "summary",
    ],
    "additionalProperties": False,
}

# Fields in a group are regenerated together because they describe one concept or
# participate in cross-field validation. To change an extraction definition,
# increment only that group's version. Adding a field to a new or existing group
# causes records missing that field to be backfilled without disturbing others.
FEATURE_GROUPS: dict[str, tuple[str, ...]] = {
    "scene": (
        "setting",
        "characters",
        "named_characters",
        "objects",
        "sensory_details",
    ),
    "narrative": ("themes", "actions", "agency", "ending", "summary"),
    "affect": ("emotions", "tone"),
    "lucidity": ("lucidity", "lucidity_level"),
    "content_intensity": (
        "violence",
        "sexual_content",
        "social_conflict",
        "threat_level",
    ),
    "dream_form": (
        "dream_mechanics",
        "bizarreness",
        "perspective",
        "memory_quality",
    ),
    "retrieval": ("retrieval_quality",),
}
FEATURE_GROUP_VERSIONS = {group: 1 for group in FEATURE_GROUPS}
BASELINE_FEATURE_GROUP_VERSIONS = {group: 1 for group in FEATURE_GROUPS}

_grouped_fields = [field for fields in FEATURE_GROUPS.values() for field in fields]
if set(_grouped_fields) != set(DREAM_FEATURE_SCHEMA["properties"]) or len(
    _grouped_fields
) != len(set(_grouped_fields)):
    raise RuntimeError("FEATURE_GROUPS must contain every feature field exactly once")

ARRAY_FIELDS = {
    name
    for name, definition in DREAM_FEATURE_SCHEMA["properties"].items()
    if definition["type"] == "array"
}
BOOLEAN_FIELDS = {"lucidity"}
NUMBER_FIELDS = {"retrieval_quality"}

SYSTEM_PROMPT = STRUCTURING_SYSTEM_PROMPT


def _is_evident_generic_role(value: str) -> bool:
    normalized = value.casefold()
    normalized = re.sub(r"^(?:a|an|the|my)\s+", "", normalized)
    if normalized in GENERIC_CHARACTER_ROLES:
        return True
    if re.fullmatch(
        r"(?:unknown|unidentified)\s+"
        r"(?:boy|child|girl|guy|man|person|woman)",
        normalized,
    ):
        return True
    return bool(
        re.fullmatch(
            r"(?:boy|girl|guy|man|person|woman)\s+(?:at|from|in)\s+.+",
            normalized,
        )
    )


def _named_character_rejection_reasons(value: str) -> list[str]:
    """Describe why a value is not a conservative proper-name span."""
    reasons: list[str] = []
    normalized = re.sub(r"\s+", " ", value.strip())
    casefolded = normalized.casefold()

    if re.search(r"[()\[\]{}]", normalized):
        reasons.append("contains parentheses or brackets")
    if re.match(r"^(?:the|a|an|my)\b", casefolded):
        reasons.append("begins with an article or possessive determiner")
    if (
        re.search(r"\b(?:also known as|a\.k\.a\.?|aka)\b", casefolded)
        or re.search(r"\s(?:-|–|—|:)\s", normalized)
        or re.search(r",\s*(?:the|a|an|my)\s+.+$", casefolded)
        or re.search(
            r"\b(?:the|a|an|my)\s+(?:\w+\s+){0,3}"
            r"(?:boy|child|girl|guy|kid|lady|man|person|woman)\b",
            casefolded,
        )
        or any(
            normalized.endswith(f" {noun}")
            for noun in GENERIC_PERSON_NOUNS
        )
        or any(
            normalized.endswith(f", {role}")
            for role in GENERIC_CHARACTER_ROLES
        )
    ):
        reasons.append("contains an explanatory role phrase")
    if (
        len(normalized) > MAX_NAMED_CHARACTER_CHARS
        or len(normalized.split()) > MAX_NAMED_CHARACTER_WORDS
    ):
        reasons.append("is an unusually long descriptive phrase")
    if _is_evident_generic_role(normalized):
        reasons.append("matches a generic character role")
    return reasons


def _source_contains_phrase(source_text: str, phrase: str) -> bool:
    compact_source = re.sub(r"\s+", " ", source_text).casefold()
    compact_phrase = re.sub(r"\s+", " ", phrase.strip()).casefold()
    return bool(
        compact_phrase
        and re.search(
            rf"(?<!\w){re.escape(compact_phrase)}(?!\w)",
            compact_source,
        )
    )


def _has_lucid_tag(tags: Sequence[object] | None) -> bool:
    if tags is None or isinstance(tags, (str, bytes)):
        return False
    for tag in tags:
        if not isinstance(tag, str):
            continue
        normalized = tag.strip().casefold().removeprefix("#").strip()
        if normalized == "lucid":
            return True
    return False


def load_dreams(path: Path | str) -> list[dict[str, Any]]:
    """Load validated dream records for feature extraction."""
    return DreamRepository(path).records()


def select_dreams(
    dreams: Sequence[dict[str, Any]],
    dream_id: str | None,
) -> list[dict[str, Any]]:
    """Select all dreams or one exact ID, retaining input order."""
    if dream_id is None:
        return list(dreams)
    selected = [dream for dream in dreams if dream.get("dream_id") == dream_id]
    if not selected:
        raise ValueError(f"Dream ID not found: {dream_id}")
    return selected


def _source_hash(dream: Mapping[str, Any]) -> str:
    return dream_text_hash(str(dream.get("text", "")))


def _stored_group_versions(record: Mapping[str, Any]) -> dict[str, int]:
    versions = record.get("feature_group_versions")
    if isinstance(versions, Mapping):
        return {
            str(group): version
            for group, version in versions.items()
            if type(version) is int
        }
    if record.get("schema_version") == LEGACY_FEATURE_VERSION_SCHEMA and all(
        field in record for field in DREAM_FEATURE_SCHEMA["properties"]
    ):
        return dict(BASELINE_FEATURE_GROUP_VERSIONS)
    return {}


def stale_feature_groups(
    dream: Mapping[str, Any],
    existing_record: Mapping[str, Any] | None,
    *,
    overwrite: bool = False,
    model: str | None = None,
) -> list[str]:
    """Return feature groups that require another model extraction."""
    if existing_record is None or overwrite:
        return list(FEATURE_GROUPS)
    if existing_record.get("structured_text_hash") != _source_hash(dream):
        return list(FEATURE_GROUPS)
    if model is not None and existing_record.get("model") != model:
        return list(FEATURE_GROUPS)
    stored_extraction_version = existing_record.get("extraction_version")
    if (
        stored_extraction_version is None
        and existing_record.get("schema_version") == LEGACY_FEATURE_VERSION_SCHEMA
    ):
        stored_extraction_version = LEGACY_EXTRACTION_VERSION
    if stored_extraction_version != EXTRACTION_VERSION:
        return list(FEATURE_GROUPS)

    stored_versions = _stored_group_versions(existing_record)
    stale = [
        group
        for group, fields in FEATURE_GROUPS.items()
        if stored_versions.get(group) != FEATURE_GROUP_VERSIONS[group]
        or any(field not in existing_record for field in fields)
    ]
    if _has_lucid_tag(dream.get("tags")) != _has_lucid_tag(
        existing_record.get("journal_tags")
    ) and "lucidity" not in stale:
        stale.append("lucidity")
    return stale


def select_pending_dreams(
    dreams: Sequence[dict[str, Any]],
    existing_records: Mapping[str, Mapping[str, Any]],
    *,
    overwrite: bool = False,
    schema_version: int = SCHEMA_VERSION,
    model: str | None = None,
) -> list[dict[str, Any]]:
    """Return dreams requiring extraction under the requested resume policy."""
    pending: list[dict[str, Any]] = []
    for dream in dreams:
        existing = existing_records.get(str(dream.get("dream_id")))
        if (
            stale_feature_groups(
                dream,
                existing,
                overwrite=overwrite,
                model=model,
            )
            or existing is None
            or existing.get("schema_version") != schema_version
            or "feature_provenance" not in existing
        ):
            pending.append(dream)
    return pending


def build_extraction_messages(
    dream: Mapping[str, Any],
    fields: Sequence[str] | None = None,
) -> list[dict[str, str]]:
    """Build the grounded system and user messages for one dream."""
    text = dream.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError(
            f"Dream {dream.get('dream_id', '<unknown>')} has no valid text."
        )

    user_prompt = structuring_user_prompt(
        dream_id=dream.get("dream_id", "unknown"),
        dream_date=dream.get("date", "unknown"),
        tags=", ".join(str(tag) for tag in dream.get("tags", [])) or "none",
        dream_text=text,
    )
    if fields is not None:
        user_prompt += (
            "\nREQUESTED FIELDS:\n"
            + ", ".join(fields)
            + "\nReturn exactly these fields. Do not regenerate or return any "
            "other fields.\n"
        )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def validate_features(
    features: Any,
    *,
    dream_text: str | None = None,
    dream_tags: Sequence[object] | None = None,
    fields: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Validate and normalize a structured Ollama response."""
    if not isinstance(features, dict):
        raise ValueError("Structured features must be a JSON object.")

    normalized_features = dict(features)
    required = set(
        DREAM_FEATURE_SCHEMA["required"] if fields is None else fields
    )
    unknown_fields = required - set(DREAM_FEATURE_SCHEMA["properties"])
    if unknown_fields:
        raise ValueError(f"Unknown structured feature fields: {sorted(unknown_fields)}")
    actual = set(normalized_features)
    if missing := sorted(required - actual):
        raise ValueError(f"Structured response is missing fields: {missing}")
    if unexpected := sorted(actual - required):
        raise ValueError(f"Structured response has unexpected fields: {unexpected}")

    for field in ARRAY_FIELDS & required:
        value = normalized_features[field]
        if not isinstance(value, list) or any(
            not isinstance(item, str) for item in value
        ):
            raise ValueError(f"{field} must be an array of strings.")
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in value:
            normalized = re.sub(r"\s+", " ", item.strip())
            if field != "named_characters":
                normalized = normalized.lower()
            identity = normalized.casefold()
            if (
                normalized
                and identity not in ARRAY_SENTINELS
                and identity not in seen
            ):
                seen.add(identity)
                cleaned.append(normalized)
        normalized_features[field] = cleaned

    invalid_names: dict[str, list[str]] = {}
    for character in normalized_features.get("named_characters", []):
        if reasons := _named_character_rejection_reasons(character):
            invalid_names[character] = reasons
    if invalid_names:
        details = "; ".join(
            f"{character!r}: {', '.join(reasons)}"
            for character, reasons in invalid_names.items()
        )
        raise ValueError(
            "named_characters must contain only explicit proper-name spans; "
            f"invalid values: {details}"
        )

    if dream_text is not None and "named_characters" in required:
        unsupported_names = [
            character
            for character in normalized_features["named_characters"]
            if not _source_contains_phrase(dream_text, character)
        ]
        if unsupported_names:
            raise ValueError(
                "named_characters must occur explicitly in the dream text; "
                f"unsupported values: {unsupported_names}"
            )

    for field in BOOLEAN_FIELDS & required:
        if type(normalized_features[field]) is not bool:
            raise ValueError(f"{field} must be a boolean.")

    for field in NUMBER_FIELDS & required:
        value = normalized_features[field]
        definition = DREAM_FEATURE_SCHEMA["properties"][field]
        if (
            type(value) not in (int, float)
            or not math.isfinite(value)
            or not definition["minimum"] <= value <= definition["maximum"]
        ):
            raise ValueError(
                f"{field} must be a finite number between "
                f"{definition['minimum']} and {definition['maximum']}."
            )
        normalized_features[field] = float(value)

    for field, definition in DREAM_FEATURE_SCHEMA["properties"].items():
        if field not in required:
            continue
        if field in ARRAY_FIELDS or field in BOOLEAN_FIELDS or field in NUMBER_FIELDS:
            continue
        value = normalized_features[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string.")
        value = re.sub(r"\s+", " ", value.strip())
        if "enum" in definition and value not in definition["enum"]:
            raise ValueError(
                f"{field} must be one of {definition['enum']}; got {value!r}."
            )
        normalized_features[field] = value

    if {"lucidity", "lucidity_level"}.issubset(required) and _has_lucid_tag(dream_tags) and (
        normalized_features["lucidity"] is not True
        or normalized_features["lucidity_level"] != "lucid"
    ):
        raise ValueError(
            "dreams tagged 'lucid' must have lucidity true and "
            "lucidity_level 'lucid'."
        )

    if {"lucidity", "lucidity_level"}.issubset(required) and normalized_features["lucidity"] != (
        normalized_features["lucidity_level"] == "lucid"
    ):
        raise ValueError(
            "lucidity must be true exactly when lucidity_level is 'lucid'."
        )
    return normalized_features


def _validation_retry_messages(
    messages: Sequence[Mapping[str, Any]],
    features: Any,
    error: ValueError,
) -> list[dict[str, Any]]:
    """Append one focused correction request after a rejected response."""
    named_character_guidance = ""
    if "named_characters" in str(error):
        named_character_guidance = (
            " For each invalid named_characters value, return only the exact "
            "proper-name span stated in the dream. If the dream gives no proper "
            "name, remove the value from named_characters and put the source-backed "
            "unnamed role or description in characters."
        )
    return [
        *(dict(message) for message in messages),
        {
            "role": "assistant",
            "content": json.dumps(features, ensure_ascii=False),
        },
        {
            "role": "user",
            "content": (
                "Your previous structured response failed application "
                f"validation:\n- {error}\n\n"
                "Return one complete corrected JSON object matching the same "
                "schema. Correct the validation error, use only information "
                "supported by the original dream text, preserve valid fields, "
                f"and do not include an explanation.{named_character_guidance}"
            ),
        },
    ]


def extract_features(
    dream: Mapping[str, Any],
    *,
    model: str = DEFAULT_STRUCTURING_MODEL,
    num_ctx: int = 8192,
    gateway: OllamaGateway | None = None,
    fields: Sequence[str] | None = None,
    existing_features: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Extract and validate structured features for one dream."""
    if num_ctx < 1:
        raise ValueError("num_ctx must be positive")
    selected_fields = tuple(
        DREAM_FEATURE_SCHEMA["required"] if fields is None else fields
    )
    if not selected_fields:
        return {}
    selected_schema = {
        "type": "object",
        "properties": {
            field: DREAM_FEATURE_SCHEMA["properties"][field]
            for field in selected_fields
        },
        "required": list(selected_fields),
        "additionalProperties": False,
    }
    messages = build_extraction_messages(
        dream,
        None if fields is None else selected_fields,
    )
    ollama = gateway or OllamaGateway()
    options = {
        "temperature": 0,
        "num_ctx": num_ctx,
        "num_predict": 1200,
    }
    dream_text = dream.get("text")
    dream_tags = dream.get("tags")
    for attempt in range(MAX_VALIDATION_ATTEMPTS):
        features = ollama.chat_json(
            schema=selected_schema,
            model=model,
            messages=messages,
            think=False,
            options=options,
        )
        try:
            validated = validate_features(
                features,
                dream_text=dream_text if isinstance(dream_text, str) else None,
                dream_tags=(
                    dream_tags
                    if isinstance(dream_tags, Sequence)
                    and not isinstance(dream_tags, (str, bytes))
                    else None
                ),
                fields=selected_fields,
            )
            if existing_features is not None:
                merged = dict(existing_features)
                merged.update(validated)
                merged = validate_features(
                    merged,
                    dream_text=dream_text if isinstance(dream_text, str) else None,
                    dream_tags=(
                        dream_tags
                        if isinstance(dream_tags, Sequence)
                        and not isinstance(dream_tags, (str, bytes))
                        else None
                    ),
                )
                return {field: merged[field] for field in selected_fields}
            return validated
        except ValueError as exc:
            if attempt + 1 == MAX_VALIDATION_ATTEMPTS:
                raise ValueError(
                    "Structured response failed validation after "
                    f"{MAX_VALIDATION_ATTEMPTS} attempts: {exc}"
                ) from exc
            messages = _validation_retry_messages(messages, features, exc)

    raise AssertionError("validation attempt loop exited unexpectedly")


def build_record(
    dream: Mapping[str, Any],
    features: Mapping[str, Any],
    *,
    model: str,
    extracted_at: datetime | None = None,
) -> dict[str, Any]:
    """Combine source metadata and extracted features into a versioned record."""
    timestamp = extracted_at or datetime.now().astimezone()
    timestamp_text = timestamp.isoformat(timespec="seconds")
    return {
        "dream_id": dream.get("dream_id"),
        "date": dream.get("date"),
        "date_sort": dream.get("date_sort"),
        "journal_tags": dream.get("tags", []),
        "source_word_count": dream.get("word_count"),
        "structured_text_hash": _source_hash(dream),
        "schema_version": SCHEMA_VERSION,
        "extraction_version": EXTRACTION_VERSION,
        "model": model,
        "extracted_at": timestamp_text,
        "feature_group_versions": dict(FEATURE_GROUP_VERSIONS),
        "feature_provenance": {
            group: {"model": model, "extracted_at": timestamp_text}
            for group in FEATURE_GROUPS
        },
        **dict(features),
    }


def update_record(
    dream: Mapping[str, Any],
    existing_record: Mapping[str, Any],
    features: Mapping[str, Any],
    refreshed_groups: Sequence[str],
    *,
    model: str,
    extracted_at: datetime | None = None,
) -> dict[str, Any]:
    """Merge selectively refreshed groups into a backward-compatible record."""
    timestamp = extracted_at or datetime.now().astimezone()
    timestamp_text = timestamp.isoformat(timespec="seconds")
    record = dict(existing_record)
    latest_extracted_at = (
        timestamp_text
        if refreshed_groups
        else existing_record.get("extracted_at", timestamp_text)
    )
    record.update(
        {
            "dream_id": dream.get("dream_id"),
            "date": dream.get("date"),
            "date_sort": dream.get("date_sort"),
            "journal_tags": dream.get("tags", []),
            "source_word_count": dream.get("word_count"),
            "structured_text_hash": _source_hash(dream),
            "schema_version": SCHEMA_VERSION,
            "extraction_version": EXTRACTION_VERSION,
            "model": model,
            "extracted_at": latest_extracted_at,
        }
    )
    record.update(features)

    versions = _stored_group_versions(existing_record)
    provenance = existing_record.get("feature_provenance")
    provenance = dict(provenance) if isinstance(provenance, Mapping) else {}
    legacy_model = existing_record.get("model", model)
    legacy_extracted_at = existing_record.get("extracted_at", timestamp_text)
    for group in FEATURE_GROUPS:
        if group in refreshed_groups or group not in versions:
            versions[group] = FEATURE_GROUP_VERSIONS[group]
        if group in refreshed_groups:
            provenance[group] = {"model": model, "extracted_at": timestamp_text}
        elif group not in provenance:
            provenance[group] = {
                "model": legacy_model,
                "extracted_at": legacy_extracted_at,
            }
    record["feature_group_versions"] = versions
    record["feature_provenance"] = provenance
    return record


def load_existing_records(path: Path | str) -> dict[str, dict[str, Any]]:
    """Load resumable structured JSONL records keyed by dream ID."""
    source_path = Path(path)
    if not source_path.exists():
        return {}
    records: dict[str, dict[str, Any]] = {}
    with source_path.open("r", encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number} of {source_path}: {exc}"
                ) from exc
            dream_id = record.get("dream_id") if isinstance(record, dict) else None
            if not isinstance(dream_id, str) or not dream_id:
                raise ValueError(
                    f"Record on line {line_number} of {source_path} has no dream_id."
                )
            records[dream_id] = record
    return records


def serialize_records(records: Mapping[str, Mapping[str, Any]]) -> str:
    """Serialize structured records as JSONL while preserving mapping order."""
    return "".join(
        json.dumps(record, ensure_ascii=False) + "\n"
        for record in records.values()
    )


class DreamStructuringService:
    """Extract validated, versioned feature records through Ollama."""

    def __init__(
        self,
        *,
        ollama_gateway: OllamaGateway,
        model: str = DEFAULT_STRUCTURING_MODEL,
        num_ctx: int = 8192,
    ) -> None:
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model must be a non-empty string")
        if num_ctx < 1:
            raise ValueError("num_ctx must be positive")
        self.ollama = ollama_gateway
        self.model = model.strip()
        self.num_ctx = num_ctx

    def extract_features(self, dream: Mapping[str, Any]) -> dict[str, Any]:
        return extract_features(
            dream,
            model=self.model,
            num_ctx=self.num_ctx,
            gateway=self.ollama,
        )

    def structure(
        self,
        dream: Mapping[str, Any],
        existing_record: Mapping[str, Any] | None = None,
        *,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        groups = stale_feature_groups(
            dream,
            existing_record,
            overwrite=overwrite,
            model=self.model,
        )
        if existing_record is None:
            features = self.extract_features(dream)
            return build_record(dream, features, model=self.model)

        fields = tuple(field for group in groups for field in FEATURE_GROUPS[group])
        existing_features = {
            field: existing_record[field]
            for field in DREAM_FEATURE_SCHEMA["properties"]
            if field in existing_record
        }
        features = extract_features(
            dream,
            model=self.model,
            num_ctx=self.num_ctx,
            gateway=self.ollama,
            fields=fields,
            existing_features=existing_features,
        )
        return update_record(
            dream,
            existing_record,
            features,
            groups,
            model=self.model,
        )
