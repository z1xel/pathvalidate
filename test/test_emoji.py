"""Tests for optional emoji removal."""

from pathlib import Path

import pytest

from pathvalidate import (
    FileNameSanitizer,
    FilePathSanitizer,
    sanitize_filename,
    sanitize_filepath,
)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("photo_😀.png", "photo_.png"),
        ("family_👨‍👩‍👧.jpg", "family_.jpg"),
        ("flag_🇯🇵.png", "flag_.png"),
    ],
)
def test_filename_emoji(source, expected):
    assert sanitize_filename(source, remove_emoji=True) == expected


def test_default_behavior_is_unchanged():
    assert sanitize_filename("photo_😀.png") == "photo_😀.png"
    assert sanitize_filepath("dir_😀/photo_🔥.png", platform="linux") == "dir_😀/photo_🔥.png"


def test_sanitizer_classes():
    assert FileNameSanitizer(remove_emoji=True).sanitize("hello_😀.txt") == "hello_.txt"
    assert (
        FilePathSanitizer(platform="linux", remove_emoji=True).sanitize("dir_😀/file_🔥.txt")
        == "dir_/file_.txt"
    )


def test_path_input_preserves_type():
    result = sanitize_filename(Path("photo_😀.png"), remove_emoji=True)
    assert result == Path("photo_.png")
    assert isinstance(result, Path)


@pytest.mark.parametrize("platform", ["linux", "windows"])
def test_filepath_emoji(platform):
    result = sanitize_filepath("images/dir_😀/photo_🔥.png", platform=platform, remove_emoji=True)
    expected = r"images\dir_\photo_.png" if platform == "windows" else "images/dir_/photo_.png"
    assert result == expected


def test_windows_keycap_emoji():
    assert sanitize_filename("file_*️⃣.txt", platform="windows", remove_emoji=True) == "file_.txt"
    assert (
        sanitize_filepath("dir/file_1️⃣.txt", platform="windows", remove_emoji=True)
        == r"dir\file_.txt"
    )


def test_preserve_nonemoji_text():
    assert (
        sanitize_filename("résumé_日本語_2026.txt", remove_emoji=True) == "résumé_日本語_2026.txt"
    )
    assert sanitize_filename("©_™_↔.txt", remove_emoji=True) == "©_™_↔.txt"
    assert sanitize_filename("©️_™️_↔️.txt", remove_emoji=True) == "__.txt"
    assert sanitize_filename("a\u200db.txt", remove_emoji=True) == "a\u200db.txt"


def test_remove_joiners_attached_to_emoji():
    assert sanitize_filename("a\u200d😀\u200db.txt", remove_emoji=True) == "ab.txt"


def test_emoji_only_filename():
    assert sanitize_filename("😀", remove_emoji=True) == ""


@pytest.mark.parametrize("platform", ["linux", "windows"])
def test_emoji_only_directory(platform):
    result = sanitize_filepath("docs/😀/report.txt", platform=platform, remove_emoji=True)
    expected = r"docs\_\report.txt" if platform == "windows" else "docs/_/report.txt"
    assert result == expected


def test_emoji_removal_does_not_create_parent_directory():
    assert (
        sanitize_filepath("docs/😀../report.txt", platform="linux", remove_emoji=True)
        == "docs/_/report.txt"
    )


def test_emoji_variation_selector_does_not_remove_punctuation():
    assert sanitize_filename("a.\ufe0fb.txt", remove_emoji=True) == "a.b.txt"
    assert sanitize_filename("a-\ufe0fb.txt", remove_emoji=True) == "a-b.txt"
    assert sanitize_filename("a1\ufe0fb.txt", remove_emoji=True) == "a1b.txt"
    assert sanitize_filename("a©\ufe0fb.txt", remove_emoji=True) == "ab.txt"
    assert sanitize_filename("🖐🏽.txt", remove_emoji=True) == ".txt"
