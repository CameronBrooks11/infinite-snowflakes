# Infinite Snowflakes

Snowflake decorations generated in OpenSCAD from a seed: every seed gives a
different snowflake with six or eight arms. Each arm ends in a small ring for
hanging, and a printed link hooks through the rings to join snowflakes.

Every seed prints in one piece: branches are clipped to their own arm, so none
are left floating.

![Seeds 0.1, 0.5, 0.7 and 0.93](assets/snowflakes.png)

## Use it

Open `src/snowflakes.scad` in [OpenSCAD](https://openscad.org) and set:

- `seed`: any number. Each gives a different snowflake. Seeds 0.00 to 1.00 in
  steps of 0.01 all differ.
- `size`: the span from the top arm's tip to the bottom one's, in mm (55 by
  default). The arms are 4 mm tall.
- `trim_branches`: see below. Leave it on.

Render, then export an STL. The console prints the number of arms.

`src/link.scad` makes the connector: a 10 mm bar with an open hook at each end,
meant to hook through the rings at the arm tips. `length` and `width` set its size.

### trim_branches

Each half-arm keeps only the branches inside its own wedge. The original
clipping missed the region below the wedge, so a branch running down from low
on the spine left a tail there. Some tails touch nothing: in seeds 0.00 to
1.00, five of the 101 printed loose pieces. Seeds 0.26 and 0.93 gave 17
pieces, 0.49 and 0.70 gave 7, and 0.60 gave 2.

With `trim_branches = true`, the default, every one of those seeds is one
piece. Trimming also removes tails that were attached, so 67 of the 101 seeds
look different from the original, including the default 0.5. Set it to
`false` to get the original geometry back exactly.

## Printing

- Print flat. Side branches are 0.6 to 1.2 mm wide, so use a 0.4 mm nozzle or
  smaller.
- A branch can reach past the arm tips. At `size = 55` the tips are 27.5 mm
  from the centre, and in 16 of the 101 seeds a branch reaches further, up to
  29.2 mm.
- Hang a snowflake by a thread through one ring, or join several with links.

## Checks

`just test` takes about 9 s on OpenSCAD 2026.10.15. It renders every seed from
0.00 to 1.00 in steps of 0.01 and checks that each is one piece, 55 mm across
and 4 mm tall. It also checks that `size` scales the snowflake, that seeds
0.26, 0.49, 0.60, 0.70 and 0.93 still give their original loose pieces with
trimming off, and the link's size.

`just images` renders the picture above. It needs ImageMagick's `montage`.

## Origin and licence

The generator and the link grew from Mariano Lambir's
[Infinite Snowflakes](https://www.printables.com/model/91770-infinite-snowflakes)
on Printables. This repository is under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); see
[LICENSE](LICENSE).
