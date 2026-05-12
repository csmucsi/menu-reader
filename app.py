import streamlit as st
import google.generativeai as genai
from PIL import Image
import smtplib
from email.mime.text import MIMEText

st.title("🍔 Menu Reader App")
st.write("Upload a photo or snap a new one, and I'll extract the prices as JSON and email it to you!")

# Set up the AI
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Function to clear the saved JSON when a new image is provided
def clear_data():
    st.session_state.json_result = None

# Initialize session state for the JSON result
if "json_result" not in st.session_state:
    st.session_state.json_result = None

# ---------------------------------------------------------
# UI: Image Inputs (Upload OR Camera)
# ---------------------------------------------------------
st.write("### Step 1: Provide a Menu Image")

# Add the file uploader. If the user uploads a new file, it triggers clear_data()
uploaded_photo = st.file_uploader("Upload an existing photo", type=['png', 'jpg', 'jpeg'], on_change=clear_data)

st.write("--- OR ---")

# The camera input. If the user snaps a new photo, it triggers clear_data()
camera_photo = st.camera_input("Take a picture of the menu", on_change=clear_data)

# Determine which image source to use. If both are somehow present, we default to the upload.
image_source = uploaded_photo if uploaded_photo else camera_photo

# ---------------------------------------------------------
# AI Processing Logic
# ---------------------------------------------------------
if image_source is not None:
    # Only run the AI if we haven't extracted data for this specific photo yet
    if st.session_state.json_result is None:
        # Force the image into standard RGB format to avoid alpha channel errors
        image = Image.open(image_source).convert('RGB')
        
        # Show the user the image they just uploaded/captured
        st.image(image, caption="Menu to Process", use_column_width=True)
        st.write("🤖 Reading the menu... please wait...")
        
        model = genai.GenerativeModel("gemini-2.5-flash") 
        prompt = "Extract the food items and their prices from this image. Return a JSON list of objects, where each object has an 'item' key and a 'price' key."
        
        try:
            # Force the AI to return strict JSON
            response = model.generate_content(
                [prompt, image],
                generation_config={"response_mime_type": "application/json"}
            )
            st.session_state.json_result = response.text
            st.success("Extraction Complete!")
            
        except Exception as e:
            st.error("Uh oh! The AI ran into a problem:")
            st.error(str(e))

    # ---------------------------------------------------------
    # UI: Email Results
    # ---------------------------------------------------------
    # If the JSON was successfully extracted, show it and display the email form
    if st.session_state.json_result:
        st.write("### Extracted Data (JSON):")
        st.code(st.session_state.json_result, language="json")
        
        st.write("---")
        st.write("### 📧 Step 2: Email the Results")
        recipient_email = st.text_input("Enter destination email address:")
        
        if st.button("Send Email"):
            if recipient_email:
                try:
                    # Pull email credentials from Streamlit Secrets
                    sender_email = st.secrets["SENDER_EMAIL"]
                    sender_password = st.secrets["SENDER_PASSWORD"]
                    
                    # Construct the email
                    msg = MIMEText(st.session_state.json_result)
                    msg['Subject'] = 'Your Menu JSON Data'
                    msg['From'] = sender_email
                    msg['To'] = recipient_email
                    
                    # Connect to Gmail and send
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                        server.login(sender_email, sender_password)
                        server.sendmail(sender_email, recipient_email, msg.as_string())
                        
                    st.success(f"JSON successfully sent to {recipient_email}!")
                except Exception as e:
                    st.error("Failed to send email. Check your Streamlit Secrets and App Password.")
                    st.error(str(e))
            else:
                st.warning("Please enter an email address first.")
else:
    # If the user clears both the camera and the uploader, reset the app entirely
    st.session_state.json_result = None
    
