"""Field-level accuracy against a labelled corpus.

Every other suite asks whether a specific behaviour is correct. This one asks
the question a user actually has: *how often is a parsed field right?*

The corpus in ``fixtures/labelled_references.json`` carries the expected value
of every field for every entry, including the fields that should come back
**empty**. That is what makes a false positive measurable: a parser that
invents a publisher takes a precision penalty here, where a suite of
``assert citation.title == ...`` tests would never notice.

Scoring is the standard one, per field:

* **true positive** - expected non-empty and parsed exactly equal to it
* **false positive** - parsed non-empty but wrong, or expected to be empty
* **false negative** - expected non-empty but parsed empty, or parsed wrongly

A wrong value counts once as a false positive and once as a false negative,
which is why both numbers fall on a single bad parse. Correct absence is not a
true positive; it is simply not counted, so a parser that returns nothing at
all scores zero rather than perfect.

The thresholds at the bottom are floors, not targets. They exist so a
heuristic change that trades accuracy for tidiness fails here instead of
shipping.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from papermint.models import Citation
from papermint.parsers.citation_parser import parse_citation

CORPUS_PATH = Path(__file__).parent / "fixtures" / "labelled_references.json"

#: The fields measured. ``authors`` is compared as an ordered list of
#: ``Family, Given`` strings; everything else is compared as text.
MEASURED_FIELDS = (
    "title",
    "authors",
    "year",
    "journal",
    "volume",
    "issue",
    "pages",
    "doi",
    "publisher",
)


def load_corpus() -> list[dict]:
    """Return every labelled reference.

    Returns:
        The corpus records, each with ``id``, ``class``, ``raw`` and
        ``expected``.
    """
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


@dataclass
class Tally:
    """Counts for one field, or for the corpus as a whole.

    Attributes:
        true_positive: Expected non-empty and parsed exactly.
        false_positive: Parsed non-empty but wrong, or expected to be empty.
        false_negative: Expected non-empty but missed or parsed wrongly.
        misses: Record ids that contributed a miss, so the report can name them.
    """

    true_positive: int = 0
    false_positive: int = 0
    false_negative: int = 0
    misses: list[str] = field(default_factory=list)

    @property
    def precision(self) -> float:
        """Return the share of produced values that were correct."""
        produced = self.true_positive + self.false_positive
        return self.true_positive / produced if produced else 1.0

    @property
    def recall(self) -> float:
        """Return the share of expected values that were produced."""
        wanted = self.true_positive + self.false_negative
        return self.true_positive / wanted if wanted else 1.0

    @property
    def f1(self) -> float:
        """Return the harmonic mean of precision and recall."""
        if not (self.precision and self.recall):
            return 0.0
        return 2 * self.precision * self.recall / (self.precision + self.recall)


def _parsed_value(citation: Citation, name: str) -> object:
    """Return one field from a parsed citation in comparable form.

    Args:
        citation: The parsed citation.
        name: The field being measured.

    Returns:
        A list of names for ``authors``, otherwise the stripped string.
    """
    if name == "authors":
        return [author.citation_name for author in citation.authors]
    return str(getattr(citation, name, "") or "").strip()


def score(records: list[dict]) -> tuple[dict[str, Tally], Tally]:
    """Measure the parser against the corpus.

    Args:
        records: The labelled records.

    Returns:
        A ``(per-field tallies, overall tally)`` pair.
    """
    per_field: dict[str, Tally] = defaultdict(Tally)
    overall = Tally()

    for record in records:
        citation = parse_citation(record["raw"])
        for name in MEASURED_FIELDS:
            wanted = record["expected"][name]
            got = _parsed_value(citation, name)
            tally = per_field[name]

            if wanted and got == wanted:
                tally.true_positive += 1
                overall.true_positive += 1
                continue

            if got:
                tally.false_positive += 1
                overall.false_positive += 1
            if wanted:
                tally.false_negative += 1
                overall.false_negative += 1
            if got or wanted:
                tally.misses.append(record["id"])
    return dict(per_field), overall


def report() -> str:
    """Render the measurement as a table.

    Printed by ``pytest -s -k accuracy_report`` and quoted in the README, so
    the published numbers are the ones the suite last measured.

    Returns:
        The report text.
    """
    records = load_corpus()
    per_field, overall = score(records)

    lines = [
        f"Labelled corpus: {len(records)} references, {len(MEASURED_FIELDS)} fields each",
        "",
        f"{'field':<12}{'precision':>11}{'recall':>9}{'F1':>8}",
        "-" * 40,
    ]
    for name in MEASURED_FIELDS:
        tally = per_field[name]
        lines.append(f"{name:<12}{tally.precision:>10.1%}{tally.recall:>9.1%}{tally.f1:>8.1%}")
    lines += [
        "-" * 40,
        f"{'overall':<12}{overall.precision:>10.1%}{overall.recall:>9.1%}{overall.f1:>8.1%}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# The gates
# ---------------------------------------------------------------------------


def test_the_corpus_covers_every_document_class():
    records = load_corpus()
    classes = {record["class"] for record in records}
    assert len(records) >= 25
    assert classes >= {
        "APA journal",
        "APA book",
        "MLA journal",
        "IEEE numbered",
        "Physics venue tail",
        "arXiv preprint",
        "Catalogue imprint",
        "Name forms",
        "Identifier",
    }


def test_every_record_labels_every_measured_field():
    # A record missing a label would drop silently out of the denominator and
    # flatter the score.
    for record in load_corpus():
        missing = set(MEASURED_FIELDS) - set(record["expected"])
        assert not missing, f"{record['id']} does not label {sorted(missing)}"


def test_field_precision_holds():
    # Precision is the honesty number: of the values the parser produced, how
    # many were right. Floored higher than recall on purpose - this project
    # would rather miss a field than invent one.
    _per_field, overall = score(load_corpus())
    assert overall.precision >= 0.90, report()


def test_field_recall_holds():
    _per_field, overall = score(load_corpus())
    assert overall.recall >= 0.80, report()


@pytest.mark.parametrize("name", ["title", "authors", "year", "doi"])
def test_the_identity_fields_hold_individually(name: str):
    # Title, authors and year are what a reference *is*; a DOI resolves it. An
    # aggregate can hide one of them collapsing, so each carries its own floor.
    per_field, _overall = score(load_corpus())
    tally = per_field[name]
    assert tally.precision >= 0.90, f"{name} precision {tally.precision:.1%}\n{report()}"


def test_a_fabricated_author_would_be_caught_here():
    # The guard on the guard. If the imprint rule regressed, catalogue-01 would
    # produce an author and this corpus would score it as a false positive.
    per_field, _overall = score(load_corpus())
    assert "catalogue-01" not in per_field["authors"].misses


def test_accuracy_report(capsys):
    # Not an assertion, a printout: `pytest -s -k accuracy_report` prints the
    # table quoted in the README.
    with capsys.disabled():
        print("\n" + report())
