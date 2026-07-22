import os  # Load environment variables and check file paths
import base64  # Base64 translates binary image data into clean text for HTTP requests
from anthropic import Anthropic
from dotenv import load_dotenv

# PILLOW TOOLS: Used to draw the menu directly into a PNG image file
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


# Helper function to convert a local image file into an API-readable block
def get_image_block(image_path):
    with open(image_path, "rb") as img_file:  # Reads raw bytes using "rb"
        b64_data = base64.b64encode(img_file.read()).decode("utf-8")
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",  # Supports JPEG/JPG reference images
            "data": b64_data
        }
    }


# Function that takes raw menu text and draws it directly onto a PNG image
def generate_menu_png(menu_text, filename="generated_menu.png"):
    #reate a blank white canvas (width=800px, height=1000px)
    width, height = 800, 1000
    canvas = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(canvas)

    #loading standard fonts (falls back to default if custom fonts aren't available)
    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        item_font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        title_font = ImageFont.load_default()
        item_font = ImageFont.load_default()

    # Set starting coordinates and line spacing
    x = 60
    y = 60
    line_height = 35

    # Draw each line of the menu onto the PNG canvas
    lines = menu_text.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            y += 15  # Add extra empty space between sections
            continue

        # Check if the line is a header/title line
        if clean_line.startswith("Type of cuisine:") or clean_line.startswith("##") or "MENU" in clean_line.upper():
            draw.text((x, y), clean_line, fill="black", font=title_font)
            y += line_height + 15
        else:
            # Draw standard menu items
            draw.text((x, y), clean_line, fill="#333333", font=item_font)
            y += line_height

    #Save the finished canvas as a PNG image file
    canvas.save(filename, "PNG")
    print(f"\n[System]: Menu image successfully created and saved as '{filename}'!")
def run_agent(agent1_output, design_request):

    system_message = """
    Your name is Ramsay.
    You design professional restaurant menus.

    You ONLY design the menu.
    Never change dishes.
    Never change ingredients.
    Never change prices.

    Use the menu created by Agent 1.
    """

    history = [
        {
            "role": "user",
            "content": f"""
This menu was created by Agent 1:

{agent1_output}

The user wants this design:

{design_request}

Create a professional menu layout.

When you output the final menu, wrap ONLY the menu inside:

[MENU_START]

...

[MENU_END]
"""
        }
    ]

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1400,
        temperature=0.7,
        system=system_message,
        messages=history
    )

    reply = response.content[0].text

    if "[MENU_START]" in reply and "[MENU_END]" in reply:
        start = reply.find("[MENU_START]") + len("[MENU_START]")
        end = reply.find("[MENU_END]")

        menu = reply[start:end].strip()

        generate_menu_png(menu)

    return reply

def run_chat():
    print('You: (type exit to quit)')
    print('To send an image, type: image: path/to/your/image.jpg')
    print('-' * 50)

    # System message defining Ramsay's identity and output format
    system_message = """
    Your name is Ramsay. You design professional menus for cafes and restaurants.
    Always be professional and polite.
    Always focus exclusively on menus and design choices.
    Always ask about style, colors.
    take the iformation about what type of cuisine and what dishes to add to the menu from another agent.
    If you can't fetch this information ask the user for it.
    Never use inappropriate language. 

    CRITICAL: When you are ready to deliver the final menu layout to the user, you MUST wrap the raw menu text inside custom clear tags like this:
    [MENU_START]
    Type of cuisine: Greek
    Greek salad ------------ 15 dollars
    Seafood mix ------------ 80 dollars
    [MENU_END]
    """

    history = []

    while True:
        user_input = input('>> ')

        if user_input.lower() == 'exit':
            break

        # Check if the user input starts with "image:" to attach a reference photo
        if user_input.lower().startswith('image:'):
            img_path = user_input.split('image:')[-1].strip()

            if os.path.exists(img_path):
                print(f"[System]: Loading reference image '{img_path}'...")
                caption = input('Add a message with your image >> ')

                content_list = [
                    get_image_block(img_path),
                    {"type": "text", "text": caption}
                ]
                history.append({'role': 'user', 'content': content_list})
            else:
                print(f"[Error]: Could not find file at '{img_path}'. Please check the path.")
                continue
        else:
            history.append({'role': 'user', 'content': user_input})

        # Send conversation history to Claude
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=1400,
            temperature=0.7,
            system=system_message,
            messages=history
        )

        reply = response.content[0].text
        print(f'\nRamsay: {reply}\n')
        history.append({'role': 'assistant', 'content': reply})

        # When Ramsay finishes, extract the menu text and trigger the PNG generator
        #This block of code is a trigger and extractor. It takes only the menu and leaves behind-->
        #<---> the commentary from the chat.
        if "[MENU_START]" in reply and "[MENU_END]" in reply:
            start_idx = reply.find("[MENU_START]") + len("[MENU_START]")
            end_idx = reply.find("[MENU_END]")
            menu_raw_content = reply[start_idx:end_idx].strip()

            # Generate PNG instead of PDF
            generate_menu_png(menu_raw_content)

if __name__ == "__main__":
    run_chat()

#------HTTP (HyperText Transfer Protocol)-------
# HTTP is the official, agreed-upon language that web browsers and servers use to talk to each other.
# Because everyone follows the same rules, a computer in Israel can talk to a server in America seamlessly.


#-----The Pillow-----
#Pillow is the most popular, go-to Python library used for handling and manipulating images.
#Pillow allows to do stuff like:
# * Open and read image files (like .jpg, .png, .gif, or .bmp).
# * Edit images (crop them, resize them, rotate them, or make thumbnails).
# * Draw things (write text onto an image, draw shapes, or change pixel colors).
# * Save files back to your computer in different formats.


#-----Commands or functions-----

# ~*startswith()*~
#is a built-in Python string tool. It acts like a quick true-or-false detector -->
#<---> that checks what characters are sitting at the very front of a text string.
#If the string begins with the exact words or letters you give it, it answers True.
#If it starts with anything else, it answers False.

# ~*OSError*~
#A built-in Python error that happens when something goes wrong at the Operating System level.
#(like trying to open a file that doesn't exist, lacking permission, 
# or asking for a system font your computer doesn't have).

# ~*ImageFont.truetype*~
#A function from the Pillow library that loads custom font files (.ttf or .otf files) --->
#<---> and sets their pixel size.

# ~*os.path.exists*~
#A tool from Python's built-in os (Operating System) module 
#that checks whether a specific file or folder actually exists on the computer's hard drive.

# ~*reply[start_idx:end_idx].strip()*~
#In Python, square brackets [start : end] -->
#<--> cut out a specific slice of text between two positions (index numbers).
# * start_idx is the character position where [MENU_START] ends.
# * end_idx is the character position where [MENU_END] begins.
# * reply[start_idx:end_idx] cuts out only the text sandwiched between those two tags.
# * .strip() removes any accidental extra white space, blank lines, 
# or tabs sitting at the very beginning or end of that sliced text block.

#~*os.path.exists(img_path):*~
#os.path.exists(img_path) is a built-in Python check that asks your computer's operating system 
#if the file or a folder actually exist in this certain path.
