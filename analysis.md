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
| Vertices | 36,091 | **218,898** ⚠️ |
| Elements | 30,145 | **192,098** ⚠️ |
| Worst scaled Jacobian | 0.560 | **0.010** ⚠️ |
| Best scaled Jacobian | 1.0 | 1.0 |
| Refinement level | 4 | not measured (see note below) |
| Time | 218 s | 4109.3 s (~68.5 min), capped run ⚠️ |

*(Table 2 itself lists Bottle1's vertex count as 36,091 — cross-checked
against this repo's own README mesh-statistics table, which agrees:
`bottle1|36091|30145|0.56`.)*

**⚠️ These numbers do not reproduce Table 2, and not only because of the
convergence cap.** Two separate issues, not one:

1. **Mesh size is ~6x too large.** Vertex/element counts come from
   `RemoveOutsideElement`'s output topology (`ProjectToIsoSurface` only
   repositions points, confirmed by the killed full-budget attempt and
   the capped rerun producing byte-identical counts) — so this mismatch
   is present regardless of how long quality improvement runs, and isn't
   explained by the `MAX_PROJ_ITER` cap. The same repo's own `bone`
   sample shows the same pattern at a smaller ratio: our M1 run produced
   19,639 vertices / 16,590 elements against this repo's own published
   10,356 / 8,619 (~1.9x). Both runs used the shipped, unmodified
   `VOXEL_SIZE`/`C_THRES`/`H_THRES` thresholds in `Initialization.h` — no
   octree-depth parameter was touched. The M4 session that fixed
   `ProjectToIsoSurface` validated the *algorithm's* convergence behavior
   against `bone` but never checked its *output mesh size* against the
   published number, so this gap went undetected until now.
   **Root-caused 2026-08-05 — not a HexOpt-style missing-code gap after
   all; see that day's summary log entry**: the shipped `C_THRES` curvature
   thresholds don't match the paper's stated values, and separately, this
   codebase's actual curvature computation doesn't match the paper's
   stated formula either. Fixed by empirical recalibration (see below).
2. **Worst SJ (0.010) reflects the deliberately-capped, under-converged
   run** (see the `MAX_PROJ_ITER` discussion below and in the summary
   log) — `ELEM_THRES` never advanced past its initial floor of `0.01`
   because no checkpoint reached `badElem=0` *and* the convergence
   tolerance simultaneously within the reduced 20-checkpoint budget, so
   this number isn't informative about the algorithm's achievable
   quality the way bone's 0.590 (this M1) / 0.61 (repo's published number)
   is. Best SJ (1.0) matches regardless, since at least one element in
   any reasonably-sized mesh tends to land near-ideal.

Given finding (1), the vertex/element/worst-SJ mismatches here shouldn't
yet be read as "the fix doesn't work" or "this M1 can't reproduce Table
2" — they're two distinct, separable problems (mesh-size and
convergence-budget), and the mesh-size one predates and is independent of
anything done in this session.

### Bottle1 pipeline timings (Apple M1)

Per-stage timings as `HexGen` reports them (`clock()` prints, in
`Main.cpp` and — as of this session, see summary log — inside
`ConstructOctree()` itself), updated live as the run progresses. Table 2
only reports one aggregate "Time" column; this breakdown is finer-grained
than the paper provides, for our own diagnostic purposes. Headings match
the paper's own algorithmic narrative (curvature/narrow-region assessment
→ octree generation → dualization → buffer clearing → buffer-zone
projection/quality improvement).

Percentages are each stage's share of that *column's own* total, so each
column's percentages sum to 100% once the column is complete. Columns
still mid-run show percentages as "pending" — a partial-time percentage
would be a moving target as remaining stages add to the denominator, so
these are only filled in once each column's run finishes and its final
total is known. Sub-rows (curvature/narrow-region and octree-balancing,
where measured separately) show their share of the *combined* row instead
of the grand total — including them in the grand-total column as well
would double-count that time — so the 100% breakdown for each column
comes from exactly five rows: read, combined octree, dualization, buffer
clearing, and projection+quality improvement.

