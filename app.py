import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import math
import io

# --- Helper: number input with +/- buttons ---
def adjustable_value(label, key, default, step=1):
    if key not in st.session_state:
        st.session_state[key] = default
    st.sidebar.markdown(f"**{label}**")
    cols = st.sidebar.columns([1, 3, 1])
    if cols[0].button("−", key=f"{key}_minus"):
        st.session_state[key] -= step
    cols[1].markdown(f"<div style='text-align:center;padding:5px 0;font-size:1.2em'>{st.session_state[key]}</div>", unsafe_allow_html=True)
    if cols[2].button("+", key=f"{key}_plus"):
        st.session_state[key] += step
    return st.session_state[key]

# --- Core Drawing Logic ---
def draw_pattern(pattern_type, draw, center, size, params):
    color, width = params['color'], params['width']

    if pattern_type == "Flower of Life":
        radius, layers = params['radius'], params['layers']
        draw.ellipse([center-radius, center-radius, center+radius, center+radius], outline=color, width=width)
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

    elif pattern_type == "Metatron's Cube":
        radius = params['radius']
        # 13 circles: 1 center + 6 inner + 6 outer
        points = [(center, center)]
        for i in range(6):
            angle = math.radians(i * 60)
            points.append((center + radius * math.cos(angle), center + radius * math.sin(angle)))
        for i in range(6):
            angle = math.radians(i * 60)
            points.append((center + 2 * radius * math.cos(angle), center + 2 * radius * math.sin(angle)))
        # Draw circles
        for px, py in points:
            draw.ellipse([px - radius, py - radius, px + radius, py + radius], outline=color, width=width)
        # Connect all points with lines
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                draw.line([points[i], points[j]], fill=color, width=width)

    elif pattern_type == "Sri Yantra":
        r = params['radius']
        # Outer circle
        draw.ellipse([center - r, center - r, center + r, center + r], outline=color, width=width)
        # 9 interlocking triangles (4 upward, 5 downward) - simplified representation
        triangle_scales = [0.95, 0.78, 0.62, 0.48, 0.36, 0.26, 0.18, 0.12, 0.07]
        for idx, s in enumerate(triangle_scales):
            sr = r * s
            if idx % 2 == 0:  # Upward triangle
                pts = [
                    (center, center - sr),
                    (center - sr * math.cos(math.radians(30)), center + sr * math.sin(math.radians(30))),
                    (center + sr * math.cos(math.radians(30)), center + sr * math.sin(math.radians(30))),
                ]
            else:  # Downward triangle
                pts = [
                    (center, center + sr),
                    (center - sr * math.cos(math.radians(30)), center - sr * math.sin(math.radians(30))),
                    (center + sr * math.cos(math.radians(30)), center - sr * math.sin(math.radians(30))),
                ]
            draw.polygon(pts, outline=color, width=width)

    elif pattern_type == "Seed of Life":
        radius = params['radius']
        draw.ellipse([center - radius, center - radius, center + radius, center + radius], outline=color, width=width)
        for i in range(6):
            angle = math.radians(i * 60)
            cx = center + radius * math.cos(angle)
            cy = center + radius * math.sin(angle)
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=color, width=width)

    elif pattern_type == "Torus / Tube Torus":
        rings = params['rings']
        radius = params['radius']
        for i in range(rings):
            angle = math.radians(i * (360 / rings))
            # Each ring is an ellipse rotated around center
            rx = radius
            ry = radius * 0.4
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            # Approximate rotated ellipse with polygon points
            pts = []
            for t in range(64):
                ta = math.radians(t * (360 / 64))
                ex = rx * math.cos(ta)
                ey = ry * math.sin(ta)
                # Rotate
                px = center + ex * cos_a - ey * sin_a
                py = center + ex * sin_a + ey * cos_a
                pts.append((px, py))
            pts.append(pts[0])
            draw.line(pts, fill=color, width=width)

    elif pattern_type == "Vesica Piscis":
        radius = params['radius']
        offset = radius / 2
        draw.ellipse([center - offset - radius, center - radius, center - offset + radius, center + radius], outline=color, width=width)
        draw.ellipse([center + offset - radius, center - radius, center + offset + radius, center + radius], outline=color, width=width)

    elif pattern_type == "Merkaba (Star Tetrahedron)":
        radius = params['radius']
        # Upward triangle
        up = [
            (center, center - radius),
            (center - radius * math.cos(math.radians(30)), center + radius * math.sin(math.radians(30))),
            (center + radius * math.cos(math.radians(30)), center + radius * math.sin(math.radians(30))),
        ]
        draw.polygon(up, outline=color, width=width)
        # Downward triangle
        down = [
            (center, center + radius),
            (center - radius * math.cos(math.radians(30)), center - radius * math.sin(math.radians(30))),
            (center + radius * math.cos(math.radians(30)), center - radius * math.sin(math.radians(30))),
        ]
        draw.polygon(down, outline=color, width=width)
        # Outer circle
        draw.ellipse([center - radius, center - radius, center + radius, center + radius], outline=color, width=width)

    elif pattern_type == "Platonic Solid (Icosahedron 2D)":
        radius = params['radius']
        # Project icosahedron vertices onto 2D - outer and inner pentagons + top/bottom
        outer = []
        inner = []
        for i in range(5):
            a_out = math.radians(i * 72 - 90)
            a_in = math.radians(i * 72 - 90 + 36)
            outer.append((center + radius * math.cos(a_out), center + radius * math.sin(a_out)))
            inner.append((center + radius * 0.5 * math.cos(a_in), center + radius * 0.5 * math.sin(a_in)))
        # Draw outer pentagon
        for i in range(5):
            draw.line([outer[i], outer[(i+1) % 5]], fill=color, width=width)
        # Draw inner pentagon
        for i in range(5):
            draw.line([inner[i], inner[(i+1) % 5]], fill=color, width=width)
        # Connect outer to inner
        for i in range(5):
            draw.line([outer[i], inner[i]], fill=color, width=width)
            draw.line([outer[i], inner[(i-1) % 5]], fill=color, width=width)
        # Connect to center top and bottom
        top = (center, center - radius)
        bot = (center, center + radius)
        for p in outer[:3]:
            draw.line([top, p], fill=color, width=width)
        for p in outer[2:]:
            draw.line([bot, p], fill=color, width=width)

    elif pattern_type == "64-Point Grid (Tetrahedron)":
        radius = params['radius']
        layers = params['layers']
        # Grid of equilateral triangles
        h = radius * math.sqrt(3) / 2
        for row in range(-layers, layers + 1):
            for col in range(-layers, layers + 1):
                x = center + col * radius + (row % 2) * (radius / 2)
                y = center + row * h
                # Draw upward triangle
                p1 = (x, y - h * 2/3)
                p2 = (x - radius/2, y + h * 1/3)
                p3 = (x + radius/2, y + h * 1/3)
                draw.polygon([p1, p2, p3], outline=color, width=width)

    elif pattern_type == "Fibonacci Spiral":
        scale = params['scale']
        iters = params['iters']
        # Draw Fibonacci rectangles and arcs
        a, b = 1, 1
        x, y = center, center
        direction = 0
        for _ in range(iters):
            r = b * scale
            if direction == 0:
                rect = [x, y, x + r, y + r]
                arc_bbox = [x, y, x + 2*r, y + 2*r]
                draw.arc(arc_bbox, 180, 270, fill=color, width=width)
                draw.rectangle(rect, outline=color, width=max(1, width // 2))
                y -= a * scale
            elif direction == 1:
                rect = [x, y, x + r, y + r]
                arc_bbox = [x - r, y, x + r, y + 2*r]
                draw.arc(arc_bbox, 270, 360, fill=color, width=width)
                draw.rectangle(rect, outline=color, width=max(1, width // 2))
                x += b * scale
            elif direction == 2:
                rect = [x - r, y, x, y + r]
                arc_bbox = [x - 2*r, y - r, x, y + r]
                draw.arc(arc_bbox, 0, 90, fill=color, width=width)
                draw.rectangle(rect, outline=color, width=max(1, width // 2))
                y += a * scale
            elif direction == 3:
                rect = [x - r, y - r, x, y]
                arc_bbox = [x - r, y - 2*r, x + r, y]
                draw.arc(arc_bbox, 90, 180, fill=color, width=width)
                draw.rectangle(rect, outline=color, width=max(1, width // 2))
                x -= b * scale
            a, b = b, a + b
            direction = (direction + 1) % 4

# --- Container Shape Drawing ---
def draw_container(draw, center, size, shape, scale_pct, color, width, rect_length=None, rect_width=None):
    r = (size // 2) * (scale_pct / 100)
    if shape == "Circle":
        draw.ellipse([center - r, center - r, center + r, center + r], outline=color, width=width)
    elif shape == "Square":
        draw.rectangle([center - r, center - r, center + r, center + r], outline=color, width=width)
    elif shape == "Rectangle":
        half_w = (rect_width / 2) if rect_width else r
        half_h = (rect_length / 2) if rect_length else r * 0.6
        draw.rectangle([center - half_w, center - half_h, center + half_w, center + half_h], outline=color, width=width)
    elif shape == "Triangle":
        pts = [
            (center, center - r),
            (center - r * math.cos(math.radians(30)), center + r * math.sin(math.radians(30))),
            (center + r * math.cos(math.radians(30)), center + r * math.sin(math.radians(30))),
        ]
        draw.polygon(pts, outline=color, width=width)
    elif shape == "Hexagon":
        pts = []
        for i in range(6):
            angle = math.radians(i * 60 - 30)
            pts.append((center + r * math.cos(angle), center + r * math.sin(angle)))
        draw.polygon(pts, outline=color, width=width)
    elif shape == "Octagon":
        pts = []
        for i in range(8):
            angle = math.radians(i * 45 - 22.5)
            pts.append((center + r * math.cos(angle), center + r * math.sin(angle)))
        draw.polygon(pts, outline=color, width=width)

# --- Smoothing & Glow Engine ---
def render_smooth_pattern(pattern_type, size, params, glow_on, container=None, scale_factor=3):
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
        if container:
            c = container
            c_rect_l = c.get('rect_length', None)
            c_rect_w = c.get('rect_width', None)
            draw_container(glow_draw, render_center, render_size, c['shape'], c['scale_pct'],
                           c['color'], glow_params['width'],
                           rect_length=c_rect_l * scale_factor if c_rect_l else None,
                           rect_width=c_rect_w * scale_factor if c_rect_w else None)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=5 * scale_factor))
        img.paste(glow_layer, (0, 0), glow_layer)

    # Sharp core lines
    main_draw = ImageDraw.Draw(img)
    draw_pattern(pattern_type, main_draw, render_center, render_size, scaled_params)

    # Draw container shape
    if container:
        c = container
        c_rect_l = c.get('rect_length', None)
        c_rect_w = c.get('rect_width', None)
        draw_container(main_draw, render_center, render_size, c['shape'], c['scale_pct'],
                       c['color'], scaled_params['width'],
                       rect_length=c_rect_l * scale_factor if c_rect_l else None,
                       rect_width=c_rect_w * scale_factor if c_rect_w else None)

    # Anti-aliasing via downsampling
    img = img.resize((size, size), resample=Image.LANCZOS)

    # Add background
    final_img = Image.new("RGB", (size, size), params['bg_color'])
    final_img.paste(img, (0, 0), img)
    return final_img

# --- Streamlit UI ---
st.set_page_config(page_title="Sacred Geometry Generator", layout="centered")
st.title("Sacred Geometry Generator")

PATTERNS = [
    "Flower of Life",
    "Seed of Life",
    "Metatron's Cube",
    "Sri Yantra",
    "Vesica Piscis",
    "Merkaba (Star Tetrahedron)",
    "Golden Ratio Spiral",
    "Fibonacci Spiral",
    "Torus / Tube Torus",
    "Platonic Solid (Icosahedron 2D)",
    "64-Point Grid (Tetrahedron)",
]

# Sidebar Configuration
st.sidebar.header("Design Controls")
pattern_choice = st.sidebar.selectbox("Select Pattern", PATTERNS)
bg_col = st.sidebar.color_picker("Background Color", "#0E1117")
line_col = st.sidebar.color_picker("Line Color", "#00FAFF")
thickness = adjustable_value("Line Thickness", "thickness", 2)
glow_active = st.sidebar.checkbox("Enable Ethereal Glow", value=True)

# Container Shape Controls
st.sidebar.header("Container Shape")
container_on = st.sidebar.checkbox("Enable Container Shape", value=False)
container_cfg = None
if container_on:
    container_shape = st.sidebar.selectbox("Container Shape", ["Circle", "Square", "Rectangle", "Triangle", "Hexagon", "Octagon"])
    container_scale = adjustable_value("Container Scale %", "container_scale", 90, step=5)
    container_cfg = {'shape': container_shape, 'scale_pct': container_scale, 'color': line_col}
    if container_shape == "Rectangle":
        container_cfg['rect_length'] = adjustable_value("Rectangle Length", "rect_length", 300, step=10)
        container_cfg['rect_width'] = adjustable_value("Rectangle Width", "rect_width", 500, step=10)

# Dynamic Sidebar Parameters
ui_params = {
    'color': line_col,
    'width': thickness,
    'bg_color': bg_col
}

if pattern_choice == "Flower of Life":
    ui_params['radius'] = adjustable_value("Circle Radius", "fol_radius", 70, step=5)
    ui_params['layers'] = adjustable_value("Pattern Layers", "fol_layers", 3)
elif pattern_choice == "Seed of Life":
    ui_params['radius'] = adjustable_value("Circle Radius", "sol_radius", 80, step=5)
elif pattern_choice == "Metatron's Cube":
    ui_params['radius'] = adjustable_value("Radius", "mc_radius", 80, step=5)
elif pattern_choice == "Sri Yantra":
    ui_params['radius'] = adjustable_value("Radius", "sy_radius", 200, step=10)
elif pattern_choice == "Vesica Piscis":
    ui_params['radius'] = adjustable_value("Circle Radius", "vp_radius", 150, step=10)
elif pattern_choice == "Merkaba (Star Tetrahedron)":
    ui_params['radius'] = adjustable_value("Radius", "mk_radius", 200, step=10)
elif pattern_choice == "Golden Ratio Spiral":
    ui_params['scale'] = adjustable_value("Spiral Scale", "grs_scale", 8)
    ui_params['iters'] = adjustable_value("Spiral Iterations", "grs_iters", 10)
elif pattern_choice == "Fibonacci Spiral":
    ui_params['scale'] = adjustable_value("Spiral Scale", "fib_scale", 8)
    ui_params['iters'] = adjustable_value("Iterations", "fib_iters", 10)
elif pattern_choice == "Torus / Tube Torus":
    ui_params['radius'] = adjustable_value("Radius", "torus_radius", 150, step=10)
    ui_params['rings'] = adjustable_value("Number of Rings", "torus_rings", 24, step=2)
elif pattern_choice == "Platonic Solid (Icosahedron 2D)":
    ui_params['radius'] = adjustable_value("Radius", "ico_radius", 200, step=10)
elif pattern_choice == "64-Point Grid (Tetrahedron)":
    ui_params['radius'] = adjustable_value("Triangle Size", "grid_radius", 40, step=5)
    ui_params['layers'] = adjustable_value("Grid Layers", "grid_layers", 4)

# Render Process
try:
    with st.spinner("Rendering smooth geometry..."):
        final_output = render_smooth_pattern(
            pattern_type=pattern_choice,
            size=800,
            params=ui_params,
            glow_on=glow_active,
            container=container_cfg
        )
        st.image(final_output, width="stretch")

    # Export Logic
    buf = io.BytesIO()
    final_output.save(buf, format="PNG")
    st.download_button("Download High-Quality PNG", buf.getvalue(), "geometry_art.png", "image/png")

except Exception as e:
    st.error(f"An error occurred: {e}")
