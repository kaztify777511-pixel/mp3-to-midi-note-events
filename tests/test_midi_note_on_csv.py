import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from midi_note_on_csv import parse_midi


def smf(track_bytes):
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480)
    track = b"MTrk" + struct.pack(">I", len(track_bytes)) + track_bytes
    return header + track


class ParserTests(unittest.TestCase):
    def test_tempo_change_and_running_status(self):
        # First event at 480 ticks under 120 BPM; second at 960 under 60 BPM.
        events = (
            b"\x00\xff\x51\x03\x07\xa1\x20"  # 500,000 us/beat
            b"\x83\x60\x90\x3c\x40"             # tick 480: C4
            b"\x00\xff\x51\x03\x0f\x42\x40"  # 1,000,000 us/beat
            b"\x83\x60\x90\x3e\x45"                 # tick 960: D4
            b"\x00\x40\x42"                          # E4, running status
            b"\x00\x3e\x00"                          # velocity-zero note-on is note-off
            b"\x00\xff\x2f\x00"
        )
        rows = parse_midi(smf(events))
        self.assertEqual([row[0] for row in rows], [0.5, 1.5, 1.5])
        self.assertEqual([row[3:6] for row in rows], [(60, "C4", 64), (62, "D4", 69), (64, "E4", 66)])

    def test_rejects_invalid_file(self):
        with self.assertRaises(ValueError):
            parse_midi(b"not MIDI")


if __name__ == "__main__":
    unittest.main()
