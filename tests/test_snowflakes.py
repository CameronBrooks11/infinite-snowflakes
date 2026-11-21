"""Render snowflakes and the link, and check each one's solids and size.

usage: python3 tests/test_snowflakes.py [OPENSCAD]

Each render uses --hardwarnings, and any ERROR or WARNING fails it. A binary
STL's separate solids are counted (triangles sharing a vertex belong to the
same solid), and sizes are checked to within 0.01 mm.
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
    # A failed assert can leave the exit status at 0, so the messages count too.
    errors = [l for l in result.stderr.splitlines() if l.startswith(("WARNING", "ERROR"))]
    if result.returncode != 0 or errors:
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
        # tips, is the size: 55 by default. Nothing reaches past the tips, so
        # it is no wider than that either.
        seeds = [f"{i / 100:.2f}" for i in range(101)]
        for seed in seeds:
            solids, size = render(openscad, SNOWFLAKES, out, {"seed": seed})
            if (solids != 1 or not close(size[1], 55) or size[0] > 55 + 0.01
                    or not close(size[2], HEIGHT)):
                failures.append(f"seed {seed}: {solids} solids, "
                                f"{size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f} mm")
        print(f"{len(seeds)} seeds checked: one piece, 55 mm across, no wider, {HEIGHT} mm tall")

        # size scales the snowflake.
        solids, size = render(openscad, SNOWFLAKES, out, {"seed": "0.5", "size": 100})
        if solids != 1 or not close(size[1], 100):
            failures.append(f"size 100: {solids} solids, y {size[1]:.2f}")
        print("size 100: checked")

        solids, size = render(openscad, LINK, out, {})
        # A 10 mm bar, and a hook of outer radius 2.4 centred 1.9 mm past each end.
        want = [4.8, 18.6, 1]
        if solids != 1 or not all(close(a, b) for a, b in zip(size, want)):
            failures.append(f"link: {solids} solids, {' x '.join(f'{s:.2f}' for s in size)} mm")
        print("link: checked")

        # examples/window_snowflake.scad: seed 0.93 at 100 mm.
        solids, size = render(openscad, os.path.join(ROOT, "examples", "window_snowflake.scad"), out, {})
        if solids != 1 or not close(size[1], 100) or not close(size[2], HEIGHT):
            failures.append(f"examples/window_snowflake.scad: {solids} solids, "
                            f"{' x '.join(f'{s:.2f}' for s in size)} mm")
        print("examples/window_snowflake.scad: checked")

    for failure in failures:
        print(f"FAIL {failure}")
    print("all checks passed" if not failures else f"{len(failures)} failed")
    sys.exit(1 if failures else 0)


main()
