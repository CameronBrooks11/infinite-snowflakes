"""Render snowflakes and the link, and check each one's solids and size.

usage: python3 tests/test_snowflakes.py [OPENSCAD]

Each render uses --hardwarnings. A binary STL's separate solids are counted
(triangles sharing a vertex belong to the same solid), and sizes are checked
to within 0.01 mm.
"""

import os
import struct
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNOWFLAKES = os.path.join(ROOT, "src", "snowflakes.scad")
LINK = os.path.join(ROOT, "src", "link.scad")
HEIGHT = 4


def measure(path):
    data = open(path, "rb").read()
    (n,) = struct.unpack_from("<I", data, 80)
    parent = {}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    for i in range(n):
        v = struct.unpack_from("<9f", data, 84 + i * 50 + 12)
        corners = [v[0:3], v[3:6], v[6:9]]
        for c in corners:
            parent.setdefault(c, c)
        root = find(corners[0])
        for c in corners[1:]:
            parent[find(c)] = root
    solids = len({find(v) for v in parent})
    size = [max(p[i] for p in parent) - min(p[i] for p in parent) for i in range(3)]
    return solids, size


def render(openscad, scad, out, defines):
    cmd = [openscad, "--hardwarnings", "--export-format", "binstl", "-o", out]
    for name, value in defines.items():
        cmd += ["-D", f"{name}={value}"]
    result = subprocess.run(cmd + [scad], capture_output=True, text=True)
    if result.returncode != 0:
        errors = [l for l in result.stderr.splitlines() if "WARNING" in l or "ERROR" in l]
        raise RuntimeError(f"openscad exited {result.returncode}: {'; '.join(errors)}")
    return measure(out)


def close(a, b):
    return abs(a - b) <= 0.01


def main():
    openscad = sys.argv[1] if len(sys.argv) > 1 else "openscad"
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "case.stl")

        # Every seed from 0.00 to 1.00 in steps of 0.01 is one piece, as tall
        # as an arm is high. Its span along y, through the top and bottom arm
        # tips, is the size: 55 by default.
        seeds = [f"{i / 100:.2f}" for i in range(101)]
        for seed in seeds:
            solids, size = render(openscad, SNOWFLAKES, out, {"seed": seed})
            if solids != 1 or not close(size[1], 55) or not close(size[2], HEIGHT):
                failures.append(f"seed {seed}: {solids} solids, y {size[1]:.2f}, z {size[2]:.2f}")
        print(f"trimmed: {len(seeds)} seeds checked for one piece, 55 mm across, {HEIGHT} mm tall")

        # size scales the snowflake.
        solids, size = render(openscad, SNOWFLAKES, out, {"seed": "0.5", "size": 100})
        if solids != 1 or not close(size[1], 100):
            failures.append(f"size 100: {solids} solids, y {size[1]:.2f}")
        print("size 100: checked")

        # With trimming off, the original clipping leaves these loose pieces.
        # If they stop appearing, trim_branches = false no longer reproduces
        # the original geometry.
        loose = {"0.26": 17, "0.49": 7, "0.60": 2, "0.70": 7, "0.93": 17}
        for seed, want in loose.items():
            solids, _ = render(openscad, SNOWFLAKES, out,
                               {"seed": seed, "trim_branches": "false"})
            if solids != want:
                failures.append(f"untrimmed seed {seed}: {solids} solids, expected {want}")
        print(f"untrimmed: {len(loose)} seeds checked for the original loose pieces")

        solids, size = render(openscad, LINK, out, {})
        want = [4, 15.8, 1]
        if solids != 1 or not all(close(a, b) for a, b in zip(size, want)):
            failures.append(f"link: {solids} solids, {' x '.join(f'{s:.2f}' for s in size)} mm")
        print("link: checked")

    for failure in failures:
        print(f"FAIL {failure}")
    print("all checks passed" if not failures else f"{len(failures)} failed")
    sys.exit(1 if failures else 0)


main()
