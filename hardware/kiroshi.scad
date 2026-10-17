// Kiroshi case for the Waveshare 7.3" e-Paper (E) panel with ribbon cable
// and a Raspberry Pi 2 Model B or Pi Zero 2 W with the e-Paper Driver HAT.
//
// Parts: front (bezel), back (shell with Pi mount), stand (desk only).
// Render one part:  openscad -D 'part="back"' -D 'pi="pi2b"' -o back.stl kiroshi.scad
//
// All sizes are in mm. Measure your hardware and check the values marked "CHECK".

/* [Options] */
pi = "zero2w";      // [zero2w, pi2b]
style = "desk";     // [desk, wall, frame]
part = "all";       // [all, front, back, stand]

/* [e-Paper panel] */
panel = [170.2, 111.2, 1.2];  // CHECK: outline width, height, thickness
view = [160, 96];             // CHECK: active area
view_offset = [0, 0];         // CHECK: active area center from panel center, seen from front
fpc_width = 40;               // CHECK: ribbon cable width at the bottom edge
fpc_offset = 0;               // CHECK: ribbon cable center from panel center, seen from front
foam = 0.5;                   // foam tape between panel and bezel

/* [Print] */
clear = 0.4;       // gap around the panel
wall = 2.4;
floor_t = 2.4;     // back plate thickness
front_t = 2;       // bezel plate thickness
tilt = 15;         // desk stand angle

/* [Hidden] */
$fn = 48;
border = style == "frame" ? 20 : 8;  // bezel width outside the panel
pocket = [panel.x + 2 * clear, panel.y + 2 * clear];
outer = [pocket.x + 2 * border, pocket.y + 2 * border];
front_h = front_t + panel.z + foam;

// Pi data: board, hole spacing, hole inset, inside depth, port height
PI = pi == "pi2b"
    ? [[85, 56], [58, 49], 3.5, 26, 17]
    : [[65, 30], [58, 23], 3.5, 18, 6];
board = PI[0];
depth = PI[3];
standoff = 4;
// Pi corner position in the back shell (seen from front): bottom, right for pi2b
pi_pos = [pi == "pi2b" ? outer.x - wall - board.x - 3 : (outer.x - board.x) / 2, wall + 2];

post_d = 7;
posts = [for (x = [border / 2, outer.x - border / 2], y = [border / 2, outer.y - border / 2]) [x, y]];

module rounded(size, h, r = 3) {
    linear_extrude(h) offset(r) offset(-r) square(size);
}

// ---------- Front bezel (print face down) ----------
module front() {
    difference() {
        rounded(outer, front_h);
        // Window, mirrored because the front is the bottom face
        translate([outer.x / 2 - view_offset.x - view.x / 2 - 0.5,
                   outer.y / 2 + view_offset.y - view.y / 2 - 0.5, -1])
            cube([view.x + 1, view.y + 1, front_h + 2]);
        // Panel pocket
        translate([border, border, front_t]) cube([pocket.x, pocket.y, front_h]);
        // Pilot holes for M3 screws
        for (p = posts) translate([p.x, p.y, 0.8]) cylinder(d = 2.5, h = front_h);
    }
}

// ---------- Back shell (print floor down) ----------
module keyhole() {
    // Hang on a screw with a head of 8 mm or less
    translate([0, 0, -1]) cylinder(d = 8, h = 10);
    translate([-2, 0, -1]) cube([4, 10, 10]);
    translate([-4, 0, floor_t]) cube([8, 10, 2.5]);
}

module back() {
    h = depth + floor_t;
    port_z = floor_t + standoff;
    keyholes = [[outer.x * 0.25, outer.y - 30], [outer.x * 0.75, outer.y - 30]];
    difference() {
        union() {
            difference() {
                rounded(outer, h);
                translate([wall, wall, floor_t]) rounded([outer.x - 2 * wall, outer.y - 2 * wall], h, 1);
            }
            for (p = posts) translate([p.x, p.y, 0]) cylinder(d = post_d, h = h);
            // Ring that holds the panel edge at the shell mouth
            translate([0, 0, h - 1.5]) linear_extrude(1.5) difference() {
                square(outer);
                translate([border + 3, border + 3]) square([pocket.x - 6, pocket.y - 6]);
            }
            // Pi standoffs
            for (x = [0, PI[1].x], y = [0, PI[1].y])
                translate([pi_pos.x + PI[2] + x, pi_pos.y + PI[2] + y, 0])
                    cylinder(d = 6, h = floor_t + standoff);
            if (style != "desk")
                for (k = keyholes) translate([k.x - 8, k.y - 6, 0]) cube([16, 22, floor_t + 4]);
        }
        // Screw holes with head recess
        for (p = posts) translate([p.x, p.y, -1]) {
            cylinder(d = 3.4, h = h + 2);
            cylinder(d = 6.5, h = 4);
        }
        // Ribbon cable gap in the ring (bottom edge)
        translate([outer.x / 2 + fpc_offset - fpc_width / 2 - 2, wall, h - 2])
            cube([fpc_width + 4, border + 4, 3]);
        // Pi pilot holes (M2.5)
        for (x = [0, PI[1].x], y = [0, PI[1].y])
            translate([pi_pos.x + PI[2] + x, pi_pos.y + PI[2] + y, floor_t])
                cylinder(d = 2.2, h = standoff + 1);
        // Port opening in the bottom wall
        translate([pi_pos.x, -1, port_z]) cube([board.x, wall + 2, PI[4] + 3]);
        // USB and Ethernet opening in the right wall (pi2b)
        if (pi == "pi2b")
            translate([outer.x - wall - 1, pi_pos.y, port_z]) cube([wall + 2, board.y, PI[4] + 3]);
        // Vent slots
        for (i = [0:4]) translate([outer.x / 2 - 24 + i * 11, outer.y / 2 + 10, -1])
            rounded([4, 30], floor_t + 2, 1.9);
        if (style != "desk")
            for (k = keyholes) translate([k.x, k.y, 0]) keyhole();
    }
}

// ---------- Desk stand ----------
module stand() {
    t = front_h + depth + floor_t + 0.6;  // case thickness + gap
    size = [outer.x * 0.6, 60, 22];
    port_x = pi_pos.x + board.x / 2 - (outer.x - size.x) / 2;  // Pi ports, stand coordinates
    difference() {
        rounded([size.x, size.y], size.z, 4);
        // Slot for the case bottom edge, tilted back
        translate([-1, 8, 6]) rotate([-tilt, 0, 0]) cube([size.x + 2, t, 40]);
        // Cable channel below the Pi ports, out at the back
        translate([port_x - 25, 8, 3]) cube([50, size.y, 30]);
    }
}

// ---------- Output ----------
if (part == "front") front();
if (part == "back") back();
if (part == "stand") stand();
if (part == "all") {
    // Exploded view, front at the bottom
    color("white") front();
    color("gray") translate([border, border, front_t + foam]) cube([pocket.x - 2 * clear, pocket.y - 2 * clear, panel.z]);
    color("silver") translate([outer.x, 0, front_h + depth + floor_t + 30]) rotate([0, 180, 0]) back();
    if (style == "desk")
        color("orange") translate([outer.x * 0.2, -80, 0]) stand();
}
