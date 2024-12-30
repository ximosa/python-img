import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import cv2
import numpy as np
import io

# Función para convertir imágenes PIL a OpenCV
def pil_to_cv2(img):
    return np.array(img)

def cv2_to_pil(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

# --- Funciones de Herramientas ---
def oscurecer_imagen(img, factor):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)

def borrador_sombras(img, umbral = 100):
    img_cv = pil_to_cv2(img)
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
    l_channel = lab[:,:,0]
    
    # Aumentar el canal L (luminosidad) en las zonas oscuras
    l_channel[l_channel < umbral] = l_channel[l_channel < umbral] + (umbral - l_channel[l_channel < umbral])
    
    # Convertir de nuevo a BGR
    img_cv_modified = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return cv2_to_pil(img_cv_modified)


def borrador_fondos(img):
    # Convertir a formato OpenCV
    img_cv = pil_to_cv2(img)

    # Convertir a espacio de color HSV
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)

    # Definir un rango de colores para el fondo (ajusta los valores según tu imagen)
    lower_background = np.array([0, 0, 200]) # Ejemplo para un fondo claro
    upper_background = np.array([180, 25, 255])

    # Crear una máscara para el fondo
    mask = cv2.inRange(hsv, lower_background, upper_background)
    
    # Invertir la máscara (para seleccionar el objeto)
    mask_inv = cv2.bitwise_not(mask)

    # Extraer el objeto
    objeto = cv2.bitwise_and(img_cv, img_cv, mask=mask_inv)

    # Hacer el fondo transparente (requiere convertir a RGBA)
    objeto_pil = cv2_to_pil(objeto).convert("RGBA")
    datas = objeto_pil.getdata()

    newData = []
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:  # fondo negro
            newData.append((0, 0, 0, 0))  # Hacer transparente
        else:
            newData.append(item)

    objeto_pil.putdata(newData)


    return objeto_pil

def ampliador_imagenes(img, factor):
    nuevo_tamano = (int(img.width * factor), int(img.height * factor))
    return img.resize(nuevo_tamano, Image.LANCZOS)

def herramienta_oscurecimiento(img, factor):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)

def inversor_fotos(img):
    return Image.eval(img, lambda i: 255 - i)

def herramienta_desenfoque(img, radio):
    return img.filter(ImageFilter.GaussianBlur(radio))

def herramienta_recorte_redondo(img):
     # Crear una máscara circular
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)

    # Aplicar la máscara
    img.putalpha(mask)
    return img

def recortar_foto(img, x1, y1, x2, y2):
    return img.crop((x1, y1, x2, y2))

def herramienta_cuentagotas(img, x, y):
    return img.getpixel((x, y))

def editor_bn(img):
    return img.convert('L')

def herramienta_invertir(img):
    return Image.eval(img, lambda i: 255 - i)

def iluminador_fotos(img, factor):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)

def herramienta_colorear(img, color):
     # Crear una imagen del mismo tamaño con el color elegido
    color_img = Image.new("RGB", img.size, color)

    # Combina la imagen original y la imagen de color
    return Image.blend(img.convert('RGB'), color_img, 0.5)

def rotador_fotos(img, grados):
    return img.rotate(grados, expand=True)

# --- Interfaz Streamlit ---
def main():
    st.title("Aplicación de Edición de Imágenes")

    uploaded_file = st.file_uploader("Carga una imagen", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Imagen original", use_column_width=True)

            tool = st.selectbox("Selecciona una herramienta", [
                "Oscurecer Imagen", "Borrador de Sombras", "Borrador de Fondos",
                "Ampliador de Imágenes", "Herramienta de Oscurecimiento", 
                "Inversor de Fotos", "Herramienta de Desenfoque",
                "Herramienta de Recorte Redondo", "Recortador de Fotos", 
                "Herramienta Cuentagotas de Color", "Editor de Fotos en Blanco y Negro",
                "Herramienta para Invertir Fotos", "Iluminador de Fotos",
                "Herramienta para Colorear Fotos", "Rotador de Fotos"
            ])

            modified_image = None

            if tool == "Oscurecer Imagen":
                factor = st.slider("Factor de Oscurecimiento", 0.0, 1.0, 0.5)
                modified_image = oscurecer_imagen(image, factor)

            elif tool == "Borrador de Sombras":
                umbral = st.slider("Umbral de oscuridad", 0, 255, 100)
                modified_image = borrador_sombras(image, umbral)

            elif tool == "Borrador de Fondos":
                modified_image = borrador_fondos(image)

            elif tool == "Ampliador de Imágenes":
                factor = st.slider("Factor de Ampliación", 1.0, 5.0, 2.0)
                modified_image = ampliador_imagenes(image, factor)

            elif tool == "Herramienta de Oscurecimiento":
                factor = st.slider("Factor de Oscurecimiento", 0.0, 1.0, 0.5)
                modified_image = herramienta_oscurecimiento(image, factor)

            elif tool == "Inversor de Fotos":
                modified_image = inversor_fotos(image)

            elif tool == "Herramienta de Desenfoque":
                radio = st.slider("Radio de Desenfoque", 1, 20, 5)
                modified_image = herramienta_desenfoque(image, radio)

            elif tool == "Herramienta de Recorte Redondo":
                 modified_image = herramienta_recorte_redondo(image)

            elif tool == "Recortador de Fotos":
                x1 = st.number_input("Coordenada x1", value=0)
                y1 = st.number_input("Coordenada y1", value=0)
                x2 = st.number_input("Coordenada x2", value=image.width)
                y2 = st.number_input("Coordenada y2", value=image.height)
                modified_image = recortar_foto(image, x1, y1, x2, y2)
            
            elif tool == "Herramienta Cuentagotas de Color":
                 x = st.number_input("Coordenada X del píxel", 0, image.width -1, 10)
                 y = st.number_input("Coordenada Y del píxel", 0, image.height-1, 10)
                 color = herramienta_cuentagotas(image, x,y)
                 st.write(f"Color en la posición ({x}, {y}): {color}")
                 modified_image = image # Mostramos la imagen original sin modificar
                 

            elif tool == "Editor de Fotos en Blanco y Negro":
                 modified_image = editor_bn(image)
            
            elif tool == "Herramienta para Invertir Fotos":
                modified_image = herramienta_invertir(image)

            elif tool == "Iluminador de Fotos":
                 factor = st.slider("Factor de Iluminación", 1.0, 3.0, 1.5)
                 modified_image = iluminador_fotos(image, factor)

            elif tool == "Herramienta para Colorear Fotos":
                color = st.color_picker("Selecciona un color", "#FF0000")
                modified_image = herramienta_colorear(image, color)

            elif tool == "Rotador de Fotos":
                grados = st.slider("Grados de Rotación", -180, 180, 0)
                modified_image = rotador_fotos(image, grados)


            if modified_image:
                st.image(modified_image, caption="Imagen modificada", use_column_width=True)
                
                # -- Descarga de la imagen --
                image_bytes = io.BytesIO()
                modified_image.save(image_bytes, format="PNG")
                image_bytes.seek(0)  # Reset buffer
                
                st.download_button(
                    label="Descargar imagen",
                    data=image_bytes,
                    file_name="modified_image.png",
                    mime="image/png"
                )
        except Exception as e:
             st.error(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
