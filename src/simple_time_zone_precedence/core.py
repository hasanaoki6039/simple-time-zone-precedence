"""Core logic for selecting the most specific time zone from a set of candidates.

The problem: given a location (identified by a string such as a city name or a
postal code) and several time zone candidates that could apply, choose the one
that is *most specific* to that location.  Specificity is defined by a simple,
predictable rule: the candidate whose ``location`` string is the longest common
prefix of the query location wins.  Ties are broken by the length of the time
zone name (shorter is more specific) and finally by lexicographic order of the
time zone name so that the result is deterministic.

This library deliberately avoids any external data sources or network calls.
It operates purely on the candidates you provide.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class TimeZoneCandidate:
    """A single time zone candidate for a location.

    Attributes:
        location: A string representing the location this candidate applies
            to.  It should be a prefix of the query location for the candidate
            to be considered.
        timezone: The IANA time zone name (e.g. ``"America/New_York"``).
    """

    location: str
    timezone: str


def select_most_specific(
    query: str, candidates: Iterable[TimeZoneCandidate]
) -> Optional[TimeZoneCandidate]:
    """Return the most specific candidate for *query*, or ``None`` if none match.

    A candidate matches if its ``location`` is a prefix of *query*.  Among
    matching candidates, the one with the longest ``location`` wins.  If two
    candidates have the same location length, the one with the shorter
    ``timezone`` string wins.  If still tied, the one whose ``timezone`` sorts
    first lexicographically wins.  This final tie-break ensures a deterministic
    result regardless of the order of *candidates*.

    Args:
        query: The location string to resolve.
        candidates: An iterable of :class:`TimeZoneCandidate` objects.

    Returns:
        The best matching candidate, or ``None`` if no candidate's location is
        a prefix of *query*.
    """
    best: Optional[TimeZoneCandidate] = None

    for candidate in candidates:
        if not query.startswith(candidate.location):
            continue

        if best is None:
            best = candidate
            continue

        # Compare by location length (longer is better).
        cand_len = len(candidate.location)
        best_len = len(best.location)
        if cand_len > best_len:
            best = candidate
            continue
        if cand_len < best_len:
            continue

        # Same location length: prefer shorter timezone name.
        cand_tz_len = len(candidate.timezone)
        best_tz_len = len(best.timezone)
        if cand_tz_len < best_tz_len:
            best = candidate
            continue
        if cand_tz_len > best_tz_len:
            continue

        # Same timezone length: lexicographic order of timezone name.
        if candidate.timezone < best.timezone:
            best = candidate

    return best
