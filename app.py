import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("🍔 Menu Reader App")
st.write("Snap a photo of a menu, and I'll extract the prices!")

# Set up the AI
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Turn on the mobile camera
camera_photo = st.camera_input("Take a picture of the menu")

if camera_photo is not None:
    # BUG FIX: Force the image into standard RGB format
    image = Image.open(camera_photo).convert('RGB')
    
    st.image(image, caption="Captured Menu", use_column_width=True)
    st.write("🤖 Reading the menu... please wait...")
    
    model = genai.GenerativeModel("gemini-1.5-flash") 
    prompt = "Extract the food items and their prices from this image. Output them as a clean text list."
    
    # BUG FIX: Safely try to call the AI and catch the exact error if it fails
    try:
        response = model.generate_content([prompt, image])
        st.success("Done!")
        st.write("### Extracted Price List:")
        st.write(response.text)
        
    except Exception as e:
        st.error("Uh oh! The AI ran into a problem:")
        st.error(str(e))
        
