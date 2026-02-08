"""Tests for rendering/svg_loader.py — SVG parsing and caching."""

import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock

import src.rendering.svg_loader as svg_loader_mod
from src.rendering.svg_loader import load_svg_paths, _parse_svg_entries, _build_result


def _make_svg_xml(path_d, fill_rule="nonzero"):
    """Build a minimal SVG XML string with one <path> element."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        f'<path d="{path_d}" fill-rule="{fill_rule}"/>'
        "</svg>"
    )


def _mock_parse(svg_map):
    """Return a side_effect function for ET.parse that uses svg_map.

    svg_map: dict mapping filename (e.g. "default.svg") to SVG XML string.
    """
    def _parse(filepath):
        fname = filepath.rsplit("/", 1)[-1]
        xml_str = svg_map.get(fname, '<svg xmlns="http://www.w3.org/2000/svg"/>')
        root = ET.fromstring(xml_str)
        tree = MagicMock()
        tree.getroot.return_value = root
        return tree
    return _parse


# Sample SVG data for tests
_SAMPLE_SVGS = {
    "bolt.svg": _make_svg_xml("M10 0L20 10", "evenodd"),
    "default.svg": _make_svg_xml("M0 0L10 10"),
    "ex.svg": _make_svg_xml("M5 5L15 15"),
}

_LISTDIR_RESULT = ["bolt.svg", "default.svg", "ex.svg", "readme.txt"]


class TestParseSvgEntries:
    """Test the raw SVG parsing step."""

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_parses_all_svg_files(self, mock_listdir, mock_parse):
        entries = _parse_svg_entries()
        # Should have 3 entries (skips readme.txt)
        assert len(entries) == 3

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_entries_have_correct_structure(self, mock_listdir, mock_parse):
        entries = _parse_svg_entries()
        # Each entry: (key, spoken_name, path_data, fill_rule)
        for entry in entries:
            assert len(entry) == 4
            key, spoken_name, d, fill_rule = entry
            assert isinstance(key, str)
            assert isinstance(spoken_name, str)
            assert isinstance(d, str)
            assert fill_rule in ("nonzero", "evenodd")

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_maps_hat_names(self, mock_listdir, mock_parse):
        entries = _parse_svg_entries()
        names = {e[0]: e[1] for e in entries}
        # HAT_NAMES maps "default" -> "dot", "bolt" -> "bolt", "ex" -> "ex"
        assert names["default"] == "dot"
        assert names["bolt"] == "bolt"
        assert names["ex"] == "ex"

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_preserves_fill_rule(self, mock_listdir, mock_parse):
        entries = _parse_svg_entries()
        by_key = {e[0]: e for e in entries}
        assert by_key["bolt"][3] == "evenodd"
        assert by_key["default"][3] == "nonzero"

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_sorted_order(self, mock_listdir, mock_parse):
        entries = _parse_svg_entries()
        keys = [e[0] for e in entries]
        assert keys == ["bolt", "default", "ex"]

    @patch.object(ET, "parse", side_effect=_mock_parse({}))
    @patch("os.listdir", return_value=["not_svg.txt"])
    def test_no_svg_files_returns_empty(self, mock_listdir, mock_parse):
        entries = _parse_svg_entries()
        assert entries == []

    @patch.object(ET, "parse", side_effect=_mock_parse({
        "empty.svg": '<svg xmlns="http://www.w3.org/2000/svg"><path d=""/></svg>',
    }))
    @patch("os.listdir", return_value=["empty.svg"])
    def test_skips_empty_path_data(self, mock_listdir, mock_parse):
        entries = _parse_svg_entries()
        assert entries == []


class TestBuildResult:
    """Test the ordering logic for default_first."""

    def _sample_entries(self):
        return [
            ("bolt", "bolt", "M10 0L20 10", "evenodd"),
            ("default", "dot", "M0 0L10 10", "nonzero"),
            ("ex", "ex", "M5 5L15 15", "nonzero"),
        ]

    def test_default_first_false(self):
        result = _build_result(self._sample_entries(), default_first=False)
        # All entries in original sorted order, no reordering
        names = [r[0] for r in result]
        assert names == ["bolt", "dot", "ex"]

    def test_default_first_true(self):
        result = _build_result(self._sample_entries(), default_first=True)
        # "dot" (from "default" key) should be first
        names = [r[0] for r in result]
        assert names[0] == "dot"
        assert "bolt" in names
        assert "ex" in names
        assert len(result) == 3

    def test_result_tuples_are_three_element(self):
        result = _build_result(self._sample_entries(), default_first=False)
        for entry in result:
            assert len(entry) == 3
            spoken_name, d, fill_rule = entry
            assert isinstance(spoken_name, str)
            assert isinstance(d, str)

    def test_no_default_entry(self):
        entries = [
            ("bolt", "bolt", "M10 0", "nonzero"),
            ("ex", "ex", "M5 5", "nonzero"),
        ]
        result = _build_result(entries, default_first=True)
        # No default key, so no reordering
        names = [r[0] for r in result]
        assert names == ["bolt", "ex"]


class TestLoadSvgPathsCaching:
    """Test that load_svg_paths caches results and avoids re-parsing."""

    def setup_method(self):
        """Clear cache before each test."""
        svg_loader_mod._cache.clear()

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_returns_list_of_tuples(self, mock_listdir, mock_parse):
        result = load_svg_paths()
        assert isinstance(result, list)
        assert all(isinstance(t, tuple) and len(t) == 3 for t in result)

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_default_first_false(self, mock_listdir, mock_parse):
        result = load_svg_paths(default_first=False)
        names = [r[0] for r in result]
        # "dot" should be in sorted position (between bolt and ex)
        assert names == ["bolt", "dot", "ex"]

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_default_first_true(self, mock_listdir, mock_parse):
        result = load_svg_paths(default_first=True)
        names = [r[0] for r in result]
        assert names[0] == "dot"

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_caching_prevents_reparse(self, mock_listdir, mock_parse):
        """After first call, subsequent calls should not re-parse SVGs."""
        load_svg_paths(default_first=False)
        initial_parse_count = mock_parse.call_count

        # Call again — should use cache, no additional parses
        load_svg_paths(default_first=False)
        load_svg_paths(default_first=True)
        load_svg_paths(default_first=False)

        assert mock_parse.call_count == initial_parse_count

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_both_variants_cached_on_first_call(self, mock_listdir, mock_parse):
        """First call populates cache for both True and False variants."""
        load_svg_paths(default_first=False)
        assert True in svg_loader_mod._cache
        assert False in svg_loader_mod._cache

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_consistent_results_across_calls(self, mock_listdir, mock_parse):
        """Repeated calls return the same data."""
        r1 = load_svg_paths(default_first=True)
        r2 = load_svg_paths(default_first=True)
        assert r1 == r2

        r3 = load_svg_paths(default_first=False)
        r4 = load_svg_paths(default_first=False)
        assert r3 == r4

    @patch.object(ET, "parse", side_effect=_mock_parse(_SAMPLE_SVGS))
    @patch("os.listdir", return_value=_LISTDIR_RESULT)
    def test_listdir_called_once(self, mock_listdir, mock_parse):
        """os.listdir should only be called once across all calls."""
        load_svg_paths(default_first=False)
        load_svg_paths(default_first=True)
        load_svg_paths(default_first=False)
        assert mock_listdir.call_count == 1
