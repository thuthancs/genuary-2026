"""Fibonacci Sequence: Draw flower petals 

1. Start with a 2 lines, each of length 2, intersecting perpendicularly.
   This creates 4 line segments, each has a length of 1
2. From there, create a petal shape by drawing a curve on both sides of each line segment
3. Then, draw 2 lines (each of length 4) diagonally (45 degrees), which are centered at the same point as the first two lines segments
4. Create a petal shape by drawing a curve on both sides of each line segment
5. Repeat step 1-4, at each step, alternatively change between vertical line segments to diagonal and increase the size based on the Fibonacci sequence * 2 (2, 4, 6, 10, 16)
"""
from operator import length_hint
import os
import matplotlib.pyplot as plt
import numpy as np


def draw_fibonacci_flower(
    ax=None,
    angle_patterns=None,
    color="orange",
    fib_lengths=None,
    fill=True,
    edge=False,
    fill_alpha=0.2,
    edge_width=0.8,
):
    """Draw a Fibonacci-based flower on the given Matplotlib axis.

    If no axis is provided, a new figure is created and saved as a single image.
    """
    created_fig = False
    if ax is None:
        fig, ax = plt.subplots()
        created_fig = True

    ax.set_aspect("equal")
    ax.axis("off")

    def draw_segment(cx, cy, angle_deg, length, visible=False, **kwargs):
        angle = np.radians(angle_deg)
        
        dx = (length / 2) * np.cos(angle)
        dy = (length / 2) * np.sin(angle)
        x0, y0 = cx - dx, cy - dy
        x1, y1 = cx + dx, cy + dy
        if visible:
            ax.plot([x0, x1], [y0, y1], **kwargs)
        return (x0, y0, x1, y1)

    def draw_petals_on_segment(x0, y0, x1, y1, curvature=0.4, **kwargs):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        
        vx, vy = x1 - x0, y1 - y0
        length = np.hypot(vx, vy)
        if length == 0:
            return
        
        ux, uy = vx / length, vy / length
        px, py = -uy, ux 
        
        c1x, c1y = mx + curvature * length * px, my + curvature * length * py
        c2x, c2y = mx - curvature * length * px, my - curvature * length * py

        # sample t from 0..1 for the two arcs
        t = np.linspace(0, 1, 40)

        # choose edge / fill color
        edge_kwargs = kwargs.copy()
        edge_color = edge_kwargs.pop("color", "orange")

        # arc 1: from (x0,y0) to (x1,y1) via c1
        x_arc1 = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * c1x + t ** 2 * x1
        y_arc1 = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * c1y + t ** 2 * y1

        # arc 2: via c2
        x_arc2 = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * c2x + t ** 2 * x1
        y_arc2 = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * c2y + t ** 2 * y1

        # draw edge if requested
        if edge:
            ax.plot(x_arc1, y_arc1, color=edge_color, linewidth=edge_width)
            ax.plot(x_arc2, y_arc2, color=edge_color, linewidth=edge_width)

        # filled petal between the two arcs
        if fill and fill_alpha > 0:
            x_fill = np.concatenate([x_arc1, x_arc2[::-1]])
            y_fill = np.concatenate([y_arc1, y_arc2[::-1]])
            ax.fill(x_fill, y_fill, color=edge_color, alpha=fill_alpha, linewidth=0)

    # Fibonacci-based lengths * 2: 2, 4, 6, 10, 16, ...
    if fib_lengths is None:
        fib_lengths = [2, 2, 4, 6, 10, 16, 26, 42, 68, 110, 178]
    cx, cy = 0.0, 0.0  # center of all generations

    # alternate between axis-aligned and diagonal lines
    if angle_patterns is None:
        angle_patterns = [
            [90, 0],    # vertical + horizontal
            [45, -45],  # diagonals
        ]

    for gen, length in enumerate(fib_lengths):
        angles = angle_patterns[gen % len(angle_patterns)]

        # compute the 2 main segments for this generation (not drawn)
        segs = []
        for ang in angles:
            segs.append(draw_segment(cx, cy, ang, length))

        # each main segment creates 2 children (its halves)
        children = []
        for (x0, y0, x1, y1) in segs:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            children.append((x0, y0, mx, my))
            children.append((mx, my, x1, y1))

        # draw petals on the 4 children for this generation
        for (x0, y0, x1, y1) in children:
            draw_petals_on_segment(x0, y0, x1, y1, color=color)

    # set limits large enough that petals are not clipped
    ax.set_xlim(-60, 60)
    ax.set_ylim(-60, 60)

    # if we created the figure here, save a standalone image
    if created_fig:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "fibonacci_flower.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.show()


def draw_fibonacci_flower_grid():
    """Create a 3x3 grid of Fibonacci flowers using the 90/45 angle pattern and varying colors."""
    fig, axes = plt.subplots(3, 3, figsize=(9, 9))
    fig.subplots_adjust(wspace=0.1, hspace=0.1)
    colors = [
        "#D94446",
        "#FA5053",
        "#FA766E",
        "#1A4A96",
        "#3E80D3",
        "#66A7E1",
        "#FF9900",
        "#FFCC33",
        "#FFE066",
    ]

    base_patterns = [
        [90, 0],
        [45, -45],
    ]

    for idx, ax in enumerate(axes.flat):
        draw_fibonacci_flower(
            ax=ax,
            angle_patterns=base_patterns,
            color=colors[idx],
            fill=True,
            edge=False,
            fill_alpha=0.2,
        )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    grid_path = os.path.join(script_dir, "fibonacci_flower_grid.png")
    fig.savefig(grid_path, dpi=300, bbox_inches="tight")
    plt.show()


def draw_fibonacci_flower_grid_outline():
    """Create a 3x3 grid of Fibonacci flowers with colored outlines and no fill."""
    fig, axes = plt.subplots(3, 3, figsize=(9, 9))
    fig.subplots_adjust(wspace=0.1, hspace=0.1)
    colors = [
        "#D94446",
        "#FA5053",
        "#FA766E",
        "#1A4A96",
        "#3E80D3",
        "#66A7E1",
        "#FF9900",
        "#FFCC33",
        "#FFE066",
    ]

    base_patterns = [
        [90, 0],
        [45, -45],
    ]

    for idx, ax in enumerate(axes.flat):
        draw_fibonacci_flower(
            ax=ax,
            angle_patterns=base_patterns,
            color=colors[idx],
            fill=False,
            edge=True,
            edge_width=1.2,
        )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    grid_path = os.path.join(script_dir, "fibonacci_flower_grid_outline.png")
    fig.savefig(grid_path, dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    draw_fibonacci_flower_grid()
    draw_fibonacci_flower_grid_outline()