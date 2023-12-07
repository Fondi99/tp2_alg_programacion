import cv2
import os

def leer_qr_desde_webcam():
    capture = cv2.VideoCapture(0)
    qrReader = cv2.QRCodeDetector()
    isScanning = True
    while isScanning:
        if cv2.waitKey(1) == ord('x'):
            isScanning = False
        _, image = capture.read()
        data, _, _ = qrReader.detectAndDecode(image)
        if data:
            isScanning = False
        cv2.imshow('Scanner de QR', image)

    capture.release()
    cv2.destroyAllWindows()

    return data if data else None

def obtener_id_qr():
    opcion = int(input("¿Cómo desea ingresar el código QR?\n1. Desde webcam\n2. Ingresar el ID\n"))

    if opcion == 1:
        return leer_qr_desde_webcam()
    elif opcion == 2:
        id_ingresado = input("Ingresa el ID del código QR (por ejemplo, 1 para 1.png): ")
        nombre_archivo = f"QR/{id_ingresado}.png"
        return decodificar_qr(nombre_archivo)
    else:
        print("Opción no válida.")
        return None

def decodificar_qr(nombre_archivo):
    if not os.path.exists(nombre_archivo):
        print(f"El archivo {nombre_archivo} no existe.")
        return None

    image = cv2.imread(nombre_archivo)
    qrReader = cv2.QRCodeDetector()
    val, b, c = qrReader.detectAndDecode(image)

    return val if val else None

def guardar_ingreso_en_archivo(timestamp, id_qr, nombre_pelicula, cant_entradas, total_consumido):
    with open("Ingresos.txt", "a") as file:
        file.write(f"{timestamp},{id_qr},{nombre_pelicula},{cant_entradas},{total_consumido}\n")

def main():
    id_qr = obtener_id_qr()
    elementos = id_qr.split('+')

    id = int(elementos[0].strip())
    nombre = elementos[1].strip()
    totem = elementos[2].strip()
    entradas = int(elementos[3].strip())
    timestamp = float(elementos[4].strip())

    if id_qr:
        guardar_ingreso_en_archivo(timestamp, id, nombre, entradas, totem)
        print("Información guardada con éxito.")
    else:
        print("No se pudo leer el código QR.")

if __name__ == "__main__":
    main()
