"""Merging entries that are certainly the same work.

A batch of a reading list will cite the same paper from several documents.
Merging them is only safe on **strong identity**, because the cost of the two
mistakes is not symmetric: showing one work twice is an annoyance, while
collapsing two different works destroys a reference the reader needed. So this
follows the rule the parsers follow - act on positive evidence, and where the
evidence is weak, do nothing.

Two entries are the same work when

* their DOIs match once normalised, which is an identifier and therefore
  decisive on its own; or
* their titles match once normalised **and** they carry the same year. A title
  alone is not enough: proceedings volumes, annual reports and chapters called
  "Introduction" repeat across years.

An entry with neither a DOI nor a title-and-year pair is never merged. That is
deliberate: a sparse entry is exactly the one whose identity is least certain.
"""

from __future__ import annotations

import re
import unicodedata

from papermint.models import Citation

#: Everything that is not a letter, digit or space, removed before two titles
#: are compared. Punctuation and casing differ between styles for the same
#: work, so comparing raw strings misses obvious duplicates.
_NOISE = re.compile(r"[^\w\s]+")

#: Runs of whitespace, collapsed so line wrapping cannot defeat a match.
_SPACES = re.compile(r"\s+")


def normalize_doi(value: str) -> str:
    """Reduce a DOI to a comparable form.

    Args:
        value: The DOI as parsed, possibly carrying a resolver prefix.

    Returns:
        The lowercase bare DOI, or an empty string.
    """
    cleaned = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]
    return cleaned.strip()


def normalize_title(value: str) -> str:
    """Reduce a title to a comparable form.

    Args:
        value: The title as parsed.

    Returns:
        A lowercase, accent-folded, punctuation-free version.
    """
    folded = unicodedata.normalize("NFKD", value)
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    return _SPACES.sub(" ", _NOISE.sub(" ", folded.lower())).strip()


def duplicate_key(citation: Citation) -> str | None:
    """Return a key identifying the work, or None when it cannot be matched.

    Args:
        citation: The citation to key.

    Returns:
        A stable key for entries carrying strong identity, otherwise None,
        which means "never merge this one".
    """
    doi = normalize_doi(citation.doi)
    if doi:
        return f"doi:{doi}"

    title = normalize_title(citation.title)
    if title and citation.year:
        return f"work:{title}|{citation.year}"
    return None


def _completeness(citation: Citation) -> tuple[int, float]:
    """Rank a citation so the fullest record survives a merge.

    Args:
        citation: The citation to rank.

    Returns:
        A ``(populated field count, confidence)`` pair, ordered.
    """
    fields = (
        citation.title,
        citation.year,
        citation.journal,
        citation.volume,
        citation.issue,
        citation.pages,
        citation.doi,
        citation.publisher,
    )
    populated = sum(1 for value in fields if value) + (1 if citation.authors else 0)
    return populated, citation.confidence


def _sources(citation: Citation) -> list[str]:
    """Return every file a citation is known to have come from.

    Args:
        citation: The citation to read.

    Returns:
        The source filenames, in order, without duplicates.
    """
    names = list(citation.merged_sources) or (
        [citation.source_file] if citation.source_file else []
    )
    return [name for name in names if name]


def deduplicate(citations: list[Citation]) -> tuple[list[Citation], int]:
    """Collapse entries that are certainly the same work.

    The surviving record is the most complete one, so a merge can only add
    information, never remove it. Every file a work appeared in is recorded on
    the survivor, because provenance is the one fact merging would otherwise
    destroy.

    Args:
        citations: Every citation in the run, in order.

    Returns:
        A ``(deduplicated citations, number removed)`` pair. Order follows each
        work's first appearance.
    """
    best: dict[str, Citation] = {}
    first_seen: dict[str, int] = {}
    unkeyed: list[tuple[int, Citation]] = []
    removed = 0

    for position, citation in enumerate(citations):
        key = duplicate_key(citation)
        if key is None:
            unkeyed.append((position, citation))
            continue

        if key not in best:
            best[key] = citation
            first_seen[key] = position
            continue

        removed += 1
        winner, loser = best[key], citation
        if _completeness(loser) > _completeness(winner):
            winner, loser = loser, winner

        sources = _sources(winner)
        for name in _sources(loser):
            if name not in sources:
                sources.append(name)
        best[key] = winner.model_copy(update={"merged_sources": sources})

    merged = [(first_seen[key], entry) for key, entry in best.items()] + unkeyed
    merged.sort(key=lambda pair: pair[0])
    return [citation for _position, citation in merged], removed


__all__ = ["deduplicate", "duplicate_key", "normalize_doi", "normalize_title"]
