import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.animation import FuncAnimation, PillowWriter


BASE_RADIUS = 1.0
BASE_DIAMETER = BASE_RADIUS * 2


def _key_poses():
    """
    Return the original 14 poses, but as key poses with explicit
    position (x, y) and squash/stretch scales (sx, sy).

    - Circles:       sx = 1,   sy = 1
    - Vert. stretch: sx < 1,   sy > 1
    - Horiz. squash: sx > 1,   sy < 1
    """
    circle = lambda x, y: {"x": x, "y": y, "sx": 1.0, "sy": 1.0}
    v_stretch = lambda x, y: {"x": x, "y": y, "sx": 0.8, "sy": 1.2}
    h_squash = lambda x, y: {"x": x, "y": y, "sx": 1.4, "sy": 0.6}

    poses = []

    # 4. Three circles of radius 1 at (1,9), (2,8), (3,7)
    poses.extend([
        circle(1, 9),
        circle(2, 8),
        circle(3, 7),
    ])

    # 5. Ellipse at (5,3), stretched vertically
    poses.append(v_stretch(5, 3))

    # 6. Horizontally stretched ball at (6,0)
    poses.append(h_squash(6, 0))

    # 7. Vertically stretched ball at (7,3)
    poses.append(v_stretch(7, 3))

    # 8. Three circles at (8,5), (9,6), (10,5)
    poses.extend([
        circle(8, 5),
        circle(9, 6),
        circle(10, 5),
    ])

    # 9. Circle of radius 1.5 at (11,3) – treat as slightly larger circle
    poses.append({"x": 11, "y": 3, "sx": 1.2, "sy": 1.2})

    # 10. Horizontally stretched ball at (12,0)
    poses.append(h_squash(12, 0))

    # 11. Vertically stretched ball at (12,3)
    poses.append(v_stretch(12, 3))

    # 12. Three circles at (14,4), (15,5), (16,4)
    poses.extend([
        circle(14, 4),
        circle(15, 5),
        circle(16, 4),
    ])

    # 13. Circle of radius 1.5 at (17,2)
    poses.append({"x": 17, "y": 2, "sx": 1.2, "sy": 1.2})

    # 14. Horizontally stretched ball at (18,0)
    poses.append(h_squash(18, 0))

    return poses


def _ease_in_out(t: float) -> float:
    """Smoothstep easing: slow in, fast middle, slow out."""
    return t * t * (3 - 2 * t)


def _tween_poses(poses, steps_between: int = 4):
    """
    Create in-between frames between each key pose using easing.

    For each consecutive pair of poses p0 -> p1, we generate
    `steps_between` interpolated poses, then include p1.
    """
    if not poses:
        return []

    frames = [poses[0]]

    for i in range(len(poses) - 1):
        p0 = poses[i]
        p1 = poses[i + 1]

        for step in range(1, steps_between + 1):
            t = step / (steps_between + 1)
            te = _ease_in_out(t)

            frame = {
                "x": p0["x"] + (p1["x"] - p0["x"]) * te,
                "y": p0["y"] + (p1["y"] - p0["y"]) * te,
                "sx": p0["sx"] + (p1["sx"] - p0["sx"]) * te,
                "sy": p0["sy"] + (p1["sy"] - p0["sy"]) * te,
            }
            frames.append(frame)

        frames.append(p1)

    return frames


def _update_ellipse_from_frame(ellipse: Ellipse, frame: dict):
    """Apply position and squash/stretch to an existing ellipse."""
    x = frame["x"]
    y = frame["y"]
    sx = frame["sx"]
    sy = frame["sy"]

    ellipse.center = (x, y)
    ellipse.width = BASE_DIAMETER * sx
    ellipse.height = BASE_DIAMETER * sy


def animate_bouncing_ball_v2(
    output_path: str = "prompt2/bouncing_ball_v2.gif",
    steps_between: int = 4,
):
    """
    Improved bouncing ball:
    - Uses your original 14 poses as key poses.
    - Adds eased in-between frames for smoother motion.
    - Interpolates squash/stretch continuously instead of snapping.
    """

    key_poses = _key_poses()
    frames = _tween_poses(key_poses, steps_between=steps_between)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_aspect("equal")
    ax.axis("off")

    # Coordinate system: x from 0‑19, y from -1‑10 to add a bit of margin
    ax.set_xlim(0, 19)
    ax.set_ylim(-1, 10)

    # Initial ellipse
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
        interval=10,  # ms between frames (lower = faster)
        blit=True,
        repeat=True,
    )

    writer = PillowWriter(fps=24)
    anim.save(output_path, writer=writer)
    plt.close(fig)


if __name__ == "__main__":
    animate_bouncing_ball_v2()
