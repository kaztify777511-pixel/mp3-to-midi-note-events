# MP3-to-MIDI note-event example

This repository contains a small, inspectable transcription example: note-on events exported from a 10.07-second C-major MP3, plus an independent frequency spot-check. It is meant for checking *what a MIDI file contains*, not for claiming a general transcription accuracy score.

The browser converter used for this example is [MIDI From MP3](https://midifrommp3.com/); the full [test write-up](https://midifrommp3.com/mp3-to-midi-c-major-test) explains how to listen back and inspect the result.

## Files

- `data/c-major-note-ons.csv`: ordered note-on times and pitches parsed from the desktop MIDI export.
- `data/c-major-spectral-check.csv`: independent strongest-frequency samples taken from the source audio.
- `tools/midi_note_on_csv.py`: a dependency-free Standard MIDI File parser that exports note-on events to CSV. It supports format 0 or 1, running status, and tempo changes; SMPTE time division is not supported.
- `METHODOLOGY.md`: provenance, measurement steps, and limitations.

## Use the parser

```sh
python tools/midi_note_on_csv.py your-file.mid > note-ons.csv
```

The CSV columns are `time_seconds,track,channel,midi_pitch,note_name,velocity`. MIDI pitch 60 is C4 (middle C). The parser reports `Note On` messages with nonzero velocity; velocity-zero `Note On` messages are note-offs and are omitted. Track numbers start at 0.

## Reproduce this example

Download the source clip from the upstream Basic Pitch test-data collection (linked in `METHODOLOGY.md`), convert it on the site, then run the parser on the resulting MIDI. The generated MIDI and source MP3 are not redistributed here. `data/c-major-note-ons.csv` was exported from the measured desktop MIDI file with this parser; event times are rounded to four decimal places.

## License

Original repository code and text are available under the MIT license in `LICENSE`. The CSV files report measured facts. This license does not cover the upstream MP3 or any third-party model or code.
