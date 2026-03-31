# 01. IMPORTACIONES
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm


# 02. CONSTANTES Y RUTAS

IMAGES_DIR  = os.getcwd() + '/images'
HEADERS_DIR = os.getcwd() + '/encabezados'

HEADER_IMAGE = f'{HEADERS_DIR}/no_borrar_1.png'
FOOTER_IMAGE = f'{HEADERS_DIR}/no_borrar_2.png'
PDF_OUTPUT   = os.getcwd() + '/inventario.pdf'

# 03. CONFIGURACIÓN DE LA PÁGINA
WIDTH, HEIGHT = A4

HEADER_HEIGHT  = 29 * mm
FOOTER_HEIGHT  = 26 * mm
TITLE_HEIGHT   =  8 * mm
SIDE_MARGIN    = 10 * mm

Y_FOOTER         = 0
Y_HEADER         = HEIGHT - HEADER_HEIGHT
Y_TITLE          = Y_FOOTER + FOOTER_HEIGHT
CONTENT_HEIGHT   = HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT - TITLE_HEIGHT - 4 * mm
Y_CONTENT        = Y_FOOTER + FOOTER_HEIGHT + TITLE_HEIGHT + 2 * mm
CONTENT_WIDTH    = WIDTH - 2 * SIDE_MARGIN
X_CONTENT        = SIDE_MARGIN


#04. FUNCIONES DE VERIFICACIÓN

def verify_dir(dir_name: str) -> bool:
    """
    Verifica que un directorio con cierto nombre exista.
        input:  la ruta completa del directorio a verificar
        output: variable booleana que da cuenta de la existencia o no del directorio
    """
    IS_DIR = False
    if os.path.isdir(dir_name) == True:
        IS_DIR = True
    else:
        IS_DIR = False

    return IS_DIR


def start_program() -> bool:
    """
    Función de inicio del programa, verifica que los directorios necesarios existan
    antes de correr cualquier otra cosa. No recibe argumentos, trabaja con las
    constantes globales HEADERS_DIR e IMAGES_DIR definidas arriba.

    Si alguno de los dos directorios no existe el programa no va a funcionar,
    así que mejor detenerlo acá.
        output: variable booleana que indica si los directorios necesarios existen
    """
    DIR_EXISTS = False

    if verify_dir(HEADERS_DIR) == True and verify_dir(IMAGES_DIR) == True:
        print('Ambos directorios encontrados, continuando...')
        DIR_EXISTS = True
        return DIR_EXISTS
    else:
        print('Uno o ambos directorios no existen, reiniciar el programa')
        DIR_EXISTS = False
        return DIR_EXISTS


# 05. FUNCIONES PARA CREAR EL DOCUMENTO

def draw_placeholder(c: canvas.Canvas, x: float, y: float, width: float, height: float, text: str) -> None:
    """
    Dibuja un rectángulo gris con texto centrado, se usa cuando no hay una imagen real
    disponible en la ruta esperada. Útil para no romper el flujo si falta algún archivo.
        input:  canvas activo, coordenadas x e y, dimensiones width y height, texto a mostrar
        output: None, dibuja directamente sobre el canvas
    """
    c.setFillColorRGB(0.88, 0.88, 0.88)
    c.rect(x, y, width, height, fill=1, stroke=0)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 8)
    c.drawCentredString(x + width / 2, y + height / 2 - 4, text)


def draw_image(c: canvas.Canvas, path: str, x: float, y: float, width: float, height: float, placeholder_text: str = "Image") -> None:
    """
    Dibuja una imagen en el canvas en la posición y dimensiones dadas. Si la ruta
    no existe o es inválida, cae al placeholder para que la página no quede vacía.
        input:  canvas activo, ruta de la imagen, coordenadas x e y, dimensiones width y height,
                texto opcional para el placeholder
        output: None, dibuja directamente sobre el canvas
    """
    IMAGE_DRAWN = False

    if path and os.path.exists(path) == True:
        c.drawImage(ImageReader(path), x, y, width=width, height=height, preserveAspectRatio=False)
        IMAGE_DRAWN = True
    else:
        draw_placeholder(c, x, y, width, height, placeholder_text)
        IMAGE_DRAWN = False


def draw_template(c: canvas.Canvas, title: str, ese_name: str) -> None:
    """
    Dibuja el header, footer y título en la página actual del canvas. Hay que llamar
    esta función antes de dibujar la imagen de contenido para que las capas queden bien.
        input:  canvas activo, nombre del archivo de imagen usado como título,
                nombre de la ESE para el encabezado superior
        output: None, dibuja directamente sobre el canvas
    """
    # Header institucional fijo en la parte superior
    draw_image(
        c, HEADER_IMAGE,
        x=0, y=Y_HEADER, width=WIDTH, height=HEADER_HEIGHT,
        placeholder_text="Header institucional (210mm x 29mm)"
    )

    # Footer con logos de certificaciones en la parte inferior
    draw_image(
        c, FOOTER_IMAGE,
        x=0, y=Y_FOOTER, width=WIDTH, height=FOOTER_HEIGHT,
        placeholder_text="Footer — Logos certificaciones (210mm x 26mm)"
    )

    # 06. CONFIGURACIÓN DEL TITULO EN LA MITAD DEL DOCUMENTO
    CLEAN_TITLE = os.path.splitext(title)[0]
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(WIDTH / 2, Y_CONTENT + CONTENT_HEIGHT + 2 * mm, ese_name)
    c.drawCentredString(WIDTH / 2, Y_TITLE + 2 * mm, CLEAN_TITLE)


# 07. CREACIÓN DEL PDF

def generate_pdf(ese_name: str) -> bool:
    """
    Función principal, recorre todas las imágenes de IMAGES_DIR y genera un PDF
    con una imagen por página, cada una con su plantilla institucional. El archivo
    queda guardado en la ruta definida en PDF_OUTPUT.
        input:  nombre de la ESE para usar en el encabezado de cada página
        output: variable booleana que indica si el PDF fue generado exitosamente
    """
    PDF_GENERATED = False

    # Solo jpg y png, ordenados alfabéticamente para que salgan en orden
    IMAGE_LIST = sorted([
        f for f in os.listdir(IMAGES_DIR)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ])

    if len(IMAGE_LIST) == 0:
        print('No se encontraron imágenes en la carpeta, verificar el directorio')
        PDF_GENERATED = False
        return PDF_GENERATED

    c = canvas.Canvas(PDF_OUTPUT, pagesize=A4)
    FORMATTED_NAME = f'Inventario de la ESE {ese_name}'

    for image_file in IMAGE_LIST:
        IMAGE_PATH = os.path.join(IMAGES_DIR, image_file)

        # Primero la plantilla y encima la imagen de contenido
        draw_template(c, title=image_file, ese_name=FORMATTED_NAME)
        c.drawImage(
            ImageReader(IMAGE_PATH),
            X_CONTENT, Y_CONTENT,
            width=CONTENT_WIDTH, height=CONTENT_HEIGHT,
            preserveAspectRatio=True, anchor='c'
        )
        c.showPage()

    c.save()
    print(f'PDF generado correctamente: {PDF_OUTPUT}  ({len(IMAGE_LIST)} páginas)')
    PDF_GENERATED = True
    return PDF_GENERATED


# 08. INICIO DEL PROGRAMA

if start_program() == True:
    ESE_NAME = input('Ingresa SOLO el nombre de la ESE donde hiciste el inventario: ')
    generate_pdf(ESE_NAME)
else:
    print('El programa no puede continuar sin los directorios necesarios')