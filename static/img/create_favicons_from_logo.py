from PIL import Image

# Source logo path (should be the new logo)
logo_path = "static/img/logo.png"

# Output favicon paths
favicon_ico = "static/img/favicon.ico"
favicon_16 = "static/img/favicon-16.png"
favicon_32 = "static/img/favicon-32.png"

# Open the logo
logo = Image.open(logo_path).convert("RGBA")

# Create 16x16 favicon
favicon16 = logo.resize((16, 16), Image.LANCZOS)
favicon16.save(favicon_16, format="PNG")

# Create 32x32 favicon
favicon32 = logo.resize((32, 32), Image.LANCZOS)
favicon32.save(favicon_32, format="PNG")

# Create .ico file with both sizes
favicon16.save(favicon_ico, format="ICO", sizes=[(16, 16), (32, 32)])

print("Favicons generated from logo.png.")
