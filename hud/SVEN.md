# Glass HUD — how to build it in React Native

*For Sven. Version 3.1, 2026-10-28 (first version 2026-10-19). Reference prototype: https://ottsme.github.io/time_machine/hud/ (code in `hud/index.html`, Map and Text modes in `hud/modes.js`).*

**Changed in version 3.1 (2026-10-28):** the map's colours and a starting Google style added as M-11. Nothing else changed.

**Changed in version 3:** the Map and Text modes are decided (Ott, 2026-10-25). See "Map mode" and "Text mode" below.

**Changed in version 2:** what the top panel shows was decided after test drives (Ott, 2026-10-25). The heading leaves with its event and is replaced by the next event, and long headings scroll instead of wrapping. See "What the top panel shows" below. The look (fonts, sizes, colours, buttons) is still being tuned.

## What changes

The picture (or the tunnel) fills the whole screen, edge to edge. No frame, no rivets. On top of it float two panels, and nothing else:

- **Top panel:** one text line (see below), then two thin bars: trip progress and progress to the next event. NEXT EVENT, ETA, metres and the PROG/NEXT labels are dropped.
- **Bottom dock:** stop (press and hold), pause, and Map / Text / Image, as five separate keys.
- **Panels are tinted glass:** the picture and the tunnel stay visible behind them. Buttons and the text card are solid.

## What the top panel shows

These rules follow the playback rulebook (`20261018_Playback_Rulebook_for_Sven.md`, v1.2); R-numbers there.

- **H-1. During an event:** the event's heading on the left and its display date on the right (e.g. `4.6 Ga`). Strip the trailing full stop from the heading and the "(bln years ago)" part from the date.
- **H-2. The heading stays as long as its event is still with the traveller:** while its picture is visible (opacity above 0) **or** its narration is still playing (R-6.5: the voice may outlive the picture). It changes only when **both** are over.
- **H-3. Then the slot shows the next stop,** as one line: `Next: [next event's heading], [its display date]`, e.g. `Next: The Proterozoic, 2.5 Ga`. There is no separate date on the right in this state. Like a "next stop" display on a bus or a train.
- **H-4. A newly fired event always takes the slot.** When an event fires (R-7.1.1), its heading and date replace whatever is shown. In a no-filler gap (R-5.4) the slot therefore goes straight from one heading to the next, with no "Next" in between.
- **H-5. "Next" means the next event not yet fired or skipped.** If an event is skipped while the previous narration plays (R-7.2), the slot was still showing the previous heading, so the traveller never sees "Next" for an event that is then dropped. After the skip, "Next" names the one after it.
- **H-6. A skipped event never appears in the slot.**
- **H-7. Ignition:** event 0's heading appears with its picture. **Arrival:** the arrival card's heading and date (`We have arrived. Today.` / `Today`). Nothing comes after it.
- **H-8. No live road date in the panel.** The traveller's actual time is shown by the time marks flying in the tunnel (R-11.5). Ott: they must float often enough and big enough to carry this on their own; to be checked on the road.
- **H-9. Long text scrolls.** If the text is wider than the slot: hold still at the start (⚙ 1.5 s), slide left at a steady speed (⚙ about 45 px/s) until the end is visible, hold (⚙ 1.2 s), fade out and back in at the start, repeat. Text that fits stands still. Fade the right edge of the slot slightly so the cut-off reads as intended. Pause stops the scrolling too.
- **H-10. Changes between states** cross-fade the text (⚙ about 0.4 s); the panel does not jump in size.

## Map mode

The map answers "where on the road is it?": the timeline laid on the road the traveller is driving.