| Stage | bone (M4, 2026-07-02) | bone (M1, 2026-08-04) | Bottle1 (M1, 2026-08-04) |
|---|---|---|---|
| Read surface mesh | ~0.4 s (0.2%) | 0.57 s (0.1%) | 1.79 s (0.0%) |
| Curvature and Narrow Region Assessment | n/a¹ | 31.6 s (57.0% of combined) | n/a¹ |
| Octree Generation (strongly balanced) | n/a¹ | 19.6 s (35.4% of combined) | n/a¹ |
| — combined (curvature + octree), as `Main.cpp` reports it¹ | ~38–39 s (14.6%) | 55.3 s (13.4%) | **1062.2 s (~17.7 min) (25.9%)** |
| Mesh Dualization | ~12–13 s (4.7%) | 17.1 s (4.1%) | **1138.9 s (~19.0 min) (27.7%)** |
| Buffer Clearing | ~13 s (4.9%) | 21.7 s (5.2%) | **815.1 s (~13.6 min) (19.8%)** |
| Buffer Zone Projection + Quality Improvement | ~200 s (75.6%) | **319.4 s (~5.3 min) (77.2%)** | **1091.3 s (~18.2 min) (26.6%)³** |
| **Total** | **~4.5 min (264.4 s summed² ⇒ 100%)** | **419.5 s (~7.0 min, `time -l` real ⇒ 100%)** | **4109.3 s (~68.5 min summed³ ⇒ 100%)** |

¹ The M4 bone run and the Bottle1 run both used a pre-split binary, so
curvature/narrow-region assessment and octree balancing are only
available as one combined number for those two ("— combined" row). The
M1 bone run (added specifically to get a same-machine comparison point,
and launched after the timing-instrumentation split) reports both
substages separately; they sum to 92.5% of the combined cell, not 100%,
because `Main.cpp`'s own combined timer also includes a small amount of
cleanup-call/`clock()`-rounding overhead between and around the two
sub-measurements.

² `bone` (M4)'s five stage values were originally reported as ranges
(e.g. "~38–39 s"); percentages use each range's midpoint, summing to
264.4 s — close to, but not identical to, the "~4.5 minutes" total
originally reported for that run (itself a rounded figure). The summed
264.4 s, not the rounded ~4.5 min, is the percentage denominator, so the
column's percentages are internally consistent and sum to exactly 100%.

Every stage so far is dramatically slower than bone's, and by increasingly
inconsistent factors relative to the ~3.5x element-count ratio: octree
construction ~28x (~21x against the M1 bone number), dualization ~87x,
buffer clearing ~63x. This pattern (large, non-uniform multipliers rather
than a roughly constant ~3.5x across stages) points toward Bottle1's thin,
coiled surface detail (handle/spiral thread, see Fig. 6(a) in the paper)
triggering much deeper curvature-driven octree refinement than bone's
simpler shape — i.e. the real driver is octree depth/leaf count, not
final output element count, and that deeper octree then compounds through
every downstream stage.

The M1-vs-M4 bone comparison also rules out "this M1 is just a slower
machine" as the main explanation. Now that bone (M1) has finished, the
gap holds up across every stage, not just octree construction: read
+40% slower, combined octree +40%, dualization +37%, buffer clearing
+67%, projection +59%, total +55% (419.5 s vs. ~270 s). That's a
consistent, modest hardware gap in the same direction throughout — nowhere
close to Bottle1's ~20–90x factor over bone on the *same* M1. So the
dominant effect really is Bottle1's own geometry, not the machine.

Bone (M1)'s projection stage also hit the same `MAX_PROJ_ITER` backstop as
the M4 run, landing on an almost identical best result
(`smallDist=2.60788e-14` on both machines, to 6 significant figures) —
consistent with the redistribution step's `rand()` calls never being
seeded (no `srand()` call anywhere in the codebase), so the "randomized"
sequence is actually the same deterministic sequence on every run,
regardless of machine.

