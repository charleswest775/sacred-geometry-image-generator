import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import math
import io

# --- Core Drawing Logic ---
def draw_pattern(pattern_type, draw, center, size, params):
    color, width = params['color'], params['width']
    
    if pattern_type == "Flower of Life":
        radius, layers = params['radius'], params['layers']
        # Central Circle
        draw.ellipse([center-radius, center-radius, center+radius, center+radius], outline=color, width=width)
        # Layering Logic
        for layer in range(1, layers + 1):
            for i in range(6):
                angle = math.radians(i * 60)
                start_x = center + (layer * radius) * math.cos(angle)
                start_y = center + (layer * radius) * math.sin(angle)
                for j in range(layer):
                    mv_angle = math.radians((i + 2) * 60)
                    cx = start_x + (j * radius) * math.cos(mv_angle)
                    cy = start_y + (j * radius) * math.sin(mv_angle)
                    draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], outline=color, width=width)
                    
    elif pattern_type == "Golden Ratio Spiral":
        scale, iters = params['scale'], params['iters']
        a, b, x, y, direction = 0, 1, center, center, 0
        for _ in range(iters):
            r = b * scale
            if direction == 0: bbox, s, e, x = [x - r, y, x + r, y + 2 * r], 270, 360, x + r
            elif direction == 1: bbox, s, e, y = [x - 2 * r, y - r, x, y + r], 0, 90, y + r
            elif direction == 2: bbox, s, e, x = [x - r, y - 2 * r, x + r, y], 90, 180, x - r
            elif direction == 3: bbox, s, e, y = [x, y - r, x + 2 * r, y + r], 180, 270, y - r
            draw.arc(bbox, start=s, end=e, fill=color, width=width)
            a, b, direction = b, a + b, (direction + 1) % 4

# --- Smoothing & Glow Engine ---
def render_smooth_pattern(pattern_type, size, params, glow_on, scale_factor=3):
    render_size = size * scale_factor
    render_center = render_size // 2
    
    # Scale parameters for high-res canvas
    scaled_params = params.copy()
    scaled_params['width'] = params['width'] * scale_factor
    if 'radius' in params: scaled_params['radius'] = params['radius'] * scale_factor
    if 'scale' in params: scaled_params['scale'] = params['scale'] * scale_factor

    # Create transparent high-res canvas
    img = Image.new("RGBA", (render_size, render_size), (0, 0, 0, 0))
    
    if glow_on:
        glow_layer = Image.new("RGBA", (render_size, render_size), (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        glow_params = scaled_params.copy()
        glow_params['width'] = scaled_params['width'] + (8 * scale_factor)
        draw_pattern(pattern_type, glow_draw, render_center, render_size, glow_params)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=5 * scale_factor))
        img.paste(glow_layer, (0, 0), glow_layer)

    # Sharp core lines
    main_draw = ImageDraw.Draw(img)
    draw_pattern(pattern_type, main_draw, render_center, render_size, scaled_params)

    # Anti-aliasing via downsampling
    img = img.resize((size, size), resample=Image.LANCZOS)
    
    # Add background
    final_img = Image.new("RGB", (size, size), params['bg_color'])
    final_img.paste(img, (0, 0), img)
    return final_img

# --- Streamlit UI ---
st.set_page_config(page_title="Sacred Geometry Generator", layout="centered")
st.title("💎 Ultra-Smooth Geometry Lab")

# Sidebar Configuration
st.sidebar.header("Design Controls")
pattern_choice = st.sidebar.selectbox("Select Pattern", ["Flower of Life", "Golden Ratio Spiral"])
bg_col = st.sidebar.color_picker("Background Color", "#0E1117")
line_col = st.sidebar.color_picker("Line Color", "#00FAFF")
thickness = st.sidebar.slider("Line Thickness", 1, 5, 2)
glow_active = st.sidebar.checkbox("Enable Ethereal Glow", value=True)

# Dynamic Sidebar Parameters
ui_params = {
    'color': line_col, 
    'width': thickness, 
    'bg_color': bg_col
}

if pattern_choice == "Flower of Life":
    ui_params['radius'] = st.sidebar.slider("Circle Radius", 20, 150, 70)
    ui_params['layers'] = st.sidebar.slider("Pattern Layers", 1, 5, 3)
else:
    ui_params['scale'] = st.sidebar.slider("Spiral Scale", 1, 20, 8)
    ui_params['iters'] = st.sidebar.slider("Spiral Iterations", 5, 15, 10)

# Render Process
try:
    with st.spinner("Rendering smooth geometry..."):
        final_output = render_smooth_pattern(
            pattern_type=pattern_choice, 
            size=800, 
            params=ui_params, 
            glow_on=glow_active
        )
        st.image(final_output, use_container_width=True)

    # Export Logic
    buf = io.BytesIO()
    final_output.save(buf, format="PNG")
    st.download_button("Download High-Quality PNG", buf.getvalue(), "geometry_art.png", "image/png")

except Exception as e:
    st.error(f"An error occurred: {e}")