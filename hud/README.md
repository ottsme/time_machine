# Glass HUD prototype

Live: https://ottsme.github.io/time_machine/hud/

A working mockup of the new in-trip panels: a small glass panel on top (heading, date, trip bar, next-event bar) and a glass dock at the bottom (stop, pause, Map / Text / Image). Everything else on screen is the picture or the tunnel.

- On a phone the screen fills the whole display. Tap the top panel to open the tune sheet.
- On a large screen it shows a 390 × 844 phone frame with the tune panel beside it.
- The tunnel scene uses the trip simulator's shader and time-mark logic, looping the real stretch from The Methuselah star (13.25 Ga) to The first quasar (13.1 Ga).
- Tuned values are kept on the device. "Copy values" puts the current numbers on the clipboard for implementation.
- The dinosaur picture is cropped from a screenshot of the current build, so it is softer and not full 9:20. The Earth picture is the real 9:20 file.