³ Bottle1's projection stage was initially let run at bone's
`MAX_PROJ_ITER=200000` setting like the other columns, but killed after
24 checkpoints (~22 min, `maxDist=0.00473` with `badElem=0` at the last
checkpoint before stopping) once its per-checkpoint cost became clear:
~56 s/checkpoint vs. bone's ~1 s/checkpoint, which extrapolated to
several hours for the full 200-checkpoint budget. `MAX_PROJ_ITER` was
reduced to `20000` (20 checkpoints) specifically for this run — a
deliberate speed/convergence trade-off, documented in `HexGen.cpp`'s
comments at the constant — and the capped rerun resumed from the
already-computed `octree.vtk`/`dualFullHex.vtk`/`dualHex.vtk` (via a
temporary, uncommitted `Main.cpp` tweak, reverted immediately after
launching) rather than redoing the ~50 minutes of earlier stages. It hit
that reduced backstop, landing on best result `badElem=0, smallDist=
0.62311` — genuinely under-converged compared to bone's ~1e-14 (see the
Bottle1 results table above for what this means for the reported worst
SJ). The killed full-budget attempt's log/mesh are preserved as
`runs/bottle1/run.log.full-attempt-killed` /
`finalMesh.vtk.full-attempt-killed`. Total in the table above (4109.3 s)
sums the *first* attempt's four completed pre-projection stages (the real
computation) plus the *capped rerun's* projection stage (1091.3 s) — the
~22 min spent on the killed attempt's partial projection work is excluded
as not contributing to the final result.

Mesh-size and scaled-Jacobian stats (`finalMesh.vtk`'s vertex/element
counts, worst/best SJ) are reported in the Bottle1 results table above,
computed via a new tool, `scripts/scaled_jacobian_stats.cpp` — a
standalone C++ program that parses a VTK hex mesh and computes min/max
scaled Jacobian using `HexGen.cpp`'s own `Sj()` function copied verbatim
(not reimplemented), so its output is guaranteed consistent with what
`HexGen` itself computes internally. Validated against bone's
`finalMesh.vtk` first (worst 0.590, best 1.0 — close to the repo's
published 0.61 for that model) before trusting it on Bottle1.

Bunny and the remaining Table 2 models will be added as their own sections
below once Bottle1's open questions (mesh-size mismatch, convergence
budget) are resolved or at least better understood.

## Bone (calibration testbed, not a Table 2 model)

`bone` isn't one of Table 2's twelve models — it's the smallest sample in
this repo's own broader `input boundaries`/`our results` collection, with
published stats in this repo's own README rather than in the paper. The
M4 session picked it as a fast iteration testbed for the
`ProjectToIsoSurface` fix; the 2026-08-05 session reused it the same way,
to calibrate `C_THRES` against a small, fast-to-rerun model before
spending Bottle1-scale time on each attempt. See the summary log below for
the full investigation; this table is the result.

