import qrcode

url = "sms:+18887661494?body=John%203:16"

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=16,
    border=4
)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white") # Data to send
img.save("qr_code.png")
img.show()