- **M-1. Base map:** a custom dark, muted style (Google Maps styling): roads, water, town names; no shops, restaurants or other points of interest.
- **M-2. Route:** the road ahead is bright (the view colour, `--light`); the road already driven is darker. The same convention as navigation apps. No era colours on any timeline for now.
- **M-3. Pins:** every event has a pin at its proportional position, past and future. Pins ahead are bright, A-cards slightly larger with a white core; passed pins are dimmer. Pins closer than a few pixels merge into a numbered cluster.
- **M-4. Only the next A-card carries its heading** on the map. No other pin shows text, so the road ahead keeps its surprises.
- **M-5. Tapping a passed pin** opens its card: date, heading, text, and a replay button. Tapping a pin ahead says only that it opens when you get there. A cluster opens a list of its passed events.
- **M-6. When an event fires,** a small card slides up above the dock: thumbnail of the event picture, date, heading, a sound indicator and a thin narration progress line. It leaves when the narration ends. Tapping it opens the full card. The map is never covered for long.
- **M-7. The car marker** is the signature red (`#9e0303`) with a white outline.
- **M-8. Two cameras,** switched with buttons on the map:
  - **Follow car:** heading-up, the car in the lower third, the road ahead visible. Pan and pinch work; touching the map stops following and shows a **Re-centre** button; after about 10 seconds untouched the map glides back to the car.
  - **Whole road:** the full route on one screen, rotated so the start sits upper left and the destination lower right, on the diagonal of the free area with some room to spare. If start and destination are close (a walking loop), rotate along the route's longest dimension instead. Pan, pinch and double-tap zoom work; a button restores the full view.
- **M-9. Compass needle:** shown whenever the map is not north-up. Tapping it turns the map north-up.
- **M-10. The top panel and the dock** are the same as in Image mode.
- **M-11. Colours.** The values the prototype uses (`hud/modes.js`, `drawMap`). Tune by eye on a real phone; these are the starting point.
  - **Base map:** ground `#12161b`, water `#0c1820`, rivers `#0f2230`, roads `#1f262e` (major roads `#262e38`). Town names: large towns `#b9c3cd`, small ones `#76828f`. No road names, no icons, no points of interest, no transit.
  - **Route ahead:** `#a9dcff` (the view colour, `--light`) with a soft glow. **Road already driven:** `#3b4652`, no glow. Both lines sit on a dark casing `rgba(4,6,9,0.85)` about 4 px wider than the line, so the route stays readable over any road.
  - **Pins ahead:** `#a9dcff`; A-cards larger, with a white core. **Passed pins:** `#6b7884`, smaller. Every pin has a thin dark outline `#080b0f`. The current event's pin has a slowly pulsing ring in `#a9dcff` (about 1.6 s per pulse). Clusters: a larger disc in the same colours with the count in dark text.
  - **Next A-card label (M-4):** a dark glass tag `rgba(8,11,16,0.84)` with a 1 px border `rgba(255,255,255,0.12)`, text `#e9eef3`.
  - **Car (M-7):** an arrow in `#9e0303` with a white outline and a faint white glow, on a soft light disc `rgba(255,255,255,0.10)`.
  - **Google style, as a starting point** (the base map only; route, pins and car are drawn by the app):

    ```json
    [
     {"elementType":"geometry","stylers":[{"color":"#12161b"}]},
     {"elementType":"labels.icon","stylers":[{"visibility":"off"}]},
     {"elementType":"labels.text.fill","stylers":[{"color":"#76828f"}]},
     {"elementType":"labels.text.stroke","stylers":[{"color":"#12161b"}]},
     {"featureType":"administrative.locality","elementType":"labels.text.fill","stylers":[{"color":"#b9c3cd"}]},
     {"featureType":"poi","stylers":[{"visibility":"off"}]},
     {"featureType":"transit","stylers":[{"visibility":"off"}]},
     {"featureType":"road","elementType":"geometry","stylers":[{"color":"#1f262e"}]},
     {"featureType":"road","elementType":"labels","stylers":[{"visibility":"off"}]},
     {"featureType":"road.highway","elementType":"geometry","stylers":[{"color":"#262e38"}]},
     {"featureType":"water","elementType":"geometry","stylers":[{"color":"#0c1820"}]}
    ]
    ```

  - **iOS:** the style only applies when `react-native-maps` uses the Google provider (`provider={PROVIDER_GOOGLE}`); Apple's maps ignore it. **Alternatively,** the same colours can be set in Google's cloud map styling (a Map ID), if that suits you better.

## Text mode

The text answers "what exactly did it say?": for reading along, rereading, and travelling with the sound off.

