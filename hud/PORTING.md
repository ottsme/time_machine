# Porting the HUD panels to React Native + Expo

*For Sven and his AI assistant. 2026-11-05. Written by Claude for Ott.*

This document is the **how**. The **what** (what the panels show and when) is in [`SVEN.md`](SVEN.md), rules H-1 to H-10, M-1 to M-11 and T-1 to T-6. The reference look is the web prototype: https://ottsme.github.io/time_machine/hud/ (code: [`index.html`](index.html), [`modes.js`](modes.js)).

The prototype is HTML and CSS. **Do not translate the CSS line by line.** Several CSS features it uses (`backdrop-filter`, `color-mix`, multiple shadows, `mask-image`) have no direct React Native equivalent. Rebuild each piece from the recipes below instead.

---

## 0 · How to work with this (for you and the AI)

### The order that avoids pain

Most of the difficulty comes from trying to get the glass blur and the glows right first. Don't. Build in three phases, and test on a real **mid-range Android phone** after each one:

1. **Flat.** Layout and behaviour only: panels in the right place, safe areas, progress bars moving, the heading scrolling, the keys working, hold-to-stop. Plain tinted panels, **no blur, no glow**. This alone already looks close to the prototype.
2. **Material.** Key gradients, the top-edge highlight, text glow, coloured halos, bar glow.
3. **Blur (optional).** Only if phases 1–2 run smoothly. The design works without it; a slightly stronger tint replaces it.

### Tell the AI your exact versions

Before anything else, give the assistant the **Expo SDK version**, the **React Native version**, and whether the app runs on the **New Architecture**. Several APIs used here changed in recent versions (`expo-blur` on Android, `boxShadow`, `filter`), and an assistant that guesses the version will give outdated code. Check with `npx expo --version` and `package.json`.

### Give the AI the files

Copy `hud/PORTING.md`, `hud/SVEN.md` and `hud/index.html` into the app repo (for example `docs/hud/`). Then reference them in chat (`#file`) so the assistant reads the real values, not its memory of what a HUD looks like.

### Which model

GitHub Copilot lets you pick the model in the chat's model picker. Which models you see depends on your plan. For this job:

- **Claude Opus 5.5** for the hard parts: the animation sequences, platform differences, blur over the tunnel, anything spanning several files. Use it in **Agent mode** (VS Code), so it can edit files and run type checks itself.
- **Claude Sonnet 5.5** for routine work once the structure is in place: small style tweaks, one component at a time. It's faster and cheaper.
- For a self-contained task ("build phase 1 of the top panel per docs/hud/PORTING.md §3"), you can also hand it to the **Claude agent on github.com**, which works on its own and opens a pull request.

Whatever the model, work in **small steps** (one component per request), run the app after each, and paste back errors and screenshots. Screenshots help a lot: the assistant can compare them with the prototype.

### A block for `.github/copilot-instructions.md`

Copilot reads this file in your repo automatically on every request. Paste this in, with your versions filled in:

```markdown
## Time Machine HUD
- Stack: Expo SDK __, React Native __, New Architecture: yes/no. TypeScript.
- The HUD spec is docs/hud/SVEN.md (behaviour) and docs/hud/PORTING.md (implementation). Follow them; ask before deviating.
- All HUD colours, sizes and timings come from src/hud/theme.ts. Never hard-code a value in a component.
- Animations: react-native-reanimated only (UI thread). No setInterval-driven animation, no JS-thread Animated API.
- Panels are absolutely positioned over the media layer (picture / tunnel) with pointerEvents="box-none" on wrappers.
- Build phase by phase: flat first, then material, then blur. Do not add blur unless asked.
- Test target: a mid-range Android phone first, iOS second.
```

---

## 1 · Packages

All installable with `npx expo install <name>`, so the versions match your SDK.

