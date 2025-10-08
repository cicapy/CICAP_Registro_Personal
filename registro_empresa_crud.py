import streamlit as st
import pandas as pd
import os
from datetime import date
import matplotlib.pyplot as plt

# =============================================
# CONFIGURACIÓN DE PÁGINA
# =============================================
st.set_page_config(page_title="CICAP – Sistema de Registro de Personal",
                   page_icon="🟩", layout="centered")

# =============================================
# APLICAR ESTILO OSCURO INSTITUCIONAL
# =============================================
if os.path.exists("assets/style.css"):
    with open("assets/style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =============================================
# BANNER INSTITUCIONAL FIJO
# =============================================
st.markdown("""
<div class="banner-cicap">
    <div class="banner-text">
        <b>🟩 Centro de Investigación y Capacitación Paraguay – CICAP</b>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================
# ARCHIVOS DE DATOS
# =============================================
ARCHIVO_EXCEL = "data/registros_personal.xlsx"
ARCHIVO_USUARIOS = "data/usuarios.xlsx"
CARPETA_DOCS = "data/documentos"
os.makedirs(CARPETA_DOCS, exist_ok=True)

# =============================================
# FUNCIONES AUXILIARES
# =============================================
def cargar_datos():
    if os.path.exists(ARCHIVO_EXCEL):
        return pd.read_excel(ARCHIVO_EXCEL)
    return pd.DataFrame(columns=[
        "ID", "Fecha de Registro", "Nombre", "CI/RUC", "Cargo",
        "Departamento", "Teléfono", "Correo", "Fecha de Ingreso",
        "Observaciones", "Archivo", "Registrado por"
    ])

def guardar_datos(df):
    df.to_excel(ARCHIVO_EXCEL, index=False)

def cargar_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        return pd.read_excel(ARCHIVO_USUARIOS)
    df = pd.DataFrame([{"Usuario": "admin", "Contraseña": "1234"}])
    df.to_excel(ARCHIVO_USUARIOS, index=False)
    return df

def guardar_usuarios(df):
    df.to_excel(ARCHIVO_USUARIOS, index=False)

def generar_id(df):
    if "ID" not in df.columns or df["ID"].dropna().empty:
        return 1
    return int(df["ID"].dropna().max() + 1)

# =============================================
# CARGAR DATOS
# =============================================
df = cargar_datos()
usuarios = cargar_usuarios()

# =============================================
# CONTROL DE SESIÓN
# =============================================
if "logueado" not in st.session_state:
    st.session_state.logueado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# =============================================
# ENCABEZADO PRINCIPAL
# =============================================
st.markdown("""
<h1 style='text-align: center; color: #1fa14a; font-weight: 800;
text-shadow: 1px 1px 2px rgba(0,0,0,0.25); letter-spacing: 0.5px; margin-top: 80px;'>
🟩 CICAP – Sistema de Registro de Personal
</h1>
""", unsafe_allow_html=True)

# =============================================
# LOGIN / REGISTRO DE USUARIO
# =============================================
if not st.session_state.logueado:
    tab1, tab2 = st.tabs(["🔑 Iniciar sesión", "📝 Crear usuario"])

    with tab1:
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if u in usuarios["Usuario"].values:
                clave = usuarios.loc[usuarios["Usuario"] == u, "Contraseña"].values[0]
                if str(p).strip() == str(clave).strip():
                    st.session_state.logueado = True
                    st.session_state.usuario = u
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta.")
            else:
                st.error("⚠️ Usuario no encontrado.")

    with tab2:
        nu = st.text_input("Nuevo usuario")
        npw = st.text_input("Nueva contraseña", type="password")
        cnpw = st.text_input("Confirmar contraseña", type="password")
        if st.button("Registrar"):
            if nu and npw and npw == cnpw:
                if nu not in usuarios["Usuario"].values:
                    usuarios = pd.concat([
                        usuarios,
                        pd.DataFrame([[nu, npw]], columns=["Usuario", "Contraseña"])
                    ], ignore_index=True)
                    guardar_usuarios(usuarios)
                    st.success("✅ Usuario creado correctamente.")
                else:
                    st.warning("⚠️ El usuario ya existe.")
            else:
                st.warning("❌ Datos incompletos o contraseñas no coinciden.")

# =============================================
# APLICACIÓN PRINCIPAL
# =============================================
else:
    st.sidebar.success(f"👋 Sesión: {st.session_state.usuario}")
    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state.logueado = False
        st.session_state.usuario = ""
        st.rerun()

    menu = st.sidebar.radio("Menú", [
        "➕ Registrar",
        "📋 Ver registros",
        "✏️ Editar",
        "🗑️ Eliminar",
        "📈 Estadísticas"
    ])

    # ----------------------------------------------------------
    # REGISTRAR
    # ----------------------------------------------------------
    if menu == "➕ Registrar":
        st.subheader("➕ Registrar nuevo empleado")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre completo")
            ci = st.text_input("Cédula o RUC")
            cargo = st.text_input("Cargo o puesto")
            depto = st.selectbox("Departamento", [
                "", "Administración", "Ventas", "Producción",
                "RRHH", "Contabilidad", "Otros"
            ])
        with c2:
            tel = st.text_input("Teléfono")
            mail = st.text_input("Correo electrónico")
            fin = st.date_input("Fecha de ingreso", value=date.today())
            obs = st.text_area("Observaciones")
        archivo = st.file_uploader("📎 Subir archivo (opcional)", type=["jpg", "jpeg", "png", "pdf"])

        if st.button("💾 Guardar registro"):
            if nombre.strip() == "":
                st.warning("⚠️ El nombre es obligatorio.")
            else:
                idn = generar_id(df)
                ruta = ""
                if archivo:
                    ruta = os.path.join(CARPETA_DOCS, f"{idn}_{archivo.name}")
                    with open(ruta, "wb") as f:
                        f.write(archivo.getbuffer())
                nuevo = pd.DataFrame([{
                    "ID": idn,
                    "Fecha de Registro": date.today().strftime("%Y-%m-%d"),
                    "Nombre": nombre,
                    "CI/RUC": ci,
                    "Cargo": cargo,
                    "Departamento": depto,
                    "Teléfono": tel,
                    "Correo": mail,
                    "Fecha de Ingreso": fin.strftime("%Y-%m-%d"),
                    "Observaciones": obs,
                    "Archivo": ruta,
                    "Registrado por": st.session_state.usuario
                }])
                df = pd.concat([df, nuevo], ignore_index=True)
                guardar_datos(df)
                st.success(f"✅ Registro guardado por {st.session_state.usuario}.")

    # ----------------------------------------------------------
    # VER REGISTROS
    # ----------------------------------------------------------
    elif menu == "📋 Ver registros":
        st.subheader("📋 Lista de empleados registrados")
        if df.empty:
            st.info("Aún no hay registros.")
        else:
            b = st.text_input("🔍 Buscar:")
            if b:
                f = df[df.apply(lambda x: x.astype(str).str.contains(b, case=False, na=False)).any(axis=1)]
                st.dataframe(f, use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)

    # ----------------------------------------------------------
    # EDITAR
    # ----------------------------------------------------------
    elif menu == "✏️ Editar":
        st.subheader("✏️ Editar registro existente")
        if not df.empty:
            s = st.selectbox("Seleccione un empleado:", df["Nombre"].tolist())
            fila = df[df["Nombre"] == s].iloc[0]
            n = st.text_input("Nombre", fila["Nombre"])
            c = st.text_input("Cargo", fila["Cargo"])
            if st.button("Actualizar"):
                df.loc[df["Nombre"] == s, "Nombre"] = n
                df.loc[df["Nombre"] == s, "Cargo"] = c
                guardar_datos(df)
                st.success("✅ Registro actualizado correctamente.")

    # ----------------------------------------------------------
    # ELIMINAR
    # ----------------------------------------------------------
    elif menu == "🗑️ Eliminar":
        st.subheader("🗑️ Eliminar registro")
        if not df.empty:
            s = st.selectbox("Seleccione:", df["Nombre"].tolist())
            if st.button("Eliminar"):
                df = df[df["Nombre"] != s]
                guardar_datos(df)
                st.warning(f"⚠️ Registro de {s} eliminado correctamente.")

    # ----------------------------------------------------------
    # ESTADÍSTICAS
    # ----------------------------------------------------------
    elif menu == "📈 Estadísticas":
        st.subheader("📊 Estadísticas")
        if df.empty:
            st.info("No hay datos para mostrar.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Registros por usuario:**")
                fig, ax = plt.subplots()
                df["Registrado por"].value_counts().plot(kind="bar", ax=ax, color="#1fa14a")
                st.pyplot(fig)
            with c2:
                st.write("**Registros por departamento:**")
                fig2, ax2 = plt.subplots()
                df["Departamento"].value_counts().plot(kind="bar", ax=ax2, color="#27ae60")
                st.pyplot(fig2)
