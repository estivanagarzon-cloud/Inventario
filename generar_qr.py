import qrcode
import os

# -------------------------
# CARPETA DONDE SE GUARDAN LOS QR
# -------------------------
carpeta = "qr_codes"

if not os.path.exists(carpeta):
    os.makedirs(carpeta)

# -------------------------
# HERRAMIENTAS / MATERIALES
# (codigo : nombre)
# -------------------------
herramientas = {
    "CEM001": "Cemento",
    "ARE001": "Arena",
    "ACR001": "Acero",
    "HER001": "Martillo",
    "HER002": "Taladro",
    "HER003": "Flexómetro",
    "HER004": "Destornillador"
}

# -------------------------
# GENERAR QRs
# -------------------------
for codigo, nombre in herramientas.items():

    # El QR solo contiene el código
    qr = qrcode.make(codigo)

    ruta = os.path.join(carpeta, f"{codigo}.png")
    qr.save(ruta)

    print(f"✔ QR generado: {codigo} - {nombre}")

print("\n🎉 Todos los códigos QR fueron generados correctamente")