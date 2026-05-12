import streamlit as st
import google.generativeai as genai
from PIL import Image
import smtplib
from email.mime.text import MIMEText

st.title("🍔 Menu Reader App")
st.write("Snap a photo of a menu, and I'll extract the prices as JSON and email it to you!")

# Set up the AI
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# We use session_state so the app remembers the JSON and doesn't re-run the AI 
# when you type in an email address or click the send button.
if "json_result" not in st.session_state:
    st.session_state.json_result = None

# Turn on the mobile camera
camera_photo = st.camera_input("Take a picture of the menu")

if camera_photo is not None:
    # Only run the AI if we haven't extracted data for this photo yet
    if st.session_state.json_result is None:
        image = Image.open(camera_photo).convert('RGB')
        st.write("🤖 Reading the menu... please wait...")
        
        model = genai.GenerativeModel("gemini-2.5-flash") 
        prompt = "Extract the food items and their prices from this image. Return a JSON list of objects, where each object has an 'item' key and a 'price' key."
        
        try:
            # We use generation_config to force the AI to return strict, clean JSON
            response = model.generate_content(
                [prompt, image],
                generation_config={"response_mime_type": "application/json"}
            )
            st.session_state.json_result = response.text
            st.success("Extraction Complete!")
            
        except Exception as e:
            st.error("Uh oh! The AI ran into a problem:")
            st.error(str(e))

    # If the JSON was successfully extracted, show it and display the email form
    if st.session_state.json_result:
        st.write("### Extracted Data (JSON):")
        st.code(st.session_state.json_result, language="json")
        
        st.write("---")
        st.write("### 📧 Email the Results")
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
    # If the user clears the camera, clear the saved JSON so they can take a new photo
    st.session_state.json_result = None
    