| `C_THRES` | Vertices | Elements | Worst SJ | Best SJ | Total time |
|---|---|---|---|---|---|
| **Published (this repo's README)** | **10,356** | **8,619** | **0.61** | 1.0 | — |
| Buggy, shipped `{0,0,0.4,0.8,1.6}` (2026-08-04) | 19,639 (1.9x) | 16,590 (1.9x) | 0.590 | 1.0 | 419.5 s |
| Paper-literal `{0.5,1,2,4,8}` (2026-08-05) | 4,584 (0.44x) | 3,570 (0.41x) | 0.550¹ | 1.0 | 117.75 s |
| **v1.2 historical `{0.1,0.2,0.4,0.8,1.6}` (2026-08-05, adopted)** | **14,856 (1.43x)** | **12,608 (1.46x)** | **0.600** | 1.0 | 313.80 s |

¹ An earlier run at this same `C_THRES` value, using a leftover
`MAX_PROJ_ITER=20000` cap carried over from the Bottle1 work rather than
bone's own established `200000` budget, produced worst SJ 0.011 —
resolved once re-run with the correct budget (0.550, shown here),
confirming that discrepancy was a convergence-budget confound, not a
quality problem with the paper-literal thresholds themselves.

v1.2's historical thresholds give the closest match on every metric
simultaneously (size within ~1.5x, worst SJ within 0.01 of published) and
were adopted for the Bottle1 redo. Neither the buggy nor the paper-literal
values are being pursued further — see the summary log for why an exact
match isn't expected from either given the curvature-formula mismatch.

## Summary log

Entries are ordered most recent first.

### 2026-08-05 — Root-causing the mesh-size mismatch; redoing bone and Bottle1 (Apple M1)

The 2026-08-04 session's Bottle1 and bone runs both produced meshes far
larger than published (Bottle1 ~6x, bone ~1.9x), left unexplained at the
time. This session root-causes it and redoes both runs.

**`C_THRES` mismatch, found by cross-referencing the paper against
`Initialization.h`.** Section 2.1 of the paper (p.3) states the curvature
refinement thresholds explicitly: *"Five curvature thresholds
`Gthres = {0.5, 1, 2, 4, 8}` are adopted. If an octree cell at level `l+4`
... satisfies `G(l+4) > Gthres[l]`, we refine it to level `l+5`."* The
shipped `Initialization.h` (unmodified from upstream, current release
"v1.3") had `C_THRES[5] = { 0, 0, 0.4, 0.8, 1.6 }` — nothing like the
paper's stated values. Checking this file's git history across releases
showed it never has matched, and got worse over time rather than better:

| Release | `C_THRES` |
|---|---|
| v1.2 (`2e5f4c0`) | `{0.1, 0.2, 0.4, 0.8, 1.6, 3.2}` (6 levels) |
| v1.2 (`f9e667c`) | `{0.1, 0.2, 0.4, 0.8, 1.6}` (dropped to 5) |
| v1.3 (`220c53f`, shipped) | `{0, 0, 0.4, 0.8, 1.6}` (**first two zeroed**) |

`H_THRES` (`{16, 8, 4, 2, 1}`) and `VOXEL_SIZE` (`10`) have been stable
across every release and already match the paper's stated
`Tthres = {16,8,4,2,1}` and its "resulting octree level ranges from 5 to
9" — only `C_THRES` was the problem. Mechanism: the refinement rule is
"refine if `G > threshold`". With `C_THRES[0] = C_THRES[1] = 0`, the
condition `G(level 4) > 0` and `G(level 5) > 0` is true for essentially
any curved region (Gaussian curvature is only exactly zero on flat
patches), making the two coarsest refinement checks effectively
unconditional — forcing far more of the octree to refine than the paper's
thresholds intend, cascading into every downstream stage (more octree
cells → more dual-mesh elements → proportionally slower dualization,
buffer clearing, and projection).

**Curvature formula/units mismatch, found by comparing the paper's stated
formula against the actual implementation.** The paper's `G` is a
cotangent-Laplacian magnitude normalized by local Voronoi cell area (units
~ 1/length): `‖Σ (cot α + cot β)(Pj − Pi)‖ / (4·Ai)`. Searching the
codebase for any cotangent- or Voronoi-based computation found none — the
only curvature computation anywhere (`HexGen.cpp`, inside `ReadRawData`,
called from `InitializeOctree`) is `r[point] += (dihedral_angle − π)²`,
summed over each edge incident to that point, where `dihedral_angle` is
the angle between the two triangle faces sharing that edge. This is a
different mathematical quantity (squared angular deviation from flat, no
area normalization, units of radians²) from the paper's stated formula
(a normalized curvature magnitude, units ~ 1/length). Because of this,
neither the buggy shipped thresholds nor the paper's literal `Gthres`
values can be "provably correct" for what this code actually computes —
there's no valid unit conversion between the two formulas. This explains
why fixing `C_THRES` to the paper's literal values didn't land on the
published mesh size either (see below) — empirical recalibration against
published stats, not formula-derived threshold values, is the right path
forward pending a possible future fix to the curvature formula itself
(out of scope for this session).

**Bone recalibration (see the Bone section above for the full results
table).** Tested three `C_THRES` values against bone (this repo's own
published 10,356 vertices / 8,619 elements / worst SJ 0.61), each with the
full `MAX_PROJ_ITER=200000` budget (bone's own established setting — one
intermediate run accidentally used a leftover `MAX_PROJ_ITER=20000` cap
carried over from the 2026-08-04 Bottle1 work, caught and corrected before
drawing conclusions from it):
- Buggy shipped values: 1.9x too big, worst SJ 0.590 (close on quality,
  wrong on size).
- Paper-literal values: 2.3x too *small* — overshot in the other
  direction — worst SJ 0.550 once re-run with the correct iteration
  budget (an earlier run at 0.011 was purely the leftover-cap confound
  described above, not a quality problem with these thresholds).
- v1.2's historical values (a previously-shipped value from this repo's
  own git history, not an arbitrary guess — chosen because it sits between
  the other two): closest match on every metric simultaneously — 1.43-1.46x
  on size, worst SJ 0.600 (within 0.01 of published). Adopted for the
  Bottle1 redo.

