# Math Video Engine

A standalone, accessible mathematical animation and video generation engine recreating core visual mathematics concepts, number theory conjectures, and Veritasium scientific paradoxes with zero external OpenGL or LaTeX runtime dependencies.

## Overview

Mathematical animation libraries often require complex toolchains, brittle system packages (such as TeX Live, Cairo, and ModernGL), and hardcoded asset paths. The Math Video Engine provides a clean, self-contained Python architecture for programmatically constructing and rendering high-resolution mathematical visualizations.

The engine recreates foundational educational scenes popularized in visual mathematics, covering linear algebra, single-variable calculus, Fourier analysis, deep learning, pure number theory (Strong and Weak Goldbach Conjectures), and seminal Veritasium physical and mathematical paradoxes.

Frames are synthesized via an internal orthographic camera projection pipeline built on Pillow and NumPy, allowing deterministic, cross-platform rendering without GPU context requirements. Export pipelines stream raw RGBA frames directly into FFmpeg for hardware-accelerated H.264/MP4 generation, with native fallbacks to animated GIF, animated WebP, and numbered image sequences.

## Architectural Design

The engine is decoupled into modular layers:

- Coordinate Projection: The Camera translates two-dimensional mathematical world coordinates into discrete raster screen pixel space. Mathematical Cartesian coordinates (+Y pointing upward with (0,0) at screen center) are mapped seamlessly to top-left inverted screen coordinates.
- Object Model (MObject): Mathematical graphical primitives (points, lines, arrows, arcs, polygons, circles, curves, coordinate planes, and neural network graphs) maintain geometric properties and affine transformation methods (shift, scale, rotate, apply_matrix).
- Visual Aesthetics: Dark slate background palette (#0F141D) with high-contrast vector highlights (3Blue1Brown color harmonies: Blue, Teal, Green, Yellow, Gold, Red, Purple).
- Animation and Timeline: Rate functions (smooth, ease-in, ease-out, bounce) and keyframe interpolators govern progressive drawing, opacity fades, affine movement, and linear grid deformations.
- Headless Rasterizer: Frame rasterization runs headlessly in memory without requiring X11, Wayland, or desktop display servers.
- Multi-Format Exporters: Direct stdout-to-stdin FFmpeg pipe encoding for MP4 video, Pillow quantization for animated GIF, lossless/lossy WebP, and PNG image sequences.

## Recreated Video Scenes Catalog

The engine includes 20 built-in scenes organized into 6 thematic modules:

### 1. Number Theory: Goldbach Conjectures
- StrongGoldbachConjectureScene: Visualizes Euler's 1742 binary conjecture that every even integer 2n > 2 is the sum of two primes. Displays prime axes, semicircular linking arcs connecting prime pairs (p1, p2), and the asymptotic growth envelope of Goldbach's comet.
- WeakGoldbachConjectureScene: Visualizes the ternary Goldbach conjecture that every odd integer 2n + 1 > 5 is the sum of three primes (p1 + p2 + p3). Illustrates Harald Helfgott's 2013 unconditional proof and the logical implication linking the Strong and Weak conjectures.

### 2. Veritasium Mathematical and Scientific Paradoxes
- CollatzConjectureScene: Recreates Veritasium's "The Simplest Math Problem No One Can Solve" (the 3x + 1 problem), visualizing hailstone trajectories ascending and collapsing deterministically into the 4 -> 2 -> 1 attractor loop.
- LogisticMapChaosScene: Recreates Veritasium's "This Equation Will Change How You See The World", illustrating the discrete logistic population recurrence x_(n+1) = r * x_n * (1 - x_n), the period-doubling cascade, the Feigenbaum constant delta ~ 4.669, and deterministic chaos.
- HundredPrisonersRiddleScene: Recreates Veritasium's "The Riddle That Seems Impossible Even If You Know The Answer", contrasting independent random selection ((1/2)^100 ~ 8 * 10^-31) against the permutation cycle loop strategy achieving a 31.18% survival probability.
- OptimalStoppingScene: Recreates Veritasium's "The Mathematics of Finding the Best Partner / 37% Rule" (the Secretary Problem), illustrating the derivative of P(r) = -r * ln(r) and the optimal 1/e ~ 36.8% rejection threshold.
- DoubleSlitInterferenceScene: Recreates Veritasium's "The Quantum Experiment That Broke Reality", illustrating coherent spherical wavefront propagation, path-length differences, and constructive/destructive interference fringes.

### 3. Linear Algebra
- VectorLinearCombinationScene: Demonstrates the canonical basis vectors i-hat and j-hat, scalar scaling, and vector addition forming the linear span.
- MatrixTransformationScene: Demonstrates how a 2x2 matrix transforms the entire coordinate space while keeping grid lines straight and evenly spaced.
- DeterminantAreaScene: Demonstrates the geometric interpretation of the determinant as the signed area scaling factor of a transformed unit square.
- EigenvectorTransformationScene: Demonstrates linear transformations where eigenvectors lie along invariant span lines, undergoing pure scalar multiplication without rotation.

### 4. Calculus
- DerivativeTangentScene: Demonstrates the fundamental derivative paradox, showing a secant line with delta x approaching zero converging smoothly to the instantaneous tangent.
- RiemannIntegralScene: Demonstrates numerical integration where Riemann rectangular partitions refine from N=4 to N=12 to N=30, converging to the exact area under a parabolic curve.
- TaylorSeriesScene: Demonstrates polynomial approximations of sin(x), displaying the Maclaurin series expansion across degrees 1, 3, and 5.

### 5. Fourier Analysis
- FourierEpicyclesScene: Demonstrates complex exponential Fourier series as rotating tip-to-tail epicycles tracing a continuous closed trajectory.
- FourierWaveDecompositionScene: Demonstrates the decomposition of a square wave into its odd harmonic sinusoidal components (1st, 3rd, and 5th harmonics).

### 6. Neural Networks and Mathematical Physics
- NeuralNetworkArchitectureScene: Demonstrates a multi-layer feedforward neural network architecture (input, two hidden layers, output) with forward signal activation pulses.
- GradientDescentOptimizationScene: Demonstrates parameter optimization across a 2D loss surface contour map, tracking trajectory steps along the negative gradient vector.
- PiCollidingBlocksScene: Demonstrates Galperin's billiard ball collision calculation of Pi, simulating elastic impacts between an obstacle wall, a small mass, and a large mass.
- BaselProblemScene: Demonstrates Euler's solution to the sum of inverse squares connecting lighthouse inverse-square law circles to pi squared divided by six.

## Feasibility Analysis and Testing of Veritasium Recreations

As part of the evaluation to determine whether all Veritasium videos can be programmatically recreated in this codebase, the catalog was analyzed and tested against programmatic rendering criteria:

1. Catalog Taxonomy and Volume:
   The Veritasium channel contains over 420 videos produced between 2011 and 2026. The catalog divides into two distinct archetypes:
   - Theoretical, Mathematical, and Algorithmic Concepts: Mathematical paradoxes, probabilistic decision theory, quantum mechanics, and recursion (for example, the Collatz Conjecture, the Logistic Map, the 100 Prisoners Problem, the Secretary Problem, and Wave Interference).
   - Live-Action Documentary and Empirical Physical Experiments: On-location journalism and physical experiments (for example, visiting Chernobyl, physical drone acrobatics, spinning high-speed gyroscopes, fluid dynamics tanks, and interview dialogues).

2. Feasibility Test Results:
   - For all theoretical, mathematical, and algorithmic Veritasium topics, programmatic rendering is 100% viable. The engine fully recreates these videos with deterministic, mathematically exact visual pipelines.
   - For live-action empirical documentary footage, programmatic synthetic generation via mathematical code is neither intended nor physically appropriate, as these works rely on photographic camera recordings of human subjects and physical materials.
   - Conclusion: All theoretical and mathematical Veritasium concepts are fully visualizable and integrated into this repository under the `Veritasium Paradoxes` module.

## Installation

### Prerequisites
- Python 3.10 or higher
- FFmpeg (optional, recommended for MP4 video export; GIF and WebP export operate without FFmpeg)

### Installing from Source

```bash
git clone https://gitlab.com/jk9576/math-video-engine.git
cd math-video-engine
pip install -e .
```

To install with development and testing dependencies:

```bash
pip install -e ".[dev]"
```

## Command-Line Interface (CLI)

The package provides the `math-video-engine` executable.

### Listing Registered Scenes

```bash
math-video-engine list
```

Outputs the catalog of 20 scenes, categories, and descriptions.

### Inspecting Scene Structure

Inspect total duration, timeline segments, and active animations before rendering:

```bash
math-video-engine inspect StrongGoldbachConjectureScene
math-video-engine inspect CollatzConjectureScene
```

### Rendering a Scene

Render a specific scene to MP4, GIF, WebP, or frame sequences:

```bash
# Render Strong Goldbach Conjecture to MP4 at 1080p 30 FPS
math-video-engine render StrongGoldbachConjectureScene --preset 1080p --fps 30 --format mp4

# Render Weak Goldbach Conjecture to animated GIF
math-video-engine render WeakGoldbachConjectureScene --preset 720p --fps 20 --format gif

# Render Veritasium Collatz Conjecture to MP4
math-video-engine render CollatzConjectureScene --preset 1080p --fps 30 --format mp4

# Render Veritasium 100 Prisoners Riddle to MP4
math-video-engine render HundredPrisonersRiddleScene --preset 1080p --fps 30 --format mp4
```

Supported resolution presets:
- `preview`: 480x270
- `480p`: 854x480
- `720p`: 1280x720 (default)
- `1080p`: 1920x1080
- `1440p`: 2560x1440
- `4k`: 3840x2160

### Batch Rendering All Scenes

To batch render all registered scenes in a single command:

```bash
math-video-engine render-all --preset 720p --fps 30 --format mp4 --output-dir output
```

## Python API Reference

### Constructing a Custom Scene

Users can author new mathematical scenes by subclassing `Scene` and implementing `construct()`:

```python
from math_video_engine import (
    Scene,
    NumberPlane,
    Vector,
    ApplyMatrix,
    Create,
    GREEN,
    YELLOW,
)

class CustomEigenScene(Scene):
    def construct(self):
        plane = NumberPlane()
        v = Vector(coords=(1.0, 1.0), color=YELLOW)
        
        self.add(plane)
        self.play(Create(v), run_time=1.0)
        self.wait(0.5)
        
        # Apply shear matrix
        shear_matrix = [[1.5, 0.5], [0.0, 1.0]]
        self.play(
            ApplyMatrix(plane, shear_matrix, run_time=2.0),
            ApplyMatrix(v, shear_matrix, run_time=2.0),
        )
        self.wait(1.0)
```

### Programmatic Rendering

```python
from math_video_engine import RenderConfig, export_video
from math_video_engine.scenes.goldbach import StrongGoldbachConjectureScene

config = RenderConfig.from_preset("1080p", fps=30)
scene = StrongGoldbachConjectureScene(config=config)
output_file = export_video(scene, output_path="output/goldbach.mp4", output_format="mp4")
print(f"Rendered video saved to {output_file}")
```

## Test Suite and Verification

The repository contains an automated test suite executed with `pytest`:

```bash
pytest -v
```

The test suite covers:
- Coordinate mapping accuracy and Camera invertibility (world to pixel and pixel to world).
- Color parsing, hex decoding, alpha composition, and gradient interpolations.
- Easing curve monotonicity and boundary conditions.
- Geometric transformations (shift, rotate, scale, matrix application).
- Z-index layer ordering and headless canvas rasterization.
- Timeline scheduling, parallel segment orchestration, and cursor advancement.
- Exporter output validation for GIF, WebP, MP4, and frame sequences.
- Integration test for all 20 registered scenes ensuring valid duration and frame synthesis.
- CLI argument parsing, subcommands, and error handling.

## Continuous Integration

A `.gitlab-ci.yml` pipeline configuration is included, automating two pipeline stages on GitLab:
1. `test`: Executes `pytest -v --tb=short` in a clean Python 3.12 Linux container with FFmpeg installed.
2. `render`: Runs smoke-test video renderings of selected scenes and stores the resulting MP4 and GIF artifacts for validation.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
