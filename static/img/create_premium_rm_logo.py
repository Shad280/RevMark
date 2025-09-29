from PIL import Image, ImageDraw, ImageFont
import os
import math

def create_premium_rm_logo():
    """
    Create a premium, professional RM logo with:
    - Modern gradient background
    - Clean, professional typography
    - Subtle shadows and depth
    - Perfect proportions
    - Professional color scheme
    """
    size = 300
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Premium color palette
    primary_green = '#1B5E20'    # Deep forest green
    accent_green = '#2E7D32'     # Medium green
    light_green = '#4CAF50'      # Bright green
    highlight = '#81C784'        # Light accent
    white = '#FFFFFF'
    shadow = (0, 0, 0, 60)       # Subtle shadow
    
    center = size // 2
    
    # Create gradient background circle with subtle shadow
    circle_radius = 130
    
    # Draw shadow first (slightly offset)
    shadow_offset = 4
    shadow_bbox = [
        center - circle_radius + shadow_offset, 
        center - circle_radius + shadow_offset,
        center + circle_radius + shadow_offset, 
        center + circle_radius + shadow_offset
    ]
    draw.ellipse(shadow_bbox, fill=shadow)
    
    # Draw main gradient circle using multiple circles for gradient effect
    for i in range(circle_radius, 0, -2):
        # Calculate gradient color
        ratio = i / circle_radius
        # Interpolate between colors for gradient effect
        if ratio > 0.7:
            color = primary_green
        elif ratio > 0.4:
            color = accent_green
        else:
            color = light_green
            
        circle_bbox = [
            center - i, center - i,
            center + i, center + i
        ]
        draw.ellipse(circle_bbox, fill=color)
    
    # Add subtle inner highlight
    highlight_radius = circle_radius - 15
    highlight_bbox = [
        center - highlight_radius, center - highlight_radius - 8,
        center + highlight_radius, center + highlight_radius - 8
    ]
    # Create subtle top highlight
    for i in range(20, 0, -1):
        alpha = int(10 - i/2)
        highlight_color = (*tuple(int(highlight[1:][j:j+2], 16) for j in (0, 2, 4)), alpha)
        small_bbox = [
            center - highlight_radius + i, center - highlight_radius - 8 + i,
            center + highlight_radius - i, center - highlight_radius + 20
        ]
        draw.ellipse(small_bbox, fill=highlight_color)
    
    # Premium letter design
    letter_height = 85
    stroke_width = 16
    
    # Optimal letter positioning for premium look
    r_x = center - 55
    m_x = center + 5
    letter_y = center - letter_height // 2
    
    # Draw premium R with rounded corners and perfect proportions
    r_width = 45
    corner_radius = 4
    
    def draw_rounded_rect(x1, y1, x2, y2, radius, fill_color):
        """Draw rectangle with rounded corners"""
        # Main rectangle
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill_color)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill_color)
        
        # Corners
        draw.ellipse([x1, y1, x1 + radius*2, y1 + radius*2], fill=fill_color)
        draw.ellipse([x2 - radius*2, y1, x2, y1 + radius*2], fill=fill_color)
        draw.ellipse([x1, y2 - radius*2, x1 + radius*2, y2], fill=fill_color)
        draw.ellipse([x2 - radius*2, y2 - radius*2, x2, y2], fill=fill_color)
    
    # R main vertical stroke (left side) with rounded ends
    draw_rounded_rect(r_x, letter_y, r_x + stroke_width, letter_y + letter_height, corner_radius, white)
    
    # R top horizontal stroke
    draw_rounded_rect(r_x, letter_y, r_x + r_width, letter_y + stroke_width, corner_radius, white)
    
    # R middle horizontal stroke (optimized length)
    mid_y = letter_y + letter_height // 2 - stroke_width // 2
    draw_rounded_rect(r_x, mid_y, r_x + r_width - 6, mid_y + stroke_width, corner_radius, white)
    
    # R top right vertical stroke (upper section only)
    draw_rounded_rect(r_x + r_width - stroke_width, letter_y, 
                     r_x + r_width, mid_y + stroke_width, corner_radius, white)
    
    # R diagonal leg - smooth, professional diagonal
    leg_start_x = r_x + r_width - stroke_width - 3
    leg_start_y = mid_y + stroke_width
    leg_end_x = r_x + r_width + 2
    leg_end_y = letter_y + letter_height
    
    # Draw smooth diagonal with anti-aliasing effect
    leg_points = []
    num_points = 50
    for i in range(num_points + 1):
        progress = i / num_points
        x = leg_start_x + (leg_end_x - leg_start_x) * progress
        y = leg_start_y + (leg_end_y - leg_start_y) * progress
        leg_points.extend([x, y])
    
    # Draw thick line for diagonal
    if len(leg_points) >= 4:
        for i in range(0, len(leg_points) - 3, 2):
            x1, y1 = leg_points[i], leg_points[i+1]
            x2, y2 = leg_points[i+2], leg_points[i+3]
            
            # Draw thick line segment
            draw.line([(x1, y1), (x2, y2)], fill=white, width=stroke_width-2)
    
    # Draw premium M with perfect geometry
    m_width = 52
    
    # M left vertical stroke
    draw_rounded_rect(m_x, letter_y, m_x + stroke_width, letter_y + letter_height, corner_radius, white)
    
    # M right vertical stroke  
    draw_rounded_rect(m_x + m_width - stroke_width, letter_y, 
                     m_x + m_width, letter_y + letter_height, corner_radius, white)
    
    # M center point (optimal position for professional look)
    center_x_m = m_x + m_width // 2
    center_y_m = letter_y + int(letter_height * 0.35)  # Golden ratio positioning
    
    # M left diagonal - smooth line
    left_start_x = m_x + stroke_width
    left_start_y = letter_y
    
    points_left = []
    num_points = 30
    for i in range(num_points + 1):
        progress = i / num_points
        x = left_start_x + (center_x_m - left_start_x) * progress
        y = left_start_y + (center_y_m - left_start_y) * progress
        points_left.extend([x, y])
    
    if len(points_left) >= 4:
        for i in range(0, len(points_left) - 3, 2):
            x1, y1 = points_left[i], points_left[i+1]
            x2, y2 = points_left[i+2], points_left[i+3]
            draw.line([(x1, y1), (x2, y2)], fill=white, width=stroke_width-2)
    
    # M right diagonal - smooth line
    right_start_x = m_x + m_width - stroke_width
    right_start_y = letter_y
    
    points_right = []
    for i in range(num_points + 1):
        progress = i / num_points
        x = right_start_x + (center_x_m - right_start_x) * progress
        y = right_start_y + (center_y_m - right_start_y) * progress
        points_right.extend([x, y])
    
    if len(points_right) >= 4:
        for i in range(0, len(points_right) - 3, 2):
            x1, y1 = points_right[i], points_right[i+1]
            x2, y2 = points_right[i+2], points_right[i+3]
            draw.line([(x1, y1), (x2, y2)], fill=white, width=stroke_width-2)
    
    # M center vertical stroke (from apex down) - shorter for better proportions
    center_stroke_height = int(letter_height * 0.45)  # Professional proportion
    draw_rounded_rect(center_x_m - stroke_width // 2, center_y_m, 
                     center_x_m + stroke_width // 2, 
                     letter_y + letter_height, corner_radius, white)
    
    # Add subtle outer glow for premium effect
    glow_img = Image.new('RGBA', (size + 20, size + 20), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    
    for i in range(5, 0, -1):
        alpha = int(8 - i)
        glow_color = (*tuple(int(light_green[1:][j:j+2], 16) for j in (0, 2, 4)), alpha)
        glow_bbox = [
            10 + center - circle_radius - i, 
            10 + center - circle_radius - i,
            10 + center + circle_radius + i, 
            10 + center + circle_radius + i
        ]
        glow_draw.ellipse(glow_bbox, fill=glow_color)
    
    # Composite glow with main image
    final_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    final_img.paste(glow_img.crop((10, 10, size + 10, size + 10)), (0, 0))
    final_img = Image.alpha_composite(final_img, img)
    
    return final_img

def create_minimal_version():
    """Create a clean, minimal version for smaller sizes"""
    size = 200
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Simplified color scheme
    green = '#2E7D32'
    white = '#FFFFFF'
    
    center = size // 2
    circle_radius = 85
    
    # Simple solid circle
    circle_bbox = [
        center - circle_radius, center - circle_radius,
        center + circle_radius, center + circle_radius
    ]
    draw.ellipse(circle_bbox, fill=green)
    
    # Simplified letters for small sizes
    letter_height = 55
    stroke_width = 10
    
    r_x = center - 35
    m_x = center + 3
    letter_y = center - letter_height // 2
    
    # Simple R
    r_width = 30
    draw.rectangle([r_x, letter_y, r_x + stroke_width, letter_y + letter_height], fill=white)
    draw.rectangle([r_x, letter_y, r_x + r_width, letter_y + stroke_width], fill=white)
    
    mid_y = letter_y + letter_height // 2 - stroke_width // 2
    draw.rectangle([r_x, mid_y, r_x + r_width - 4, mid_y + stroke_width], fill=white)
    draw.rectangle([r_x + r_width - stroke_width, letter_y, r_x + r_width, mid_y + stroke_width], fill=white)
    
    # Simple diagonal
    draw.line([(r_x + r_width - 8, mid_y + stroke_width), (r_x + r_width, letter_y + letter_height)], 
              fill=white, width=stroke_width-2)
    
    # Simple M
    m_width = 35
    draw.rectangle([m_x, letter_y, m_x + stroke_width, letter_y + letter_height], fill=white)
    draw.rectangle([m_x + m_width - stroke_width, letter_y, m_x + m_width, letter_y + letter_height], fill=white)
    
    center_x_m = m_x + m_width // 2
    center_y_m = letter_y + letter_height // 3
    
    draw.line([(m_x + stroke_width, letter_y), (center_x_m, center_y_m)], fill=white, width=stroke_width-2)
    draw.line([(m_x + m_width - stroke_width, letter_y), (center_x_m, center_y_m)], fill=white, width=stroke_width-2)
    draw.rectangle([center_x_m - stroke_width//2, center_y_m, center_x_m + stroke_width//2, letter_y + letter_height], fill=white)
    
    return img

# Create premium logo
print("🎨 Creating premium RM logo...")
logo = create_premium_rm_logo()

# Save main logo (high resolution for web)
logo_240 = logo.resize((240, 240), Image.Resampling.LANCZOS)
logo_240.save('logo_premium_rm.png', 'PNG', optimize=True, quality=95)
print("✅ Created premium RM logo: logo_premium_rm.png")

# Create square version
logo_square = logo.resize((120, 120), Image.Resampling.LANCZOS)
logo_square.save('logo_square_premium_rm.png', 'PNG', optimize=True, quality=95)
print("✅ Created premium RM square logo: logo_square_premium_rm.png")

# Create minimal version for favicons
minimal = create_minimal_version()

# Favicons from minimal version
favicon_32 = minimal.resize((32, 32), Image.Resampling.LANCZOS)
favicon_32.save('favicon_premium_rm_32.png', 'PNG', optimize=True)

favicon_16 = minimal.resize((16, 16), Image.Resampling.LANCZOS)
favicon_16.save('favicon_premium_rm_16.png', 'PNG', optimize=True)

print("✅ Created premium RM favicons")
print("🎉 Premium, professional RM logo with gradient, shadows, and perfect typography is ready!")
print("📈 Features: Gradient background, subtle shadows, rounded corners, professional proportions, and glow effect!")
