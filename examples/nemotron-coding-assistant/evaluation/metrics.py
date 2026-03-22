"""
Coding-specific evaluation metrics.

Provides pass@k, syntax correctness, code style, BLEU,
and execution success metrics for evaluating code generation models.
"""

import ast
import math
from typing import List, Optional

from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


class CodingMetrics:
    """
    Computes coding evaluation metrics for generated code samples.
    """

    def pass_at_k(
        self,
        n_samples: List[int],
        n_correct: List[int],
        k: int = 1,
    ) -> float:
        """
        Compute pass@k metric (unbiased estimator from the Codex paper).

        Args:
            n_samples: Number of generated samples per problem
            n_correct: Number of correct samples per problem
            k: k value for pass@k
        """
        if not n_samples:
            return 0.0

        total = 0.0
        count = 0
        for n, c in zip(n_samples, n_correct):
            if n < k:
                continue
            if c == 0:
                total += 0.0
            elif c >= n:
                total += 1.0
            else:
                total += 1.0 - math.comb(n - c, k) / math.comb(n, k)
            count += 1

        return total / max(count, 1)

    def syntax_correctness(self, code: str, language: str = "python") -> bool:
        """Check if code is syntactically correct."""
        if language != "python":
            return True  # only Python AST check for now

        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def syntax_correctness_rate(
        self,
        code_samples: List[str],
        language: str = "python",
    ) -> float:
        """Compute fraction of syntactically correct samples."""
        if not code_samples:
            return 0.0
        correct = sum(1 for c in code_samples if self.syntax_correctness(c, language))
        return correct / len(code_samples)

    def code_bleu(
        self,
        generated: List[str],
        references: List[str],
    ) -> float:
        """
        Compute CodeBLEU (simplified BLEU over code tokens).

        This is a simplified version; for full CodeBLEU use the
        codebleu package.
        """
        if not generated or not references:
            return 0.0

        total_score = 0.0
        for gen, ref in zip(generated, references):
            gen_tokens = self._tokenize_code(gen)
            ref_tokens = self._tokenize_code(ref)
            if not ref_tokens:
                continue
            matches = sum(1 for t in gen_tokens if t in set(ref_tokens))
            precision = matches / max(len(gen_tokens), 1)
            length_penalty = min(1.0, len(gen_tokens) / max(len(ref_tokens), 1))
            total_score += precision * length_penalty

        return total_score / max(len(generated), 1)

    def execution_success_rate(
        self,
        results: List[bool],
    ) -> float:
        """Compute the fraction of successfully executing code samples."""
        if not results:
            return 0.0
        return sum(1 for r in results if r) / len(results)

    def average_code_length(self, code_samples: List[str]) -> float:
        """Compute average length of generated code in tokens."""
        if not code_samples:
            return 0.0
        total = sum(len(self._tokenize_code(c)) for c in code_samples)
        return total / len(code_samples)

    def style_adherence(
        self,
        code: str,
        language: str = "python",
    ) -> float:
        """
        Score code style adherence (0-1).

        Checks basic style rules like line length, naming conventions, etc.
        """
        if language != "python":
            return 1.0

        score = 1.0
        lines = code.split("\n")

        long_lines = sum(1 for line in lines if len(line) > 100)
        if lines:
            long_ratio = long_lines / len(lines)
            score -= long_ratio * 0.3

        if "  " in code and "\t" in code:
            score -= 0.2

        has_docstring = '"""' in code or "'''" in code
        has_functions = "def " in code
        if has_functions and not has_docstring:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def _tokenize_code(self, code: str) -> List[str]:
        """Simple code tokenizer that splits on whitespace and punctuation."""
        import re
        tokens = re.findall(r'[a-zA-Z_]\w*|[^\s\w]', code)
        return tokens
