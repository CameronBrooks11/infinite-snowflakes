// Infinite Snowflakes: a snowflake decoration from a seed. Every seed gives a different
// snowflake, with six or eight arms, each ending in a ring to hang it by or to hook a link
// through (src/link.scad). MIT licence; see LICENSE.

/* [Snowflake] */
// Any number; each gives a different snowflake
seed = 0.5; // [0:0.01:1]
// Span from the top arm's tip to the bottom one's (mm)
size = 55; // [20:1:200]

/* [Hidden] */
HEIGHT = 4;            // thickness of the whole snowflake (mm)
$fn = 32;

// All dimensions below are for a 55 mm snowflake, then scaled to `size`, so a seed
// keeps its shape at any size.
R = 27.5;              // centre to the outside of a tip ring
RING_OUT = 2.2;        // tip ring, outer and inner radius
RING_IN = 1.2;
SPINE_W = 1.6;
TIP = R - RING_OUT;    // where the spine ends, at the ring's centre
HUB = 3;               // the plate at the centre: its circumradius at minimum

// Every random choice is one draw from this list, so a seed always gives the same flake.
S = round(seed * 100000);
r = rands(0, 1, 32, S);
function pick(i, lo, hi) = lo + r[i] * (hi - lo);

ARMS = r[0] < 0.5 ? 6 : 8;
HALF = 180 / ARMS;     // half the angle between neighbouring arms
PAIRS = floor(pick(1, 2, 5));   // 2 to 4 pairs of side branches per arm
PLATE = pick(2, HUB, 9);        // radius of the central plate
HOLE = r[3] < 0.5;              // whether the plate has a hole in it

// Branch i: where it leaves the spine (fraction of TIP), its angle to the spine, its
// length before trimming, and its width.
function at(i) = pick(4 + 4 * i, 0.25, 0.85);
function angle(i) = pick(5 + 4 * i, 25, 75);
function want(i) = pick(6 + 4 * i, 3, 14);
function width(i) = pick(7 + 4 * i, 0.6, 1.2);

// The longest a branch may be: its far edge stays inside its arm's wedge, clear of the
// neighbouring arm's branches, and short of the tip ring. Each branch starts on the spine,
// so the flake is one piece whatever the seed.
function fit(x, a, w, want_len) =
  let (
    gap = sin(a) - cos(a) * tan(HALF),
    wedge = gap > 0 ? (x * tan(HALF) - w) / gap : 1e9,
    reach = (TIP - RING_OUT - w - x) / max(cos(a), 0.05)
  ) max(0, min(want_len, wedge, reach));

module stroke(a, b, w) hull() { translate(a) circle(d = w); translate(b) circle(d = w); }

module arm() {
  stroke([0, 0], [TIP, 0], SPINE_W);
  for (i = [0:PAIRS - 1]) {
    x = at(i) * TIP;
    a = angle(i);
    w = width(i);
    len = fit(x, a, w, want(i));
    if (len > w) for (s = [-1, 1]) stroke([x, 0], [x + len * cos(a), s * len * sin(a)], w);
  }
  translate([TIP, 0]) difference() { circle(r = RING_OUT); circle(r = RING_IN); }
}

module plate() {
  difference() {
    circle(r = PLATE, $fn = ARMS);
    if (HOLE) circle(r = PLATE * 0.45, $fn = ARMS);
  }
}

module snowflake_2d() {
  // The first arm points up, so the top and bottom tips span `size`.
  for (k = [0:ARMS - 1]) rotate(90 + k * 360 / ARMS) arm();
  rotate(90) plate();
}

echo(str("seed ", seed, ": ", ARMS, " arms"));
linear_extrude(HEIGHT) scale(size / 55) snowflake_2d();
