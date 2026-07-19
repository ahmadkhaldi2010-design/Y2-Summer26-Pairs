import os #here we import basically the ai and load everything till the function "run chat"
import base64 #base64 is a translating system that take binary 1 and 0 and translates them into text that includes characters like =, +, /


from anthropic import Anthropic
from dotenv import load_dotenv

# ReportLab tools to build the actual PDF file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Helper function to convert a local image file into an API-readable block
def get_image_block(image_path):
    with open(image_path, "rb") as img_file: #reads the raw bites the "rbb" instead of usual characters like letteers
        b64_data = base64.b64encode(img_file.read()).decode("utf-8") #It translates every few bits of data into a highly specific, -->
        #<--> ultra-safe set of 64 standard characters (A-Z, a-z, 0-9, and a couple of symbols).
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",  # Supports standard JPEG/JPG references
            "data": b64_data
        }
    }

# Function that takes the raw text from the AI and builds a clean PDF file
def generate_menu_pdf(menu_text, filename="generated_menu.pdf"):
    # 1. Create a document container matching standard letter paper size
    doc = SimpleDocTemplate(filename, pagesize=letter) #This line tells the computer to create a blank document file --->
    #<----> and cut it into a "letter" format which is the most commonly used one for printers
    story = [] # Holds the structural elements of the PDF sequentially
    
    # 2. Grab default text styles and add custom formatting for the menu
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('MenuTitle', parent=styles['Heading1'], alignment=1, spaceAfter=20)
    item_style = ParagraphStyle('MenuItem', parent=styles['Normal'], fontSize=12, spaceAfter=8)
    
    # 3. Process the AI's response line by line to build the document layout
    lines = menu_text.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        
        # If the line looks like a title or header, use the large title style:
        if clean_line.startswith("Type of cuisine:") or clean_line.startswith("##") or "MENU" in clean_line.upper():
            story.append(Paragraph(f"<b>{clean_line}</b>", title_style))
        else:
            # Otherwise, add it as a standard menu item line
            story.append(Paragraph(clean_line, item_style))
            
    # 4. Compile all elements and write the physical PDF file to disk
    doc.build(story)
    print(f"\n[System]: PDF successfully created and saved as '{filename}'!")

def run_chat():
    print('You: (type exit to quit)')
    print('To send an image, type: image: path/to/your/image.jpg')
    print('-' * 50)
    
    # We update the system prompt to explicitly command the AI how to format the final menu
    system_message = """
    Your name is Ramsay. You design professional menus.
    You are professional and polite.
    Focus exclusively on menus and design choices.
    Always ask about style, colors, and cuisine type.
    
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

        # Check if the user is trying to submit an image file
        if user_input.lower().startswith('image:'):
            # Extract the file path from the string (e.g., "image: ref.jpg" -> "ref.jpg")
            img_path = user_input.split('image:')[-1].strip()
            
            if os.path.exists(img_path):
                print(f"[System]: Loading reference image '{img_path}'...")
                # Ask the user for context text to go along with the image
                caption = input('Add a message with your image >> ')
                
                # Assemble a multi-part content list containing both the image block and the text block
                content_list = [
                    get_image_block(img_path),
                    {"type": "text", "text": caption}
                ]
                history.append({'role': 'user', 'content': content_list})
            else:
                print(f"[Error]: Could not find file at '{img_path}'. Please check the path.")
                continue
        else:
            # Standard text entry
            history.append({'role': 'user', 'content': user_input})

        # Send the conversation state over to Claude
        response = client.messages.create(
            model='claude-3-5-sonnet-20241022', # Sonnet handles vision/image understanding exceptionally well
            max_tokens=600,
            temperature=0.7,
            system=system_message,
            messages=history
        )
        
        reply = response.content[0].text
        print(f'\nRamsay: {reply}\n')
        history.append({'role': 'assistant', 'content': reply})
        
        # Check if the AI included our trigger tags indicating the menu is ready to print
        if "[MENU_START]" in reply and "[MENU_END]" in reply:
            # Extract only the menu text inside those tags
            start_idx = reply.find("[MENU_START]") + len("[MENU_START]")
            end_idx = reply.find("[MENU_END]")
            menu_raw_content = reply[start_idx:end_idx].strip()
            
            # Fire our PDF generation sequence
            generate_menu_pdf(menu_raw_content)

run_chat()


#------HTTP (HyperText Transfer Protocol)-------
# HTTP is the official, agreed-upon language that web browsers and servers use to talk to each other. 
# Because everyone follows the same rules, a computer in Israel can talk to a server in America seamlessly.