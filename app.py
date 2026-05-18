from flask import Flask, request, redirect, session, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "inventario_secreto"

# =========================
# USUARIOS
# =========================
USUARIOS = {
    "admin": "1234",
    "almacen": "5678"
}

# =========================
# BASE DE DATOS
# =========================
def init_db():

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE,
            material TEXT,
            cantidad INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# LOGIN REQUIRED
# =========================
def login_required():
    return "user" in session

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user = request.form["user"]
        password = request.form["password"]

        if user in USUARIOS and USUARIOS[user] == password:

            session["user"] = user
            return redirect("/")

        else:

            return """
            <h2>❌ Usuario o contraseña incorrectos</h2>
            <a href="/login">Volver</a>
            """

    return """
    <!DOCTYPE html>
    <html>
    <head>

        <title>Login Inventario</title>

        <style>

            body{
                margin:0;
                padding:0;
                font-family: Arial;
                background-image:url('https://images.unsplash.com/photo-1504307651254-35680f356dfd?q=80&w=1974&auto=format&fit=crop');
                background-size:cover;
                background-position:center;
                height:100vh;
                display:flex;
                justify-content:center;
                align-items:center;
            }

            .login-box{
                background:rgba(0,0,0,0.75);
                padding:40px;
                border-radius:20px;
                width:320px;
                color:white;
                box-shadow:0px 0px 20px rgba(0,0,0,0.5);
            }

            h1{
                text-align:center;
                margin-bottom:30px;
            }

            input{
                width:100%;
                padding:12px;
                margin-top:5px;
                margin-bottom:20px;
                border:none;
                border-radius:10px;
                font-size:16px;
            }

            button{
                width:100%;
                padding:12px;
                background:#ff9800;
                border:none;
                border-radius:10px;
                color:white;
                font-size:16px;
                cursor:pointer;
            }

            button:hover{
                background:#e68900;
            }

        </style>

    </head>

    <body>

        <div class="login-box">

            <h1>🏗 Inventario Obra</h1>

            <form method="post">

                Usuario:
                <input name="user">

                Contraseña:
                <input type="password" name="password">

                <button>Entrar</button>

            </form>

        </div>

    </body>
    </html>
    """

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():

    session.clear()
    return redirect("/login")

