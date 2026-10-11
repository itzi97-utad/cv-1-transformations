# Computer Vision – Practice 1: Transformations

U-tad 2026/27 · Groups of 3 · **Due Sun 18 Oct 2026, 23:59 (CEST)** on Blackboard · no late submissions.
One member uploads a single `.ipynb` with the group names, the code, the results shown, and the justification of methods, parameters and results.

## Tasks

| Img | Task | Restriction | Pts | Notebook |
|---|---|---|---|---|
| 1 | Adaptive histogram equalisation / CLAHE, enhance contrast | own implementation | 2 | `01_clahe` |
| 2 | Remove noise | | 0.75 | `02_denoise` |
| 3 | Remove noise | | 0.75 | `03_denoise` |
| 4 | Gaussian filter, implement + apply | own implementation | 1.5 | `04_gaussian` |
| 5 | Kuwahara filter, implement + apply | own implementation | 1.5 | `05_kuwahara` |
| 6 | Edges of the objects | | 0.75 | `06_edges` |
| 7 | Detect objects | | 0.75 | `07_object_detection` |
| 8 | Locate key points | | 0.75 | `08_keypoints` |
| 9–10 | Compare the two images | | 1.25 | `09_10_comparison` |

**Penalties** (per image): weak or missing justification · methods that don't generalise to other sizes/channels, or missing parameters · result not the best possible.
**Image not graded:** result below 400×400 · colour image turned into black and white (or vice versa) · library used where it's forbidden.
Falsified results = 0 for the whole practice. Resizing is always allowed (keep ≥ 400×400).

All 10 images are colour (sizes from 500×750 up to 6092×4062), so every result must stay in colour.

## Setup

```bash
conda env create -f environment.yml      # or: make env
conda activate cv-p1
nbstripout --install                     # once per clone: keeps outputs out of git
```

Then download **Images.zip** from the assignment on Blackboard and unzip it into `data/raw/` (it's git-ignored, so every member does this once):

```bash
unzip ~/Downloads/Images.zip -d data/raw/
```

## Workflow

* Each task has its own notebook in `notebooks/`, so the three of us can work in parallel without notebook merge conflicts.
* `00_setup.ipynb` holds imports and shared helpers (`load_image`, `show`, `show_hist`, `check_resolution`, `resize_max_side`, `check_generic`). Each section notebook pulls it in with a `%run` cell tagged `dev-only`.
* Images are loaded in **RGB** order (OpenCV reads BGR; `load_image` converts).
* Group names go in `00_title.ipynb`.
* `make check` flags forbidden library calls in 01/04/05, colour→grey conversions and leftover TODOs.
* `make build` merges `00_title` → `00_setup` → `01…09_10` into `submission/P1_Transformations.ipynb` (dropping the `dev-only` cells), runs it from top to bottom and saves it with all outputs. That's the file to upload.

## Open questions for Sílvia

* Edges (6) and keypoints (8): most detectors (`cv2.Canny`, SIFT/ORB) work on a single channel internally. Is a greyscale conversion *inside* the method OK if the result is drawn on the colour image?
* Gaussian (4): is `cv2.filter2D` with a kernel we build ourselves allowed, or do we have to do the convolution by hand too?
