#!/usr/bin/env python3
"""Print note-on events from a Standard MIDI File as CSV (standard library only)."""

import csv
import io
import struct
import sys


def variable_int(data, position):
    value = 0
    for _ in range(4):
        if position >= len(data):
            raise ValueError("Truncated variable-length integer")
        byte = data[position]
        position += 1
        value = (value << 7) | (byte & 0x7f)
        if not byte & 0x80:
            return value, position
    raise ValueError("Variable-length integer is too long")


def parse_midi(content):
    if content[:4] != b"MThd" or len(content) < 14:
        raise ValueError("Not a Standard MIDI File")
    header_length = struct.unpack_from(">I", content, 4)[0]
    if header_length < 6 or len(content) < 8 + header_length:
        raise ValueError("Invalid MIDI header")
    midi_format, track_count, division = struct.unpack_from(">HHH", content, 8)
    if midi_format not in (0, 1) or not track_count:
        raise ValueError("Only MIDI format 0 and 1 are supported")
    if division & 0x8000 or not division:
        raise ValueError("SMPTE or zero time division is not supported")

    cursor = 8 + header_length
    notes = []
    tempos = [(0, 0, 500000)]  # tick, ordering, microseconds per beat
    for track in range(track_count):
        if content[cursor:cursor + 4] != b"MTrk" or cursor + 8 > len(content):
            raise ValueError("Missing MIDI track")
        length = struct.unpack_from(">I", content, cursor + 4)[0]
        data = content[cursor + 8:cursor + 8 + length]
        if len(data) != length:
            raise ValueError("Truncated MIDI track")
        cursor += 8 + length
        tick = position = order = 0
        running_status = None
        while position < len(data):
            delta, position = variable_int(data, position)
            tick += delta
            order += 1
            if position >= len(data):
                raise ValueError("Truncated MIDI event")
            if data[position] & 0x80:
                status = data[position]
                position += 1
                if status < 0xf0:
                    running_status = status
                else:
                    running_status = None
            elif running_status is not None:
                status = running_status
            else:
                raise ValueError("Data byte without running status")

            if status == 0xff:
                if position >= len(data):
                    raise ValueError("Truncated meta event")
                kind = data[position]
                position += 1
                size, position = variable_int(data, position)
                payload = data[position:position + size]
                if len(payload) != size:
                    raise ValueError("Truncated meta payload")
                position += size
                if kind == 0x51 and size == 3:
                    tempos.append((tick, track * 1000000 + order, int.from_bytes(payload, "big")))
            elif status in (0xf0, 0xf7):
                size, position = variable_int(data, position)
                position += size
                if position > len(data):
                    raise ValueError("Truncated SysEx event")
            elif 0x80 <= status <= 0xef:
                kind = status & 0xf0
                size = 1 if kind in (0xc0, 0xd0) else 2
                payload = data[position:position + size]
                if len(payload) != size or any(byte & 0x80 for byte in payload):
                    raise ValueError("Invalid channel event")
                position += size
                if kind == 0x90 and payload[1] > 0:
                    notes.append((tick, track, order, status & 0x0f, payload[0], payload[1]))
            else:
                raise ValueError("Unsupported MIDI system event")

    # Type-1 tempo events may live in a separate track. All tracks share ticks.
    tempos.sort(key=lambda row: (row[0], row[1]))
    notes.sort(key=lambda row: (row[0], row[1], row[2]))
    output = []
    tempo_index = 0
    current_tick = 0
    current_seconds = 0.0
    current_tempo = 500000
    for tick, track, _, channel, pitch, velocity in notes:
        while tempo_index < len(tempos) and tempos[tempo_index][0] <= tick:
            tempo_tick, _, new_tempo = tempos[tempo_index]
            current_seconds += (tempo_tick - current_tick) * current_tempo / division / 1000000
            current_tick = tempo_tick
            current_tempo = new_tempo
            tempo_index += 1
        seconds = current_seconds + (tick - current_tick) * current_tempo / division / 1000000
        output.append((seconds, track, channel, pitch, note_name(pitch), velocity))
    return output


def note_name(pitch):
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return names[pitch % 12] + str(pitch // 12 - 1)


def main(path, stream):
    with open(path, "rb") as source:
        rows = parse_midi(source.read())
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(("time_seconds", "track", "channel", "midi_pitch", "note_name", "velocity"))
    for seconds, track, channel, pitch, name, velocity in rows:
        writer.writerow((f"{seconds:.4f}", track, channel, pitch, name, velocity))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python midi_note_on_csv.py your-file.mid > note-ons.csv")
    try:
        main(sys.argv[1], sys.stdout)
    except (OSError, ValueError) as error:
        raise SystemExit(str(error))
