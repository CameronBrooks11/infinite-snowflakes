default:
    @just --list

# Render 101 seeds, the untrimmed loose-piece seeds and the link, and check each
test:
    python3 tests/test_snowflakes.py

# Render the README pictures into assets/
images:
    @mkdir -p assets
    montage -version >/dev/null
    for s in 0.1 0.5 0.7 0.93; do openscad --render --camera=0,0,0,0,0,0,150 --imgsize=300,300 --colorscheme=Tomorrow -D seed=$s -o assets/seed-$s.png src/snowflakes.scad; done
    montage assets/seed-0.1.png assets/seed-0.5.png assets/seed-0.7.png assets/seed-0.93.png -tile 4x1 -geometry +4+4 assets/snowflakes.png
    rm assets/seed-*.png
