# Glass HUD — how to build it in React Native

*For Sven. Version 2, 2026-10-25 (first version 2026-10-19). Reference prototype: https://ottsme.github.io/time_machine/hud/ (code in `hud/index.html`).*

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

## Building blocks

- **Layout:** one full-screen layer for the picture/tunnel; the panels are absolutely positioned Views on top, offset with `react-native-safe-area-context`. Draw under the status bar and the gesture bar. The Play Store's current target API levels force edge-to-edge on Android anyway, so this design is built for it.
- **Glass:** a dark tint, a 1 px border `rgba(255,255,255,0.12)`, a rounded corner, and optionally a backdrop blur.
  - **iOS:** `expo-blur` `BlurView` (or `@react-native-community/blur`) is native and cheap.
  - **Android:** live blur is more expensive. Also, view-based blur libraries often cannot see what a GL or Skia surface draws underneath them, so blurring over the tunnel may show nothing. Test this first, on a mid-range phone.
  - **If the tunnel is drawn in `@shopify/react-native-skia`:** draw the panel backgrounds in the same Canvas with `BackdropBlur` clipped to rounded rects. It's one GPU pass, it works on both platforms, and the RN controls just sit on top.
  - **Fallback if blur costs too much:** no blur, a stronger tint. It still looks right; the blur is a nice-to-have.
- **Progress bars:** two thin Views (track + fill), animated with Reanimated. Drive the fill with `transform: scaleX` from the left, not `width`, so it stays on the UI thread. A soft glow is a shadow in the bar colour.
- **Scrolling heading (H-9):** a `Text` inside a clipping View, measured with `onTextLayout`; if wider than the View, animate `translateX` with Reanimated in the hold–slide–hold–fade sequence. Do not use a marquee library that loops continuously.
- **Text mode:** a nearly solid card (`rgba(10,13,18,0.93)`) in a `ScrollView`, placed between the two panels. The picture stays behind it.
- **Dock:** five keys of one material (soft vertical gradient, thin light top edge, drop shadow). Only the symbols are coloured and softly lit: Stop red, Pause amber, Map/Text/Image one shared colour. The engaged view key, and Pause while paused, get a soft halo in their own colour. Stop needs a press-and-hold (about 0.9 s) so a bump in the road cannot end the trip. Icons from `lucide-react-native`. Coloured halos: easy on iOS (`shadowColor`); on Android draw them in Skia or with a shadow library, because `elevation` shadows cannot be coloured.
- **Fonts:** still being chosen for legibility from the passenger seat: Barlow Semi Condensed or Atkinson Hyperlegible Next for the panel, Literata for the card text. All are open licence; bundle them with `expo-font`.
- **Pictures:** `resizeMode="cover"`. 9:20 frames fill most phones almost exactly. The images' safe zone (subject clear of top 12% / bottom 25%) keeps subjects out from under the panels.

## Numbers

Ott is tuning the final values in the prototype. Its "Copy values" button outputs them as JSON: tint, blur, sizes, gaps, radius, colours, font, scroll speed and pause. Take the numbers from there, not from this page.

## Two questions back to you

1. Expo or bare React Native?
2. How is the tunnel drawn now: Skia, `expo-gl`, a WebView, something else?

The answer decides the blur and halo routes above.
