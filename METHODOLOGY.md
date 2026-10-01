# How this example was measured

## Source and setup

The source was `C_major.mp3` from [Spotify's Basic Pitch TypeScript test data](https://github.com/spotify/basic-pitch-ts/tree/main/test_data). The measured clip duration was 10.0702040816 seconds. We used the MP3-to-MIDI converter at [MIDI From MP3](https://midifrommp3.com/) and saved its desktop Standard MIDI File export. The export was Type 1, with 480 ticks per beat, a timing track, and two nonempty note tracks named `Lower register` and `Upper register`. Those names mean pitch-range grouping, not instrument or hand recognition.

## MIDI events

We parsed the exported MIDI and sorted its note-on events by time, then track and in-track order. `data/c-major-note-ons.csv` contains the 15 measured note-on events, rounded to four decimal places. The last note-on was at about 8.54 seconds; the MIDI file ended at about 9.99 seconds. The sequence was C4 through C5 and back to C4. The desktop and mobile test exports had the same note-on sequence in this one test.

The reusable parser in `tools/midi_note_on_csv.py` can inspect another MIDI file. It reads the file's tempo events rather than assuming a fixed BPM; it does not infer note pitch from an MP3.

## Independent audio spot-check

For `data/c-major-spectral-check.csv`, we examined 0.18-second windows at 0.6-second intervals starting 0.4 seconds into the MP3. For each window we recorded the strongest FFT bin between 200 and 1200 Hz. The nearest equal-tempered MIDI pitch was calculated as `round(69 + 12*log2(frequency_hz/440))`. This is a simple sanity check on the pitch order, not a complete ground-truth transcription. It cannot establish note durations, polyphonic accuracy, or performance on other recordings.

## Limits

This is one short, clean scale. It does not show performance on chords, vocals, drums, full mixes, reverberation, or noisy recordings. The test files and measurement log are retained locally by the site operator; the MP3 and generated MIDI are not redistributed in this repository.
