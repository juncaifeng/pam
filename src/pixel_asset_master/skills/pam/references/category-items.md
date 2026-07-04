# Item / Prop Pixel Art Guide

Weapons, potions, keys, chests, collectibles, and UI icons.

## 1. Readability at Small Sizes

- At 16×16, an item should be recognizable as a single icon.
- At 32×32, add 1 level of detail (grip, label, shine).
- At 64×64, add material suggestion (wood grain, metal edge, liquid).

## 2. Canvas & Framing

| Type | Size | Notes |
|------|------|-------|
| UI icon | 16×16 ~ 32×32 | Centered, high contrast |
| Inventory item | 32×32 | Slight 3/4 perspective for depth |
| World pickup | 32×32 ~ 64×64 | Ground shadow, readable from above |

## 3. Perspective

- Use **3/4 view** for most items to show top and front faces.
- Avoid pure top-down unless the game camera is top-down.
- Weapons should point diagonally (usually 45°) to maximize blade length.

## 4. Color & Material

- Metal: 2–3 cool gray tones + 1 bright highlight.
- Wood: 2–3 warm brown tones.
- Liquid: 1 base color + 1 highlight pixel for "glint".
- Magic: 1 accent color for glow; do not overuse.

## 5. Common Anti-patterns

| ❌ Bad | ✅ Good |
|--------|---------|
| Flat, front-facing icon in a 3D game | 3/4 perspective with shadow |
| Too many tiny details | 1 focal detail + simple base shape |
| Colors blend with UI background | Use border or contrasting outline |
| Potion looks like a blob | Neck, body, and cork silhouette |

## 6. Optional Animation

- Idle pickup: subtle bob (1–2 px) or sparkle on highlight pixel.
- Open chest: 2–4 frame lid lift.
- Magic item: pulsing glow on accent color.

## 7. Validation Checklist

- [ ] `pam validate-assets <project>` passes in strict mode
- [ ] Item is centered in frame
- [ ] Recognizable at target display size
- [ ] No more than declared max colors
- [ ] If animated, loop is seamless and subtle
