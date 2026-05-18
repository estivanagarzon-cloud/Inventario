from flask import Flask, request, redirect, session, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "inventario_secreto"

# -------------------------
# USUARIOS (BÁSICO)
# -------------------------
USUARIOS = {
    "admin": "1234",
    "almacen": "5678"
}

# -------------------------
# BASE DE DATOS
# -------------------------
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

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]

        if user in USUARIOS and USUARIOS[user] == password:
            session["user"] = user
            return redirect("/")
        else:
            return "<h3> Login incorrecto</h3><a href='/login'>Volver</a>"

    return """
    <h1> Login Inventario</h1>

    <form method="post">
        Usuario:<br>
        <input name="user"><br><br>

        Contraseña:<br>
        <input type="password" name="password"><br><br>

        <button>Entrar</button>
    </form>
    """

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# -------------------------
# PROTECCIÓN
# -------------------------
def login_required():
    return "user" in session

# -------------------------
# DASHBOARD
# -------------------------
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

    bajos = [m for m, c in datos if c <= 10]

    html = f"""
    <h1>📊 Dashboard Inventario Obra Civil</h1>

    <p>👤 Usuario: {session["user"]}</p>
    <a href="/logout">Cerrar sesión</a>

    <h2>Resumen</h2>
    <p>Total materiales: {total_items}</p>
    <p>Total unidades: {total_unidades}</p>

    <h2> Bajo stock</h2>
    """

    if bajos:
        for b in bajos:
            html += f"<p style='color:red;'> {b}</p>"
    else:
        html += "<p>Todo en niveles normales</p>"

    html += """
    <hr>

    <h2> Entrada</h2>
    <form action="/entrada" method="post">
        Material: <input name="material"><br><br>
        Cantidad: <input type="number" name="cantidad"><br><br>
        <button>Agregar</button>
    </form>

    <h2> Salida</h2>
    <form action="/salida" method="post">
        Material: <input name="material"><br><br>
        Cantidad: <input type="number" name="cantidad"><br><br>
        <button>Retirar</button>
    </form>

    <h2> Inventario</h2>
    """

    for m, c in datos:
        color = "red" if c <= 10 else "black"
        html += f"<p style='color:{color}'><b>{m}</b>: {c}</p>"

    html += """
    <br><br>
    <a href="/reporte"><button>📊 Generar Excel</button></a>
    """

    return html

# -------------------------
# ENTRADA
# -------------------------
@app.route("/entrada", methods=["POST"])
def entrada():

    if not login_required():
        return redirect("/login")

    material = request.form["material"]
    cantidad = int(request.form["cantidad"])

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute("SELECT cantidad FROM inventario WHERE material = ?", (material,))
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

# -------------------------
# SALIDA
# -------------------------
@app.route("/salida", methods=["POST"])
def salida():

    if not login_required():
        return redirect("/login")

    material = request.form["material"]
    cantidad = int(request.form["cantidad"])

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute("SELECT cantidad FROM inventario WHERE material = ?", (material,))
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

# -------------------------
# REPORTE EXCEL
# -------------------------
@app.route("/reporte")
def reporte():

    if not login_required():
        return redirect("/login")

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute("SELECT material, cantidad FROM inventario")
    datos = cursor.fetchall()

    conn.close()

    df = pd.DataFrame(datos, columns=["Material", "Cantidad"])
    df.to_excel("reporte_inventario.xlsx", index=False)

    return "<h3>📊 Reporte generado</h3><a href='/'>Volver</a>"

# -------------------------
# FUTURO QR (BASE LISTA)
# -------------------------
@app.route("/qr_entrada/<codigo>/<int:cantidad>")
def qr_entrada(codigo, cantidad):

    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()

    cursor.execute("SELECT cantidad FROM inventario WHERE codigo = ?", (codigo,))
    r = cursor.fetchone()

    if r:
        nueva = r[0] + cantidad
        cursor.execute(
            "UPDATE inventario SET cantidad = ? WHERE codigo = ?",
            (nueva, codigo)
        )

    conn.commit()
    conn.close()

    return jsonify({"mensaje": "entrada QR registrada"})

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
