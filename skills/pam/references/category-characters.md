# Character Pixel Art Guide

Humanoid characters: heroes, NPCs, enemies with human-like proportions.

## 1. Silhouette First

- The character must be **instantly readable** from its silhouette alone.
- Use a strong, unique pose; avoid standing perfectly straight (front-facing only when explicitly requested).
- Head/body/limb proportions should match the declared style:
  - Chibi: 1:1 ~ 1:2 head-to-body
  - Realistic: 1:6 ~ 1:8
  - Heroic: 1:4 ~ 1:6

## 2. Canvas & Size Rules

| Asset | Recommended Size | Notes |
|-------|------------------|-------|
| Idle frame | declared base size | Symmetric or near-symmetric |
| Walk frame | declared base size | 4–8 frames, 8–12 fps |
| Attack frame | declared base size | Wind-up → strike → recovery |
| Portrait / UI icon | 16×16 ~ 32×32 | Face only, high contrast |

## 3. Animation Cycles

### Idle
- 2–4 frames
- Subtle breathing/bobbing (1–2 px vertical shift)
- Keep feet planted

### Walk
- 4–8 frames
- Contact → push → passing → high-point
- Avoid sliding feet; ensure forward motion matches stride length

### Attack
- 4–6 frames
- Exaggerate the weapon/arm extension on the strike frame
- Add 1–2 frame anticipation before the hit

## 4. Color & Shading

- Limit to declared palette.
- Cel-shaded: 2–3 tones per material.
- Light source top-left by default; keep consistent across all frames.
- Eyes/mouth should remain readable at game display size.

## 5. Common Anti-patterns

| ❌ Bad | ✅ Good |
|--------|---------|
| Floating limbs with no connection | Clear joints, at least 1 px connector |
| Symmetric "T-pose" in action frames | Dynamic, weight-shifted poses |
| Tiny facial features lost at 1× scale | Simplified, high-contrast face dots |
| All frames share identical silhouette | Silhouette changes clearly per action |

## 6. Validation Checklist

- [ ] `pam validate-assets <project>` passes in strict mode
- [ ] Silhouette is recognizable in every frame
- [ ] Eyes/weapon/key detail visible at 1× scale
- [ ] Loop point for idle/walk is seamless
- [ ] All frames use the same palette subset
