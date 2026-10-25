# Glass HUD prototype

Live: https://ottsme.github.io/time_machine/hud/

A working mockup of the new in-trip panels: a small glass panel on top (heading, date, trip bar, next-event bar) and a glass dock at the bottom (stop, pause, Map / Text / Image). Everything else on screen is the picture or the tunnel.

- On a phone the screen fills the whole display. Tap the top panel to open the tune sheet.
- On a large screen it shows a 390 × 844 phone frame with the tune panel beside it.
- The tunnel scene uses the trip simulator's shader and time-mark logic, looping the real stretch from The Methuselah star (13.25 Ga) to The first quasar (13.1 Ga).
- Tuned values are kept on the device. "Copy values" puts the current numbers on the clipboard for implementation.
- Both event pictures are the real 9:20 files.

## v9: Map and Text modes

- **Map and Text run a drive through the whole Universe deck** (186 km at a steady 90 km/h, narration at 14 characters a second). Pause stops it; Stop restarts it. Position slider and jump buttons are in the Layout panel. Image mode keeps the scene picker.
- **Map:** follow-car and whole-road cameras, pan, pinch, wheel and double-tap zoom, compass, re-centre; all pins visible, only the next A-card labelled; tap a passed pin to reopen its card. The map itself is a hand-drawn stand-in for the real Google map.
- **Text:** logbook of passed cards, current card highlighted sentence by sentence, Next stop line, Back to now.
- **Card texts are not in this repo** (it is public). `deck_universe.js` holds only positions, headings, dates, tiers and text lengths. Load the private texts file once per device with **Load card texts**; it stays in that browser. Without it, only *The age of dinosaurs* and *Modern Earth* show their text.
