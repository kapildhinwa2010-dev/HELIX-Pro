# HELIX-Pro

[![CI](https://github.com/kapildhinwa2010-dev/HELIX-Pro/actions/workflows/ci.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/HELIX-Pro/actions/workflows/ci.yml)
[![CodeQL](https://github.com/kapildhinwa2010-dev/HELIX-Pro/actions/workflows/codeql.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/HELIX-Pro/actions/workflows/codeql.yml)

Spiral-addressed byte memory with XOR parity and an integrity report.

## What it does

HelixMemory writes records across consecutive spiral cells (wrapping at
the edge), protects rows with XOR parity, and reports health via
integrity_report(). Pro additions over HELIX-Lib: full-record
read_record() round-trip and the report itself.

    from helix_pro import HelixMemory

    memory = HelixMemory(size=8, record_size=4)
    memory.write("alpha", b"\x01\x02\x03\x04")
    print(memory.read_record("alpha"))
    print(memory.integrity_report())

## API

- HelixMemory.write / read_record / read_cell / verify / corrupt /
  integrity_report / usage
- spiral_coordinates(size) - the deterministic spiral walk

## Honest results and limitations

- XOR parity detects odd numbers of flipped bits per row; even flips
  cancel and pass verification. Parity does not locate the bad cell, so
  integrity_report() can flag corrupt rows but cannot name or repair
  them. There is no automatic correction despite the Pro name.
- Keys hash to a start index by character sum: different keys can map to
  overlapping cell ranges and silently overwrite each other.
- Research toy for the spiral-addressing idea, not trustworthy storage.

## Status

Part of the kapildhinwa2010-dev toolkit experiments. CI and CodeQL run on
every push to main. License: MIT.
