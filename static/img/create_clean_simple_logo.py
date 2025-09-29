from PIL import Image, ImageDraw
import os

def create_clean_separated_logo():
    """
    Create a clean, simple logo with properly separated R and M letters.
    """
    size = 240
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Green color
    green = '#2d8f3f'
    
    # Draw main circle
    circle_radius = 105
    center = size // 2
    circle_bbox = [center - circle_radius, center - circle_radius, 
                   center + circle_radius, center + circle_radius]
    draw.ellipse(circle_bbox, fill=green)
    
    # Letter dimensions - cleaner, simpler
    letter_height = 55
    stroke_width = 9
    
    # Position letters with good separation
    r_x = center - 38
    m_x = center + 6
    letter_y = center - letter_height // 2
    
    # Draw R - simple and clean
    r_width = 28
    
    # R left vertical line
    draw.rectangle([r_x, letter_y, r_x + stroke_width, letter_y + letter_height], fill='white')
    
    # R top horizontal
    draw.rectangle([r_x, letter_y, r_x + r_width, letter_y + stroke_width], fill='white')
    
    # R middle horizontal
    mid_y = letter_y + letter_height // 2 - stroke_width // 2
    draw.rectangle([r_x, mid_y, r_x + r_width - 3, mid_y + stroke_width], fill='white')
    
    # R top right vertical
    draw.rectangle([r_x + r_width - stroke_width, letter_y, 
                   r_x + r_width, mid_y + stroke_width], fill='white')
    
    # R diagonal leg - clean line
    for i in range(12):
        y_pos = mid_y + stroke_width + i * 2.5
        x_pos = r_x + 12 + i * 1.3
        if y_pos < letter_y + letter_height and x_pos < r_x + r_width:
            draw.rectangle([x_pos, y_pos, x_pos + stroke_width - 1, y_pos + 3], fill='white')
    
    # Draw M - simple and clean
    m_width = 38
    
    # M left vertical
    draw.rectangle([m_x, letter_y, m_x + stroke_width, letter_y + letter_height], fill='white')
    
    # M right vertical  
    draw.rectangle([m_x + m_width - stroke_width, letter_y, 
                   m_x + m_width, letter_y + letter_height], fill='white')
    
    # M center diagonals meeting at middle point
    center_x_m = m_x + m_width // 2
    center_y_m = letter_y + letter_height // 2.2
    
    # Left diagonal of M
    steps = 15
    for i in range(steps):
        progress = i / (steps - 1)
        x_pos = int(m_x + stroke_width + (center_x_m - 3 - m_x - stroke_width) * progress)
        y_pos = int(letter_y + (center_y_m - letter_y) * progress)
        draw.rectangle([x_pos, y_pos, x_pos + stroke_width - 1, y_pos + 2], fill='white')
    
    # Right diagonal of M
    for i in range(steps):
        progress = i / (steps - 1)
        x_pos = int(m_x + m_width - stroke_width + (center_x_m + 3 - m_x - m_width + stroke_width) * progress)
        y_pos = int(letter_y + (center_y_m - letter_y) * progress)
        draw.rectangle([x_pos, y_pos, x_pos + stroke_width - 1, y_pos + 2], fill='white')
    
    # M center vertical (short one from meeting point down)
    draw.rectangle([center_x_m - stroke_width // 2, center_y_m, 
                   center_x_m + stroke_width // 2, letter_y + letter_height], fill='white')
    
    # No connection - clean separate letters
    return img

# Create the logo
logo = create_clean_separated_logo()

# Save different sizes
logo_200 = logo.resize((200, 200), Image.Resampling.LANCZOS)
logo_200.save('logo_clean_separated.png', 'PNG', optimize=True)
print("✅ Created clean separated logo: logo_clean_separated.png")

logo_120 = logo.resize((120, 120), Image.Resampling.LANCZOS)
logo_120.save('logo_square_clean_separated.png', 'PNG', optimize=True)
print("✅ Created clean separated square logo: logo_square_clean_separated.png")

# Create favicons
logo_32 = logo.resize((32, 32), Image.Resampling.LANCZOS)
logo_32.save('favicon_clean_separated_32.png', 'PNG', optimize=True)

logo_16 = logo.resize((16, 16), Image.Resampling.LANCZOS)
logo_16.save('favicon_clean_separated_16.png', 'PNG', optimize=True)

print("✅ Created clean separated favicons")
print("🎉 Clean, separate R&M logo with no connection is ready!")
