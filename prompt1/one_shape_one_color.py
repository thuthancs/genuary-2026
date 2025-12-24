"""
Code planning: This script generates an image containing a single geometric shape of a specific color.

1. Start by drawing a circle of a specific radius and color with a chosen opacity
2. Draw an invisible square that fits inside that circle
3. Draw 4 smaller cicles, each touches one side of the square
4. Continue until max_iterations is reached
5. Save the image as a PNG file
"""
import matplotlib.pyplot as plt


def _draw_pattern(ax,
                  radius: float,
                  color: str,
                  alpha: float,
                  max_iterations: int,
                  shrink_fraction: float,
                  center_x: float,
                  center_y: float):
    """Draw one recursive circle pattern centered at (center_x, center_y)."""

    def _draw_recursive(cx: float, cy: float, r: float, iteration: int):
        circle = plt.Circle((cx, cy), r, color=color, alpha=alpha, fill=True, linewidth=0)
        ax.add_patch(circle)
        if iteration >= max_iterations:
            return

        # Calculate the side length of the inscribed square
        side = r * (2 ** 0.5)
        half_side = side / 2

        # Make each smaller circle a fixed fraction of the current circle
        smaller_r = r * shrink_fraction

        # Place circle centers so each child circle is tangent to
        # one edge of the (invisible) inscribed square.
        centers = [
            (cx - half_side - smaller_r, cy),  # touches left edge
            (cx + half_side + smaller_r, cy),  # touches right edge
            (cx, cy - half_side - smaller_r),  # touches bottom edge
            (cx, cy + half_side + smaller_r),  # touches top edge
        ]

        for (nx, ny) in centers:
            _draw_recursive(nx, ny, smaller_r, iteration + 1)

    _draw_recursive(center_x, center_y, radius, 0)


def draw_one_shape_one_color(radius: float,
                             color: str,
                             alpha: float,
                             max_iterations: int,
                             shrink_fraction: float,
                             output_path: str):
    
    # Create a square canvas
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw a single pattern at the origin
    _draw_pattern(ax, radius, color, alpha, max_iterations, shrink_fraction, 0.0, 0.0)

    # Give extra room so outer circles are not clipped
    margin = radius * 1.8
    ax.set_xlim(-margin, margin)
    ax.set_ylim(-margin, margin)

    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)


def draw_grid_one_shape_one_color(radius: float,
                                  color: str,
                                  alpha: float,
                                  max_iterations: int,
                                  shrink_fractions_3x3,
                                  output_path: str):
    """
    Draw a 3x3 grid of patterns, each with its own shrink_fraction.

    shrink_fractions_3x3 should be a list of 3 lists, each with 3 values.
    """

    fig, axes = plt.subplots(3, 3, figsize=(8, 8))

    # Same view box for every subplot so patterns are comparable
    margin = radius * 1.8

    for row in range(3):
        for col in range(3):
            ax = axes[row][col]
            ax.set_aspect("equal")
            ax.axis("off")

            shrink_fraction = shrink_fractions_3x3[row][col]
            _draw_pattern(ax, radius, color, alpha, max_iterations,
                          shrink_fraction, 0.0, 0.0)

            ax.set_xlim(-margin, margin)
            ax.set_ylim(-margin, margin)

    fig.tight_layout(pad=0.5)

    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)

if __name__ == "__main__":
    # You can tweak these values to experiment:
    # - radius changes the overall size
    # - color picks the shape color
    # - alpha controls opacity (0.0 transparent → 1.0 solid)
    # - max_iterations controls how dense/complex the pattern becomes
    # Example: single pattern
    # draw_one_shape_one_color(radius = 2,
    #                          color = "pink",
    #                          alpha = 0.2,
    #                          max_iterations = 2,
    #                          shrink_fraction = 0.7,
    #                          output_path = "prompt1/one_shape_one_color_single.png")

    # Example: 3x3 grid with different shrink fractions
    grid_shrink_fractions = [
        [0.7, 0.75, 0.8],
        [0.85, 0.9, 0.95],
        [1.0, 1.1, 1.2],
    ]
    draw_grid_one_shape_one_color(
        radius=2,
        color="pink",
        alpha=0.2,
        max_iterations=2,
        shrink_fractions_3x3=grid_shrink_fractions,
        output_path="prompt1/one_shape_one_color_grid.png",
    )
        
        
        
        
    