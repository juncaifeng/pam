# Plant Pixel Art Guide

Trees, flowers, vines, grass, and other vegetation.

## 1. Silhouette First

- A plant must be identifiable by its overall shape, not just its color.
- For trees: clearly separate **trunk**, **main branches**, and **leaf canopy**.
- For flowers/grass: exaggerate the most recognizable part (petals, blade shape).

## 2. Canvas Rules

| Asset | Size | Notes |
|-------|------|-------|
| Tree | 64×64 or larger | Trunk at least 2 px wide, branches readable |
| Bush / shrub | 32×32 ~ 64×64 | Round or asymmetrical mass |
| Flower | 16×16 ~ 32×32 | Petal silhouette over detail |
| Grass blade / tuft | 8×8 ~ 16×16 | Simple, repeatable clusters |

## 3. Animation: Wind / Sway

- Use a **gentle sine offset** on branch/tip pixels.
- Amplitude guide:
  - 64×64 tree tips: 3–6 px horizontal sway
  - 32×32 bush: 1–3 px
  - 16×16 grass: 1–2 px
- **Phase offset**: outer branches should lag behind the trunk/center.
- Avoid all parts moving in perfect sync.

## 4. Leaf Density

- Do not fill the canopy with noise.
- Use leaf **clusters**: 3–7 pixels of the same or adjacent palette colors.
- Leave gaps (negative space) so branches remain visible.
- Maximum leaf pixels per frame: ~30–40% of canopy area.

## 5. Color & Palette

- Trunk: 2–4 brown/gray tones.
- Leaves: 2–4 green tones + 1 highlight.
- Flowers: 1–2 accent colors, keep small.
- Avoid neon or oversaturated greens unless explicitly requested.

## 6. Common Anti-patterns

| ❌ Bad | ✅ Good |
|--------|---------|
| Solid green blob | Clusters with visible branch structure |
| All leaves the same color | 2–3 tone variation by depth/light |
| Trunk invisible inside canopy | Use darker trunk + lighter leaf edges |
| Sway so subtle it looks static | Tips move 3+ px in 64×64 canvas |
| Symmetric "lollipop" canopy | Asymmetric, natural mass |

## 7. Validation Checklist

- [ ] `pam validate-assets <project>` passes in strict mode
- [ ] Trunk and at least 2 main branches are visible
- [ ] Canopy is not > 50% single-color noise
- [ ] Animation loop is seamless
- [ ] Sway amplitude matches canvas size
