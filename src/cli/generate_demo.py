#!/usr/bin/env python3
"""Generate a README-ready Markdown transcript of a dream-agent run."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from cli import dream_agent
from dream_analyzer.agent import (
    AgentResponse,
    AgentTraceError,
    DreamRagAgent,
    ToolExecution,
    ToolRequest,
)


DEFAULT_OUTPUT = Path("outputs/readme_demo.md")


def build_parser(
    parser: argparse.ArgumentParser | None = None,
) -> argparse.ArgumentParser:
    """Build the demo CLI using the same runtime options as ``ask``."""
    parser = dream_agent.build_parser(parser)
    parser.description = (
        "Run the dream agent and save a README-ready Markdown transcript."
    )
    for action in parser._actions:
        if action.dest == "output":
            action.default = DEFAULT_OUTPUT
            action.help = (
                "Markdown destination (default: outputs/readme_demo.md)."
            )
            break
    return parser


def format_demo_markdown(
    question: str,
    response: AgentResponse,
    *,
    settings: Mapping[str, Any] | None = None,
    include_debug: bool = False,
) -> str:
    """Render the public parts of one agent run as a Markdown demo."""
    lines = [
        "# Dream Analyzer Demo",
        "",
        "## User Question",
        "",
        *_blockquote(question.strip()),
        "",
    ]

    if settings:
        lines.extend(["## Run Settings", ""])
        lines.extend(
            f"- **{name}:** `{_inline_code(value)}`"
            for name, value in settings.items()
        )
        lines.append("")

    lines.extend(["## Agent Tool Calls", ""])
    if not response.tool_executions and not response.unexecuted_tool_calls:
        lines.extend(["No tool calls were recorded.", ""])
    for index, execution in enumerate(response.tool_executions, start=1):
        lines.extend(_format_tool_call(index, execution))

    offset = len(response.tool_executions)
    for index, request in enumerate(response.unexecuted_tool_calls, start=offset + 1):
        lines.extend(_format_unexecuted_tool_call(index, request))

    if include_debug:
        lines.extend(["## Agent Turn Trace", ""])
        if not response.turn_traces:
            lines.extend(["No agent turns were recorded.", ""])
        for index, turn in enumerate(response.turn_traces, start=1):
            phase = "final synthesis" if turn.forced_synthesis else "tool loop"
            lines.extend(
                [
                    f"### Turn {index}: {phase}",
                    "",
                    _code_block(
                        json.dumps(
                            {
                                "tools_enabled": turn.tools_enabled,
                                "request_prompt": turn.request_prompt,
                                "assistant_message": dict(turn.assistant_message),
                                "diagnostics": dict(turn.diagnostics),
                            },
                            ensure_ascii=False,
                            indent=2,
                            sort_keys=True,
                            default=str,
                        ),
                        "json",
                    ),
                    "",
                ]
            )

    retrieved = _unique_retrieved_dreams(response.tool_executions)
    lines.extend(["## Dreams Retrieved", ""])
    if not retrieved:
        lines.extend(["No dream records were returned by the tools.", ""])
    for index, item in enumerate(retrieved.values(), start=1):
        dream = item["dream"]
        calls = ", ".join(str(number) for number in item["calls"])
        lines.extend(
            [
                f"### {index}. Dream `{_inline_code(dream.get('dream_id', 'unknown'))}`",
                "",
                f"- Date: `{_inline_code(dream.get('date', 'unknown'))}`",
                f"- Returned by tool calls: `{calls}`",
                "",
                _code_block(dream.get("text", ""), "text"),
                "",
            ]
        )

    ranking = DreamRagAgent.rank_dream_evidence(response.tool_executions)
    lines.extend(["## Final Dream Ranking", ""])
    if not ranking:
        lines.extend(
            [
                "No dream ranking was produced (the response may use analytical "
                "tool results instead).",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "The agent combines distinct retrieval rankings with reciprocal-rank "
                "fusion (RRF).",
                "",
                "| Rank | Dream ID | Date | RRF score | Best source rank | Methods | Source ranks |",
                "|---:|---|---|---:|---:|---|---|",
            ]
        )
        for rank, dream in enumerate(ranking, start=1):
            methods = ", ".join(dream.get("retrieval_methods", []))
            sources = ", ".join(
                f"call {source['search']}: #{source['rank']} ({source['retrieval_method']})"
                for source in dream.get("sources", [])
            )
            lines.append(
                f"| {rank} | {_table_cell(dream.get('dream_id', 'unknown'))} "
                f"| {_table_cell(dream.get('date', 'unknown'))} "
                f"| {float(dream.get('rrf_score', 0.0)):.6f} "
                f"| {dream.get('best_rank', '')} | {_table_cell(methods)} "
                f"| {_table_cell(sources)} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Model Response",
            "",
            response.answer.rstrip() or "*(The model returned an empty response.)*",
            "",
        ]
    )
    return "\n".join(lines)


def generate(args: argparse.Namespace, parser: argparse.ArgumentParser) -> Path:
    """Run the existing agent and write its demo transcript."""
    dream_agent.validate_args(parser, args)
    agent = dream_agent.build_agent(
        chroma_path=args.chroma_path,
        collection_name=args.collection_name,
        embed_model=args.embed_model,
        top_k=args.top_k,
        max_chars_per_dream=args.max_chars_per_dream,
        dreams_path=args.dreams_path,
        structured_dreams_path=args.structured_dreams_path,
        characters_path=args.characters_path,
    )
    try:
        response = agent.answer(
            args.question,
            chat_model=args.chat_model,
            num_ctx=args.num_ctx,
            num_predict=args.num_predict,
            temperature=args.temperature,
            max_tool_calls=args.max_tool_calls,
            max_synthesis_dreams=args.max_synthesis_dreams,
        )
    except AgentTraceError as exc:
        response = AgentResponse(
            answer=f"[No final answer: {exc}]",
            tool_executions=exc.completed_executions,
            assistant_messages=exc.assistant_messages,
            turn_traces=exc.turn_traces,
            unexecuted_tool_calls=exc.pending_tool_calls,
        )
        output_path = _write_demo(args, response)
        print(f"Saved partial demo to {output_path}", file=sys.stderr)
        raise SystemExit(2) from None

    output_path = _write_demo(args, response)
    print(f"Saved README demo to {output_path}")
    return output_path


def _write_demo(args: argparse.Namespace, response: AgentResponse) -> Path:
    report = format_demo_markdown(
        args.question,
        response,
        settings=dream_agent.report_settings(args),
        include_debug=args.debug,
    )
    return dream_agent.save_markdown_report(Path(args.output), report)


def _format_tool_call(index: int, execution: ToolExecution) -> list[str]:
    result = execution.report_result or execution.result
    status = "cached" if execution.cached else "executed"
    if not result.get("ok"):
        status = "error"
    lines = [
        f"### Tool Call {index}: `{_inline_code(execution.name)}`",
        "",
        f"Status: `{status}`",
        "",
        _code_block(
            json.dumps(
                dict(execution.arguments),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                default=str,
            ),
            "json",
        ),
        "",
    ]
    if not result.get("ok"):
        lines.extend([f"Error: {result.get('error', 'unknown tool error')}", ""])
    return lines


def _format_unexecuted_tool_call(index: int, request: ToolRequest) -> list[str]:
    return [
        f"### Tool Call {index}: `{_inline_code(request.name)}`",
        "",
        "Status: `not executed`",
        "",
        _code_block(
            json.dumps(
                dict(request.arguments),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                default=str,
            ),
            "json",
        ),
        "",
    ]


def _unique_retrieved_dreams(
    executions: Sequence[ToolExecution],
) -> dict[str, dict[str, Any]]:
    dreams: dict[str, dict[str, Any]] = {}
    for call_number, execution in enumerate(executions, start=1):
        result = execution.report_result or execution.result
        if not result.get("ok"):
            continue
        for dream in result.get("dreams", []) or []:
            dream_id = str(dream.get("dream_id", "unknown"))
            if dream_id not in dreams:
                dreams[dream_id] = {"dream": dream, "calls": [call_number]}
            else:
                dreams[dream_id]["calls"].append(call_number)
    return dreams


def _blockquote(value: str) -> list[str]:
    return [f"> {line}" if line else ">" for line in value.splitlines()]


def _inline_code(value: Any) -> str:
    return str(value).replace("`", "'").replace("\n", " ")


def _table_cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def _code_block(value: Any, language: str) -> str:
    text = str(value)
    longest_run = 0
    current_run = 0
    for character in text:
        if character == "`":
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 0
    fence = "`" * max(4, longest_run + 1)
    return f"{fence}{language}\n{text}\n{fence}"


def run(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser | None = None,
) -> Path:
    parser = parser or build_parser()
    return generate(args, parser)


def main() -> None:
    parser = build_parser()
    run(parser.parse_args(), parser)


if __name__ == "__main__":
    main()
