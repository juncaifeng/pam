# Animal Pixel Art Guide

Quadrupeds, birds, insects, and other creatures.

## 1. Silhouette & Proportion

- Exaggerate the most distinctive features: horns, wings, tail, ears, beak.
- At small sizes (16×16–32×32), prefer a **side view** for readability.
- Use reference anatomy but simplify to the essential 3–5 shapes.

## 2. Size & Perspective

| Type | Recommended View | Notes |
|------|------------------|-------|
| Quadruped | Side or 3/4 | Show body, 4 legs, tail clearly |
| Bird | Side | Wing silhouette is key |
| Insect | Top or side | Exaggerate wings/antennae |

## 3. Animation Cycles

### Walk / Run (quadrupeds)
- 4–6 frames
- Diagonal leg pairs move together
- Body bob: 1–2 px up/down
- Tail follows with 1–2 frame delay

### Fly (birds / insects)
- 2–4 frames for fast flapping
- 6–8 frames for slow gliding
- Wing tips should reach highest/lowest point on different frames

### Idle
- Breathing, ear flick, tail wag
- Keep it subtle to avoid distraction

## 4. Color & Texture

- Use a small palette subset: 1 base + 1 shadow + 1 highlight per body region.
- Fur/feathers: suggest texture with short clusters, not individual hairs.
- Avoid noisy single-pixel salt-and-pepper patterns.

## 5. Common Anti-patterns

| ❌ Bad | ✅ Good |
|--------|---------|
| Legs blend into body | Use 1 px darker outline or negative space |
| Symmetric left/right copies | Slight asymmetry for natural pose |
| Wings too small to read | Wing span at least 50% of body width |
| All frames identical except legs | Head/tail/body should participate in motion |

## 6. Validation Checklist

- [ ] `pam validate-assets <project>` passes in strict mode
- [ ] At least 3 distinct body parts visible in silhouette
- [ ] Animation loop has no "snap" at the transition
- [ ] Feet/wings do not visually detach from body
- [ ] Color count per frame ≤ declared per-sprite budget
