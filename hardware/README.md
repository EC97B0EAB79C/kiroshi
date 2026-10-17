# Kiroshi case

3D-printable case for the Waveshare 7.3" e-Paper (E) panel (ribbon cable)
with the e-Paper Driver HAT on a Raspberry Pi 2 Model B or Pi Zero 2 W.

The model is parametric: `kiroshi.scad` (OpenSCAD).
Ready files are in `stl/`.

## Parts

| File | Part | Size (mm) |
| --- | --- | --- |
| `front_desk.stl`, `front_wall.stl` | Front bezel | 187 x 128 x 3.7 |
| `front_frame.stl` | Front bezel, wide border | 227 x 168 x 3.7 |
| `back_<pi>_<style>.stl` | Back shell with Pi mount | Pi Zero 2 W: depth 20.4, Pi 2B: depth 28.4 |
| `stand_<pi>_desk.stl` | Desk stand (15°) | 112 x 60 x 22 |

Styles:
- `desk`: case and stand. The cable goes out at the back of the stand.
- `wall`: case with 2 keyholes on the back.
- `frame`: like `wall`, with a 20 mm border like a photo frame.

Your printer bed must be 190 x 130 mm or larger (frame: 230 x 170 mm).
For a smaller bed, make `border` smaller in the file.

## Check before you print

I took these values from the published data. Measure your parts with a
caliper and change the values marked `CHECK` in `kiroshi.scad`:

- Panel outline (`panel`), active area (`view`, `view_offset`)
- Ribbon cable width and position (`fpc_width`, `fpc_offset`)
- Make sure that the ribbon cable reaches the Driver HAT.
  If not, move the Pi with `pi_pos`.

Print the front bezel first. Put the panel in it to check the fit.

## Print

- Material: PLA or PETG, 0.2 mm layers, 3 walls, 20% infill
- Front: face down. Back: floor down. Stand: base down. No supports.

## Assembly

You need:
- 4 x M3 x 25 screws (Pi Zero 2 W) or M3 x 30 (Pi 2B), self-tapping
- 4 x M2.5 x 6 screws for the Pi
- Foam tape, 0.5 mm, for the panel

1. Put foam tape on the inner edge of the front bezel.
2. Put the panel in the bezel, display side down. The ribbon cable is at the bottom.
3. Attach the Pi to the back shell with the M2.5 screws. Put the Driver HAT on the Pi.
4. Connect the ribbon cable to the Driver HAT.
5. Put the back shell on the bezel. Attach it with the 4 M3 screws.

Note: the Pi 2 Model B has no Wi-Fi. Use Ethernet or a USB Wi-Fi adapter.
The right side of the case has an opening for the USB and Ethernet ports.

## Make other variants

```sh
openscad -D 'pi="pi2b"' -D 'style="wall"' -D 'part="back"' -o back.stl kiroshi.scad
```

`part="all"` shows all parts together.
