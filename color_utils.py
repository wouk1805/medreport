# color_utils.py
# ============================================================================
# Color Manipulation Utilities
# ============================================================================

def lighten_color(hex_color, factor):
    """
    Lighten a hex color by a factor
    
    Args:
        hex_color (str): Hex color string (e.g., '#FF0000')
        factor (float): Lightening factor (0.0 to 1.0)
        
    Returns:
        str: Lightened hex color string
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    
    return f"#{r:02x}{g:02x}{b:02x}"

def darken_color(hex_color, factor):
    """
    Darken a hex color by a factor
    
    Args:
        hex_color (str): Hex color string (e.g., '#FF0000')
        factor (float): Darkening factor (0.0 to 1.0)
        
    Returns:
        str: Darkened hex color string
    """
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    r = max(0, int(r * (1 - factor)))
    g = max(0, int(g * (1 - factor)))
    b = max(0, int(b * (1 - factor)))
    
    return f"#{r:02x}{g:02x}{b:02x}"

def hex_to_rgb(hex_color):
    """
    Convert hex color to RGB tuple
    
    Args:
        hex_color (str): Hex color string (e.g., '#FF0000')
        
    Returns:
        tuple: RGB values (r, g, b)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    """
    Convert RGB values to hex color
    
    Args:
        r (int): Red value (0-255)
        g (int): Green value (0-255)
        b (int): Blue value (0-255)
        
    Returns:
        str: Hex color string
    """
    return f"#{r:02x}{g:02x}{b:02x}"

def adjust_brightness(hex_color, brightness_factor):
    """
    Adjust brightness of a color
    
    Args:
        hex_color (str): Hex color string
        brightness_factor (float): Factor to adjust brightness (>1 brighter, <1 darker)
        
    Returns:
        str: Adjusted hex color string
    """
    r, g, b = hex_to_rgb(hex_color)
    
    # Adjust each component
    r = min(255, max(0, int(r * brightness_factor)))
    g = min(255, max(0, int(g * brightness_factor)))
    b = min(255, max(0, int(b * brightness_factor)))
    
    return rgb_to_hex(r, g, b)

def blend_colors(color1, color2, ratio=0.5):
    """
    Blend two colors together
    
    Args:
        color1 (str): First hex color
        color2 (str): Second hex color
        ratio (float): Blend ratio (0.0 = all color1, 1.0 = all color2)
        
    Returns:
        str: Blended hex color
    """
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    
    r = int(r1 * (1 - ratio) + r2 * ratio)
    g = int(g1 * (1 - ratio) + g2 * ratio)
    b = int(b1 * (1 - ratio) + b2 * ratio)
    
    return rgb_to_hex(r, g, b)