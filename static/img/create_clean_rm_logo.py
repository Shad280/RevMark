from PIL import Image, ImageDraw
import os

def create_clean_rm_logo():
    """
    Create a clean, simple RM logo with just better typography and proportions.
    No fancy effects - just clean, professional letters.
    """
    size = 240
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Simple, clean green - same as before
    green = '#2d8f3f'
    white = '#ffffff'
    
    center = size // 2
    
    # Simple solid circle - clean and minimal
    circle_radius = 100
    circle_bbox = [center - circle_radius, center - circle_radius,
                   center + circle_radius, center + circle_radius]
    draw.ellipse(circle_bbox, fill=green)
    
    # Improved letter proportions and spacing
    letter_height = 70  # Slightly taller for better presence
    stroke_width = 14   # Slightly thicker for better readability
    
    # Better positioned letters with optimal spacing
    r_x = center - 48   # Better left positioning
    m_x = center + 8    # Better right positioning
    letter_y = center - letter_height // 2
    
    # Draw clean R with better proportions
    r_width = 38  # Slightly wider for better balance
    
    # R main vertical stroke (left side) - clean rectangle
    draw.rectangle([r_x, letter_y, r_x + stroke_width, letter_y + letter_height], fill=white)
    
    # R top horizontal stroke - full width
    draw.rectangle([r_x, letter_y, r_x + r_width, letter_y + stroke_width], fill=white)
    
    # R middle horizontal stroke - slightly shorter for better proportions
    mid_y = letter_y + letter_height // 2 - stroke_width // 2
    draw.rectangle([r_x, mid_y, r_x + r_width - 6, mid_y + stroke_width], fill=white)
    
    # R top right vertical stroke (upper section only)
    draw.rectangle([r_x + r_width - stroke_width, letter_y, 
                   r_x + r_width, mid_y + stroke_width], fill=white)
    
    # R diagonal leg - cleaner, more precise diagonal
    leg_start_x = r_x + r_width - stroke_width - 4
    leg_start_y = mid_y + stroke_width
    leg_end_x = r_x + r_width + 2
    leg_end_y = letter_y + letter_height
    
    # Draw clean diagonal using line method
    draw.line([(leg_start_x + stroke_width//2, leg_start_y), 
               (leg_end_x - stroke_width//2, leg_end_y)], 
              fill=white, width=stroke_width-2)
    
    # Draw clean M with better proportions
    m_width = 44  # Slightly wider for better balance
    
    # M left vertical stroke
    draw.rectangle([m_x, letter_y, m_x + stroke_width, letter_y + letter_height], fill=white)
    
    # M right vertical stroke
    draw.rectangle([m_x + m_width - stroke_width, letter_y, 
                   m_x + m_width, letter_y + letter_height], fill=white)
    
    # M center meeting point - better positioned
    center_x_m = m_x + m_width // 2
    center_y_m = letter_y + int(letter_height * 0.38)  # Better proportion
    
    # M left diagonal - clean line
    left_start_x = m_x + stroke_width
    left_start_y = letter_y
    draw.line([(left_start_x, left_start_y), (center_x_m, center_y_m)], 
              fill=white, width=stroke_width-2)
    
    # M right diagonal - clean line
    right_start_x = m_x + m_width - stroke_width
    right_start_y = letter_y
    draw.line([(right_start_x, right_start_y), (center_x_m, center_y_m)], 
              fill=white, width=stroke_width-2)
    
    # M center vertical stroke (from meeting point down) - proper length
    center_stroke_start_y = center_y_m - stroke_width // 2  # Start slightly above meeting point
    draw.rectangle([center_x_m - stroke_width // 2, center_stroke_start_y, 
                   center_x_m + stroke_width // 2, letter_y + letter_height], fill=white)
    
    return img

def create_minimal_clean_version():
    """Create an even cleaner version for small sizes"""
    size = 200
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    green = '#2d8f3f'
    white = '#ffffff'
    
    center = size // 2
    circle_radius = 85
    
    # Simple circle
    circle_bbox = [center - circle_radius, center - circle_radius,
                   center + circle_radius, center + circle_radius]
    draw.ellipse(circle_bbox, fill=green)
    
    # Smaller, cleaner letters
    letter_height = 58
    stroke_width = 12
    
    r_x = center - 40
    m_x = center + 6
    letter_y = center - letter_height // 2
    
    # Simple clean R
    r_width = 32
    draw.rectangle([r_x, letter_y, r_x + stroke_width, letter_y + letter_height], fill=white)
    draw.rectangle([r_x, letter_y, r_x + r_width, letter_y + stroke_width], fill=white)
    
    mid_y = letter_y + letter_height // 2 - stroke_width // 2
    draw.rectangle([r_x, mid_y, r_x + r_width - 4, mid_y + stroke_width], fill=white)
    draw.rectangle([r_x + r_width - stroke_width, letter_y, r_x + r_width, mid_y + stroke_width], fill=white)
    
    draw.line([(r_x + r_width - 8, mid_y + stroke_width), (r_x + r_width, letter_y + letter_height)], 
              fill=white, width=stroke_width-2)
    
    # Simple clean M
    m_width = 36
    draw.rectangle([m_x, letter_y, m_x + stroke_width, letter_y + letter_height], fill=white)
    draw.rectangle([m_x + m_width - stroke_width, letter_y, m_x + m_width, letter_y + letter_height], fill=white)
    
    center_x_m = m_x + m_width // 2
    center_y_m = letter_y + int(letter_height * 0.38)
    
    draw.line([(m_x + stroke_width, letter_y), (center_x_m, center_y_m)], fill=white, width=stroke_width-2)
    draw.line([(m_x + m_width - stroke_width, letter_y), (center_x_m, center_y_m)], fill=white, width=stroke_width-2)
    draw.rectangle([center_x_m - stroke_width//2, center_y_m - stroke_width//2, 
                   center_x_m + stroke_width//2, letter_y + letter_height], fill=white)
    
    return img

# Create clean logo
print("🎨 Creating clean, simple RM logo...")
logo = create_clean_rm_logo()

# Save main logo
logo_240 = logo.resize((240, 240), Image.Resampling.LANCZOS)
logo_240.save('logo_clean_rm.png', 'PNG', optimize=True)
print("✅ Created clean RM logo: logo_clean_rm.png")

# Create square version
logo_square = logo.resize((120, 120), Image.Resampling.LANCZOS)
logo_square.save('logo_square_clean_rm.png', 'PNG', optimize=True)
print("✅ Created clean RM square logo: logo_square_clean_rm.png")

# Create minimal version for favicons
minimal = create_minimal_clean_version()

# Favicons
favicon_32 = minimal.resize((32, 32), Image.Resampling.LANCZOS)
favicon_32.save('favicon_clean_rm_32.png', 'PNG', optimize=True)

favicon_16 = minimal.resize((16, 16), Image.Resampling.LANCZOS)
favicon_16.save('favicon_clean_rm_16.png', 'PNG', optimize=True)

print("✅ Created clean RM favicons")
print("🎉 Clean, simple RM logo with better typography and proportions is ready!")
print("📐 Features: Better spacing, cleaner lines, improved proportions - no fancy effects!")
