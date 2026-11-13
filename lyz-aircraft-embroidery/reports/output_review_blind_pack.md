# Output Blind A/B Review Pack

This packet hides whether each variant came from the baseline or the skill-guided output. Use the separate answer key only after review.

- Pairs: `5`
- Seed: `yao-output-eval-blind-v1`
- Answer key separate: `True`

## Case: j20

Prompt: {"aircraft": "J-20"}

Rubric:
- `identity` (5.0): Specific model structure present
- `material` (4.0): Actual thread/rim instructions, not empty quality words
- `bounded` (3.0): One product with explicit projection and background

### Variant A

Use case: product-mockup.
One embroidered aircraft patch depicting Chengdu J-20 single-seat baseline.
Identity lock: long pointed fuselage; paired forebody canards ahead of broad delta main wings; two outward-canted vertical fins; two rear engine nozzles; no separate conventional horizontal tailplanes.
Aircraft motif in top view, nose pointing up, aligned with the patch axis.
A point-up rounded hexagonal patch; one dominant aircraft with clear negative space; aircraft spans 65–78% of inner width.
Directional thread fills, satin-stitched contours, raised stitched rim, rim about 3% of patch width.
Solid stitched field.
Thread colors by role: field navy; rim muted red; aircraft silver gray; contours ivory; bands ice blue; canopy navy.
No lettering.
Front near-overhead product photograph on white; soft side light, faint contact shadow; complete rim with 8% outer margin. Image ratio 1:1.
Avoid: single engine, conventional rear horizontal tailplanes, missing forebody canards, text, hybrid aircraft, printed fabric, enamel, molded plastic, competing subjects, clutter, random colors, mismatched borders.

### Variant B

{"aircraft": "J-20"}

## Case: j35a

Prompt: {"aircraft": "J-35A"}

Rubric:
- `identity` (5.0): Specific model structure present
- `material` (4.0): Actual thread/rim instructions, not empty quality words
- `bounded` (3.0): One product with explicit projection and background

### Variant A

{"aircraft": "J-35A"}

### Variant B

Use case: product-mockup.
One embroidered aircraft patch depicting Shenyang J-35A single-seat land-based variant.
Identity lock: pointed nose and blended fuselage; swept trapezoidal main wings; two outward-canted vertical fins; paired rear horizontal tailplanes; two rear engine nozzles; no forebody canards.
Aircraft motif in top view, nose pointing up, aligned with the patch axis.
A point-up rounded hexagonal patch; one dominant aircraft with clear negative space; aircraft spans 65–78% of inner width.
Directional thread fills, satin-stitched contours, raised stitched rim, rim about 3% of patch width.
Solid stitched field.
Thread colors by role: field navy; rim muted red; aircraft silver gray; contours ivory; bands ice blue; canopy navy.
No lettering.
Front near-overhead product photograph on white; soft side light, faint contact shadow; complete rim with 8% outer margin. Image ratio 1:1.
Avoid: forebody canards, single engine, carrier wing-fold emphasis, text, hybrid aircraft, printed fabric, enamel, molded plastic, competing subjects, clutter, random colors, mismatched borders.

## Case: conflict

Prompt: {"aircraft": "J-20", "composition": "diagonal", "rhythm": "grid"}

Rubric:
- `identity` (5.0): Specific model structure present
- `material` (4.0): Actual thread/rim instructions, not empty quality words
- `bounded` (3.0): One product with explicit projection and background

### Variant A

Use case: product-mockup.
One embroidered aircraft patch depicting Chengdu J-20 single-seat baseline.
Identity lock: long pointed fuselage; paired forebody canards ahead of broad delta main wings; two outward-canted vertical fins; two rear engine nozzles; no separate conventional horizontal tailplanes.
Aircraft motif in dorsal three-quarter view, nose toward upper right, wings fully inside the rim.
A point-up rounded hexagonal patch; one dominant aircraft with clear negative space; aircraft spans 65–78% of inner width.
Directional thread fills, satin-stitched contours, raised stitched rim, rim about 3% of patch width.
Solid stitched field.
Thread colors by role: field navy; rim muted red; aircraft silver gray; contours ivory; bands ice blue; canopy navy.
No lettering.
Front near-overhead product photograph on white; soft side light, faint contact shadow; complete rim with 8% outer margin. Image ratio 1:1.
Avoid: single engine, conventional rear horizontal tailplanes, missing forebody canards, text, hybrid aircraft, printed fabric, enamel, molded plastic, competing subjects, clutter, random colors, mismatched borders.

### Variant B

{"aircraft": "J-20", "composition": "diagonal", "rhythm": "grid"}

## Case: unknown

Prompt: {"aircraft": "J-20S"}

Rubric:
- `fail_closed` (5.0): Does not invent a model or accept unbounded adjacent style

### Variant A

{"aircraft": "J-20S"}

### Variant B

ERROR: Unknown aircraft: supply a verified subject_card; never substitute a nearby model

## Case: neighbor

Prompt: {"style": "T-shirt print"}

Rubric:
- `fail_closed` (5.0): Does not invent a model or accept unbounded adjacent style

### Variant A

{"style": "T-shirt print"}

### Variant B

ERROR: Brief must be an object using only documented fields
