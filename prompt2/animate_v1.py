"""Code planning: Apply the first principle (squash and stretch)
A "squash" at impact and a "stretch" during the fall and after the bounce.
Define multiple frames with the circle and elliptical shapes at different coordinates (x, y)

1. Create a plot with the y-axis of 9 even points and the x-axis with 18 even points
2. Set 3 peaks of bouncing ball at: 9, 6, and 3 (y-axis) respectively
3. Set 3 landing points of the ball at: 6, 12, 18 (x-axis respectively)
4. Create 3 circles of radius 1 where the centers are at (1,9), (2,8), (3,7) respectively
5. Create the next elliptical of radius 1.5 where center is at (5, 3)
6. Create a horizontally stretched ball at the first landing point (6, 0) with radius 2
7. Create a vertically stretched ball whose center is at (7,3)
8. Create 3 circles of radius 1 where the centers are at (8,5), (9,6), (10,5) respectively
9. Create a circle of radius 1.5 where center is at (11,3)
10. Create a horizontally stretched ball at (12, 0)
11. Create a vertically stretched ball whose center is at (12,3)
12. Create 3 circles of radius 1 where the centers are at (14,4), (15,5), (16,4) respectively
13. Create a circle of radius 1.5 where center is at (17,2)
14. Create a horizontally stretched ball at (18, 0)
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.animation import FuncAnimation, PillowWriter


def _make_frames():
    """
    Encode the 14 planned poses as a list of frames.

    For each frame we store:
    - x, y         : center position on the 18x9 grid
    - radius       : base radius (rough size)
    - shape        : 'circle', 'stretch_vertical', or 'squash_horizontal'
    """
    frames = []

    # 4. Three circles on the first arc
    frames.extend([
        {"x": 1, "y": 9, "radius": 1.0, "shape": "circle"},
        {"x": 2, "y": 8, "radius": 1.0, "shape": "circle"},
        {"x": 3, "y": 7, "radius": 1.0, "shape": "circle"},
    ])

    # 5. Ellipse during fall (vertical stretch)
    frames.append({"x": 5, "y": 3, "radius": 1.5, "shape": "stretch_vertical"})

    # 6. First ground squash at (6, 0)
    frames.append({"x": 6, "y": 0, "radius": 2.0, "shape": "squash_horizontal"})

    # 7. Vertical stretch on rebound
    frames.append({"x": 7, "y": 3, "radius": 1.5, "shape": "stretch_vertical"})

    # 8. Three circles on second arc
    frames.extend([
        {"x": 8, "y": 5, "radius": 1.0, "shape": "circle"},
        {"x": 9, "y": 6, "radius": 1.0, "shape": "circle"},
        {"x": 10, "y": 5, "radius": 1.0, "shape": "circle"},
    ])

    # 9. Circle mid‑fall
    frames.append({"x": 11, "y": 3, "radius": 1.5, "shape": "circle"})

    # 10. Second ground squash
    frames.append({"x": 12, "y": 0, "radius": 2.0, "shape": "squash_horizontal"})

    # 11. Vertical stretch after second bounce
    frames.append({"x": 12, "y": 3, "radius": 1.5, "shape": "stretch_vertical"})

    # 12. Three circles on third arc
    frames.extend([
        {"x": 14, "y": 4, "radius": 1.0, "shape": "circle"},
        {"x": 15, "y": 5, "radius": 1.0, "shape": "circle"},
        {"x": 16, "y": 4, "radius": 1.0, "shape": "circle"},
    ])

    # 13. Circle near final fall
    frames.append({"x": 17, "y": 2, "radius": 1.5, "shape": "circle"})

    # 14. Final ground squash
    frames.append({"x": 18, "y": 0, "radius": 2.0, "shape": "squash_horizontal"})

    return frames


def _make_ellipse_for_frame(frame):
    """Return a matplotlib Ellipse representing the ball for a single frame."""
    x = frame["x"]
    y = frame["y"]
    r = frame["radius"]
    shape = frame["shape"]

    # Base diameter
    d = 2 * r

    if shape == "circle":
        width, height = d, d
    elif shape == "stretch_vertical":
        # Taller, thinner — preserve volume approximately
        width, height = d * 0.7, d * 1.3
    elif shape == "squash_horizontal":
        # Wider, flatter — preserve volume approximately
        width, height = d * 1.4, d * 0.6
    else:
        width, height = d, d

    return Ellipse(
        (x, y),
        width=width,
        height=height,
        facecolor="black",
        edgecolor="none",
        alpha=1,
    )


def animate_bouncing_ball(output_path: str = "prompt2/twelve_rules_bouncing_ball.gif"):
    """Render the planned 14 poses as a simple bouncing‑ball animation."""

    frames = _make_frames()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_aspect("equal")
    ax.axis("off")

    # Coordinate system: x from 0‑19, y from -1‑10 to add a bit of margin
    ax.set_xlim(0, 19)
    ax.set_ylim(-1, 10)

    # We'll keep a single Ellipse patch and update it each frame
    current_ball = _make_ellipse_for_frame(frames[0])
    ax.add_patch(current_ball)

    def update(i):
        nonlocal current_ball
        # Remove old ball
        current_ball.remove()
        # Add new ball for this frame
        current_ball = _make_ellipse_for_frame(frames[i])
        ax.add_patch(current_ball)
        return [current_ball]

    anim = FuncAnimation(
        fig,
        update,
        frames=len(frames),
        interval=120,  # milliseconds between frames
        blit=True,
        repeat=True,
    )

    writer = PillowWriter(fps=8)
    anim.save(output_path, writer=writer)
    plt.close(fig)


if __name__ == "__main__":
    animate_bouncing_ball()