| Package | Used for |
|---|---|
| `react-native-safe-area-context` | Top panel and dock clear of the notch and gesture bar |
| `react-native-reanimated` | Progress bars, scrolling heading, hold-to-stop, fades |
| `expo-linear-gradient` | Key surfaces, panel sheen (or the core `backgroundImage`, §6) |
| `react-native-svg` + `lucide-react-native` | Icons: square, pause, play, map, align-left, image |
| `@expo-google-fonts/barlow-semi-condensed` | The panel font (current choice for the car) |
| `expo-haptics` | A short buzz when hold-to-stop completes |
| `expo-keep-awake` | Screen stays on during the trip |
| `expo-status-bar`, `expo-navigation-bar` | Hide system bars during the trip |
| `expo-blur` | Phase 3 only |

---

## 2 · Screen structure

```
TripScreen
├─ MediaLayer            (full screen: event picture(s) + tunnel; under everything)
├─ HudLayer              (absoluteFill, pointerEvents="box-none")
│  ├─ TopPanel           (absolute; top = insets.top + T.topGap; left/right = T.inset)
│  │  ├─ GlassBackground
│  │  ├─ HeadingRow      (ScrollingHeading + date)
│  │  └─ Bars            (ProgressBar trip, ProgressBar next)
│  └─ Dock               (absolute; bottom = insets.bottom + T.dockBottom; left/right = T.inset)
│     ├─ HoldToStopKey
│     ├─ Key (pause)
│     └─ Key ×3 (map / text / image)
└─ TextMode / MapMode    (between the panels when active; see SVEN.md)
```

- The media layer draws **edge to edge**, under the status bar and the gesture bar. Only the panels respect the safe areas.
- Wrappers that cover the screen get `pointerEvents="box-none"`, so touches pass through to the map in Map mode.

---

## 3 · The theme file

