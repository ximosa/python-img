import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import io
from io import BytesIO
import pkg_resources
import os

# --- Funciones de Utilería ---

def optimizar_imagen(img, max_size=(800, 800)):
    """Optimiza el tamaño de una imagen para reducir su peso."""
    img.thumbnail(max_size)
    return img

def pil_to_cv2(img):
    """Convierte una imagen PIL a formato OpenCV."""
    return np.array(img)

def cv2_to_pil(img):
    """Convierte una imagen OpenCV a formato PIL."""
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

# --- Funciones de Herramientas ---
def oscurecer_imagen(img, factor):
    """Oscurece una imagen."""
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)

def borrador_sombras(img, umbral=100):
    """Aclara sombras en la imagen."""
    img_cv = pil_to_cv2(img)
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
    l_channel = lab[:,:,0]
    l_channel[l_channel < umbral] = l_channel[l_channel < umbral] + (umbral - l_channel[l_channel < umbral])
    img_cv_modified = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    return cv2_to_pil(img_cv_modified)

def borrador_fondos(img):
    """Elimina el fondo de una imagen."""
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
    """Amplía una imagen."""
    nuevo_tamano = (int(img.width * factor), int(img.height * factor))
    return img.resize(nuevo_tamano, Image.LANCZOS)

def herramienta_oscurecimiento(img, factor):
    """Oscurece una imagen (alias para oscurecer_imagen)."""
    return oscurecer_imagen(img, factor)

def inversor_fotos(img):
    """Invierte los colores de una imagen."""
    return Image.eval(img, lambda i: 255 - i)

def herramienta_desenfoque(img, radio):
    """Aplica un desenfoque a la imagen."""
    return img.filter(ImageFilter.GaussianBlur(radio))

def herramienta_recorte_redondo(img):
    """Recorta una imagen a una forma redonda."""
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
    img.putalpha(mask)
    return img

def recortar_foto(img, x1, y1, x2, y2):
    """Recorta una imagen según coordenadas."""
    return img.crop((x1, y1, x2, y2))

def herramienta_cuentagotas(img, x, y):
    """Obtiene el color de un píxel."""
    return img.getpixel((x, y))

def editor_bn(img):
    """Convierte una imagen a blanco y negro."""
    return img.convert('L')

def herramienta_invertir(img):
    """Invierte los colores de una imagen (alias para inversor_fotos)."""
    return inversor_fotos(img)

def iluminador_fotos(img, factor):
    """Ilumina una imagen."""
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)

def herramienta_colorear(img, color):
    """Colorea una imagen."""
    color_img = Image.new("RGB", img.size, color)
    return Image.blend(img.convert('RGB'), color_img, 0.5)

def rotador_fotos(img, grados):
    """Rota una imagen."""
    return img.rotate(grados, expand=True)


# Nueva función para agregar texto usando OpenCV
def agregar_texto_a_imagen(img, texto, posicion, tamaño, color):
   """Agrega texto a una imagen utilizando OpenCV."""
   img_cv = pil_to_cv2(img)

   # Convierte el color RGB de PIL a BGR de OpenCV
   color_bgr = (color[2], color[1], color[0])

   # Define el tipo de fuente
   font = cv2.FONT_HERSHEY_SIMPLEX

   # Escala del texto
   scale = tamaño / 30.0
   
   #Calcula el tamaño del texto
   text_size = cv2.getTextSize(texto, font, scale, 1)[0]

   # Calcula la posición del texto
   if posicion == "arriba":
      x = int((img.width - text_size[0]) / 2)
      y = 30 # Margen superior
   elif posicion == "centro":
       x = int((img.width - text_size[0]) / 2)
       y = int((img.height + text_size[1]) / 2)
   elif posicion == "abajo":
      x = int((img.width - text_size[0]) / 2)
      y = int(img.height - 20) #Margen Inferior
   else:  # Coordenadas personalizadas
      x, y = map(int, posicion.split(','))
      x = int(x)
      y = int(y)
    
   # Agrega el texto a la imagen
   cv2.putText(img_cv, texto, (x, y), font, scale, color_bgr, 1, cv2.LINE_AA)
   return cv2_to_pil(img_cv)

# --- Interfaz Streamlit ---
def main():
    st.title("Aplicación de Edición de Imágenes")

    uploaded_file = st.file_uploader("Carga una imagen", type=["jpg", "jpeg", "png", "webp"])

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            
            # Optimizar la imagen al cargarla
            image = optimizar_imagen(image)

            st.image(image, caption="Imagen original", use_container_width=True)

            tool = st.selectbox("Selecciona una herramienta", [
                "Oscurecer Imagen", "Borrador de Sombras", "Borrador de Fondos",
                "Ampliador de Imágenes", "Herramienta de Oscurecimiento", 
                "Inversor de Fotos", "Herramienta de Desenfoque",
                "Herramienta de Recorte Redondo", "Recortador de Fotos", 
                "Herramienta Cuentagotas de Color", "Editor de Fotos en Blanco y Negro",
                "Herramienta para Invertir Fotos", "Iluminador de Fotos",
                "Herramienta para Colorear Fotos", "Rotador de Fotos", "Agregar Texto"
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

            elif tool == "Agregar Texto":
                texto = st.text_input("Texto a agregar", "Tu Título Aquí")
                posicion = st.selectbox("Posición del texto", ["arriba", "centro", "abajo", "personalizada(x,y)"])
                if posicion == "personalizada(x,y)":
                    posicion = st.text_input("Coordenada X,Y (Ejemplo 10,50)", "10,10")
                tamaño = st.slider("Tamaño del texto", 10, 100, 30)
                color = st.color_picker("Color del texto", "#FFFFFF")  # Color por defecto: blanco
                modified_image = agregar_texto_a_imagen(image.copy(), texto, posicion, tamaño, color)
                

            if modified_image:
                st.image(modified_image, caption="Imagen modificada", use_container_width=True)
                
                # --- Descarga de la imagen ---
                # Optimizar la imagen antes de la descarga
                optimized_download_image = optimizar_imagen(modified_image.copy())
                
                
                image_bytes = io.BytesIO()
                try:
                  optimized_download_image.save(image_bytes, format="webp", lossless=True, quality=80)
                  mime="image/webp"
                  file_name="modified_image.webp"
                except:
                   optimized_download_image.save(image_bytes, format="PNG")
                   mime="image/png"
                   file_name="modified_image.png"

                
                image_bytes.seek(0)
                
                st.download_button(
                    label="Descargar imagen",
                    data=image_bytes,
                    file_name=file_name,
                    mime=mime
                )
        except Exception as e:
             st.error(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()
