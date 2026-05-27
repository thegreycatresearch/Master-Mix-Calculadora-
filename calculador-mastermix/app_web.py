import streamlit as st
import pandas as pd
from datetime import datetime
import calculos

# Configuración inicial de la página web
st.set_page_config(
    page_title="Master Mix Calculadora",
    page_icon="🧬",
    layout="centered"
)

# Encabezado principal de la aplicación
st.title("Master Mix Calculadora v1.0")
st.markdown("#### *Laboratorio de Genética Molecular (CONICET - CENPAT)*")
st.write("---")

# --- SECCIÓN 1: CAPTURA DE DATOS (PANEL IZQUIERDO / LATERAL) ---
st.sidebar.header("Parámetros del Ensayo")

n_muestras = st.sidebar.number_input("Cantidad de muestras reales:", min_value=1, value=10, step=1)
vol_final = st.sidebar.number_input("Volumen FINAL de PCR por tubo (uL):", min_value=0.1, value=25.0, step=0.5)
vol_adn = st.sidebar.number_input("Volumen de ADN molde por tubo (uL):", min_value=0.0, value=2.0, step=0.5)
porcentaje_error = st.sidebar.number_input("Colchón de pipeteo (% error extra):", min_value=0.0, value=10.0, step=1.0)

st.sidebar.write("---")
st.sidebar.header("Configuración de Reactivos")
tipo_protocolo = st.sidebar.radio("Seleccioná el protocolo:", ["Estándar GenMol", "Personalizado (Carga manual)"])

# Definición del diccionario de reactivos según la selección
if tipo_protocolo == "Personalizado (Carga manual)":
    reactivos = {
        "Buffer PCR (uL)": st.sidebar.number_input("• Buffer PCR:", min_value=0.0, value=2.5),
        "dNTPs (uL)": st.sidebar.number_input("• dNTPs:", min_value=0.0, value=0.5),
        "Primer Forward (uL)": st.sidebar.number_input("• Primer Forward:", min_value=0.0, value=1.0),
        "Primer Reverse (uL)": st.sidebar.number_input("• Primer Reverse:", min_value=0.0, value=1.0),
        "Taq Polimerasa (uL)": st.sidebar.number_input("• Taq Polimerasa:", min_value=0.0, value=0.2)
    }
else:
    reactivos = {
        "Buffer PCR (10x)": 2.5,
        "dNTPs (10mM)": 0.5,
        "Primer Forward (10 uM)": 1.0,
        "Primer Reverse (10 uM)": 1.0,
        "Taq Polimerasa": 0.2
    }

# --- SECCIÓN 2: PROCESAMIENTO Y RENDERIZADO ---

# Ejecutamos la lógica matemática de tu archivo calculos.py
res = calculos.calcular_componentes(n_muestras, vol_final, vol_adn, porcentaje_error, reactivos)

if res["error"]:
    st.error("**¡ERROR DE CONSISTENCIA EN EL PROTOCOLO!**")
    st.warning(f"**Motivo:** {res['motivo_error']}")
    if "reactivos_fijos" in res:
        st.info(f"La suma de reactivos ({res['reactivos_fijos']} uL) + ADN ({vol_adn} uL) supera el volumen final configurado ({vol_final} uL).")
else:
    # Si todo está bien, mostramos las métricas clave en tarjetas interactivas
    st.subheader(f"Resultados del Lote (Proyectado para {res['n_total_rxs']:.2f} reacciones)")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Volumen Master Mix / Tubo", f"{res['vol_mm_por_tubo']:.2f} uL")
    col2.metric("ADN Template / Tubo", f"{vol_adn:.2f} uL")
    col3.metric("Total Tubo Madre", f"{res['total_tubo_master']:.2f} uL")

    # --- DISEÑO DE LA TABLA DE VOLÚMENES ---
    st.markdown("### Tabla de Pipeteo")
    
    # Formateamos los datos para meterlos en una tabla limpia de Streamlit
    datos_tabla = []
    # Primero agregamos el agua libre de nucleasas
    datos_tabla.append({
        "Componente": "Agua libre de nucleasas",
        "1 Tubo (uL)": f"{res['vol_agua_individual']:.2f}",
        f"Master Mix Total (+{porcentaje_error}%)": f"{res['totales_mix']['Agua libre de nucleasas']:.2f} uL"
    })
    # Después el resto de los reactivos dinámicos
    for comp, vol_ind in reactivos.items():
        datos_tabla.append({
            "Componente": f"{comp.split(' (')[0]}",
            "1 Tubo (uL)": f"{vol_ind:.2f}",
            f"Master Mix Total (+{porcentaje_error}%)": f"{res['totales_mix'][comp]:.2f} uL"
        })
    
    # Convertimos a DataFrame de Pandas para renderizarlo de forma nativa
    df = pd.DataFrame(datos_tabla)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- CUADRO DE INSTRUCCIONES OPERATIVAS ---
    st.info(
        f"**Instrucciones de Mesada:**\n"
        f"1. En un tubo Eppendorf de 1.5 mL, armá el Master Mix agregando los volúmenes totales de la tabla anterior (Total: **{res['total_tubo_master']:.2f} uL**).\n"
        f"2. Alicuotá **{res['vol_mm_por_tubo']:.2f} uL** de ese mix en cada tubo de la placa/strip.\n"
        f"3. Sumá los **{vol_adn:.2f} uL** de tu muestra de ADN molde de forma independiente por tubo."
    )

    # --- COLOFÓN DE CONTROL DE CALIDAD Y EXPORTACIÓN ---
    st.write("---")
    if res["balance_masa_ok"]:
        st.success("**Control de Calidad (QA/QC):** Balance de masa convergente. Los microvolúmenes cierran perfectamente.")
    else:
        st.warning("**Control de Calidad (QA/QC):** Se detectó un desvío mínimo en el redondeo decimal flotante.")

    # Generación de texto plano para descarga automática del reporte
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reporte_txt = (
        f"=========================================================\n"
        f"        REPORTE DE MESADA - GENMOL PCR TOOLS\n"
        f"        Fecha y Hora: {timestamp}\n"
        f"=========================================================\n\n"
        f"Muestras: {n_muestras} | Volumen Final: {vol_final} uL | ADN: {vol_adn} uL\n\n"
        f"Volumen total a armar en Eppendorf Madre: {res['total_tubo_master']:.2f} uL\n"
        f"Fraccionar por pocillo: {res['vol_mm_por_tubo']:.2f} uL de Mix + {vol_adn:.2f} uL de ADN.\n"
    )

    # Botón de descarga nativo en el navegador
    st.download_button(
        label="Descargar Reporte de Lote (.txt)",
        data=reporte_txt,
        file_name=f"pcr_web_reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
