"""Tests for HELIX-Pro: record round-trip, parity, integrity report."""

import pytest

from helix_pro import HelixMemory, spiral_coordinates


def test_record_roundtrip():
    memory = HelixMemory(size=8, record_size=4)
    memory.write("alpha", b"\x01\x02\x03\x04")
    assert memory.read_record("alpha") == b"\x01\x02\x03\x04"


def test_verify_detects_corruption():
    memory = HelixMemory(size=8, record_size=4)
    memory.write("alpha", b"\x01\x02\x03\x04")
    assert memory.verify() is True
    memory.corrupt("alpha")
    assert memory.verify() is False


def test_integrity_report_clean():
    memory = HelixMemory(size=8, record_size=4)
    memory.write("alpha", b"\x01\x02\x03\x04")
    report = memory.integrity_report()
    assert report["parity_ok"] is True
    assert report["corrupt_rows"] == []
    assert report["stored_keys"] == 1


def test_integrity_report_after_corruption():
    memory = HelixMemory(size=8, record_size=4)
    memory.write("alpha", b"\x01\x02\x03\x04")
    memory.corrupt("alpha")
    report = memory.integrity_report()
    assert report["parity_ok"] is False
    assert len(report["corrupt_rows"]) >= 1


def test_write_validates():
    memory = HelixMemory(size=8, record_size=4)
    with pytest.raises(ValueError):
        memory.write("a", b"wrong-length")


def test_spiral_covers_grid_once():
    coords = spiral_coordinates(5)
    assert len(coords) == 25 and len(set(coords)) == 25
