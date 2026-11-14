// A link to join snowflakes: a straight bar with an open hook at each end. Each hook
// slips through the ring at an arm tip. Print it flat. MIT licence; see LICENSE.

/* [Link] */
// Length of the bar between the hooks (mm)
length = 10; // [4:1:40]
// Width and thickness of the link's wire (mm)
width = 1; // [0.6:0.1:2]

/* [Hidden] */
$fn = 48;
HOOK_IN = 1.4;       // inside radius of a hook: room for a tip ring's 1 mm band
GAP = 1.4;           // the hook's opening, wide enough to pass the band through

// One hook, centred at the origin, open toward +x.
module hook() {
  difference() {
    circle(r = HOOK_IN + width);
    circle(r = HOOK_IN);
    translate([0, -GAP / 2]) square([HOOK_IN + width + 1, GAP]);
  }
}

linear_extrude(width) {
  translate([-width / 2, -length / 2]) square([width, length]);
  for (s = [-1, 1]) translate([0, s * (length / 2 + HOOK_IN + width / 2)]) rotate(s > 0 ? 0 : 180) hook();
}
