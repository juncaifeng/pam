# Terrain Tile Pixel Art Guide

Ground, wall, path, water, and other repeatable tiles.

## 1. Seamless Tiling (Mandatory)

- Left edge must match right edge; top edge must match bottom edge.
- Test by placing 2×2 copies side by side before declaring done.
- Use wrap-aware noise or mirror the last row/column if needed.

## 2. Avoid Obvious Patterns

| ❌ Forbidden | ✅ Replace with |
|-------------|----------------|
| Centered star / cross / plus | Random off-center features |
| 4 equal quadrants | Voronoi / irregular cells |
| Regular sine waves | Low-frequency value noise |
| Horizontal stripe layers | Diagonal or random blobs |
| Symmetric corner motifs | Single asymmetric accent |
| Straight diagonal cracks | Random-walk segments |

## 3. Color Distribution

Use probability buckets for natural variation:
- 70% main color
- 15% dark accent (-1 palette step)
- 10% light accent (+1 palette step)
- 5% emphasis / rare feature

Avoid salt-and-pepper noise and pure-white speckles on ground tiles.

## 4. Edge Color Continuity

- Tile edges should use the same color distribution as the interior.
- No black border line around the tile.
- No drastically different 1-pixel border color.

## 5. Feature Density

- Sparse details: cracks, pebbles, grass tufts ≤ 1% of tile area.
- Features should be scattered, not clustered or aligned.
- Cracks should use short random-walk segments, never straight lines crossing the tile.

## 6. Tile Set Layout

For autotile transitions, use one of:
- **Simple**: center + 4 edges + 4 corners = 9 tiles
- **Bitmask**: 47 tiles covering all edge combinations
- **Autotile**: 5×3 grid (2×2 corners + 4 edges + center + 4 inner corners)

## 7. Validation Checklist

- [ ] `pam validate-assets <project>` passes in strict mode
- [ ] 2×2 grid test shows no visible seams
- [ ] Adjacent tile transitions feel natural
- [ ] No symmetric features (rotate 90° / flip looks different)
- [ ] Feature density ≤ 1%
- [ ] No visible white speckle noise at fullscreen scale
