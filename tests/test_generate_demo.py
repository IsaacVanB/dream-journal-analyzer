from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cli import generate_demo
from dream_analyzer.agent import AgentResponse, ToolExecution, ToolRequest


class GenerateDemoTests(unittest.TestCase):
    def response(self) -> AgentResponse:
        semantic_result = {
            "ok": True,
            "retrieval_method": "semantic",
            "dreams": [
                {
                    "dream_id": "shared|dream",
                    "date": "1/2/2024",
                    "distance": 0.1,
                    "text": "I found a hidden room.",
                },
                {
                    "dream_id": "semantic-only",
                    "date": "1/3/2024",
                    "distance": 0.2,
                    "text": "A door appeared behind a shelf.",
                },
            ],
        }
        keyword_result = {
            "ok": True,
            "retrieval_method": "bm25",
            "dreams": [
                {
                    "dream_id": "keyword-only",
                    "date": "1/4/2024",
                    "score": 2.0,
                    "text": "The words hidden room were on a sign.",
                },
                {
                    "dream_id": "shared|dream",
                    "date": "1/2/2024",
                    "score": 1.0,
                    "text": "I found a hidden room.",
                },
            ],
        }
        return AgentResponse(
            answer="Hidden rooms recur as unexpected spaces (shared|dream, 1/2/2024).",
            tool_executions=(
                ToolExecution(
                    name="search_dreams",
                    arguments={"query": "unexpected hidden spaces"},
                    result=semantic_result,
                    report_result=semantic_result,
                ),
                ToolExecution(
                    name="search_dreams_by_keywords",
                    arguments={"query": "hidden room"},
                    result=keyword_result,
                    report_result=keyword_result,
                ),
            ),
            unexecuted_tool_calls=(
                ToolRequest(name="search_dreams", arguments={"query": "rooms"}),
            ),
        )

    def test_report_contains_full_agent_demo(self) -> None:
        report = generate_demo.format_demo_markdown(
            "What do hidden rooms mean?",
            self.response(),
            settings={"Chat model": "qwen3:8b"},
        )

        self.assertIn("## User Question", report)
        self.assertIn("> What do hidden rooms mean?", report)
        self.assertIn("## Agent Tool Calls", report)
        self.assertIn('"query": "unexpected hidden spaces"', report)
        self.assertIn("Status: `not executed`", report)
        self.assertIn("## Dreams Retrieved", report)
        self.assertEqual(report.count("I found a hidden room."), 1)
        self.assertIn("## Final Dream Ranking", report)
        self.assertIn("| 1 | shared\\|dream |", report)
        self.assertIn("call 1: #1 (semantic)", report)
        self.assertIn("call 2: #2 (bm25)", report)
        self.assertIn("## Model Response", report)
        self.assertIn("Hidden rooms recur as unexpected spaces", report)

    def test_parser_defaults_to_readme_demo_output(self) -> None:
        args = generate_demo.build_parser().parse_args(["What recurs?"])

        self.assertEqual(args.output, generate_demo.DEFAULT_OUTPUT)

    def test_generate_uses_existing_agent_and_saves_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "demo.md"
            parser = generate_demo.build_parser()
            args = parser.parse_args(["What recurs?", "--output", str(output)])
            fake_agent = unittest.mock.Mock()
            fake_agent.answer.return_value = self.response()

            with patch.object(generate_demo.dream_agent, "build_agent", return_value=fake_agent):
                saved = generate_demo.generate(args, parser)

            self.assertEqual(saved, output)
            self.assertTrue(output.is_file())
            self.assertIn("# Dream Analyzer Demo", output.read_text(encoding="utf-8"))
            fake_agent.answer.assert_called_once()


if __name__ == "__main__":
    unittest.main()
