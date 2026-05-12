import streamlit as st
import google.generativeai as genai
from PIL import Image

st.title("🍔 Menu Reader App")
st.write("Snap a photo of a menu, and I'll extract the prices!")

# Set up the AI (using a secure secret key)
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Turn on the mobile camera
camera_photo = st.camera_input("Take a picture of the menu")

if camera_photo is not None:
    image = Image.open(camera_photo)
    st.image(image, caption="Captured Menu", use_column_width=True)
    
    st.write("🤖 Reading the menu... please wait...")
    
    # Send the image to the AI
    model = genai.GenerativeModel("gemini-1.5-flash") 
    prompt = "Extract the food items and their prices from this image. Output them as a clean text list."
    response = model.generate_content([prompt, image])
    
    # Show the results
    st.success("Done!")
    st.write("### Extracted Price List:")
    st.write(response.text)
  