**Bottle1 redo, and a second, separate bottleneck found.** With
`C_THRES` recalibrated, launched Bottle1 with the full `MAX_PROJ_ITER=
200000` budget. Streamed per-stage completions live rather than polling
after the fact. `GetCellValue()`'s curvature/narrow-region assessment
substage alone took 724.4s (~12 min) — nearly as long as the *entire*
combined octree stage took under the old buggy thresholds (1062s), and
drastically disproportionate to bone's 11.0s for the same substage with
the same thresholds (65.8x longer, vs. only ~2.45x more input triangles:
29,664 vs. 12,088). Paused the run (killed after octree construction
finished, ~34 min in) to investigate rather than let it continue on an
unbounded timeline.

**First hypothesis (wrong, corrected below)**: initially suspected
`GetCellValue()`'s thickness/narrow-region check (`HexGen.cpp:950-986`) —
a brute-force all-pairs loop, for every triangle `i` ray-testing against
every other triangle `j > i` via `Intersect()`, with no spatial
acceleration structure (no BVH/octree/kd-tree) and no early exit — exactly
the paper's described operation ("shooting a ray... to find the shortest
intersection with other triangular elements"), implemented as literal
O(n²) over the input triangle count. Reasoned that O(n²) scaling
(bone: 12,088 triangles → ~73M pairs; Bottle1: 29,664, 2.45x more →
~440M pairs, **6.0x more**) explained part of the 65.8x slowdown, with an
unexplained ~11x remainder attributed to `Intersect()` costing more per
call on Bottle1's geometry.

**Actual root cause, confirmed by direct instrumentation**: this was
wrong — the O(n²) triangle-pair loop is fast (bone 1.57s, Bottle1 9.7s;
its trailing `unordered_set`-based dedup step is negligible, <0.003s for
both). Added temporary `clock()` instrumentation splitting
`GetCellValue()`'s three phases (raw O(n²) loop, dedup, and the trailing
`ComputeCellValue()` recursive sweep it calls at line ~1035) confirmed the
real cost is almost entirely the third phase:

| Phase | bone | Bottle1 | Ratio |
|---|---|---|---|
| O(n²) raw loop (thickness/curvature candidate collection) | 1.57 s | 9.70 s | 6.2x |
| `unordered_set` dedup | 0.0007 s | 0.0023 s | 3.3x |
| `ComputeCellValue()` recursive sweep | ~9.45 s (inferred) | **720.6 s** | **~76x** |

`ComputeCellValue()` (`HexGen.cpp:1039` onward) recurses over every octree
node; at each of the five tested refinement levels (4-8, corresponding to
`refineTri0..4`/`refineTriPt0..4`) it does a **linear scan through that
level's entire candidate list** for every cell being classified at that
level (e.g. `HexGen.cpp:1217-1241` for the coarsest level, scanning
`refineTriPt0`/`refineTri0` — up to 41,442/64,506 raw candidates for
Bottle1 — with up to 12 `Intersect()` box-face calls per triangle
candidate), stopping only on the first hit. There's no spatial index (no
BVH, no reuse of the octree structure itself, no spatial hash) for this
lookup — it's the same brute-force pattern as the (much cheaper) O(n²)
loop, but applied per-*octree-cell* rather than per-*triangle*, and the
candidate lists it scans are themselves 2.9-3.2x larger for Bottle1
(deduped `refineTri0`: 15,444 vs. bone's 5,386; `refineTriPt0`: 6,036 vs.
3,134). Both factors — more octree cells needing classification at deep
levels (Bottle1's coiled/spiral surface drives refinement into more of the
volume) and larger per-level candidate lists to scan against each one —
compound multiplicatively rather than adding, which is why the observed
~76x so heavily overshoots the ~6x that raw triangle-count scaling alone
would predict, and why the naive "O(n²) in triangle count" framing above
was the wrong place to look.