- **T-1. A logbook:** the current card is a solid card; passed cards stack above it as compact rows (date, heading). Scrolling up rereads them; tapping a row opens its text. The log ends with a **Next stop** line (heading, date) and never shows the text of anything ahead.
- **T-2. The card stands still while it is read.** The log moves only (a) when a new card arrives: one calm glide of about 1.1 s, eased in and out, to show the card's start; and (b) when the sentence being read reaches the bottom edge of a long card: one glide that brings that sentence near the top, like turning a page. Never a continuous follow (Ott: moving text is too hard to read in a car). When the traveller scrolls away, following stops and a **Back to now** button appears.
- **T-2a. A finished card folds away slowly** (about 1.5 s; 0.7 s when the next event follows at once): its text fades, the card shrinks into a log row, and only then does the log settle. Nothing jumps. A new card fades in and rises slightly (about 0.9 s).
- **T-3. Highlight by sentence:** the sentence being read is lit, sentences already read stay normal, sentences not yet read are dimmed. Sentence, not word (Ott).
- **T-4. Timing from Google TTS:** narration is pre-generated, so the timings are fetched once at generation. Put an SSML `<mark name="s1"/>` before each sentence and request `enableTimePointing: ["SSML_MARK"]` (v1beta1 `text:synthesize`); the reply gives each mark's time in seconds. Store those times as a small file next to each audio file. Check that the chosen voice returns timepoints: the newest premium voices (Chirp 3 HD) support only part of SSML. Fallback if a card has no timings: share the audio length between sentences by character count.
- **T-5. Background:** the tunnel behind the log, strongly muted: about 10% brightness and 30% speed, so its motion does not pull the eye (tunable; a plain dark ground is the alternative).
- **T-6. Fonts:** card text in Literata or Atkinson Hyperlegible Next (still being compared), size from the HUD values.

## Building blocks

- **Layout:** one full-screen layer for the picture/tunnel; the panels are absolutely positioned Views on top, offset with `react-native-safe-area-context`. Draw under the status bar and the gesture bar. The Play Store's current target API levels force edge-to-edge on Android anyway, so this design is built for it.
- **Glass:** a dark tint, a 1 px border `rgba(255,255,255,0.12)`, a rounded corner, and optionally a backdrop blur.
  - **iOS:** `expo-blur` `BlurView` (or `@react-native-community/blur`) is native and cheap.
  - **Android:** live blur is more expensive. Also, view-based blur libraries often cannot see what a GL or Skia surface draws underneath them, so blurring over the tunnel may show nothing. Test this first, on a mid-range phone.
  - **If the tunnel is drawn in `@shopify/react-native-skia`:** draw the panel backgrounds in the same Canvas with `BackdropBlur` clipped to rounded rects. It's one GPU pass, it works on both platforms, and the RN controls just sit on top.
  - **Fallback if blur costs too much:** no blur, a stronger tint. It still looks right; the blur is a nice-to-have.
- **Progress bars:** two thin Views (track + fill), animated with Reanimated. Drive the fill with `transform: scaleX` from the left, not `width`, so it stays on the UI thread. A soft glow is a shadow in the bar colour.
- **Scrolling heading (H-9):** a `Text` inside a clipping View, measured with `onTextLayout`; if wider than the View, animate `translateX` with Reanimated in the hold–slide–hold–fade sequence. Do not use a marquee library that loops continuously.
- **Text mode:** a `FlatList` (or `ScrollView`) between the two panels; the current card is nearly solid (`rgba(10,13,18,0.93)`).
- **Map mode:** `react-native-maps` with a custom dark style JSON; the route as two polylines (driven, ahead) split at the car's position; pins as markers.
- **Dock:** five keys of one material (soft vertical gradient, thin light top edge, drop shadow). Only the symbols are coloured and softly lit: Stop red, Pause amber, Map/Text/Image one shared colour. The engaged view key, and Pause while paused, get a soft halo in their own colour. Stop needs a press-and-hold (about 0.9 s) so a bump in the road cannot end the trip. Icons from `lucide-react-native`. Coloured halos: easy on iOS (`shadowColor`); on Android draw them in Skia or with a shadow library, because `elevation` shadows cannot be coloured.
- **Fonts:** still being chosen for legibility from the passenger seat: Barlow Semi Condensed or Atkinson Hyperlegible Next for the panel, Literata for the card text. All are open licence; bundle them with `expo-font`.
- **Pictures:** `resizeMode="cover"`. 9:20 frames fill most phones almost exactly. The images' safe zone (subject clear of top 12% / bottom 25%) keeps subjects out from under the panels.

## Numbers

Ott is tuning the final values in the prototype. Its "Copy values" button outputs them as JSON: tint, blur, sizes, gaps, radius, colours, font, scroll speed and pause. Take the numbers from there, not from this page.

## Two questions back to you

1. Expo or bare React Native?
2. How is the tunnel drawn now: Skia, `expo-gl`, a WebView, something else?

The answer decides the blur and halo routes above.
