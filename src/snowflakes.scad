seed = .5;
size = 55;
// Clip each branch to its own arm, so every seed prints as one piece. Turn it
// off for the original geometry, where some seeds leave loose pieces.
trim_branches = true;

module mirror_keep(angle = [ 1, 0, 0 ])
{
    children();
    mirror(angle) children();
}

module rotate_keep(angle)
{
    children();
    rotate(angle) children();
}

angles = [ 45, 90, -45 ];

module snowflake_arm(seed, angle, size)
{
    height = 4;
    mirror_keep() union()
    {
        difference()
        {
            union()
            {
                translate([ 0, size - height / 2, height / 2 ]) rotate([ 0, 90, 0 ], $fn = 12)
                    cylinder(height / 4, r = height / 2, center = true);
                cube([ height / 8, size - height / 2, height ]);
            }
            translate([ 0, size - height / 2, height / 2 ]) rotate([ 0, 90, 0 ], $fn = 12)
                cylinder(height / 4 + .1, r = height / 3.2, center = true);
        }
        linear_extrude(height) if (trim_branches)
        {
            // Keep only what lies in this half-arm's wedge: between the spine
            // and angle + 0.1 degrees from it, and short of the tip.
            intersection()
            {
                polygon([ [ 0, 0 ], [ 0, size ], [ size * tan(angle + .1), size ] ]);
                snowflake_branches(seed, size);
            }
        }
        else
        {
            // The original clipping. It leaves the tails of branches that
            // run out below the wedge, and some of those touch nothing.
            difference()
            {
                snowflake_branches(seed, size);
                rotate(-angle - .1) square([ 100, 100 ]);
                mirror([ 1, 0, 0 ]) square([ 100, 100 ]);
                translate([ 0, size, 0 ]) square([ 100, 100 ]);
            }
        }
    }
}

module snowflake_branches(seed, size)
{
    union()
    {
        r = rands(0, 1, 10000, seed = seed);
        for (i = [0:round(rands(1, 6, 1, seed = seed)[0])])
        {
            anglei = round((len(angles) - 1) * (r[10 * i + 3]));
            translate([ 0, round(size * .7 * r[10 * i + 1]) - .5 ]) rotate(angles[anglei])
                square([ (r[10 * i + 5] + 1.) * .6, size ], center = true);
        }
    }
}

module rotate_copy(count)
{
    for (i = [1:count])
    {
        rotate((360 / count) * i)
        {
            children();
        }
    }
}

module snowflake(seed, size = 50)
{

    n = [ 6, 8 ][round(rands(0, 1, 1, seed)[0])];
    echo(n);
    rotate_copy(n)
    {
        snowflake_arm(seed, (360 / (n * 2)), size / 2);
    }
}

snowflake(seed, size);