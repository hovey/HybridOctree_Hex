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

## Table 2, reproduced from the paper

The paper's own Table 2 (p.10), transcribed in full below for reference.
**`Tong 2024`** (bold) is the paper's "ours" row — the method this repo
reproduces. The other rows are prior work the paper compares against,
cited there as `[25]`, `[26]`, `[36]`; relabeled here as first-author
surname + year, each linked to a live copy of the actual paper (open PDF
where one exists; DOI landing page otherwise — noted per link since not
all of these are open access).

- **Tong 2024** — H. Tong, E. Halilaj, Y.J. Zhang, *HybridOctree_Hex*, J.
  Comput. Sci. 78 (2024) 102278. [Open PDF (arXiv)](https://arxiv.org/pdf/2401.05984) · [DOI](https://doi.org/10.1016/j.jocs.2024.102278)
  — this is the paper this whole page is about; same reference as the
  intro above.
- **Hu 2013** (`[25]`) — K. Hu, J. Qian, Y. Zhang, *Adaptive
  all-hexahedral mesh generation based on a hybrid octree and bubble
  packing*, 22nd International Meshing Roundtable, Orlando, FL, Oct.
  2013. [Google Scholar search](https://scholar.google.com/scholar?q=Adaptive+all-hexahedral+mesh+generation+based+on+a+hybrid+octree+and+bubble+packing)
  — no DOI or open PDF found for this one (an IMR "research notes" track
  paper, not part of the Springer-published proceedings volume); linked
  to a search as the best available pointer.
- **Gao 2019** (`[26]`) — X. Gao, H. Shen, D. Panozzo, *Feature
  Preserving Octree‐Based Hexahedral Meshing*, Computer Graphics Forum 38
  (5) (2019) 135–149. [Open PDF (author-hosted, NYU)](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) · [DOI](https://doi.org/10.1111/cgf.13795)
  — the method most of Table 2's comparison rows are against.
- **Zhang 2013** (`[36]`) — Y. Zhang, X. Liang, G. Xu, *A robust
  2‑refinement algorithm in octree or dual‑contouring dodecahedral tree
  based all‑hexahedral mesh generation*, Comput. Methods Appl. Mech.
  Engrg. 256 (2013) 88–100. [DOI](https://doi.org/10.1016/j.cma.2012.12.020)
  — DOI-only; no open PDF found.

Each model gets its own mini-table below (Method / Vertices / Elements /
Worst SJ / Best SJ / Refinement Level / Time), in the paper's own Table 2
order. Time (min) is Time (s) ÷ 60, added here — not in the original
table — for readability on the slower rows.

### 1. Bottle1 (Genus-1)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 39,326 | 33,635 | 0.181 | 0.999 | 4 | 8,175 | 136.3 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **36,091** | **30,145** | **0.560** | **1.0** | **4** | **218** | **3.6** |

### 2. Bunny (Genus-0)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Hu 2013](https://scholar.google.com/scholar?q=Adaptive+all-hexahedral+mesh+generation+based+on+a+hybrid+octree+and+bubble+packing) | 46,476 | 39,605 | 0.00100 | 1.0 | 3 | 462 | 7.7 |
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 35,330 | 29,698 | 0.292 | 0.999 | 4 | 3,569 | 59.5 |
| [Zhang 2013](https://doi.org/10.1016/j.cma.2012.12.020) | 119,799 | 106,730 | 3.85×10⁻⁵ | 1.0 | 3 | 258 | 4.3 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **26,375** | **21,695** | **0.570** | **1.0** | **4** | **358** | **6.0** |

### 3. David (Genus-0)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 127,778 | 112,314 | 0.126 | 0.999 | 4 | 38,866 | 647.8 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **319,465** | **282,957** | **0.560** | **1.0** | **6** | **10,450** | **174.2** |

### 4. Deformed Armadillo (Genus-0)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 43,591 | 35,611 | 0.0678 | 0.999 | 4 | 6,573 | 109.6 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **43,216** | **34,939** | **0.560** | **1.0** | **5** | **3,431** | **57.2** |

### 5. Dragon Stand2 (Genus-1)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 74,618 | 61,441 | 0.0290 | 0.999 | 5 | 23,062 | 384.4 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **62,576** | **50,853** | **0.560** | **1.0** | **4** | **2,052** | **34.2** |

### 6. Gargoyle (Genus-0)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 157,008 | 135,737 | 0.0702 | 0.999 | 4 | – | – |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **273,704** | **236,689** | **0.550** | **1.0** | **4** | **8,769** | **146.2** |

*(Gargoyle's Gao 2019 time is "–" in the original — the paper doesn't
report a value for that cell.)*

### 7. Head (Genus-0)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Zhang 2013](https://doi.org/10.1016/j.cma.2012.12.020) | 64,258 | 56,419 | 0.0130 | 1.0 | 3 | 169 | 2.8 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **62,782** | **55,038** | **0.550** | **1.0** | **5** | **444** | **7.4** |

### 8. Lion Recon (Genus-0)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 134,140 | 115,245 | 0.178 | 0.999 | 4 | 18,755 | 312.6 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **112,847** | **95,251** | **0.570** | **1.0** | **4** | **2,046** | **34.1** |

### 9. Oil Pump (Genus-4)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 75,033 | 63,012 | 0.117 | 0.999 | 4 | 14,301 | 238.4 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **233,702** | **196,455** | **0.540** | **1.0** | **5** | **9,742** | **162.4** |

### 10. Ramses (Genus-0)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 54,634 | 46,923 | 0.0161 | 0.999 | 4 | 9,395 | 156.6 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **44,790** | **37,993** | **0.590** | **1.0** | **4** | **713** | **11.9** |

### 11. Red Circular Box (Genus-0)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 409,011 | 367,583 | 0.215 | 0.999 | 4 | 71,626 | 1193.8 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **351,881** | **313,866** | **0.560** | **1.0** | **4** | **7,547** | **125.8** |

### 12. Thai Statue (Genus-3)

| Method | Vertices | Elements | Worst SJ | Best SJ | Refinement Level | Time (s) | Time (min) |
|---|---|---|---|---|---|---|---|
| [Gao 2019](https://cims.nyu.edu/gcl/papers/2019-OctreeMeshing.pdf) | 70,561 | 59,470 | 0.180 | 0.999 | 4 | 26,075 | 434.6 |
| **[Tong 2024](https://arxiv.org/pdf/2401.05984)** | **64,764** | **53,831** | **0.550** | **1.0** | **4** | **1,845** | **30.8** |

## Bottle1 (Genus-1)

| Metric | Tong et al. 2024 (Table 2) | 2026-08-04 (buggy `C_THRES`, capped) | 2026-08-05 (calibrated `C_THRES`, full budget) |
|---|---|---|---|
| Vertices | 36,091 | 218,898 ⚠️ | **212,990** ⚠️ |
| Elements | 30,145 | 192,098 ⚠️ | **186,832** ⚠️ |
| Worst scaled Jacobian | 0.560 | 0.010 (capped) | **0.530** ✓ close |
| Best scaled Jacobian | 1.0 | 1.0 | 1.0 |
| Refinement level | 4 | not measured | not measured (see note below) |
| Time | 218 s | 4109.3 s (~68.5 min) | **12590.2 s (~209.8 min real; ~142.3 min active compute — see note below)** ⚠️ |

*(Table 2 itself lists Bottle1's vertex count as 36,091 — cross-checked
against this repo's own README mesh-statistics table, which agrees:
`bottle1|36091|30145|0.56`.)*

**2026-08-05 update — convergence is fixed, mesh size and timing are
not.** With `C_THRES` recalibrated and the full `MAX_PROJ_ITER=200000`
budget restored, the run converged excellently: `badElem=0,
smallDist=3.76×10⁻¹¹` — essentially machine precision, and worst SJ
(0.530) landed close to Table 2's 0.560. That confirms the earlier
0.010 was purely the deliberate `MAX_PROJ_ITER=20000` cap (2026-08-04),
not an algorithm problem — resolved.

**But mesh size barely moved** — 218,898 → 212,990 vertices, only a
~2.7% reduction — despite the same `C_THRES` fix taking `bone` from
19,639 → 14,856 vertices (a ~24% reduction, into a good match against
its published stats; see the Bone section below). This is a new
finding: `C_THRES` (curvature) clearly isn't the dominant octree-
refinement driver for Bottle1 the way it is for `bone`.

**`H_THRES` hypothesis tested and refuted (2026-08-05).** The leading
hypothesis was that `H_THRES` (thickness/narrow-region, `{16,8,4,2,1}`,
unchanged and already matching the paper) dominates for Bottle1
specifically, given its thin coiled/spiral surface detail. Tested cheaply
(octree-construction-only, ~17 min, not the full pipeline) by halving
`H_THRES` to `{8,4,2,1,0.5}` — a much stricter thickness gate. Result:
octree size barely changed (358,307→354,875 points, ~1%), refuting the
hypothesis. `H_THRES` reverted to the paper-matching value. Neither
threshold, tuned individually, explains Bottle1's over-refinement — see
the summary log for the still-open question this leaves, and a genuine
code-level anomaly found in the thickness computation along the way
(worth investigating further, though it turned out not to be the answer
here).

**Timing**: `/usr/bin/time -l`'s wall-clock ("real") total was 12590.2s
(~209.8 min), but the sum of `HexGen`'s own internal stage timers only
accounts for 8537.8s (~142.3 min) — a ~4052s (~67.5 min) gap. Traced to a
system sleep during the run: `caffeinate` (keeping the Mac awake) died
partway through and wasn't immediately relaunched, so part of the "3+
hours" included the machine being asleep, not active computation.
~142.3 min of actual compute time is the more meaningful number to
compare against Table 2's 218s — still roughly **39x** longer, and per
the summary log's synthesis below, not something `C_THRES` calibration
was ever going to fix (that's a mesh-*quality*/*size* tuning constant,
disconnected from the `ComputeCellValue()` performance bottleneck driving
the timing gap).

Given all this, the vertex/element/timing mismatches here shouldn't be
read as "the fix doesn't work" — quality/convergence *is* fixed, cleanly.
Mesh size and timing are separate, still-open problems, and the timing
one in particular looks structural (see the summary log's synthesis) —
not something further `C_THRES` tuning is likely to resolve on its own.

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

| Stage | bone (M4, 2026-07-02) | bone (M1, 2026-08-04) | Bottle1 (M1, 2026-08-04, buggy `C_THRES`, capped) | Bottle1 (M1, 2026-08-05, calibrated `C_THRES`, full budget) |
|---|---|---|---|---|
| Read surface mesh | ~0.4 s (0.2%) | 0.57 s (0.1%) | 1.79 s (0.0%) | 1.90 s (0.0%) |
| Curvature and Narrow Region Assessment | n/a¹ | 31.6 s (57.0% of combined) | n/a¹ | 725.0 s (71.6% of combined) |
| Octree Generation (strongly balanced) | n/a¹ | 19.6 s (35.4% of combined) | n/a¹ | 43.9 s (4.3% of combined) |
| — combined (curvature + octree), as `Main.cpp` reports it¹ | ~38–39 s (14.6%) | 55.3 s (13.4%) | **1062.2 s (~17.7 min) (25.9%)** | **1012.4 s (~16.9 min) (11.9%)** |
| Mesh Dualization | ~12–13 s (4.7%) | 17.1 s (4.1%) | **1138.9 s (~19.0 min) (27.7%)** | **1045.8 s (~17.4 min) (12.2%)** |
| Buffer Clearing | ~13 s (4.9%) | 21.7 s (5.2%) | **815.1 s (~13.6 min) (19.8%)** | **785.0 s (~13.1 min) (9.2%)** |
| Buffer Zone Projection + Quality Improvement | ~200 s (75.6%) | **319.4 s (~5.3 min) (77.2%)** | **1091.3 s (~18.2 min) (26.6%)³** | **5692.8 s (~94.9 min) (66.7%)⁴** |
| **Total** | **~4.5 min (264.4 s summed² ⇒ 100%)** | **419.5 s (~7.0 min, `time -l` real ⇒ 100%)** | **4109.3 s (~68.5 min summed³ ⇒ 100%)** | **8537.8 s (~142.3 min summed active compute ⇒ 100%)⁴** |

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

⁴ The 2026-08-05 `bottle1-v3` run (calibrated `C_THRES`, full
`MAX_PROJ_ITER=200000` budget) ran for `/usr/bin/time -l`'s reported
12590.2s "real" — but the sum of `HexGen`'s own internal stage timers
only accounts for 8537.8s, a ~4052s (~67.5 min) gap. Traced to a system
sleep during the run (`caffeinate`, keeping the Mac awake, died partway
through per `pmset -g log` and wasn't immediately relaunched) — part of
the raw wall-clock duration was the machine asleep, not computation. The
table above uses the summed 8537.8s (active compute only) as each
stage's percentage denominator, consistent with how the other columns'
percentages are computed from their own summed/reported stage times
rather than a raw wall-clock figure that could include idle gaps. The
projection stage converged excellently despite the sleep interruption —
`badElem=0, smallDist=3.76×10⁻¹¹`, essentially machine precision — but
mesh size barely changed from the buggy 2026-08-04 run (218,898 →
212,990 vertices, ~2.7% smaller) despite `C_THRES` recalibration, unlike
`bone`'s ~24% reduction with the same fix; see the Bottle1 results table
above and the summary log's synthesis below for the still-open
`H_THRES` hypothesis this raises.

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

*Ordered oldest to newest*

| Date | Machine | Narrative |
|---|---|---|
| 2026-07-02 – 2026-07-03 | M4 | Got this fork building on macOS, then found and fixed a genuine upstream bug — `ProjectToIsoSurface()` had an infinite loop with no exit path, an unbounded quality-ratchet, and a convergence tolerance borrowed from an unrelated check. Fixed and verified against `bone`, the smallest sample model. Separately, this is also where the sibling `HexOpt` repo's own gap was first found (its public code doesn't implement the AL/L-BFGS/ReHQJ method its paper claims). |
| 2026-08-04 | M1 | Cloned the fork here, cleaned up ~600K lines of build cruft the M4 session had accidentally committed, and ran the first Bottle1 reproduction attempt. Result: a mesh ~6x too large and a worst scaled Jacobian far below Table 2's — the size gap unexplained at the time, the quality gap eventually traced to a deliberately reduced iteration budget. |
| 2026-08-05 | M1 | Root-caused the mesh-size gap to two separate issues — the shipped curvature thresholds didn't match the paper's stated values, and (independently) this codebase's curvature *formula* doesn't match the paper's stated formula either. Recalibrated empirically using `bone` as a fast testbed, which fixed `bone`'s mesh size well and got Bottle1's convergence *quality* to match closely — but Bottle1's mesh size and, especially, its runtime (~27x slower than `bone` even fully calibrated) remained largely unmoved. Spent most of the day testing *why*: three hypotheses for the over-refinement (`C_THRES` alone, `H_THRES` alone, octree-balancing propagation) were each tested and refuted, and a fourth (spatial dispersion of refinement candidates) showed a real but insufficient effect. Also traced a related finding in the sibling `HexOpt` repo: its restored optimizer code looks structurally like `HybridOctree_Hex`'s own older algorithm, not the CAD 2026 paper's claimed method, backed by a definitive date-based proof (see `hovey/HexOpt`'s README). |

## Detailed log

*Ordered newest to oldest*

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
`clock()`/`std::cout` instrumentation used to isolate this has since been
removed from `HexGen.cpp` (its purpose served — see the commit removing
it), replaced with a short permanent comment at the `ComputeCellValue()`
call site pointing back to this finding. Both Bottle1 reruns from this
session (`runs/bottle1-v2/`, killed mid-run; `runs/diag-bottle1/`, killed
once diagnostic data was captured) are being kept alongside the
2026-08-04 `runs/bottle1/` and the final `runs/bottle1-v3/` as
before/after evidence.

**Synthesis: why Bottle1 has been so hard to reproduce.** The
`bottle1-v3` run (calibrated `C_THRES`, full `MAX_PROJ_ITER=200000`
budget) has now finished — 8537.8s (~142.3 min) active compute (see
footnote 4 above for the wall-clock-vs-active-compute distinction) —
against Table 2's reported 218s. Worth stepping back and separating
what's actually been fixed from what hasn't.

*Three separable problems, not one.* Convergence quality (fixed,
cleanly), mesh size (fixed, partially — see below, this turned out to be
more complicated than first thought), and runtime (still unsolved) are
close to independent of each other. Fixing one didn't fix the others.

*Convergence — fixed cleanly.* `badElem=0, smallDist=3.76×10⁻¹¹`,
essentially machine precision. Worst SJ (0.530) landed close to Table
2's 0.560. The earlier 0.010 (2026-08-04) was purely the deliberate
`MAX_PROJ_ITER=20000` cap, not an algorithm problem.

*Mesh size — root-caused, but the fix barely worked for Bottle1
specifically.* The shipped `C_THRES` didn't match the paper's stated
values, and separately, the codebase's actual curvature formula doesn't
match the paper's stated formula either (a different, unnormalized
quantity — no valid unit conversion between the two). Empirical
recalibration against `bone`'s known-good published stats got `bone`'s
size within ~1.5x — but the *same* recalibrated `C_THRES` only took
Bottle1 from 218,898 → 212,990 vertices, a ~2.7% reduction, nowhere near
`bone`'s ~24% improvement with the identical fix. That's a finding:
`C_THRES` (curvature) isn't the dominant octree-refinement driver for
Bottle1 the way it is for `bone`. The follow-up hypothesis — `H_THRES`
(thickness/narrow-region) dominates instead, given Bottle1's thin
coiled/spiral surface detail — was tested and refuted: halving `H_THRES`
only shrank the octree by ~1%. Neither threshold, tuned individually,
explains Bottle1's over-refinement — still an open question (see the
2026-08-05 log entry's `H_THRES` test for the details, including a
genuine code-level anomaly found in the thickness-distance computation
along the way that didn't turn out to be the answer here either).

*Runtime — the real story, and not explained by either fix above.*
Comparing `bone` (calibrated) against Bottle1 (calibrated), same code,
same machine:

| Stage | bone (calibrated) | Bottle1 (calibrated) | Ratio |
|---|---|---|---|
| Octree construction | ~55 s | ~1012 s | ~18x |
| Dual mesh generation | ~7 s | ~1046 s | ~150x |
| Buffer clearing | ~8–22 s | ~785 s | ~36–100x |
| Projection/quality | ~238 s | ~5693 s (~94.9 min) | ~24x |
| **Total** | **~5.2 min** | **~142.3 min active compute** | **~27x** |

Bottle1 only has 2.45x more input triangles than bone. None of these
ratios are anywhere close to 2.45x, or even the ~6x naive O(n²)-in-
triangle-count reasoning would predict. The confirmed cause for octree
construction specifically (not guessed — see the `ComputeCellValue()`
instrumentation above) is that octree-cell classification does a
brute-force linear scan with no spatial acceleration structure, and both
the number of cells needing classification and the candidate-list sizes
are inflated by Bottle1's more complex geometry, compounding
multiplicatively. Dualization and buffer-clearing show the same
disproportionate pattern and likely hide similar unaccelerated scans,
though those haven't been isolated with the same direct instrumentation
yet. Projection/quality's ~24x, by contrast, is largely just iteration
count — a much larger mesh takes more `gradient()`/redistribution passes
to reach the same convergence quality, a more "expected" kind of slowdown
than the other three stages' scaling.

*Why 218s is probably unreachable with the current public code at all.*
Even a "perfectly calibrated" run of the current public code cannot
plausibly finish in 218s. `bone` — a much smaller, simpler model — takes
~5.2 minutes on its own, and its quality-improvement stage alone (238s)
is already almost as long as Table 2's entire reported Bottle1 time. For
Bottle1 to finish in 218s, whatever Tong actually ran would need spatial
acceleration in `ComputeCellValue()` (and likely elsewhere) that simply
isn't in the code currently on GitHub.

This lines up with a pattern confirmed in *both* of Tong's public repos
this session: `HexOpt`'s own README documents (with his own email
confirmation) that the public `meshQuality.cpp` doesn't implement the
method the CAD 2026 paper claims — and structurally, that code looks
like it's actually derived from `HybridOctree_Hex`'s own older algorithm
instead (see `hovey/HexOpt`'s README, 2026-08-05 entry). The most likely
explanation for Bottle1's timing gap is the same shape of problem: the
version of `HexGen.cpp` that's public doesn't have the optimizations
that the version used to generate Table 2 had. This isn't a mistake in
this reproduction's methodology — it's a real, structural gap between
the published performance numbers and the current state of the public
code, on top of the mesh-size question — see the `H_THRES` and
octree-balancing tests immediately below, both of which ruled out their
respective candidates and narrowed the mesh-size question down to
"Bottle1's curvature/thickness candidates are more spatially dispersed
across its geometry than bone's," not yet fully confirmed.

**`H_THRES` hypothesis test (2026-08-05).** Before testing, re-read
`GetCellValue()`'s thickness computation (`HexGen.cpp:936-985`) against
the paper's stated method ("shooting a ray from `Pi` along its normal
direction to find the shortest intersection with other triangular
elements") — structurally it matches (ray from a triangle's centroid
along its normal, tested against every other triangle via `Intersect()`),
*unlike* the curvature computation's outright formula mismatch. But
found a genuine anomaly along the way: the code scales the raw
ray-intersection distance by `max(|dir_x|,|dir_y|,|dir_z|)` — the
dominant-axis component of the (unit, normalized) triangle-normal
direction — before comparing it to `H_THRES` (`HexGen.cpp:952-954`). That
factor is always in `[1/√3, 1]`, so it always *shrinks* the effective
distance relative to true Euclidean distance, by up to ~42% for normals
oriented diagonally to the octree axes. Plausible rationale (converting
to an octree-cell-crossing-relevant metric rather than raw 3D distance)
rather than an obvious bug like the `C_THRES` zeros, but not something
the paper's plain-language description mentions either. A coiled/spiral
surface like Bottle1's has far more diagonally-oriented normals than
bone's simpler shape, so this seemed like a promising lead.

Tested empirically rather than reasoning it through further: halved
`H_THRES` to `{8,4,2,1,0.5}` — a much stricter thickness gate that should
sharply cut the number of triangle pairs flagged as "thin enough to
refine" if thickness detection were the dominant driver. Ran cheaply
(octree-construction-only, ~17 min via `build-h-thres-test/`, killed
immediately after `ConstructOctree()` completed — no need for the full
~142 min pipeline just to read `octree.vtk`'s point/cell counts) rather
than committing to another multi-hour full run. Result: `octree.vtk` went
from 358,307/300,560 (points/cells) to 354,875/297,368 — a ~1% change.
**Hypothesis refuted.** `H_THRES` reverted to the paper-matching
`{16,8,4,2,1}` in `Initialization.h`.

Neither `C_THRES` nor `H_THRES`, tuned individually, explains Bottle1's
disproportionate over-refinement relative to `bone`. Remaining
candidates, none yet tested: (a) the octree balancing rule
(`StrongBalancedOctree()`'s 2:1 constraint) propagating refinement far
beyond the initially-flagged cells, so that once *some* threshold flags
enough scattered cells across Bottle1's more extensive/complex surface,
balancing alone forces widespread deep refinement regardless of exactly
which threshold triggered the initial flags; (b) some other input
property (e.g. `VOXEL_SIZE`/model-to-box-scale interaction, or an
octree-orientation-vs-geometry effect like the paper's own oil-pump
discussion) not captured by either threshold at all. This remains open;
`bottle1-h-thres-test/` and `build-h-thres-test/` were both deleted after
capturing the result (throwaway experiment, not meaningful to preserve).

**Octree-balancing hypothesis tested and refuted (2026-08-05).** Tested
candidate (a) above: does `StrongBalancedOctree()`'s 2:1 balancing pass
propagate refinement far beyond what `GetCellValue()` initially flags,
disproportionately for Bottle1? Instrumented `ConstructOctree()`
(temporarily) to count `octreeArray`'s true-entries immediately before
and after the balancing call, run cheaply on both models
(octree-construction-only, killed right after — `bone` finishes in
~1 min, Bottle1 in ~17 min):

| | Before balancing | After balancing | Amplification |
|---|---|---|---|
| bone | 2,777 | 3,633 | +30.8% |
| Bottle1 | 34,785 | 42,937 | +23.4% |

**Refuted, decisively.** Balancing amplifies bone *more* than Bottle1 in
relative terms (+30.8% vs. +23.4%), the opposite of what the hypothesis
predicted. More importantly: the Bottle1-vs-bone disparity is already
almost fully present *before* balancing ever runs (34,785/2,777 ≈ 12.53x)
and barely changes after it (42,937/3,633 ≈ 11.82x) — closely matching
the final octree's own ~11.7x disparity (358,307 vs. 30,733 points, from
the earlier `octree.vtk` comparison). So the entire disproportion
originates in `GetCellValue()`'s initial cell-marking, not in balancing
propagation. Since neither `C_THRES` nor `H_THRES`, tuned individually,
explains that marking disparity either (both tested and refuted above),
the likely remaining explanation is candidate (b): Bottle1's raw
curvature/thickness candidate lists are only ~3x larger than bone's (from
the earlier `GetCellValue()` diagnostic — `refineTriPt0` raw: 41,442 vs.
12,959), but produce a ~12x larger marked-cell count — meaning those
candidates are more spatially *dispersed* across Bottle1's more elongated,
coiled geometry, touching many more distinct octree cells rather than
clustering within a smaller set of them the way bone's more compact
shape's candidates would. If so, this isn't a fixable threshold-tuning
bug at all — it may be a genuine, correct consequence of applying this
octree strategy to an elongated/coiled shape, and reproducing Table 2's
mesh size for Bottle1 specifically might require a different mechanism
entirely (spatially-adaptive thresholds, or whatever Tong's original,
non-public implementation actually did) rather than anything tunable in
the current public code. Not yet confirmed — would need to inspect the
spatial distribution of `refineTri0`/`refineTriPt0` directly (e.g.
bounding-box coverage as a fraction of the model's overall extent) to
verify the dispersion theory rather than infer it from these aggregate
counts alone. The temporary `octreeArray` count instrumentation has been
removed from `HexGen.cpp`, replaced with a short permanent comment
pointing to this finding; `diag-balance-bone/`/`diag-balance-bottle1/`
and `build-balance-test/` were deleted after capturing the result.

**Spatial-dispersion hypothesis tested (2026-08-05) — partial support,
not a full explanation.** Tested candidate (b): are Bottle1's
curvature/thickness candidate points more spatially *dispersed* across
its geometry (touching many more distinct octree cells) rather than
clustered, versus bone's? Instrumented `GetCellValue()` to compare
`refineTriPt0`'s (the coarsest tested level's deduped candidate points)
bounding box against the full model's bounding box, run *very* cheaply
(only the O(n²) candidate-collection loop, well before the expensive
`ComputeCellValue()` sweep — ~10-15s per model, not minutes):

| | Candidate count | Candidate bbox / model bbox (volume) | Candidate density (pts/unit³) |
|---|---|---|---|
| bone | 3,134 | 71.6% | 0.0477 |
| Bottle1 | 6,036 | 99.1% | 0.0299 |

Bottle1's candidates do span nearly its entire bounding box (99.1% vs.
bone's 71.6%) with only ~1.93x more points — and are actually *sparser*
in point-density terms (~0.625x bone's density), consistent with being
more spread out rather than clustered. But combining the count ratio
(1.93x) and bbox-coverage ratio (1.38x) only predicts a ~2.7x
marked-cell difference — far short of the ~12.5x actually observed
before balancing. **Real effect, insufficient magnitude.** Bounding-box
volume is a poor proxy for what `ComputeCellValue()` actually tests
(discrete octree-cell occupancy at each level, not convex-hull volume) —
a bounding box can be nearly full while still leaving most individual
grid cells empty, so this test likely *understates* true dispersion.
Resolving this further would need a finer test: actual occupied-cell
counts on a fixed grid (e.g. voxelize `refineTriPt0` at the octree's own
resolution and count non-empty voxels) rather than a single aggregate
bounding-box ratio. Not done yet. The temporary bounding-box
instrumentation has been removed from `HexGen.cpp`, replaced with a
permanent comment; `diag-disp-bone/`, `diag-disp-bottle1/`, and
`build-dispersion-test/` were deleted after capturing the result.

**Status of the mesh-size investigation**: all three candidate
hypotheses tested so far (`C_THRES`, `H_THRES`, octree-balancing
propagation) are refuted or insufficient on their own; spatial dispersion
of candidates shows a real but only partial effect. The ~12x
Bottle1-vs-bone disparity in marked octree cells remains not fully
explained.

---

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
