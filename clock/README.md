# History Clock — simulator

Watch face simulator for the History Clock: the time is always a year (16:32 = AD 1632).
Built for a Galaxy S25+ held upright; install it from Chrome with "Add to home screen" and it opens full screen.

Live: https://ottsme.github.io/time_machine/clock/

- `index.html` — the face and the tuning sheet (Time, Look, Layout, Review). One edit button, bottom right.
- `data.js` — event texts by year. Years not in the file show placeholder lines. Replace this file with the real list.
- Backgrounds are drawn in code: colours drift through keyframe years, patterns change by sub-period and cross-fade over the last minutes before a change.
- Settings and review flags are stored on the phone only (localStorage keys `hc-sim`, `hc-time`, `hc-flags`).
