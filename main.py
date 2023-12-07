import cv2

capture = cv2.VideoCapture(0)
qrReader = cv2.QRCodeDetector()
isScanning = True
while isScanning:
    #Con la X cerras el programa
    if cv2.waitKey(1)==ord('x'):
        isScanning = False
    _, image = capture.read()
    data, one, _ = qrReader.detectAndDecode(image)
    if data:
        isScanning = False
    cv2.imshow('Scaner de QR', image)

#El str(data) tiene lo que sea que traiga el QR eso metelo a un file
print(str(data))
cv2.destroyAllWindows()