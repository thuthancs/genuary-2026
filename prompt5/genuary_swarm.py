"""Write “Genuary”. Avoid using a font.

Swarm particles to form the letters of the word “Genuary”. Each letter should be clearly distinguishable, and the overall composition should be visually appealing. Use a variety of colors and sizes for the particles to create depth and interest. The background should be a solid color that contrasts well with the particles. Save the final image as "genuary_swarm.png".

Code Planning:
1. Define where the letter should be:
    - Create a grid or coordinate system to position the letters (x, y)
    - Define the shape of each letter using points or a simple font outline.
        + G: formed by 5 segments (a vertical line connected from (7, 0) to (7, 5), a top horizontal line from (7,5) to (11,5), a middle horizontal line from (7,3) to (11,3), and a bottom horizontal line from (7,0) to (11,0))
        + N: formed by 3 line segments - a vertical line from (13,0) to (13,5), a diagonal line from (17, 0) to (13, 5), and a vertical line from (0, 17) to (17, 5)
        + U: formed by 3 line segments - a vertical line from (19, 0) to (19, 5), a horizontal line from (19, 0) to (23, 0), and a vertical line from (23, 0) to (23, 5)
        + A: formed by 3 line segments - a diagonal line from (25, 0) to (29, 5), a horizontal line from (27, 3) to (31, 3), and a diagonal line from (29, 5) to (33,0)
        + R: formed by 2 line segments - a vertical line from (35, 0) to (35, 5), a horizontal line from (35, 5) to (40, 5)
        + Y: formed by 3 line segments - a diagonal line from (42, 5) to (44, 3), a vertical line from (44,3) to (44,0), and a diagonal line from (44, 3) to (46, 5)
2. Generate particles:
    - For each letter, generate a set of particles that roughly follow the shape of the letter.
    - Use random variations in position, size, and color to create a swarm effect.
    - The particles move directly towards the letters target (like magnet)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


def make_letter_segments():
    """
    Define simple line-segment skeletons for each letter in "GENUARY".
    Coordinates are on a coarse grid; we scale/normalize later.
    """
    # Format: list of ((x1, y1), (x2, y2)) segments
    segments = []

    # Coordinate layout (x‑range for each letter, y in [0, 5]).
    # Letter width ≈ 4 units, gap between letters ≈ 4 units for clear spacing:
    # G:  [0, 4.5]
    # E:  [8, 12]
    # N:  [16, 20]
    # U:  [24, 28]
    # A:  [32, 36]
    # R:  [40, 44]
    # Y:  [48, 52]

    # G: more classic G, with slightly extended bars and a clear inner bar
    segments += [
        ((0, 0), (0, 5)),       # left vertical
        ((0, 5), (4.5, 5)),     # top (slightly extended)
        ((0, 0), (4.5, 0)),     # bottom (slightly extended)
        ((4.5, 0), (4.5, 2.7)),  # right vertical (opening above)
        ((2.2, 2.7), (4.5, 2.7)),  # inner bar
    ]

    # E: left stem with three horizontals
    segments += [
        ((8, 0), (8, 5)),        # left vertical
        ((8, 5), (12, 5)),       # top
        ((8, 2.5), (10.8, 2.5)),  # middle (noticeably shorter)
        ((8, 0), (12, 0)),       # bottom
    ]

    # N: left vertical, diagonal, right vertical
    segments += [
        ((16, 0), (16, 5)),
        ((16, 5), (20, 0)),
        ((20, 0), (20, 5)),
    ]

    # U
    segments += [
        ((24, 5), (24, -0.5)),   # drop slightly below baseline
        ((24, -0.5), (28, -0.5)),
        ((28, -0.5), (28, 5)),
    ]

    # A
    segments += [
        ((32, 0), (34, 5)),
        ((36, 0), (34, 5)),
        ((33, 3), (35, 3)),
    ]

    # R: stem + rounded-ish loop + diagonal leg
    segments += [
        ((40, 0), (40, 5)),    # main stem
        ((40, 5), (43.5, 5)),  # top of loop
        ((43.5, 5), (44, 4.2)),
        ((44, 4.2), (44, 3.2)),
        ((44, 3.2), (43.5, 2.5)),
        ((43.5, 2.5), (40, 2.5)),
        ((40, 2.5), (44, 0)),  # diagonal leg
    ]

    # Y: raise meeting point of the fork a bit
    segments += [
        ((48, 5), (50, 3.5)),
        ((52, 5), (50, 3.5)),
        ((50, 3.5), (50, 0)),
    ]

    return segments


def sample_points_on_segments(
    segments,
    points_per_segment: int = 300,
    thickness: float = 0.0,
    rails: int = 1,
):
    """
    Sample many points along each line segment.

    - points_per_segment: number of samples along the length of the stroke.
    - thickness: distance to either side of the segment normal to create width.
    - rails: how many parallel "rails" across the thickness. 1 = hairline, 3+
      gives a chunkier letterform.
    """
    all_points = []

    for (x1, y1), (x2, y2) in segments:
        t = np.linspace(0.0, 1.0, points_per_segment, endpoint=True)
        xs = x1 + (x2 - x1) * t
        ys = y1 + (y2 - y1) * t
        base_pts = np.stack([xs, ys], axis=1)

        dx = x2 - x1
        dy = y2 - y1
        length = np.hypot(dx, dy)

        if thickness > 0.0 and rails > 1 and length > 0:
            # Unit normal vector perpendicular to the stroke
            nx = -dy / length
            ny = dx / length
            # Evenly spaced offsets across the stroke thickness
            offsets = np.linspace(-thickness, thickness, rails)
            for off in offsets:
                offset_vec = np.array([nx * off, ny * off])
                all_points.append(base_pts + offset_vec)
        else:
            all_points.append(base_pts)

    return np.vstack(all_points)


def _ease_in_out(t: float) -> float:
    """Smoothstep easing for nicer motion."""
    return t * t * (3 - 2 * t)


def _hsv_to_rgb(h, s, v):
    """Vectorized HSV → RGB conversion for arrays."""
    h = h % 1.0
    i = np.floor(h * 6).astype(int)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i_mod = i % 6

    r = np.choose(i_mod, [v, q, p, p, t, v])
    g = np.choose(i_mod, [t, v, v, q, p, p])
    b = np.choose(i_mod, [p, p, t, v, v, q])
    return np.stack([r, g, b], axis=-1)


def create_swarm_gif(
    width=1600,
    height=900,
    background_color=(1.0, 1.0, 1.0),
    n_frames=80,
    attraction_strength=0.08,
    jitter=0.008,
    seed=42,
    output_path="genuary_swarm.gif",
    final_frame_path="genuary_swarm.png",
):
    """
    Animate particles swarming in to form the word "Genuary"
    and save as an animated GIF.
    """
    rng = np.random.default_rng(seed)

    # Build target positions along letter skeletons
    segments = make_letter_segments()
    # Fewer points per segment but with multiple rails to give stroke width
    targets_letter_space = sample_points_on_segments(
        segments,
        points_per_segment=60,
        thickness=0.18,
        rails=3,
    )

    # Optionally widen the letters (and overall word) horizontally
    width_scale = 1.35  # >1.0 makes each letter position wider relative to height
    cx_grid = 0.5 * (targets_letter_space[:, 0].min() + targets_letter_space[:, 0].max())
    targets_letter_space[:, 0] = cx_grid + (targets_letter_space[:, 0] - cx_grid) * width_scale

    # Normalize letter coordinates into [0, 1] in both axes
    min_x, min_y = targets_letter_space.min(axis=0)
    max_x, max_y = targets_letter_space.max(axis=0)
    norm_x = (targets_letter_space[:, 0] - min_x) / (max_x - min_x)
    norm_y = (targets_letter_space[:, 1] - min_y) / (max_y - min_y)

    # Apply padding and map to canvas coordinates in [0, 1]
    pad_x = 0.08
    pad_y = 0.15
    px = pad_x + (1 - 2 * pad_x) * norm_x
    py = pad_y + (1 - 2 * pad_y) * norm_y
    targets = np.stack([px, py], axis=1)

    n_particles = targets.shape[0]

    # Initial positions: random across full canvas
    starts = rng.random((n_particles, 2))

    # Jittered targets so we don't land exactly on the line
    jittered_targets = targets + rng.normal(scale=0.01, size=targets.shape)

    # Precompute swarm positions over time using eased interpolation
    all_positions = []
    for frame_idx in range(n_frames):
        t = frame_idx / (n_frames - 1) if n_frames > 1 else 1.0
        alpha = _ease_in_out(t)

        # Noise stronger at the start, fades quickly near the end so the last
        # frame clearly reads as letters.
        noise_scale = jitter * (1.0 - alpha) ** 3
        noise = rng.normal(scale=noise_scale, size=starts.shape)

        pos = (1.0 - alpha) * starts + alpha * jittered_targets + noise
        pos = np.clip(pos, 0.0, 1.0)
        all_positions.append(pos)

    all_positions = np.stack(all_positions, axis=0)  # (T, N, 2)

    # Visual properties (based on target x‑position so they stay consistent)
    base_sizes = rng.uniform(5, 35, size=n_particles)
    center_x = 0.5
    dist_center = np.abs(targets[:, 0] - center_x)
    size_boost = np.exp(-((dist_center / 0.25) ** 2))
    sizes = base_sizes * (0.7 + 0.8 * size_boost)

    # Colors: warm‑cool palette
    base_hues = rng.uniform(0.0, 1.0, size=n_particles)
    warm_mask = size_boost > 0.7
    base_hues[warm_mask] = 0.05 + 0.1 * rng.random(np.sum(warm_mask))  # reds/oranges
    sats = rng.uniform(0.6, 1.0, size=n_particles)
    vals = rng.uniform(0.7, 1.0, size=n_particles)
    colors = _hsv_to_rgb(base_hues, sats, vals)

    # Make edges slightly dimmer to draw eye to center
    edge_falloff = np.exp(-((dist_center / 0.33) ** 2))
    colors = colors * (0.4 + 0.6 * edge_falloff)[:, None]

    # Create figure
    dpi = 200
    fig_w = width / dpi
    fig_h = height / dpi
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(background_color)

    scatter = ax.scatter(
        all_positions[0, :, 0],
        all_positions[0, :, 1],
        s=sizes,
        c=colors,
        marker="o",
        linewidths=0,
        alpha=0.95,
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])

    def update(frame_idx):
        scatter.set_offsets(all_positions[frame_idx])
        return (scatter,)

    anim = FuncAnimation(
        fig,
        update,
        frames=n_frames,
        interval=80,
        blit=True,
        repeat=True,
    )

    writer = PillowWriter(fps=10)
    anim.save(output_path, writer=writer)

    # Also save a high‑res PNG of the final frame
    if final_frame_path:
        scatter.set_offsets(all_positions[-1])
        fig.savefig(final_frame_path, dpi=dpi, facecolor=background_color)

    plt.close(fig)


if __name__ == "__main__":
    create_swarm_gif()

