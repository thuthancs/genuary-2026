"""
Boolean Algebra Sun Gradient

AND: The result is true if both operands are true.
OR: The result is true if at least one operand is true.
NOT: The result is the opposite of the operand.

Create a sun gradient using boolean algebra.
- start with the center pixel with the color #A33800
- AND: if the adjacent pixel (up, down, left, right) is white and is adjacent to the center pixel, set the current pixel color to #A33800 with 50% opacity
- OR: if the pixel is adjacent to the non-center pixel (up, left, right), set the color to 50% opacity fo the parent pixel
- NOT: if the pixel is not adjacent to the center pixel, skip
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple (0-255)."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def blend_colors(color1, color2, alpha):
    """Blend two colors with alpha transparency."""
    return tuple(int(c1 * (1 - alpha) + c2 * alpha) for c1, c2 in zip(color1, color2))


def create_sun_frame(
    width=800,
    height=800,
    center_color="#A33800",
    background_color="#FFFFFF",
    suns=None,
    current_radius_factor=0
):
    """
    Create a single frame of the sun gradient at a specific radius.
    suns: list of (x, y, max_radius) tuples for sun center positions and sizes
    current_radius_factor: 0.0 to 1.0, how much of each sun's max_radius to show
    """
    center_rgb = hex_to_rgb(center_color)
    bg_rgb = hex_to_rgb(background_color)
    
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :, :] = bg_rgb
    
    if suns is None:
        suns = [(width // 2, height // 2, min(width, height) // 4)]
    
    # Create coordinate grids
    y_coords, x_coords = np.ogrid[:height, :width]
    
    # Process each sun
    for cx, cy, max_radius in suns:
        dx = x_coords - cx
        dy = y_coords - cy
        distance = np.sqrt(dx*dx + dy*dy)
        
        current_radius = current_radius_factor * max_radius
        
        # Only process pixels within current_radius
        is_within_current_radius = distance <= current_radius
        
        # Boolean conditions
        is_center = distance == 0
        is_adjacent_to_center = (distance > 0) & (distance <= np.sqrt(2))
        
        # Center: full color (only if radius > 0)
        if current_radius > 0:
            img[is_center] = center_rgb
            
            # AND: (adjacent to center) AND (within radius) → 50% opacity
            and_condition = is_adjacent_to_center & is_within_current_radius
            for y in range(height):
                for x in range(width):
                    if and_condition[y, x]:
                        # Blend with existing color if already has sun color
                        existing = img[y, x, :]
                        if np.array_equal(existing, bg_rgb):
                            blended = blend_colors(bg_rgb, center_rgb, 0.5)
                            img[y, x, :] = blended
                        else:
                            # If overlapping with another sun, blend both
                            blended = blend_colors(existing, center_rgb, 0.5)
                            img[y, x, :] = blended
            
            # OR: (within radius) → gradient based on distance
            or_mask = is_within_current_radius & ~is_center & ~is_adjacent_to_center
            
            for y in range(height):
                for x in range(width):
                    if or_mask[y, x]:
                        dist = distance[y, x]
                        normalized_dist = dist / max_radius
                        
                        # Gradient: 50% at inner edge, fading to 0% at outer edge
                        opacity = 0.5 * (1.0 - normalized_dist)
                        opacity = max(0.0, opacity)
                        
                        existing = img[y, x, :]
                        if np.array_equal(existing, bg_rgb):
                            blended = blend_colors(bg_rgb, center_rgb, opacity)
                            img[y, x, :] = blended
                        else:
                            # Blend with existing sun color
                            blended = blend_colors(existing, center_rgb, opacity)
                            img[y, x, :] = blended
    
    return img


def create_boolean_sun_gradient(
    width=800,
    height=800,
    center_color="#A33800",
    background_color="#FFFFFF",
    suns=None,
    output_path="boolean_sun.png"
):
    """
    Create a sun gradient using boolean algebra rules.
    """
    img = create_sun_frame(width, height, center_color, background_color, suns, current_radius_factor=1.0)
    
    pil_img = Image.fromarray(img, 'RGB')
    pil_img.save(output_path)
    print(f"Saved to {output_path}")
    
    return img


def animate_boolean_sun_gradient(
    width=800,
    height=800,
    center_color="#A33800",
    background_color="#FFFFFF",
    suns=None,
    output_path="boolean_sun_anim.gif",
    frames=60,
    fps=10
):
    """
    Animate the sun gradient growing outward from multiple centers.
    Shows the progressive application of boolean algebra rules.
    """
    if suns is None:
        suns = [(width // 2, height // 2, min(width, height) // 4)]
    
    # Pre-compute all frames
    all_frames = []
    for frame_idx in range(frames):
        # Ease in-out for smoother animation
        t = frame_idx / (frames - 1) if frames > 1 else 1.0
        # Smoothstep easing
        t_eased = t * t * (3 - 2 * t)
        current_radius_factor = t_eased
        frame = create_sun_frame(width, height, center_color, background_color, suns, current_radius_factor)
        all_frames.append(frame)
    
    # Create animation
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.axis('off')
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.invert_yaxis()  # Match image coordinates
    
    im = ax.imshow(all_frames[0], extent=[0, width, height, 0], aspect='auto')
    
    def update(frame_idx):
        im.set_array(all_frames[frame_idx])
        return [im]
    
    anim = FuncAnimation(
        fig,
        update,
        frames=frames,
        interval=1000/fps,
        blit=True,
        repeat=True
    )
    
    writer = PillowWriter(fps=fps)
    anim.save(output_path, writer=writer)
    plt.close(fig)
    print(f"Animation saved to {output_path}")


if __name__ == "__main__":
    # Random seed for reproducibility (optional)
    np.random.seed(42)
    
    width, height = 800, 800
    num_suns = 10
    
    # Generate random sun positions and sizes
    min_radius = 100
    max_radius = 550
    margin = max_radius  # Keep suns away from edges
    
    suns = []
    for _ in range(num_suns):
        x = np.random.uniform(margin, width - margin)
        y = np.random.uniform(margin, height - margin)
        radius = np.random.uniform(min_radius, max_radius)
        suns.append((x, y, radius))
    
    # Create static image with multiple suns
    create_boolean_sun_gradient(
        width=width,
        height=height,
        suns=suns,
        output_path="prompt7/boolean_sun.png"
    )
    
    # Create growing animation with multiple suns
    animate_boolean_sun_gradient(
        width=width,
        height=height,
        suns=suns,
        output_path="prompt7/boolean_sun_anim.gif",
        frames=60,
        fps=10
    )