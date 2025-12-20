from PIL import Image, ImageDraw, ImageFont

# Create a 1024x1024 image with gradient background
size = 1024
img = Image.new('RGB', (size, size), color='#6366F1')
draw = ImageDraw.Draw(img)

# Draw a simple gas pump icon
# Pump body
pump_color = 'white'
draw.rectangle([350, 400, 674, 800], fill=pump_color)

# Pump top/roof
draw.rectangle([300, 350, 724, 420], fill=pump_color)

# Display screen
draw.rectangle([400, 480, 624, 600], fill='#1e293b')

# Nozzle holder on side
draw.rectangle([674, 500, 750, 600], fill=pump_color)
draw.ellipse([724, 480, 776, 620], fill='#94a3b8')

# Hose
draw.arc([724, 480, 850, 620], start=270, end=90, fill='#64748b', width=15)

# Base
draw.rectangle([320, 800, 704, 850], fill='#475569')

# Add text "AT" below
try:
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
except:
    font = ImageFont.load_default()

text = "AT"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
text_x = (size - text_width) // 2
text_y = 870

draw.text((text_x, text_y), text, fill='white', font=font)

# Save the image
img.save('/Users/mert/Documents/GitHub/MyWorkplace/flutter_akaryakit/assets/app_icon.png')
print("Icon created successfully!")
