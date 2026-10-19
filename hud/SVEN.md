# Glass HUD — how to build it in React Native

*For Sven, 2026-10-19. Reference prototype: https://ottsme.github.io/time_machine/hud/ (code in `hud/index.html`).*

## What changes

The picture (or the tunnel) fills the whole screen, edge to edge. No frame, no rivets. On top of it float two panels, and nothing else:

- **Top panel:** heading + date on one line, then two thin bars: trip progress (white) and progress to the next event (red). NEXT EVENT, ETA, metres and the PROG/NEXT labels are dropped. In the tunnel, the heading slot shows the deck name and the date ticks with the road position.
- **Bottom dock:** stop, pause, and a Map / Text / Image switch.
- **Panels are tinted glass:** the picture and the tunnel stay visible behind them. Buttons, the active tab and the text card are solid.

## Building blocks

- **Layout:** one full-screen layer for the picture/tunnel; the panels are absolutely positioned Views on top, offset with `react-native-safe-area-context`. Draw under the status bar and the gesture bar. The Play Store's current target API levels force edge-to-edge on Android anyway, so this design is built for it.
- **Glass:** a dark tint (`rgba(8,11,16,≈0.38)`), a 1 px border `rgba(255,255,255,0.12)`, radius 14, and a backdrop blur (~18 px).
  - **iOS:** `expo-blur` `BlurView` (or `@react-native-community/blur`) is native and cheap.
  - **Android:** live blur is more expensive. Also, view-based blur libraries often cannot see what a GL or Skia surface draws underneath them, so blurring over the tunnel may show nothing. Test this first, on a mid-range phone.
  - **If the tunnel is drawn in `@shopify/react-native-skia`:** draw the panel backgrounds in the same Canvas with `BackdropBlur` clipped to rounded rects. It's one GPU pass, it works on both platforms, and the RN controls just sit on top.
  - **Fallback if blur costs too much:** no blur, tint raised to about 0.6. It still looks right; the blur is a nice-to-have.
- **Progress bars:** two Views (3 px track, 3 px fill), animated with Reanimated. Drive the fill with `transform: scaleX` from the left, not `width`, so it stays on the UI thread.
- **Heading:** one `Text` with `numberOfLines={2}`, `adjustsFontSizeToFit` and `minimumFontScale={0.84}`. The rule is full size first, then one step smaller, then two lines. No marquee.
- **Text mode:** a nearly solid card (`rgba(10,13,18,0.93)`) in a `ScrollView`, placed between the two panels. The picture stays behind it.
- **Dock:** a stop button and a pause button (44 × 44, solid), then a three-way segmented control with the active tab solid white. Icons from `lucide-react-native` (map, align-left, image, square, pause).
- **Fonts:** Space Grotesk (UI), JetBrains Mono (dates and numbers, tabular), Literata (card text). All are open licence; bundle them with `expo-font` or as assets.
- **Pictures:** `resizeMode="cover"`. 9:20 frames fill most phones almost exactly. The images' safe zone (subject clear of top 12% / bottom 25%) already keeps subjects out from under the panels.

## Numbers

Ott is tuning the final values in the prototype. Its "Copy values" button outputs them as JSON: tint, blur, sizes, gaps, radius and colours. Take the numbers from there, not from this page.

## Two questions back to you

1. Expo or bare React Native?
2. How is the tunnel drawn now: Skia, `expo-gl`, a WebView, something else?

The answer decides the blur route above.
