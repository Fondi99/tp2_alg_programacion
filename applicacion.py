import cv2
import os


def leer_qr_desde_webcam():
    captura = cv2.VideoCapture(0)
    lector_qr = cv2.QRCodeDetector()
    escaneando = True

    while escaneando:
        if cv2.waitKey(1) == ord('x'):
            escaneando = False
        _, imagen = captura.read()
        datos, _, _ = lector_qr.detectAndDecode(imagen)
        if datos:
            escaneando = False
        cv2.imshow('Escáner de QR', imagen)

    captura.release()
    cv2.destroyAllWindows()

    return datos if datos else None


def obtener_id_qr():
    opcion = int(input("¿Cómo desea ingresar el código QR?\n1. Desde la webcam\n2. Ingresar el ID\n"))

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

    imagen = cv2.imread(nombre_archivo)
    lector_qr = cv2.QRCodeDetector()
    valor, _, _ = lector_qr.detectAndDecode(imagen)

    return valor if valor else None


def guardar_ingreso_en_archivo(timestamp, id_qr, nombre_pelicula, cant_entradas, total_consumido):
    with open("Ingresos.txt", "a") as archivo:
        archivo.write(f"{timestamp},{id_qr},{nombre_pelicula},{cant_entradas},{total_consumido}\n")


def main():
    id_qr = obtener_id_qr()

    if id_qr:
        elementos = id_qr.split('+')
        id = int(elementos[0].strip())
        nombre = elementos[1].strip()
        totem = elementos[2].strip()
        entradas = int(elementos[3].strip())
        timestamp = float(elementos[4].strip())

        guardar_ingreso_en_archivo(timestamp, id, nombre, entradas, totem)
        print("Información guardada con éxito.")
    else:
        print("No se pudo leer el código QR.")


if __name__ == "__main__":
    main()
