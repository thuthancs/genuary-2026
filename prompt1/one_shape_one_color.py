"""
Code planning: This script generates an image containing a single geometric shape of a specific color.

1. Start by drawing a circle of a specific radius and color with a chosen opacity
2. Draw an invisible square that fits inside that circle
3. Draw 4 smaller cicles, each touches one side of the square
4. Continue until max_iterations is reached
5. Save the image as a PNG file
"""
import matplotlib.pyplot as plt

def draw_one_shape_one_color(radius: float,
                             color: str,
                             alpha: float,
                             max_iterations: int,
                             output_path: str):
    
    # Create a square canvas
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect('equal')
    ax.axis('off')
    
    def _draw_recursive(cx: float, cy: float, 
                        r: float, iteration: int):
        circle = plt.Circle((cx, cy), r, color=color, alpha=alpha, fill=True, linewidth=0)
        ax.add_patch(circle)
        if iteration >= max_iterations:
            return
        
        # Calculate the side length of the inscribed square
        side = r * (2 ** 0.5)
        half_side = side / 2
        
        # Make each smaller circle a fixed fraction of the current circle
        shrink_fraction = 0.7 # try values between 0 and 1
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
    
    # Start the recursive drawing
    _draw_recursive(0, 0, radius, 0)

    # Give extra room so outer circles are not clipped
    margin = radius * 1.8
    ax.set_xlim(-margin, margin)
    ax.set_ylim(-margin, margin)

    fig.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)

if __name__ == "__main__":
    # You can tweak these values to experiment:
    # - radius changes the overall size
    # - color picks the shape color
    # - alpha controls opacity (0.0 transparent → 1.0 solid)
    # - max_iterations controls how dense/complex the pattern becomes
    draw_one_shape_one_color(radius = 2,
                             color = "pink",
                             alpha = 0.2,
                             max_iterations = 2,
                             output_path = "prompt1/one_shape_one_color.png")
        
        
        
        
    