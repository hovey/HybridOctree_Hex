#!/usr/bin/env python3
"""Removes unreferenced vertices from a HybridOctree_Hex "_tri.raw" triangle
mesh, and writes the cleaned mesh as .raw, .off, .obj, and .stl.

A vertex is unreferenced when no triangle uses it.  bone_tri.raw has one.
Its vertex 0 repeats vertex 1, and no triangle refers to it.  The header
then counts 6047 points where 6046 are in use.  The face indices also run
1 to 6046, which reads as 1-based but is 0-based.

The tool drops each unreferenced vertex and renumbers the rest in their
original order.  It copies coordinates as text, so no value changes.  Every
triangle keeps the same three coordinates, in the same order.  The outputs
take the input's name plus "_cleaned":

    bone_tri.raw -> bone_tri_cleaned.raw
                    bone_tri_cleaned.off
                    bone_tri_cleaned.obj
                    bone_tri_cleaned.stl

Conventions follow raw_to_off.py and off_to_obj.py.  The .raw indices are
0-based.  The .off header carries the true edge count, where raw_to_off.py
writes 0.  The .obj indices are 1-based and the file has no header.  The
.stl is binary with float32 coordinates, which is the form automesh writes
and reads.

The input must pass raw_to_off.py's validation first.  A file with a bad
header or a bad triangle is not cleaned.  A file with nothing to remove is
left alone.

bone_tri_cleaned.* came from this tool.  Run on bone_tri.raw, it reproduces
those four files byte for byte.

Usage
-----
    python tools/raw_clean.py "input boundaries/bone_tri.raw"
    python tools/raw_clean.py "input boundaries/bone_tri.raw" --check   # report only
"""
import argparse
import struct
import sys
from pathlib import Path

from raw_to_off import raw_validate


def raw_read(*, path):
    """Returns the vertex lines (kept as text) and the faces of a .raw file."""
    lines = path.read_text().split("\n")
    num_vertices, num_triangles = (int(v) for v in lines[0].split())
    vertices = [line.strip() for line in lines[1:1 + num_vertices]]
    faces = [tuple(int(v) for v in line.split())
             for line in lines[1 + num_vertices:1 + num_vertices + num_triangles]]
    return vertices, faces


def vertices_prune(*, vertices, faces):
    """Drops the vertices no face uses, and renumbers the faces to match.

    Returns the kept vertices, the renumbered faces, and the dropped
    vertex indices.  The kept vertices stay in their original order.
    """
    used = {i for face in faces for i in face}
    dropped = [i for i in range(len(vertices)) if i not in used]
    new_index = {}
    for old in range(len(vertices)):
        if old in used:
            new_index[old] = len(new_index)
    kept = [vertices[old] for old in sorted(new_index)]
    renumbered = [tuple(new_index[i] for i in face) for face in faces]
    return kept, renumbered, dropped


def edges_count(*, faces):
    """Returns the number of distinct undirected edges."""
    return len({frozenset((f[k], f[(k + 1) % 3])) for f in faces for k in range(3)})


def raw_write(*, path, vertices, faces):
    with open(path, "w") as out:
        out.write(f"{len(vertices)} {len(faces)}\n")
        out.writelines(f"{v}\n" for v in vertices)
        out.writelines(f"{a} {b} {c}\n" for a, b, c in faces)


def off_write(*, path, vertices, faces):
    with open(path, "w") as out:
        out.write(f"OFF\n{len(vertices)} {len(faces)} {edges_count(faces=faces)}\n")
        out.writelines(f"{v}\n" for v in vertices)
        out.writelines(f"3 {a} {b} {c}\n" for a, b, c in faces)


def obj_write(*, path, vertices, faces):
    with open(path, "w") as out:
        out.writelines(f"v {v}\n" for v in vertices)
        out.writelines(f"f {a + 1} {b + 1} {c + 1}\n" for a, b, c in faces)


def normal_compute(*, a, b, c):
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    length = sum(x * x for x in n) ** 0.5 or 1.0
    return tuple(x / length for x in n)


def stl_write(*, path, vertices, faces, label):
    points = [tuple(float(x) for x in v.split()) for v in vertices]
    with open(path, "wb") as out:
        out.write(label.encode().ljust(80, b" ")[:80])
        out.write(struct.pack("<I", len(faces)))
        for a, b, c in faces:
            pa, pb, pc = points[a], points[b], points[c]
            out.write(struct.pack("<12fH", *normal_compute(a=pa, b=pb, c=pc),
                                  *pa, *pb, *pc, 0))


def raw_clean(*, raw_path, check=False):
    """Cleans one .raw file.  Returns the vertex and triangle counts, or None
    when there is nothing to remove.  Raises ValueError on a failed validation."""
    problems = raw_validate(path=raw_path)
    if problems:
        raise ValueError("; ".join(problems))
    vertices, faces = raw_read(path=raw_path)
    kept, renumbered, dropped = vertices_prune(vertices=vertices, faces=faces)
    if not dropped:
        return None
    for i in dropped:
        twins = [j for j, v in enumerate(vertices) if v == vertices[i] and j != i]
        note = f"repeats vertex {twins[0]}" if twins else "has no twin"
        print(f"  {raw_path.name}: vertex {i} is unreferenced and {note}")
    if not check:
        stem = raw_path.with_name(raw_path.stem + "_cleaned")
        raw_write(path=stem.with_suffix(".raw"), vertices=kept, faces=renumbered)
        off_write(path=stem.with_suffix(".off"), vertices=kept, faces=renumbered)
        obj_write(path=stem.with_suffix(".obj"), vertices=kept, faces=renumbered)
        stl_write(path=stem.with_suffix(".stl"), vertices=kept, faces=renumbered,
                  label=f"{stem.name}.stl, from {stem.name}.raw")
    return len(kept), len(renumbered)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", help="One or more .raw files")
    parser.add_argument("--check", action="store_true",
                        help="Report the unreferenced vertices; don't write any files")
    args = parser.parse_args()

    failures = []
    for raw_path in (Path(p).expanduser() for p in args.paths):
        try:
            counts = raw_clean(raw_path=raw_path, check=args.check)
        except ValueError as e:
            print(f"SKIPPED {raw_path.name}: {e}", file=sys.stderr)
            failures.append(raw_path.name)
            continue
        if counts is None:
            print(f"{raw_path.name}: clean, nothing to remove")
        elif args.check:
            print(f"{raw_path.name}: would keep {counts[0]} vertices, {counts[1]} triangles")
        else:
            print(f"{raw_path.name}: {counts[0]} vertices, {counts[1]} triangles "
                  f"-> {raw_path.stem}_cleaned.{{raw,off,obj,stl}}")

    if failures:
        print(f"\n{len(failures)} file(s) failed validation and were not cleaned: "
              f"{', '.join(failures)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
