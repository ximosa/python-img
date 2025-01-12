import streamlit as st
import cv2

st.title("OpenCV Test")
try:
    st.write(f"OpenCV version: {cv2.__version__}")
except Exception as e:
    st.error(f"Error al importar OpenCV: {e}")