One file holds every number. Start from these values (the prototype's look, with the **Car preset** sizes, since the app is read from the passenger seat). **Replace them with Ott's final values:** he exports them from the prototype with **Copy values**. The mapping from his JSON keys is in the comments.

```ts
// src/hud/theme.ts
export const T = {
  inset: 7,             // inset      side gap of both panels
  topGap: 12,           // top        gap above the top panel, added to insets.top
  dockBottom: 22,       //            gap below the dock, added to insets.bottom
  radius: 14,           // radius     top panel corner

  glass: {
    tint: '#080b10',    // tint
    opacity: 0.36,      // glass      tint opacity (0.12 if blur is on and strong)
    blur: 14,           // blur       phase 3 only
    sheen: 0.3,         // sheen      white gradient at the top of the panel
    edge: 0.18,         // edge       1 px highlight along the top edge
    border: 'rgba(255,255,255,0.12)',
  },

  type: {
    family: 'BarlowSemiCondensed_600SemiBold', // font
    heading: 28,        // title_
    date: 23,           // dateSize
    headingColor: '#f4f6f8', // headCol
    dateColor: '#f4f6f8',    // dateCol
    glow: 0.25,         // textGlow
  },

  bars: {
    height: 5.5,        // bar
    gap: 4,
    trip: '#6f93ab',    // tripCol
    next: '#a9dcff',    // nextCol
    glow: 0.5,          // barGlow
    trackTrip: 'rgba(255,255,255,0.12)',
    trackNext: 'rgba(255,255,255,0.08)',
  },

  heading: {
    scrollSpeed: 45,    // scrollSpeed  px per second
    holdStart: 1.5,     // scrollPause  s
    holdEnd: 1.2,       //              s
    fade: 0.4,          //              s, H-9 and H-10
  },

  keys: {
    height: 58,         // key
    radius: 12,         // keyR
    gap: 8,
    face: '#262b32',    // btn
    faceTop: '#373c42', // btn lightened by finish (0.5 → about 8 % white)
    faceBottom: '#202429', // btn darkened by finish (0.5 → about 17 % black)
    edge: 0.18,         // edge
    shadow: 0.5,        // shadow
    labels: false,      // labels
    labelSize: 12,      // labelSize
    holdToStop: 900,    // ms
  },

  lights: {
    view: '#a9dcff',    // light   Map / Text / Image
    stop: '#ff4a3d',    // stop
    pause: '#ffb22e',   // pause
    glow: 0.6,          // glow    symbol glow
    halo: 0.55,         // halo    halo strength when engaged
    haloSize: 14,       // haloSize
  },
} as const;

/** '#a9dcff' + 0.45 → 'rgba(169,220,255,0.45)' */
export const alpha = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
};
```

If Ott changes **Buttons** colour or **Finish**, recompute `faceTop` and `faceBottom` (mix the face colour with white or black by the percentages in the comment), or ask the assistant to add a small `mix()` helper.

---

## 4 · Phase 1 — flat

### 4.1 Glass background (flat version)

A plain tinted rectangle with a border. Used by the top panel (and the optional dock tray).

```tsx
// src/hud/GlassBackground.tsx
import { StyleSheet, View } from 'react-native';
import { T, alpha } from './theme';

export function GlassBackground({ radius = T.radius }: { radius?: number }) {
  return (
    <View
      pointerEvents="none"
      style={[
        StyleSheet.absoluteFill,
        {
          borderRadius: radius,
          backgroundColor: alpha(T.glass.tint, T.glass.opacity),
          borderWidth: 1,
          borderColor: T.glass.border,
        },
      ]}
    />
  );
}
```

### 4.2 Top panel

```tsx
// src/hud/TopPanel.tsx
import { StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { T } from './theme';
import { GlassBackground } from './GlassBackground';
import { ScrollingHeading } from './ScrollingHeading';
import { ProgressBar } from './ProgressBar';

type Props = {
  text: string;            // heading (H-1) or "Next: …, 2.5 Ga" (H-3)
  date?: string;           // shown only in the event state (H-1); undefined in the Next state
  trip: number;            // 0…1
  next: number;            // 0…1, progress to the next anchor
  paused: boolean;
};

export function TopPanel({ text, date, trip, next, paused }: Props) {
  const insets = useSafeAreaInsets();
  return (
    <View style={[styles.panel, { top: insets.top + T.topGap }]}>
      <GlassBackground />
      <View style={styles.row}>
        <ScrollingHeading text={text} paused={paused} style={styles.heading} />
        {date ? <Text style={styles.date}>{date}</Text> : null}
      </View>
      <View style={{ gap: T.bars.gap }}>
        <ProgressBar value={trip} color={T.bars.trip} track={T.bars.trackTrip} />
        <ProgressBar value={next} color={T.bars.next} track={T.bars.trackNext} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  panel: {
    position: 'absolute', left: T.inset, right: T.inset,
    paddingHorizontal: 14, paddingTop: 11, paddingBottom: 12, gap: 9,
    borderRadius: T.radius,
  },
  row: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  heading: {
    fontFamily: T.type.family, fontSize: T.type.heading, color: T.type.headingColor,
    letterSpacing: -0.2,
  },
  date: {
    fontFamily: T.type.family, fontSize: T.type.date, color: T.type.dateColor,
    fontVariant: ['tabular-nums'],
  },
});
```

### 4.3 Progress bar

`value` can change as often as the GPS updates; Reanimated smooths it on the UI thread.

```tsx
// src/hud/ProgressBar.tsx
import { useEffect } from 'react';
import { View } from 'react-native';
import Animated, { useAnimatedStyle, useSharedValue, withTiming } from 'react-native-reanimated';
import { T } from './theme';

export function ProgressBar({ value, color, track }: { value: number; color: string; track: string }) {
  const v = useSharedValue(value);
  useEffect(() => { v.value = withTiming(Math.max(0, Math.min(1, value)), { duration: 250 }); }, [value]);
  const fill = useAnimatedStyle(() => ({ width: `${v.value * 100}%` }));
  return (
    <View style={{ height: T.bars.height, borderRadius: T.bars.height / 2, backgroundColor: track }}>
      <Animated.View style={[{ height: '100%', borderRadius: T.bars.height / 2, backgroundColor: color }, fill]} />
    </View>
  );
}
```

(`SVEN.md` suggests `scaleX`; animating `width` is simpler and fast enough for two thin bars. Use `scaleX` with `transformOrigin: 'left'` only if profiling says so.)

### 4.4 Scrolling heading (H-9, H-10)

Text that fits stands still. Text that doesn't: hold → slide to the end → hold → fade out → jump back → fade in → repeat.

The trick is to **measure the text without constraining it**: a horizontal `ScrollView` with scrolling disabled lets its content be as wide as it wants, so `onLayout` gives the true text width.

```tsx
// src/hud/ScrollingHeading.tsx
import { useEffect, useState } from 'react';
import { ScrollView, TextStyle, View } from 'react-native';
import Animated, {
  Easing, FadeIn, FadeOut, cancelAnimation, useAnimatedStyle, useSharedValue,
  withDelay, withRepeat, withSequence, withTiming,
} from 'react-native-reanimated';
import { T } from './theme';

export function ScrollingHeading({ text, paused, style }: { text: string; paused: boolean; style: TextStyle }) {
  const [boxW, setBoxW] = useState(0);
  const [textW, setTextW] = useState(0);
  const x = useSharedValue(0);
  const op = useSharedValue(1);
  const over = Math.max(0, Math.ceil(textW - boxW) + 6);

  useEffect(() => {
    cancelAnimation(x); cancelAnimation(op);
    x.value = 0; op.value = 1;
    if (paused || textW <= boxW + 1 || boxW === 0) return;
    const { scrollSpeed, holdStart, holdEnd, fade } = T.heading;
    const slide = (over / scrollSpeed) * 1000;
    const half = (fade * 1000) / 2;
    // both sequences last exactly holdStart + slide + holdEnd + fade, so they stay in step
    x.value = withRepeat(withSequence(
      withDelay(holdStart * 1000, withTiming(-over, { duration: slide, easing: Easing.linear })),
      withDelay(holdEnd * 1000 + half, withTiming(0, { duration: 0 })),   // jump back while invisible
      withTiming(0, { duration: half }),                                  // wait while fading in
    ), -1);
    op.value = withRepeat(withSequence(
      withDelay(holdStart * 1000 + slide + holdEnd * 1000, withTiming(0, { duration: half })),
      withTiming(1, { duration: half }),
    ), -1);
    return () => { cancelAnimation(x); cancelAnimation(op); };
  }, [text, textW, boxW, paused]);

  const run = useAnimatedStyle(() => ({ transform: [{ translateX: x.value }], opacity: op.value }));

  return (
    <View style={{ flex: 1, overflow: 'hidden' }} onLayout={e => setBoxW(e.nativeEvent.layout.width)}>
      {/* key={text}: a new text cross-fades in (H-10) */}
      <Animated.View key={text} entering={FadeIn.duration(T.heading.fade * 1000)} exiting={FadeOut.duration(T.heading.fade * 1000)}>
        <ScrollView horizontal scrollEnabled={false} showsHorizontalScrollIndicator={false}>
          <Animated.Text style={[style, run]} onLayout={e => setTextW(e.nativeEvent.layout.width)}>
            {text}
          </Animated.Text>
        </ScrollView>
      </Animated.View>
    </View>
  );
}
```

Notes:

- Pause stops the scroll and puts the text back at the start; that's fine.
- The soft fade at the right edge (H-9) is phase 2: a `LinearGradient` from transparent to the panel tint over the last ~18 px, or `@react-native-masked-view/masked-view` if you want a true alpha fade. Skip it in phase 1.

### 4.5 Keys and the dock (flat)

```tsx
// src/hud/Key.tsx
import { ReactNode } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { T } from './theme';

type Props = { light: string; on?: boolean; label?: string; square?: boolean; onPress?: () => void; children: ReactNode; accessibilityLabel: string };

export function Key({ light, on, label, square, onPress, children, accessibilityLabel }: Props) {
  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel}
      accessibilityState={{ selected: !!on }}
      style={({ pressed }) => [
        styles.key,
        square ? { width: T.keys.height } : { flex: 1 },
        on && { borderColor: light },
        pressed && { transform: [{ translateY: 1 }] },
      ]}
    >
      <View style={{ alignItems: 'center', gap: 3, opacity: on ? 1 : 0.82 }}>
        {children}
        {T.keys.labels && label ? <Text style={[styles.label, { color: light }]}>{label.toUpperCase()}</Text> : null}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  key: {
    height: T.keys.height, borderRadius: T.keys.radius,
    backgroundColor: T.keys.face, borderWidth: 1, borderColor: 'rgba(255,255,255,0.07)',
    alignItems: 'center', justifyContent: 'center',
  },
  label: { fontFamily: T.type.family, fontSize: T.keys.labelSize, letterSpacing: 1.2 },
});
```

Icons: `lucide-react-native` with `color={light}` and `size={Math.round(T.keys.height * 0.38)}`: `Square` (filled) for stop, `Pause` / `Play`, `Map`, `AlignLeft`, `Image`.

### 4.6 Hold to stop

The key fills with red from the bottom while held. Released early: a short hint ("Hold to stop the trip"). Completed: haptic + stop.

```tsx
// src/hud/HoldToStopKey.tsx
import { useRef } from 'react';
import { Pressable, StyleSheet } from 'react-native';
import * as Haptics from 'expo-haptics';
import { Square } from 'lucide-react-native';
import Animated, { cancelAnimation, useAnimatedStyle, useSharedValue, withTiming, Easing } from 'react-native-reanimated';
import { T, alpha } from './theme';

export function HoldToStopKey({ onStop, onHint }: { onStop: () => void; onHint: () => void }) {
  const fill = useSharedValue(0);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const done = useRef(false);

  const start = () => {
    done.current = false;
    fill.value = withTiming(1, { duration: T.keys.holdToStop, easing: Easing.linear });
    timer.current = setTimeout(() => {
      done.current = true;
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      onStop();
    }, T.keys.holdToStop);
  };
  const end = () => {
    if (timer.current) clearTimeout(timer.current);
    cancelAnimation(fill);
    fill.value = withTiming(0, { duration: 150 });
    if (!done.current) onHint();
  };

  const bar = useAnimatedStyle(() => ({ height: `${fill.value * 100}%` }));
  return (
    <Pressable onPressIn={start} onPressOut={end} accessibilityRole="button" accessibilityLabel="Stop trip (press and hold)"
      style={[styles.key, { width: T.keys.height }]}>
      <Animated.View style={[{ position: 'absolute', left: 0, right: 0, bottom: 0, backgroundColor: alpha(T.lights.stop, 0.3) }, bar]} />
      <Square size={Math.round(T.keys.height * 0.3)} color={T.lights.stop} fill={T.lights.stop} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  key: {
    height: T.keys.height, borderRadius: T.keys.radius, overflow: 'hidden',
    backgroundColor: T.keys.face, borderWidth: 1, borderColor: 'rgba(255,255,255,0.07)',
    alignItems: 'center', justifyContent: 'center',
  },
});
```

### 4.7 Dock

```tsx
<View pointerEvents="box-none" style={{ position: 'absolute', left: T.inset, right: T.inset, bottom: insets.bottom + T.dockBottom, flexDirection: 'row', gap: T.keys.gap }}>
  <HoldToStopKey onStop={stopTrip} onHint={() => showToast('Hold to stop the trip')} />
  <Key square light={T.lights.pause} on={paused} onPress={togglePause} accessibilityLabel={paused ? 'Resume' : 'Pause'}>
    {paused ? <Play color={T.lights.pause} fill={T.lights.pause} size={22} /> : <Pause color={T.lights.pause} fill={T.lights.pause} size={22} />}
  </Key>
  <Key light={T.lights.view} on={mode === 'map'}   label="Map"   onPress={() => setMode('map')}   accessibilityLabel="Map"><MapIcon color={T.lights.view} size={22} /></Key>
  <Key light={T.lights.view} on={mode === 'text'}  label="Text"  onPress={() => setMode('text')}  accessibilityLabel="Text"><AlignLeft color={T.lights.view} size={22} /></Key>
  <Key light={T.lights.view} on={mode === 'image'} label="Image" onPress={() => setMode('image')} accessibilityLabel="Image"><ImageIcon color={T.lights.view} size={22} /></Key>
</View>
```

Import the icons under other names, so they don't shadow JavaScript's `Map` and React Native's `Image`: `import { Map as MapIcon, Image as ImageIcon, AlignLeft, Pause, Play } from 'lucide-react-native'`.

**End of phase 1.** Check against §8 before going on.

---

## 5 · Phase 2 — material

### 5.1 Key surface: gradient + top edge + drop shadow

Put the **shadow and halo on an outer View** and the **gradient inside an inner View with `overflow: 'hidden'`**. A shadow on a view that clips its own content gets cut off on some platforms.

```tsx
<View style={[{ borderRadius: T.keys.radius }, shadowStyle, on && haloStyle(light)]}>
  <View style={{ borderRadius: T.keys.radius, overflow: 'hidden', borderWidth: 1, borderColor: on ? alpha(light, T.lights.halo * 0.7) : 'rgba(255,255,255,0.07)' }}>
    <LinearGradient
      colors={[T.keys.faceTop, T.keys.face, T.keys.faceBottom]}
      locations={[0, 0.48, 1]}
      style={StyleSheet.absoluteFill}
    />
    {/* 1 px highlight along the top edge */}
    <View style={{ position: 'absolute', left: 0, right: 0, top: 0, height: 1, backgroundColor: `rgba(255,255,255,${T.keys.edge * 1.2})` }} />
    {/* … icon and label … */}
  </View>
</View>
```

The same top-edge line goes on the top panel (`T.glass.edge`), so the panel and the keys look like one set. The panel's **sheen** is a `LinearGradient` from `rgba(255,255,255, T.glass.sheen × 0.12)` to transparent at 60 % of the height, under the content.

### 5.2 Drop shadow and coloured halo

**If the app runs on the New Architecture** (the default on recent Expo SDKs), React Native's `boxShadow` style does both, with web syntax:

```ts
const shadowStyle = { boxShadow: `0 ${T.keys.shadow * 6}px ${T.keys.shadow * 14}px rgba(0,0,0,${T.keys.shadow * 0.7})` };
const haloStyle = (c: string) => ({
  boxShadow: `0 ${T.keys.shadow * 6}px ${T.keys.shadow * 14}px rgba(0,0,0,${T.keys.shadow * 0.7}), 0 0 ${T.lights.haloSize}px ${alpha(c, T.lights.halo * 0.85)}`,
});
```

(On Android, outset `boxShadow` needs Android 9 or newer.)

**On the old architecture:** iOS can use `shadowColor: light, shadowRadius: T.lights.haloSize, shadowOpacity: T.lights.halo, shadowOffset: {width: 0, height: 0}`. Android's `elevation` shadow can't be coloured, so either skip the halo there (the brighter border already marks the engaged key) or draw it with Skia.

### 5.3 Glowing symbols

Lucide icons are SVG, so wrap them in a View:

- **iOS:** a View with a transparent background and `shadowColor: light, shadowRadius: T.lights.glow * 5, shadowOpacity: 0.9, shadowOffset: {width: 0, height: 0}`. On iOS the shadow follows the icon's shape.
- **Android (New Architecture, Android 12+):** `filter: \`drop-shadow(0 0 ${T.lights.glow * 5}px ${light})\``. On older Android, no glow; the bright colour alone is fine.

Engaged keys: icon opacity 1 and a slightly bigger glow (× 1.4). Not engaged: opacity 0.82.

### 5.4 Glowing text and bars

- **Heading and date:** `textShadowColor: alpha(color, T.type.glow * 0.7)`, `textShadowRadius: T.type.glow * 10`, `textShadowOffset: {width: 0, height: 0}`. Works on both platforms. Keep it subtle: legibility first.
- **Bars:** on the New Architecture, `boxShadow: \`0 0 ${T.bars.glow * 8}px ${color}\`` on the fill. Otherwise, no glow.

---

## 6 · Phase 3 — blur (optional)

Only if phases 1–2 run at a steady frame rate on the mid-range Android phone. **Start from how the tunnel is drawn**, because blur can only blur what the blur view can see:

| Tunnel drawn with | Blur route |
|---|---|
| `@shopify/react-native-skia` | Draw the panel backgrounds **inside the same Skia Canvas** with `BackdropBlur` clipped to a rounded rect at the panels' positions. The RN panels on top become transparent (no `GlassBackground`). One GPU pass, both platforms, and the most reliable route. |
| `expo-gl`, a WebView, or a video | View-based blur often can't see this content and shows a flat tint instead. Test once; if it fails, **skip blur** and raise `T.glass.opacity` to about 0.5. |
| Only for event pictures (plain `Image`) | `expo-blur` works; see below. |

**`expo-blur` (SDK 58):** on Android, blur is opt-in. Wrap the **media layer** (the content to be blurred) in a `BlurTargetView`, pass its ref to each `BlurView` as `blurTarget`, and set `blurMethod="dimezisBlurViewSdk31Plus"` (falls back to a plain tint below Android 12). `BlurView` ignores `borderRadius`; put it inside a View with `borderRadius` and `overflow: 'hidden'`. Check the docs for your SDK version, since this API changed recently: https://docs.expo.dev/versions/latest/sdk/blur-view/

With blur on, the tint can go back down to Ott's lighter value.

---

## 7 · Trip-screen basics

- **Edge to edge:** the media layer fills the whole screen; only the panels use `useSafeAreaInsets()`.
- **System bars:** `<StatusBar hidden />` from `expo-status-bar` during the trip; hide the Android navigation bar with `expo-navigation-bar` (check its docs for your SDK, since some calls changed with edge-to-edge).
- **Keep awake:** `useKeepAwake()` from `expo-keep-awake` in the trip screen.
- **Fonts:** `useFonts({ BarlowSemiCondensed_500Medium, BarlowSemiCondensed_600SemiBold })` from `@expo-google-fonts/barlow-semi-condensed`; don't render the HUD until they're loaded.
- **Performance:** every animation runs in Reanimated on the UI thread. Don't drive anything from `setInterval` or React state at 60 fps. Position updates (GPS) may update React state a few times a second; the bars smooth them.

---

## 8 · Done when

Phase 1:

- [ ] Top panel and dock sit inside the safe areas on a notched phone and on a phone with a gesture bar; the picture runs under both bars.
- [ ] Heading + date in the event state; `Next: …, 2.5 Ga` with no date in the Next state (H-1, H-3).
- [ ] A long heading holds, slides, holds, fades, repeats; a short one stands still; pause stops it (H-9).
- [ ] A new heading cross-fades in; the panel doesn't jump in height (H-10).
- [ ] Both bars move smoothly with the GPS position.
- [ ] Five separate keys; Map / Text / Image switch modes, the engaged one is marked; Pause toggles Pause/Play.
- [ ] Stop needs about 0.9 s of holding, shows the red fill, and buzzes; a short tap only shows the hint.
- [ ] Touches outside the panels reach the map in Map mode.

Phase 2:

- [ ] Keys have the gradient face, the top-edge line and a drop shadow; the engaged key and Pause-while-paused have a halo in their own colour.
- [ ] Symbols glow softly (iOS; Android 12+ on the New Architecture).
- [ ] Heading and date have a faint glow and stay sharp.

Phase 3:

- [ ] Blur shows the moving tunnel behind the panels, or blur is off and the tint is raised.
- [ ] Still a steady frame rate on the mid-range Android phone.

---

## 9 · CSS → React Native, quick reference

| Prototype (CSS) | React Native |
|---|---|
| `position:absolute; left/right: var(--inset)` | `position: 'absolute', left: T.inset, right: T.inset` |
| `env(safe-area-inset-top)` | `useSafeAreaInsets().top` |
| `background: color-mix(in srgb, tint X%, transparent)` | `backgroundColor: alpha(tint, X)` |
| `backdrop-filter: blur()` | §6 (Skia `BackdropBlur` or `expo-blur`), or nothing |
| `linear-gradient(...)` | `expo-linear-gradient`, or the core `backgroundImage` style on recent RN |
| `box-shadow: inset 0 1px 0 …` | a 1 px absolute View at the top |
| `box-shadow: 0 0 14px colour` | `boxShadow` (New Architecture), else iOS `shadow*` |
| `filter: drop-shadow()` on an icon | iOS `shadow*` on a wrapper; Android `filter` (12+, New Architecture) |
| `text-shadow` | `textShadowColor` / `textShadowRadius` / `textShadowOffset` |
| `mask-image` fade at the edge | `LinearGradient` overlay or `@react-native-masked-view/masked-view` |
| CSS transitions / keyframes | Reanimated `withTiming`, `withSequence`, `withRepeat`, layout animations |
| `font-variant-numeric: tabular-nums` | `fontVariant: ['tabular-nums']` |

Questions about the look → Ott (the prototype is the reference). Questions about when things appear → `SVEN.md` and the playback rulebook.