This is a genuine performance bottleneck in the shipped algorithm's
implementation, entirely unrelated to `C_THRES` calibration — it would
affect any sufficiently geometrically complex input model, not just
Bottle1, since it's driven by how much of the octree needs deep
refinement, not by input triangle count directly. The diagnostic
`clock()`/`std::cout` instrumentation added to isolate this
(`HexGen.cpp`, marked `TEMPORARY` in comments) is still in place pending a
decision on next steps — not yet removed or built into a permanent fix.
Both Bottle1 reruns from this session (`runs/bottle1-v2/`, killed
mid-run; `runs/diag-bottle1/`, killed once diagnostic data was captured)
are being kept alongside the 2026-08-04 `runs/bottle1/` as before/after
evidence.

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
- **Same-machine bone comparison**: launched a full (non-throwaway) `bone_tri.raw` run on this M1
  (`runs/bone-m1/`, using the split-timing binary) specifically to separate "M1 is a slower machine
  than the M4" from "Bottle1 is geometrically harder," since both effects could otherwise look similar
  in the raw numbers. Result: bone is a consistent ~37–67% slower on this M1 across every stage
  (419.5s total vs. ~270s on the M4) — a real but modest hardware gap, nowhere near Bottle1's ~20–90x
  factor over bone on the same M1. Also notable: bone (M1)'s projection stage converged to an almost
  bit-identical best result as the M4 run (`smallDist` matches to 6 significant figures) — the
  codebase never calls `srand()` (confirmed via `grep`), so the "randomized" redistribution step is
  actually a fixed, machine-independent sequence.
- **`MAX_PROJ_ITER` reduced for Bottle1 specifically**: let Bottle1's projection stage run at bone's
  `MAX_PROJ_ITER=200000` setting initially, like the other columns, but killed it after 24 checkpoints
  (~22 min, `maxDist` down to 0.00473 with `badElem=0`) once the per-checkpoint cost became clear
  (~56s/checkpoint vs. bone's ~1s/checkpoint — a full 200-checkpoint run would have extrapolated to
  several hours for this one model). Reduced `MAX_PROJ_ITER` to `20000` in `HexGen.cpp` specifically
  (comment there documents the reasoning and that it's not a general per-model-tuned parameter, just a
  smaller fixed backstop), rebuilt, and resumed from the already-computed
  `octree.vtk`/`dualFullHex.vtk`/`dualHex.vtk` (via a temporary, uncommitted `Main.cpp` `progress`
  tweak, reverted immediately after launching) rather than redoing the ~50 minutes of earlier stages.
  The killed full-budget attempt's log and best mesh are preserved as
  `runs/bottle1/run.log.full-attempt-killed` / `finalMesh.vtk.full-attempt-killed` for the record.
- **Scaled-Jacobian stats tool**: wrote `scripts/scaled_jacobian_stats.cpp`, a standalone C++ program
  that reads a VTK hex mesh and reports min/max scaled Jacobian using `HexGen.cpp`'s own `Sj()`
  function copied verbatim (not reimplemented), so it can't silently diverge from what `HexGen` itself
  computes. Validated against bone's `finalMesh.vtk` (worst 0.590, best 1.0 — close to the repo's
  published 0.61) before trusting it on Bottle1.
- **Result — does not reproduce Table 2, for two separable reasons, not one**: Bottle1's capped run
  finished at 218,898 vertices / 192,098 elements, worst SJ 0.010, best SJ 1.0, total 4109.3 s
  (~68.5 min), against Table 2's 36,091 / 30,145, [0.560; 1.0], 218 s. (1) Mesh size is ~6x too large,
  and — confirmed by the killed full-budget attempt and the capped rerun producing byte-identical
  vertex/element counts — this is independent of the `MAX_PROJ_ITER` cap; `RemoveOutsideElement`'s
  output topology is what it is regardless of how long the later quality-improvement stage runs. The
  same oversizing shows up on bone too (19,639/16,590 here vs. this repo's own published 10,356/8,619,
  ~1.9x), and neither run touched `VOXEL_SIZE`/`C_THRES`/`H_THRES`. The M4 session validated
  `ProjectToIsoSurface`'s convergence *behavior* against bone but never checked output mesh *size*
  against the published number, so this predates today and went unnoticed until now — structurally
  similar to the already-documented gap in the sibling `HexOpt` repo (public code not matching what
  generated its paper's published results), though not yet confirmed to be the same root cause. (2)
  Worst SJ (0.010) separately reflects the deliberately-capped, under-converged run — `ELEM_THRES`
  never left its initial `0.01` floor — and isn't informative about the algorithm's achievable quality
  the way bone's 0.590/0.61 is. See the Bottle1 results table above for the full breakdown; worth
  raising the mesh-size question with Hua Tong before spending more time chasing convergence on
  Bottle1 or moving on to Bunny.

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
