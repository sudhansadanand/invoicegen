import streamlit as st
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Streamlit layout settings
st.set_page_config(
    page_title="Signature Capture",
    layout="wide"
)

# Create a canvas to capture the signature
canvas = st_canvas(
    width=600,  # Set the width of the canvas
    height=200,  # Set the height of the canvas
    drawing_mode="freedraw",  # Set the drawing mode to free draw
    key="canvas",
)

# Add a button to save the signature
if st.button("Save Signature"):
    # Get the signature data as a numpy array
    signature_data = canvas.image_data.astype(np.uint8)
    st.image(signature_data, use_column_width=True, caption="Captured Signature")
