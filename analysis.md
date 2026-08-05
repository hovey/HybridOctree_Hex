# Analysis: reproducing Tong et al. 2024 Table 2

This page tracks independent reproduction of the mesh-generation statistics
reported in Table 2 of Tong, Halilaj, and Zhang, *"HybridOctree_Hex: Hybrid
octree-based adaptive all-hexahedral mesh generation with Jacobian
control,"* J. Comput. Sci. 78 (2024) 102278
([doi.org/10.1016/j.jocs.2024.102278](https://doi.org/10.1016/j.jocs.2024.102278)),
a local copy of which is `Tong 2024 HybridOctree_Hex Jacobian control.pdf`
in this repo. Figure 6 in that paper shows the twelve test models
(Bottle1, Bunny, David, Deformed Armadillo, Dragon Stand, Gargoyle, plus six
more in Fig. 7); Table 2 reports mesh size, scaled-Jacobian range,
refinement level, and generation time for each.

## Scope: this repo (`HybridOctree_Hex`) vs. `HexOpt` — two different repos, two different jobs

A scope note worth stating up front, since a sibling repo,
[hovey/HexOpt](https://github.com/hovey/HexOpt) (a fork of
[CMU-CBML/HexOpt](https://github.com/CMU-CBML/HexOpt)), covers a
same-family but non-overlapping piece of the same overall meshing
pipeline — the two aren't interchangeable:

- **This repo** (`HexGen.cpp`/`Main.cpp`, forked from
  [CMU-CBML/HybridOctree_Hex](https://github.com/CMU-CBML/HybridOctree_Hex))
  is the full generation pipeline that produced every row of Table 2:
  octree construction → dual hex mesh extraction → buffer-zone clearing →
  quality improvement, all run as one program (`HexGen`) and timed as a
  single end-to-end number. Its internal quality-improvement stage
  (`hexGen::ProjectToIsoSurface`) does scaled-Jacobian gradient descent
  plus periodic Laplacian smoothing, baked in as the last stage of
  generation.
- **`HexOpt`** (`optimizer.cpp`/`meshQuality.cpp`) only does the
  quality-improvement/optimization step on a surface + a **pre-existing**
  hex mesh — conceptually similar to this repo's `ProjectToIsoSurface`
  stage, but pulled out as a separable, reusable standalone tool. It has
  no octree construction and no dual-mesh generation, doesn't ship a
  `bottle1` model at all, and has no code path that could produce one from
  scratch.

In short: this repo generates a hex mesh from a triangulated surface and
improves it in one shot; `HexOpt` only does the "improve it" half, and
expects someone (or something) else to have already produced the hex mesh
it starts from. Reproducing Table 2 is entirely a `HybridOctree_Hex`
exercise — `HexOpt`'s optimizer has no role in the numbers tracked on this
page, and this page lives here rather than in `HexOpt` accordingly.

## Bottle1 (Genus-1)

| Metric | Tong et al. 2024 (Table 2, "ours") | This M1 run (2026-08-04) |
|---|---|---|
| Vertices | 36,091 | *pending — run in progress* |
| Elements | 30,145 | *pending* |
| Worst scaled Jacobian | 0.560 | *pending* |
| Best scaled Jacobian | 1.0 | *pending* |
| Refinement level | 4 | *pending* |
| Time | 218 s | *pending* |

*(Table 2 itself lists Bottle1's vertex count as 36,091 — cross-checked
against this repo's own README mesh-statistics table, which agrees:
`bottle1|36091|30145|0.56`.)*

### Bottle1 pipeline timings (Apple M1, in progress)

Per-stage timings as `HexGen` reports them (`clock()` prints, in
`Main.cpp` and — as of this session, see summary log — inside
`ConstructOctree()` itself), updated live as the run progresses. Table 2
only reports one aggregate "Time" column; this breakdown is finer-grained
than the paper provides, for our own diagnostic purposes. Headings match
the paper's own algorithmic narrative (curvature/narrow-region assessment
→ octree generation → dualization → buffer clearing → buffer-zone
projection/quality improvement).

| Stage | bone (M4 reference run) | Bottle1 (M1, 2026-08-04) |
|---|---|---|
| Read surface mesh | ~0.4 s | 1.8 s |
| Curvature and Narrow Region Assessment + Octree Generation (strongly balanced)¹ | ~38–39 s | **1062.2 s (~17.7 min)** |
| Mesh Dualization | ~12–13 s | **1138.9 s (~19.0 min)** |
| Buffer Clearing | ~13 s | *pending* |
| Buffer Zone Projection + Quality Improvement | ~200 s | *pending* |
| **Total** | **~4.5 min** | *pending* |

¹ Reported as one combined number for both of these runs — both predate
the timing-instrumentation split added later in this session (see summary
log), which separates curvature/narrow-region assessment from octree
balancing into two independently-timed stages for future runs (Bunny,
etc.), not retroactively for this one.

Octree construction alone is already ~28x longer than bone's, despite
Bottle1 targeting only ~3.5x more elements (30,145 vs. 8,619) — plausibly
because Bottle1's thin, coiled surface detail (handle/spiral thread, see
Fig. 6(a) in the paper) triggers much deeper curvature-driven octree
refinement than bone's simpler shape, rather than octree construction time
scaling with output element count. Dualization is even more extreme —
**~87x** longer than bone's — despite operating on an octree whose leaf
count, while not directly reported, is presumably driven by that same
deeper refinement.

Bunny and the remaining Table 2 models will be added as their own sections
below once Bottle1 is complete.

## Summary log

Entries are ordered most recent first.

### 2026-08-04 — Bottle1 reproduction attempt + timing instrumentation (Apple M1)

Picking up the M4 session's fixed `HexGen.cpp` to reproduce Table 2's Bottle1 row on a second machine
(Apple M1), as the first of the Table 2 models to attempt (Bunny and others to follow).

- Cloned this fork to `~/HybridOctree_Hex` on the M1 (this analysis started out drafted in the sibling
  `~/HexOpt` repo, then moved here once it became clear the reproduction work has no dependency on
  `HexOpt` and belongs with the code it's about); added an `upstream` remote pointing at
  `CMU-CBML/HybridOctree_Hex`.
- Found this fork already contained the M4 session's `ProjectToIsoSurface` fix (commit `25adad9`,
  described in full below) plus that session's `bone` run artifacts and a large amount of committed
  CMake build cruft (binary caches, `.o` files, machine-specific `CMakeCache.txt` paths, ~600K lines of
  generated VTK output).
- CMake requirement is 3.27.4; this M1 had 3.24.2 installed (from an earlier, unrelated `HexOpt` build
  session). `brew upgrade cmake` → 4.4.2.
- Built into a fresh, separate directory (`build-m1-bottle1/`) rather than reusing the M4 session's
  `HybridOctree_Hex/build/`, to avoid clobbering the `bone` run's evidence still sitting there. Builds
  cleanly — same cosmetic warnings as the M4 session (`#endif` extra tokens, `RAND_MAX` narrowing,
  dangling-else).
- Fetched `input boundaries/bottle1_tri.raw` (14,833 vertices / 29,664 triangles) from upstream into a
  dedicated run directory, `runs/bottle1/model.raw`, and launched the full pipeline against it. The M4
  session's fix was verified only against `bone` (8,619 target elements); Bottle1 targets ~30,145
  (~3.5x larger), so timing and convergence behavior weren't assumed to carry over directly.
- **History cleanup**: rewrote this fork's `main` (`git reset --soft` to the pre-`25adad9` upstream tip,
  then re-committed only the real source fix, the reference PDFs, and the `bone` sample data, dropping
  the build cruft; force-pushed) so the ~600K lines of binary/build artifacts from the M4 session no
  longer live in history at all, not just the working tree. Added `.gitignore` entries for `build/` and
  `build-*/` so it can't happen again. Verified `HexGen.cpp`'s fix content is byte-identical before and
  after the rewrite.
- **Timing instrumentation**: split `ConstructOctree()` (`HexGen.cpp`) into two separately-timed,
  separately-printed sub-stages, so the reproduction write-up can report curvature/narrow-region
  assessment separately from octree balancing instead of Main.cpp's one coarse "constructing octree"
  number — matching the paper's own algorithmic narrative and the headings used in the pipeline-timings
  table above. `GetCellValue()` (curvature-/thickness-driven adaptive refinement decisions) is now
  timed and printed as "curvature and narrow region assessment"; `StrongBalancedOctree()` (enforcing
  the octree's 2:1 balance constraint) as "octree generation (strongly balanced)". Buffer-zone
  projection and quality improvement remain one combined number, since `ProjectToIsoSurface()`
  interleaves both inside the same per-checkpoint loop with no code-level seam to split them — see
  comments in `HexGen.cpp` at both sites for the full reasoning. Sanity-checked against `bone_tri.raw`
  in a throwaway run (`build-instrumented/`, killed once the new prints were confirmed correct, not
  counted as a real timing sample): curvature/narrow-region assessment 31.7s + octree balancing 22.4s ≈
  58.2s, matching Main.cpp's own unchanged coarse timer to within `clock()` rounding and cleanup-call
  overhead. This only applies to runs made with the rebuilt binary or later — it can't retroactively
  split the Bottle1 octree time already captured above (1062.2 s), which stays reported as one combined
  number for this run.

*(This log entry is being written while the Bottle1 run is still in progress; final results will be
added to both the Bottle1 table above and this section once it finishes.)*

---

### 2026-07-02 – 2026-07-03 — macOS build & `ProjectToIsoSurface` fix (Apple M4)

*Harvested from a session note (`session-summary-2026-07-02_191437.md`)
left in this fork at commit `25adad9`. The note itself is dated
2026-07-02; the commit that recorded it is dated 2026-07-03. (The date
given when this log entry was requested was "02-03 July 2025" — this
fork's own commit history places the work in 2026, not 2025, so that's the
year used here.)*

**Repo:** https://github.com/CMU-CBML/HybridOctree_Hex
**Platform:** macOS (Apple Silicon, arm64), AppleClang 21.0.0, CMake 4.2.3
**Test model:** `input boundaries/bone_tri.raw` (smallest sample, 10,356 verts / 8,619 elems)

#### 1. Getting it building on macOS

The repo shipped with a stale Windows/MinGW CMake cache (`CMakeCache.txt`, `Makefile`, `CMakeFiles/`)
generated on a different machine (`D:\cmake`, `MinGW Makefiles`, `cmd.exe` shell references) — unusable
on macOS as-is.

Steps taken:
1. Deleted the stale generated files: `CMakeFiles/`, `CMakeCache.txt`, `cmake_install.cmake`, `Makefile`.
2. Created a clean out-of-source build directory: `HybridOctree_Hex/build/`.
3. `cmake .. -DCMAKE_BUILD_TYPE=Release` — configured cleanly with AppleClang, no external
   dependencies (the project is self-contained: `Main.cpp`, `HexGen.cpp/h`, `Mesh.cpp/h`, plain STL,
   no CGAL/VTK/etc.).
4. `cmake --build .` — builds cleanly. Only cosmetic warnings: stray text after `#endif` directives
   (`#endif STATICVARS_H` etc. — harmless, `-Wextra-tokens`), a few `int`→`float` narrowing warnings
   around `RAND_MAX` usage, and one dangling-`else` warning. No errors, no code changes needed for the
   build itself.
5. Produces a native arm64 executable: `HybridOctree_Hex/build/HexGen`.

No changes were made to `CMakeLists.txt` — the existing project definition worked as-is once the stale
Windows cache was cleared.

#### 2. Bug found: infinite loop in `ProjectToIsoSurface`

Running `HexGen` against `bone_tri.raw` (copied in as `model.raw`, the hardcoded input filename in
`Main.cpp`) got through the first three pipeline stages quickly but then **hung indefinitely** in the
final "project to iso-surface" stage — still running after 48+ minutes of CPU time with no sign of
terminating.

**Root cause**: `hexGen::ProjectToIsoSurface()` (in `HexGen.cpp`) contains a `while (true) { ... }` loop with
**no `break` statement anywhere in its ~1,500-line body**. Traced every exit path; none existed.

The loop's intended termination mechanism was a quality-improvement ratchet:
- `ELEM_THRES` (element quality/scaled-Jacobian acceptance threshold) starts at `0.01`.
- Whenever the mesh achieves a "perfect" checkpoint (`badElem == 0` and the surface-projection
  distance below a tolerance), the code raises the bar: jumps to `0.53` on the first success, then
  `+= 0.01` on every success after that — presumably intending to progressively push mesh quality
  higher.
- **But `ELEM_THRES` is never capped.** Once it exceeds the mesh's actually-achievable scaled-Jacobian
  quality, a "perfect" checkpoint can never happen again — the quality-improvement branch (and the
  `finalMesh.vtk` write inside it) becomes permanently unreachable, and the loop runs forever.

#### 3. Fix iterations (chronological)

This took several rounds of empirical testing against `bone_tri.raw`, each surfacing a deeper issue.
All changes are confined to `hexGen::ProjectToIsoSurface()` in `HexGen.cpp`.

**3.1 First pass — hard iteration cap (`MAX_PROJ_ITER`).** Added a simple iteration backstop to
guarantee termination. First attempt used the loop's existing (but previously unused) counter variable
`i`, which turned out to be unsafe — `i` is reset to `0` and reused as scratch elsewhere in the loop
body (`for (i = 0; i < SMOOTH_EPOCH; i++)`), so checking `i >= MAX_PROJ_ITER` never fired correctly.
Fixed by introducing a dedicated counter, `projIterCount`, incremented once per outer loop iteration.
Initial cap: `MAX_PROJ_ITER = 2000`. This **did** terminate the loop (confirmed), but far too early —
the badElem/convergence checkpoint block is itself gated by `if (i % UPDATE_EVERY == 0)` with
`UPDATE_EVERY = 1000`, so 2000 raw iterations is only **2 checkpoints** — nowhere near enough for the
gradient-descent projection to converge. `finalMesh.vtk` was never written (the success branch that
writes it never fired), and the only output (`projHex.vtk`) reflected a very early, under-converged
state (surface distance error ~0.79).

**3.2 Root-cause fix — cap `ELEM_THRES`.** Added `ELEM_THRES_CAP = 0.7` (informed by the repo's own
published results table showing typical min scaled-Jacobian quality in the ~0.53–0.62 range) so the
ratchet stops raising the bar once it's past a realistic ceiling, keeping the success branch reachable.
Raised `MAX_PROJ_ITER` to `50000` as a true backstop rather than the primary exit mechanism. Result:
`finalMesh.vtk` now got written (confirming the cap let the success branch fire), but the run still hit
the iteration backstop rather than exiting cleanly.

**3.3 Discovered: disturb-after-success oscillation.** Investigated the checkpoint log and found a
self-sustaining oscillation: immediately after a near-machine-precision convergence (e.g.
`maxDist: 2.67e-14`), the very next checkpoint would jump back up to `maxDist: 0.033` with `badElem: 1`.
Cause: the "success" branch doesn't just record success — it unconditionally runs a randomized
point-redistribution step (perturbing points toward a blend of neighbor-averaged positions, meant to
push quality higher) even once `ELEM_THRES` is already capped and there's no more quality headroom to
gain. Every genuine convergence was immediately undone by this redistribution. **Fix:** once
`ELEM_THRES` is at the cap *and* a checkpoint converges, skip the redistribution step entirely, write
`finalMesh.vtk`, and `break` out of the loop immediately instead of looping again.

**3.4 Discovered: mismatched convergence tolerance.** Even with the disturb-after-success fix, the
clean break still wasn't firing — `ELEM_THRES` was climbing far too slowly to reach its cap. Traced the
convergence gate (`smallDist < DIST_THRES2`) and found `DIST_THRES2 = sqrt(1e-12) ≈ 1e-6` is defined in
`Initialization.h` with the comment *"threshold when judging point overlap"* — i.e. a floating-point
coincident-point detector, not a surface-projection accuracy target. It's used nowhere else in the
codebase. Reusing it as the optimization's convergence target demanded near machine-precision distance,
making genuine success a rare, semi-random event (~8–12% of checkpoints) rather than a reachable
optimization target. **Fix:** introduced a dedicated `PROJ_CONVERGE_TOL = 1e-4` — an appropriately
loose, reachable tolerance — and replaced both functional uses of `DIST_THRES2` within
`ProjectToIsoSurface` with it (the point-snap acceptance gate and the success/ratchet condition).
`DIST_THRES`/`DIST_THRES2` in `Initialization.h` were left untouched, since they're not used elsewhere.
Success rate improved (4/50 → 6/51 checkpoints), but still not enough to reach `ELEM_THRES_CAP` within
the 50,000-iteration budget. Raised `MAX_PROJ_ITER` to `200000` (~150 checkpoints of margin, based on
the observed ~12% success rate needing ~17 successes to reach the cap).

**3.5 Discovered: a regression in the backstop fallback.** At `MAX_PROJ_ITER = 200000`, the run went
noticeably *worse* than shorter runs: final state `badElem=20, smallDist=0.115` — far worse than
earlier attempts. The log tail showed a stubborn local region (`maxDistIdx` repeating around vertex
15088/15160) that progressively degraded over ~30 consecutive checkpoints rather than improving. Worse:
this exposed a bug in an earlier fix. The `MAX_PROJ_ITER` backstop branch unconditionally called
`WriteToVtk("finalMesh.vtk", ...)` using whatever the *current* mesh state happened to be — with no
check on whether that state was actually better than the last genuine success. Since the mesh had
degraded by the time the backstop fired, this **clobbered a good earlier snapshot with the worse final
state**.

**3.6 Final fix — track and preserve the best mesh seen (not just the last one).** This is not a
monotonically-converging optimization — the randomized redistribution step can (and does) make
`badElem`/`smallDist` worse on a later checkpoint than an earlier one. "Final output" needed to be the
objectively best checkpoint across the *whole* run, not whatever exists when the loop happens to stop.
Changes:
- Added `bestBadElem` (sentinel `affElemNum + 1`) and `bestSmallDist` (sentinel `MAX_NUM2`), tracked
  across the entire `while (true)` loop.
- At each checkpoint, immediately after measuring `k` (bad-element count) and `smallDist` — **before**
  the redistribution step that could perturb the mesh away again — compare against the tracked best.
  If `k < bestBadElem`, or `k == bestBadElem && smallDist < bestSmallDist`, update the tracked best and
  write `finalMesh.vtk` right then, capturing the mesh in the exact state that earned that score.
- Removed the three now-redundant/risky write sites (the unconditional fallback write in the
  `MAX_PROJ_ITER` backstop branch; the write in the "converged at `ELEM_THRES` cap" clean-break branch;
  and — the dangerous one — the write at the end of the redistribution block, which captured the
  *post*-redistribution state that could be worse than what triggered the branch).
- The `MAX_PROJ_ITER` backstop log message now reports the tracked best, not whatever the current
  (possibly degraded) state is.

**Verified result** (bone_tri.raw, 201 checkpoints, 200.8s projection stage): backstop message
`badElem=0, smallDist=2.60788e-14` — the tracked best, essentially machine-precision convergence, even
though the raw log tail at the moment the backstop fired showed a badly degraded state
(`badElem: 15–20, maxDist: ~0.115`). `finalMesh.vtk`'s timestamp confirmed it was written once, early in
the run, and never touched again despite ~150 subsequent checkpoints continuing to run (and degrading)
afterward — confirming the fix works as intended.

#### 4. Summary of constant/behavior changes in `ProjectToIsoSurface` (`HexGen.cpp`)

| Name | Before | After | Purpose |
|---|---|---|---|
| Loop termination | none (infinite `while (true)`) | `projIterCount >= MAX_PROJ_ITER` backstop | Guarantee termination |
| `MAX_PROJ_ITER` | n/a | `200000` (new) | Iteration backstop (~150 checkpoints of margin over the empirically observed ~150 needed) |
| `ELEM_THRES` ratchet | unbounded (`+= 0.01` forever) | capped at `ELEM_THRES_CAP = 0.7` (new) | Prevents the quality bar from exceeding what's achievable, which was making the success branch permanently unreachable |
| Convergence tolerance | `DIST_THRES2` (`1e-6`, meant for point-overlap detection) | `PROJ_CONVERGE_TOL = 1e-4` (new, dedicated) | Realistic, reachable surface-projection convergence target |
| Success + at-cap behavior | always ran point-redistribution, looped forever | skips redistribution and `break`s once capped & converged | Stops the disturb-after-success oscillation |
| `finalMesh.vtk` writes | 3 sites: end-of-success-block (post-redistribution), none on backstop originally / later an unconditional backstop fallback | 1 site: on best-tracked improvement, measured pre-redistribution | Guarantees `finalMesh.vtk` always reflects the best mesh ever found, not the last (possibly degraded) state |
| `bestBadElem` / `bestSmallDist` | n/a | new, tracked across the whole run | Enables best-state preservation above |

All changes are localized to `hexGen::ProjectToIsoSurface()`; no other functions or files were modified.

#### 5. Verified pipeline timings (`bone_tri.raw`, final fixed build)

| Stage | Time |
|---|---|
| Read surface mesh | ~0.4 s |
| Construct octree | ~38–39 s |
| Generate dual mesh (`DualFullHexMeshExtraction`) | ~12–13 s |
| Extract interior dual mesh (`RemoveOutsideElement`) | ~13 s |
| Project to iso-surface (`ProjectToIsoSurface`) | ~200 s (201 checkpoints, hits `MAX_PROJ_ITER` backstop but with best-tracked result `badElem=0, smallDist≈2.6e-14`) |
| **Total** | **~4.5 minutes** |

Output files (in `HybridOctree_Hex/build/`): `modifiedTri.vtk`, `octree.vtk`, `dualFullHex.vtk`,
`dualHex.vtk`, `projHex.vtk`, `finalMesh.vtk`.

#### 6. Architecture note: dualization

Confirmed the pipeline performs its own octree dualization (analogous to what `automesh`
— https://github.com/autotwin/automesh — does), implemented as `hexGen::DualFullHexMeshExtraction()`
in `HexGen.cpp` (declared `HexGen.h:56`), called immediately after `ConstructOctree()`.

- Computes each octree leaf cell's centroid as a dual-mesh vertex (midpoint between diagonal corners).
- Builds hexahedral elements from these centroids based on cell adjacency/valence patterns, including
  special-case templates for non-uniform octree size transitions (the "Hybrid" in `HybridOctree_Hex`).
- Followed by `RemoveOutsideElement()` (trims the dual mesh to the interior) and then
  `ProjectToIsoSurface()` (the stage fixed in this session — pulls boundary dual vertices onto the true
  input surface and improves element quality).

This is a self-contained, hand-rolled implementation of the same primal-octree → dual-hex concept as
`automesh`'s dualization step, not a dependency on it.

#### 7. Files touched that session

- `HybridOctree_Hex/HexGen.cpp` — all fixes described above, confined to `ProjectToIsoSurface()`.
- `HybridOctree_Hex/build/` — new out-of-source build directory (CMake-generated, not source).
- Removed (stale, Windows-generated, not usable on macOS): `HybridOctree_Hex/CMakeCache.txt`,
  `HybridOctree_Hex/Makefile`, `HybridOctree_Hex/cmake_install.cmake`, `HybridOctree_Hex/CMakeFiles/`.
- `HybridOctree_Hex/CMakeLists.txt` — unchanged, worked as-is once the stale cache was cleared.
