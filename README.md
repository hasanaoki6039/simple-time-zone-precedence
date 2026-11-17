# simple-time-zone-precedence

Select the most specific time zone for a location from multiple candidates.

```python
from simple_time_zone_precedence import TimeZoneCandidate, select_most_specific

candidates = [
    TimeZoneCandidate("New York", "America/New_York"),
    TimeZoneCandidate("New York City", "America/New_York"),
    TimeZoneCandidate("", "UTC"),
]

best = select_most_specific("New York, NY", candidates)
print(best.timezone)  # America/New_York
```

## Why this exists

When resolving a location to a time zone, you often have several candidates that
could apply: a broad fallback (e.g. `""` for UTC), a country-level zone, and a
city-level zone.  Picking the wrong one silently shifts timestamps.  This
library makes the choice explicit and deterministic.

The trade-off: specificity is defined purely by the length of the matching
location prefix.  That is simple and predictable, but it means you must supply
candidates whose `location` strings are meaningful prefixes of your queries.
It does not inspect time zone databases or geographic hierarchies.

## Awkward edge

An empty `location` (`""`) is a prefix of every query, so it acts as a
catch-all.  It will only be selected if no other candidate matches, because any
non-empty match has a longer location.  This is intentional: it lets you provide
a fallback without special-casing it in your code.

## API

- `TimeZoneCandidate(location: str, timezone: str)`
- `select_most_specific(query: str, candidates: Iterable[TimeZoneCandidate]) -> Optional[TimeZoneCandidate]`

Ties are broken first by shorter `timezone` name, then by lexicographic order
of the `timezone` name, so the result does not depend on the order of the input.
