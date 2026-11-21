# History Clock — simulator

Watch face simulator for the History Clock: the time is always a year (16:32 = AD 1632).
Built for a Galaxy S25+ held upright; install it from Chrome with "Add to home screen" and it opens full screen.

Live: https://ottsme.github.io/time_machine/clock/

- `index.html` — the face and the tuning sheet (Time, Look, Colours, Layout, Review). One edit button, bottom right.
- `data.js` — **sample texts only** (21 years); other years show placeholder lines. The full texts are private (repository `history_clock_data`, with the watch face and its tools); load them with Review → Load texts from file. They stay in that browser and are never published.
- Backgrounds are drawn in code: colours drift through keyframe years; each sub-period has its own frieze (laurels, meander, mosaic, knotwork, tracery, astrolabe limb, cogs, drafting scale, orbits) and faint field texture, cross-fading over the last minutes before a change.
- The frieze rule: the event text and the complication always stay inside the frieze. The text takes up to three lines, each as wide as the frieze allows at its height; line breaks are balanced, and shorter texts are centred in the three-line space.
- One complication by default: a pill at 6 o'clock with the day and date (Layout → Complications; the old two circles remain as "arc").
- Layout → Outlines draws every element's box, the frieze and the clearance line (simulator only).
- Only the future keeps a field texture (the starfield); every other period has its frieze alone.
- A soft seconds glow travels once round the frieze every minute (Look → Seconds; off in always-on mode).
- Settings and review flags are stored in the browser only (localStorage keys `hc-sim`, `hc-time`, `hc-flags`). The installed app and a Chrome tab may keep separate copies: use Review → Save notes to file / Load notes from file to back them up or move them.

## Updating the texts

The texts, the Excel and the watch face build live in the private repository `ottsme/history_clock_data`.

    python3 -I tools/xlsx_to_data.py History_Clock_4_Claude.xlsx > data.js

Future years get a label automatically: SCHEDULED (certain), PERHAPS (guesses, plans, anything marked "(?)"),
SCI-FI (fiction) or none (anniversaries). Move a year with the OVERRIDE table at the top of the script.