# =========================
# DASHBOARD
# =========================
@app.route("/")
def inicio():

    if not login_required():
        return redirect("/login")

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute("SELECT material, cantidad FROM inventario")
    datos = cursor.fetchall()

    conn.close()

    total_items = len(datos)
    total_unidades = sum([c for _, c in datos])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>

        <title>Inventario Obra</title>

        <style>

            body{{
                margin:0;
                padding:0;
                font-family:Arial;
                background-image:url('https://images.unsplash.com/photo-1541888946425-d81bb19240f5?q=80&w=2070&auto=format&fit=crop');
                background-size:cover;
                background-position:center;
                color:white;
            }}

            .overlay{{
                background:rgba(0,0,0,0.75);
                min-height:100vh;
                padding:40px;
            }}

            .card{{
                background:rgba(255,255,255,0.1);
                padding:20px;
                border-radius:20px;
                margin-bottom:20px;
                backdrop-filter: blur(5px);
            }}

            h1{{
                font-size:40px;
            }}

            input{{
                width:100%;
                padding:12px;
                margin-top:5px;
                margin-bottom:15px;
                border:none;
                border-radius:10px;
                font-size:15px;
            }}

            button{{
                padding:12px 20px;
                border:none;
                border-radius:10px;
                background:#ff9800;
                color:white;
                font-size:15px;
                cursor:pointer;
            }}

            button:hover{{
                background:#e68900;
            }}

            .material{{
                background:rgba(255,255,255,0.1);
                padding:10px;
                border-radius:10px;
                margin-bottom:10px;
            }}

            .top-bar{{
                display:flex;
                justify-content:space-between;
                align-items:center;
                flex-wrap:wrap;
            }}

            a{{
                color:#ffd54f;
                text-decoration:none;
            }}

        </style>

    </head>

    <body>

    <div class="overlay">

        <div class="top-bar">

            <h1>📦 Inventario de Obra Civil</h1>

            <div>
                👤 {session["user"]} |
                <a href="/logout">Cerrar sesión</a>
            </div>

        </div>

        <div class="card">

            <h2>📊 Resumen General</h2>

            <p>Total materiales: {total_items}</p>
            <p>Total unidades: {total_unidades}</p>

        </div>

        <div class="card">

            <h2>➕ Entrada de Material</h2>

            <form action="/entrada" method="post">

                Material:
                <input name="material">

                Cantidad:
                <input type="number" name="cantidad">

                <button>Agregar</button>

            </form>

        </div>

        <div class="card">

            <h2>➖ Salida de Material</h2>

            <form action="/salida" method="post">

                Material:
                <input name="material">

                Cantidad:
                <input type="number" name="cantidad">

                <button>Retirar</button>

            </form>

        </div>

        <div class="card">

            <h2>📦 Inventario Actual</h2>
    """

    for material, cantidad in datos:

        color = "#ff5252" if cantidad <= 10 else "#4caf50"

        html += f"""
        <div class="material">
            <b>{material}</b>

            <span style="float:right; color:{color};">
                Cantidad: {cantidad}
            </span>
        </div>
        """

    html += """
        </div>

        <div class="card">

            <a href="/reporte">
                <button>📊 Descargar Excel</button>
            </a>

            <a href="/scanner">
                <button>📷 Escanear QR</button>
            </a>

        </div>

    </div>

    </body>
    </html>
    """

    return html

# =========================
# ENTRADA
# =========================
@app.route("/entrada", methods=["POST"])
def entrada():

    if not login_required():
        return redirect("/login")

    material = request.form["material"]
    cantidad = int(request.form["cantidad"])

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT cantidad FROM inventario WHERE material = ?",
        (material,)
    )

    r = cursor.fetchone()

    if r:

        nueva = r[0] + cantidad

        cursor.execute(
            "UPDATE inventario SET cantidad = ? WHERE material = ?",
            (nueva, material)
        )

    else:

        cursor.execute(
            "INSERT INTO inventario (material, cantidad) VALUES (?, ?)",
            (material, cantidad)
        )

    conn.commit()
    conn.close()

    return redirect("/")

# =========================
# SALIDA
# =========================
@app.route("/salida", methods=["POST"])
def salida():

    if not login_required():
        return redirect("/login")

    material = request.form["material"]
    cantidad = int(request.form["cantidad"])

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT cantidad FROM inventario WHERE material = ?",
        (material,)
    )

    r = cursor.fetchone()

    if r:

        nueva = r[0] - cantidad

        if nueva < 0:
            nueva = 0

        cursor.execute(
            "UPDATE inventario SET cantidad = ? WHERE material = ?",
            (nueva, material)
        )

    conn.commit()
    conn.close()

    return redirect("/")

# =========================
# REPORTE EXCEL
# =========================
@app.route("/reporte")
def reporte():

    if not login_required():
        return redirect("/login")

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute("SELECT material, cantidad FROM inventario")
    datos = cursor.fetchall()

    conn.close()

    df = pd.DataFrame(
        datos,
        columns=["Material", "Cantidad"]
    )

    archivo = "reporte_inventario.xlsx"

    df.to_excel(archivo, index=False)

    return f"""
    <h2>📊 Reporte generado correctamente</h2>

    <p>Archivo: {archivo}</p>

    <a href="/">Volver</a>
    """

# =========================
# SCANNER QR
# =========================
@app.route("/scanner")
def scanner():

    return """
    <!DOCTYPE html>
    <html>
    <head>

        <title>Scanner QR</title>

        <script src="https://unpkg.com/html5-qrcode"></script>

        <style>

            body{
                font-family:Arial;
                background:#111;
                color:white;
                text-align:center;
                padding:20px;
            }

            #reader{
                width:300px;
                margin:auto;
            }

            button{
                padding:10px 20px;
                border:none;
                border-radius:10px;
                background:#ff9800;
                color:white;
                font-size:16px;
                cursor:pointer;
            }

        </style>

    </head>

    <body>

        <h1>📷 Escáner QR</h1>

        <div id="reader"></div>

        <p id="resultado">Esperando QR...</p>

        <script>

            function onScanSuccess(decodedText, decodedResult){

                document.getElementById("resultado").innerHTML =
                    "Código detectado: " + decodedText;

                window.location.href =
                    "/qr_entrada/" + decodedText + "/1";
            }

            let html5QrCode = new Html5Qrcode("reader");

            Html5Qrcode.getCameras().then(devices => {

                if(devices && devices.length){

                    let cameraId = devices[0].id;

                    html5QrCode.start(
                        cameraId,
                        {
                            fps:10,
                            qrbox:250
                        },
                        onScanSuccess
                    );
                }

            });

        </script>

        <br><br>

        <a href="/">
            <button>Volver</button>
        </a>

    </body>
    </html>
    """

# =========================
# QR ENTRADA
# =========================
@app.route("/qr_entrada/<codigo>/<int:cantidad>")
def qr_entrada(codigo, cantidad):

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT cantidad FROM inventario WHERE codigo = ?",
        (codigo,)
    )

    r = cursor.fetchone()

    if r:

        nueva = r[0] + cantidad

        cursor.execute(
            "UPDATE inventario SET cantidad = ? WHERE codigo = ?",
            (nueva, codigo)
        )

    conn.commit()
    conn.close()

    return f"""
    <h2>✅ Entrada registrada</h2>

    <p>Código QR: {codigo}</p>

    <a href="/scanner">
        <button>Escanear otro</button>
    </a>
    """

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
