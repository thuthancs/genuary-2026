import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.animation import FuncAnimation, PillowWriter


BASE_RADIUS = 1.0
BASE_DIAMETER = BASE_RADIUS * 2.0


def _generate_bounce_frames(
    x_start: float,
    x_end: float,
    peak_height: float,
    air_steps: int,
    include_squash: bool,
):
    """
    Generate frames for one bounce using a simple parabolic arc.

    - x(t) moves linearly from x_start to x_end
    - y(t) follows y = peak_height * 4 * t * (1 - t), t in [0, 1]
    - squash & stretch are derived from height: closer to ground => more stretch
    - at the landing (t = 1) we optionally add a short squash sequence
    """
    frames = []

    # Airborne frames (exclude t=0 and t=1 so we can control impact separately)
    for i in range(1, air_steps + 1):
        t = i / (air_steps + 1)  # (0, 1)

        x = x_start + (x_end - x_start) * t
        y = peak_height * 4.0 * t * (1.0 - t)

        # Height ratio (0 near ground, 1 at peak)
        height_ratio = y / peak_height if peak_height > 0 else 0.0

        # More vertical stretch when closer to ground, but stay subtle
        stretch_strength = 0.35
        vertical_scale = 1.0 + stretch_strength * (1.0 - height_ratio)
        horizontal_scale = 1.0 / vertical_scale  # approx volume preservation

        frames.append(
            {"x": x, "y": y, "sx": horizontal_scale, "sy": vertical_scale}
        )

    # Landing at x_end, y=0 with squash sequence
    if include_squash:
        squash_x = x_end
        squash_y = 0.0

        # Ease into squash, hit max squash, then ease out slightly
        squash_poses = [
            {"sx": 1.2, "sy": 0.8},
            {"sx": 1.6, "sy": 0.5},
            {"sx": 1.3, "sy": 0.7},
        ]

        for pose in squash_poses:
            frames.append(
                {
                    "x": squash_x,
                    "y": squash_y,
                    "sx": pose["sx"],
                    "sy": pose["sy"],
                }
            )

    return frames


def _generate_all_frames():
    """
    Generate frames for three bounces across the screen with
    decreasing peak heights and consistent timing.
    """
    all_frames = []

    bounces = [
        # (x_start, x_end, peak_height)
        (0.0, 6.0, 9.0),
        (6.0, 12.0, 6.0),
        (12.0, 18.0, 3.0),
    ]

    for idx, (x0, x1, h) in enumerate(bounces):
        frames = _generate_bounce_frames(
            x_start=x0,
            x_end=x1,
            peak_height=h,
            air_steps=14,
            include_squash=True,
        )
        all_frames.extend(frames)

    return all_frames


def _update_ellipse_from_frame(ellipse: Ellipse, frame: dict):
    """Apply position and squash/stretch to an existing ellipse."""
    x = frame["x"]
    y = frame["y"]
    sx = frame["sx"]
    sy = frame["sy"]

    ellipse.center = (x, y)
    ellipse.width = BASE_DIAMETER * sx
    ellipse.height = BASE_DIAMETER * sy


def animate_bouncing_ball_v3(
    output_path: str = "prompt2/bouncing_ball_v3.gif",
):
    """
    Bouncing ball with:
    - Parabolic motion for each bounce (physically consistent arcs)
    - Decreasing bounce heights
    - Continuous squash & stretch based on height
    - Extra squash frames exactly at impact
    """

    frames = _generate_all_frames()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_aspect("equal")
    ax.axis("off")

    # Coordinate system: x from 0‑19, y from -1‑10 to add a bit of margin
    ax.set_xlim(0, 19)
    ax.set_ylim(-1, 10)

    initial = frames[0]
    ball = Ellipse(
        (initial["x"], initial["y"]),
        width=BASE_DIAMETER * initial["sx"],
        height=BASE_DIAMETER * initial["sy"],
        facecolor="black",
        edgecolor="none",
        alpha=1.0,
    )
    ax.add_patch(ball)

    def update(i):
        frame = frames[i]
        _update_ellipse_from_frame(ball, frame)
        return [ball]

    anim = FuncAnimation(
        fig,
        update,
        frames=len(frames),
        interval=40,  # ms between frames
        blit=True,
        repeat=True,
    )

    writer = PillowWriter(fps=24)
    anim.save(output_path, writer=writer)
    plt.close(fig)


if __name__ == "__main__":
    animate_bouncing_ball_v3()
