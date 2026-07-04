# Creature / Monster Pixel Art Guide

Fantasy creatures, monsters, bosses, and non-real beings.

## 1. Design Principle

- Exaggerate 1–2 signature traits: horns, claws, glowing eyes, tentacles, wings.
- Silhouette should communicate threat or fantasy archetype immediately.
- Use asymmetry to make the creature feel organic or otherworldly.

## 2. Size & Anatomy

| Type | Size | Notes |
|------|------|-------|
| Small minion | 16×16 ~ 32×32 | Big head, simple limbs |
| Standard monster | 32×32 ~ 64×64 | Full body + 1 special feature |
| Boss | 64×64 ~ 128×128 | Multiple limbs, layered details |

## 3. Animation Cycles

### Idle
- Heavy creatures: slow breathing, 3–4 frames
- Fast creatures: twitching / antennae movement, 2–3 frames

### Attack
- Wind-up → strike → impact → recovery
- Add a "flash" or pose extreme on the impact frame
- 4–6 frames typical

### Hurt / Die
- 2–4 frames
- Recoil + color desaturation / blink if palette allows
- Death can fade or collapse

### Special (cast / roar / fly)
- Use the special feature: wings spread, mouth glows, magic aura
- Keep core body stable

## 4. Color & Effects

- Use a limited palette: 1–2 body tones + 1 accent for eyes/glow/magic.
- Glowing parts should use the brightest palette color, but avoid full-white unless specified.
- Bosses can use a second "rage" palette subset for phase changes.

## 5. Common Anti-patterns

| ❌ Bad | ✅ Good |
|--------|---------|
| Generic blob with red eyes | Distinct horns, claws, or body plan |
| Too many colors | 3–5 core colors + 1 accent |
| Symmetrical "clip-art" monster | Asymmetric wounds, horns, posture |
| Attack with no anticipation | Clear wind-up frame |
| Tiny details lost at 1× | Simplify to readable shapes |

## 6. Validation Checklist

- [ ] `pam validate-assets <project>` passes in strict mode
- [ ] Signature feature is visible at 1× scale
- [ ] Attack animation has anticipation and impact
- [ ] All frames share the same light direction
- [ ] No color outside declared palette
