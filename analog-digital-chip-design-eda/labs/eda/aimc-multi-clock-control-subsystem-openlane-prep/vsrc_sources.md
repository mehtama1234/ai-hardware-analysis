# Modeled PDN source locations

The two `.loc` files under `src/` provide four VPWR and four VGND source
locations for the explicit-source OpenLane experiment. Coordinates are in
microns and use OpenROAD's `x,y,bump_edge_length,voltage` format.

These locations were aligned to legal PDN nodes reported by the preceding
run. They are package-analysis assumptions for this local block; they are not
measurements from a package, board, or silicon. Replace them with package and
board-derived locations before making product power-integrity claims.
