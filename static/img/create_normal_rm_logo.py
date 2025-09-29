from PIL import Image, ImageDraw, ImageFont
import os

def create_normal_rm_logo():
    """
    Create a logo with normal, standard-looking R and M letters.
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
    
    # Letter dimensions for normal-looking letters
    letter_height = 60
    stroke_width = 12
    
    # Position letters with good separation
    r_x = center - 45
    m_x = center + 8
    letter_y = center - letter_height // 2
    
    # Draw R - normal letter shape
    r_width = 32
    
    # R main vertical line (left side)
    draw.rectangle([r_x, letter_y, r_x + stroke_width, letter_y + letter_height], fill='white')
    
    # R top horizontal line
    draw.rectangle([r_x, letter_y, r_x + r_width, letter_y + stroke_width], fill='white')
    
    # R middle horizontal line (slightly shorter)
    mid_y = letter_y + letter_height // 2 - stroke_width // 2
    draw.rectangle([r_x, mid_y, r_x + r_width - 4, mid_y + stroke_width], fill='white')
    
    # R top right vertical line (upper half only)
    draw.rectangle([r_x + r_width - stroke_width, letter_y, 
                   r_x + r_width, mid_y + stroke_width], fill='white')
    
    # R diagonal leg - straight clean diagonal
    leg_start_x = r_x + r_width - stroke_width - 4
    leg_start_y = mid_y + stroke_width
    leg_end_x = r_x + r_width
    leg_end_y = letter_y + letter_height
    
    # Draw diagonal as series of rectangles
    leg_length = int(((leg_end_x - leg_start_x)**2 + (leg_end_y - leg_start_y)**2)**0.5)
    for i in range(leg_length):
        progress = i / leg_length
        x = int(leg_start_x + (leg_end_x - leg_start_x) * progress)
        y = int(leg_start_y + (leg_end_y - leg_start_y) * progress)
        draw.rectangle([x, y, x + stroke_width - 2, y + stroke_width - 2], fill='white')
    
    # Draw M - normal letter shape
    m_width = 40
    
    # M left vertical line
    draw.rectangle([m_x, letter_y, m_x + stroke_width, letter_y + letter_height], fill='white')
    
    # M right vertical line
    draw.rectangle([m_x + m_width - stroke_width, letter_y, 
                   m_x + m_width, letter_y + letter_height], fill='white')
    
    # M diagonals meeting at center
    center_x_m = m_x + m_width // 2
    center_y_m = letter_y + letter_height // 2.5  # Not too high, not too low
    
    # Left diagonal of M
    left_diag_length = int(((center_x_m - m_x - stroke_width)**2 + (center_y_m - letter_y)**2)**0.5)
    for i in range(left_diag_length):
        progress = i / left_diag_length
        x = int(m_x + stroke_width + (center_x_m - m_x - stroke_width) * progress)
        y = int(letter_y + (center_y_m - letter_y) * progress)
        draw.rectangle([x, y, x + stroke_width - 2, y + stroke_width - 2], fill='white')
    
    # Right diagonal of M
    right_diag_length = int(((m_x + m_width - stroke_width - center_x_m)**2 + (center_y_m - letter_y)**2)**0.5)
    for i in range(right_diag_length):
        progress = i / right_diag_length
        x = int(center_x_m + (m_x + m_width - stroke_width - center_x_m) * progress)
        y = int(letter_y + (center_y_m - letter_y) * progress)
        draw.rectangle([x, y, x + stroke_width - 2, y + stroke_width - 2], fill='white')
    
    # M center vertical line (from meeting point down)
    draw.rectangle([center_x_m - stroke_width // 2, center_y_m, 
                   center_x_m + stroke_width // 2, letter_y + letter_height], fill='white')
    
    return img

# Create the logo
logo = create_normal_rm_logo()

# Save different sizes
logo_200 = logo.resize((200, 200), Image.Resampling.LANCZOS)
logo_200.save('logo_normal_rm.png', 'PNG', optimize=True)
print("✅ Created normal R&M logo: logo_normal_rm.png")

logo_120 = logo.resize((120, 120), Image.Resampling.LANCZOS)
logo_120.save('logo_square_normal_rm.png', 'PNG', optimize=True)
print("✅ Created normal R&M square logo: logo_square_normal_rm.png")

# Create favicons
logo_32 = logo.resize((32, 32), Image.Resampling.LANCZOS)
logo_32.save('favicon_normal_rm_32.png', 'PNG', optimize=True)

logo_16 = logo.resize((16, 16), Image.Resampling.LANCZOS)
logo_16.save('favicon_normal_rm_16.png', 'PNG', optimize=True)

print("✅ Created normal R&M favicons")
print("🎉 Normal, standard-looking R&M letters are ready!")
