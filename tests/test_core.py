import unittest

from simple_time_zone_precedence import TimeZoneCandidate, select_most_specific


class TestSelectMostSpecific(unittest.TestCase):
    def test_no_candidates(self):
        self.assertIsNone(select_most_specific("anywhere", []))

    def test_no_match(self):
        candidates = [TimeZoneCandidate("New York", "America/New_York")]
        self.assertIsNone(select_most_specific("Los Angeles", candidates))

    def test_single_match(self):
        candidates = [TimeZoneCandidate("New York", "America/New_York")]
        result = select_most_specific("New York, NY", candidates)
        self.assertEqual(result, candidates[0])

    def test_longest_location_wins(self):
        candidates = [
            TimeZoneCandidate("New", "America/New_York"),
            TimeZoneCandidate("New York", "America/New_York"),
        ]
        result = select_most_specific("New York, NY", candidates)
        self.assertEqual(result, candidates[1])

    def test_tie_on_location_length_shorter_timezone_wins(self):
        # Both locations have length 3 and match "abc".
        # "A" (length 1) is shorter than "AA" (length 2).
        candidates = [
            TimeZoneCandidate("abc", "AA"),
            TimeZoneCandidate("abc", "A"),
        ]
        result = select_most_specific("abc", candidates)
        self.assertEqual(result, candidates[1])

    def test_tie_on_location_and_timezone_length_lexicographic(self):
        # Both locations length 3, both timezones length 2.
        # "AA" < "BB" lexicographically.
        candidates = [
            TimeZoneCandidate("abc", "BB"),
            TimeZoneCandidate("abc", "AA"),
        ]
        result = select_most_specific("abc", candidates)
        self.assertEqual(result, candidates[1])

    def test_order_independence(self):
        candidates = [
            TimeZoneCandidate("abc", "BB"),
            TimeZoneCandidate("abc", "AA"),
            TimeZoneCandidate("ab", "CC"),
        ]
        # Expected: "abc" beats "ab" (longer location).
        # Between the two "abc" candidates, "AA" wins.
        expected = TimeZoneCandidate("abc", "AA")
        self.assertEqual(select_most_specific("abc", candidates), expected)
        self.assertEqual(select_most_specific("abc", reversed(candidates)), expected)

    def test_exact_match_beats_longer_non_prefix(self):
        candidates = [
            TimeZoneCandidate("New York", "America/New_York"),
            TimeZoneCandidate("New York City", "America/New_York"),
        ]
        # "New York City" is not a prefix of "New York", so it does not match.
        result = select_most_specific("New York", candidates)
        self.assertEqual(result, candidates[0])

    def test_empty_location_matches_everything(self):
        # An empty location is a prefix of any string, so it is a valid
        # fallback candidate.  It should lose to any non-empty matching prefix.
        candidates = [
            TimeZoneCandidate("", "UTC"),
            TimeZoneCandidate("New", "America/New_York"),
        ]
        result = select_most_specific("New York", candidates)
        self.assertEqual(result, candidates[1])

    def test_empty_query_matches_only_empty_location(self):
        candidates = [
            TimeZoneCandidate("", "UTC"),
            TimeZoneCandidate("New", "America/New_York"),
        ]
        result = select_most_specific("", candidates)
        self.assertEqual(result, candidates[0])

    def test_duplicate_candidates(self):
        c = TimeZoneCandidate("abc", "AA")
        candidates = [c, c]
        self.assertEqual(select_most_specific("abc", candidates), c)

    def test_generator_input(self):
        candidates = (TimeZoneCandidate("a", "A"), TimeZoneCandidate("ab", "B"))
        result = select_most_specific("abc", candidates)
        self.assertEqual(result, TimeZoneCandidate("ab", "B"))


if __name__ == "__main__":
    unittest.main()
