import streamlit as st
import pandas as pd
from datetime import datetime
import calculos

# 1. Configuracion de pagina basica
st.set_page_config(
    page_title="GenMol PCR Calculator",
    layout="centered"
)

# 2. Inyeccion de diseño con st.html (Estética Bioluminiscencia Cyber)
st.html("""
    <style>
    /* Fondo principal de la aplicacion (Obsidiana Profundo) */
    .stApp, .stMain, .stAppViewContainer {
        background-color: #0f121d !important;
    }
    
    /* Fondo del panel lateral (Un tono mas suave para generar contraste) */
    [data-testid="stSidebar"] {
        background-color: #161b2c !important;
    }
    
    /* Textos principales y de las metricas (Blanco Nieve ultra legible) */
    h1, h2, h3, h4, p, label, span, .stMarkdown p, [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }
    
    /* Asegurar texto claro para todas las etiquetas de la barra lateral */
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #f8fafc !important;
    }
    
    /* Botones y descargas (Menta Glacial Claro - Resalta un monton con letras oscuras) */
    button {
        background-color: #a7f3d0 !important;
        color: #0f121d !important;
        border: 1px solid #a7f3d0 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px;
    }
    
    /* Efecto Hover al pasar el mouse por los botones (Menta un toque mas intenso) */
    button:hover {
        background-color: #6ee7b7 !important;
        border-color: #6ee7b7 !important;
        color: #0f121d !important;
    }
    
    /* --- TOQUES DE CONTRASTE (Violeta Amatista UV) --- */
    /* Linea inferior y texto de la solapa activa (Tabs) */
    button[data-baseweb="tab"] div[aria-selected="true"] {
        color: #c084fc !important;
    }
    
    /* Lineas divisorias de la aplicacion (st.write("---")) */
    hr {
        border-color: #c084fc !important;
        opacity: 0.5;
    }
    
    /* Texto de las pestañas inactivas (Celeste apagado para mantener jerarquia) */
    button[data-baseweb="tab"] {
        color: #64748b !important;
    }
    
    /* Titulos secundarios de las metricas de resultados */
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    /* Contenedores de informacion especiales (st.info, st.warning) */
    div[data-testid="stNotification"] {
        background-color: #1e293b !important;
        border-left: 5px solid #c084fc !important;
    }
    </style>
""")

# 3. Encabezado institucional de la aplicacion
st.title("GENMOL-PCR: Calculador Web v1.2")
st.markdown("#### *Laboratorio de Genetica Molecular (CONICET - CENPAT)*")
st.write("---")

# 4. Estructuracion en solapas funcionales
tab_mix, tab_ciclado, tab_dilucion = st.tabs([
    "Calculo de Master Mix", 
    "Optimizacion de Ciclado Termico", 
    "Asistente de Diluciones"
])

# --- SOLAPA 1: CALCULO DE MASTER MIX ---
with tab_mix:
    st.sidebar.header("Parametros del Ensayo")
    
    formato_lote = st.sidebar.selectbox(
        "Configuracion rapida de lote:", 
        ["Manual", "Placa 96 pocillos (Completa)", "Placa 384 pocillos (Completa)"]
    )
    
    if formato_lote == "Placa 96 pocillos (Completa)":
        n_muestras = 96
        porcentaje_error_predeterminado = 12.0
    elif formato_lote == "Placa 384 pocillos (Completa)":
        n_muestras = 384
        porcentaje_error_predeterminado = 15.0
    else:
        n_muestras = st.sidebar.number_input("Cantidad de muestras reales:", min_value=1, value=10, step=1)
        porcentaje_error_predeterminado = 10.0

    vol_final = st.sidebar.number_input("Volumen FINAL de PCR por tubo (uL):", min_value=0.1, value=25.0, step=0.5)
    vol_adn = st.sidebar.number_input("Volumen de ADN molde por tubo (uL):", min_value=0.0, value=2.0, step=0.5)
    porcentaje_error = st.sidebar.number_input("Colchon de pipeteo (% error extra):", min_value=0.0, value=porcentaje_error_predeterminado, step=1.0)

    st.sidebar.write("---")
    st.sidebar.header("Configuracion de Reactivos")
    tipo_protocolo = st.sidebar.radio("Selecciona el protocolo:", ["Estandar GenMol", "Personalizado (Carga manual)"])

    if tipo_protocolo == "Personalizado (Carga manual)":
        reactivos = {
            "Buffer PCR (uL)": st.sidebar.number_input("Buffer PCR:", min_value=0.0, value=2.5),
            "dNTPs (uL)": st.sidebar.number_input("dNTPs:", min_value=0.0, value=0.5),
            "Primer Forward (uL)": st.sidebar.number_input("Primer Forward:", min_value=0.0, value=1.0),
            "Primer Reverse (uL)": st.sidebar.number_input("Primer Reverse:", min_value=0.0, value=1.0),
            "Taq Polimerasa (uL)": st.sidebar.number_input("Taq Polimerasa:", min_value=0.0, value=0.2)
        }
    else:
        reactivos = {
            "Buffer PCR (10x)": 2.5,
            "dNTPs (10mM)": 0.5,
            "Primer Forward (10 uM)": 1.0,
            "Primer Reverse (10 uM)": 1.0,
            "Taq Polimerasa": 0.2
        }

    st.sidebar.write("---")
    st.sidebar.header("Aditivos Especiales (Opcional)")
    activar_aditivos = st.sidebar.checkbox("Añadir Co-solventes (Plantillas Complejas)")

    if activar_aditivos:
        tipo_aditivo = st.sidebar.selectbox("Selecciona el aditivo:", ["DMSO", "Glicerol", "Formamida"])
        vol_aditivo = st.sidebar.number_input(f"Volumen de {tipo_aditivo} por tubo (uL):", min_value=0.0, value=1.25, step=0.25)
        if vol_aditivo > 0:
            reactivos[f"Aditivo ({tipo_aditivo})"] = vol_aditivo

    res = calculos.calcular_componentes(n_muestras, vol_final, vol_adn, porcentaje_error, reactivos)

    if res["error"]:
        st.error("[ERROR] RESTRICCION DE VOLUMEN DETECTADA")
        st.warning(f"Motivo: {res['motivo_error']}")
        if "reactivos_fijos" in res:
            st.info(f"La suma de reactivos fijos ({res['reactivos_fijos']} uL) mas el ADN asignado ({vol_adn} uL) excede la capacidad total configurada ({vol_final} uL).")
    else:
        if formato_lote != "Manual":
            st.info(f"Modo automatico activo: Configurado para {formato_lote}")
            
        st.subheader(f"Resultados del Lote (Calculado para {res['n_total_rxs']:.2f} reacciones)")
        
        # Panel metrico principal
        col1, col2, col3 = st.columns(3)
        col1.metric("Volumen Master Mix / Tubo", f"{res['vol_mm_por_tubo']:.2f} uL")
        col2.metric("ADN Template / Tubo", f"{vol_adn:.2f} uL")
        col3.metric("Total Tubo Madre", f"{res['total_tubo_master']:.2f} uL")

        st.markdown("### Tabla de Pipeteo")
        
        datos_tabla = []
        datos_tabla.append({
            "Componente": "Agua libre de nucleasas",
            "1 Tubo (uL)": f"{res['vol_agua_individual']:.2f}",
            f"Master Mix Total (+{porcentaje_error}%)": f"{res['totales_mix']['Agua libre de nucleasas']:.2f} uL"
        })
        
        for comp, vol_ind in reactivos.items():
            datos_tabla.append({
                "Componente": comp,
                "1 Tubo (uL)": f"{vol_ind:.2f}",
                f"Master Mix Total (+{porcentaje_error}%)": f"{res['totales_mix'][comp]:.2f} uL"
            })
        
        df = pd.DataFrame(datos_tabla)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.info(
            f"INSTRUCCIONES DE OPERACION EN MESADA:\n\n"
            f"1. En un tubo de volumen adecuado, armar el Master Mix combinando los volumenes consolidados de la columna 'Master Mix Total' (Total: {res['total_tubo_master']:.2f} uL).\n\n"
            f"2. Homogeneizar por inversion suave y alicuotar {res['vol_mm_por_tubo']:.2f} uL del mix en cada pocillo.\n\n"
            f"3. Incorporar los {vol_adn:.2f} uL de la muestra de ADN de forma independiente por reaccion."
        )

        st.write("---")
        if res["balance_masa_ok"]:
            st.success("CONTROL DE CALIDAD (QA/QC): Balance de masa convergente. Los microvolumenes cierran perfectamente.")
        else:
            st.warning("CONTROL DE CALIDAD (QA/QC): Se detecto un desvio marginal en el redondeo decimal flotante.")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reporte_txt = (
            f"=========================================================\n"
            f"        REPORTE DE MESADA - GENMOL PCR TOOLS\n"
            f"        Fecha y Hora: {timestamp}\n"
            f"=========================================================\n\n"
            f"Muestras: {n_muestras} | Volumen Final: {vol_final} uL | ADN: {vol_adn} uL\n"
            f"Volumen total a armar en Eppendorf Madre: {res['total_tubo_master']:.2f} uL\n"
            f"Fraccionar por pocillo: {res['vol_mm_por_tubo']:.2f} uL de Mix + {vol_adn:.2f} uL de ADN.\n"
        )

        st.download_button(
            label="Descargar Reporte de Lote (.txt)",
            data=reporte_txt,
            file_name=f"pcr_web_reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# --- SOLAPA 2: OPTIMIZACION DE CICLADO TERMICO ---
with tab_ciclado:
    st.subheader("Calculador de Perfil Termico para Termociclador")
    st.markdown("Estima las temperaturas y tiempos clave para la reaccion en base a tus cebadores y secuencia blanco.")
    
    col_tm, col_bp = st.columns(2)
    tm_input = col_tm.number_input("Tm del Primer mas debil (Grados C):", min_value=20.0, max_value=85.0, value=60.0, step=0.5)
    bp_input = col_bp.number_input("Longitud esperada del amplicon (Pares de bases - bp):", min_value=50, max_value=10000, value=500, step=50)
    
    ciclado_res = calculos.calcular_parametros_ciclado(tm_input, bp_input)
    
    st.write("---")
    st.markdown("### Perfil de Termociclador Recomendado (Polimerasa Estandar)")
    
    st.code(
        f"1. Desnaturalizacion Inicial : 95 C por 3:00 minutos\n"
        f"2. Desnaturalizacion (Ciclos): 95 C por 0:30 segundos\n"
        f"3. Anillamiento (Annealing)  : {ciclado_res['ta']} C por 0:30 segundos\n"
        f"4. Extension (Ciclos)       : 72 C por {ciclado_res['tiempo_ext_seg']} segundos\n"
        f"5. Extension Final          : 72 C por 5:00 minutos",
        language="text"
    )

# --- SOLAPA 3: ASISTENTE DE DILUCIONES ---
with tab_dilucion:
    st.subheader("Calculadora de Concentraciones (C1 * V1 = C2 * V2)")
    st.markdown("Usa esta herramienta para calcular el volumen individual de algun reactivo antes de cargarlo a la par.")
    
    col_c1, col_c2, col_v2 = st.columns(3)
    c_stock = col_c1.number_input("Concentracion Stock (C1):", min_value=0.0, value=10.0, key="c1_tab")
    c_final = col_c2.number_input("Concentracion Final (C2):", min_value=0.0, value=0.4, key="c2_tab")
    v_target = col_v2.number_input("Volumen Final Tubo (V2 - uL):", min_value=0.0, value=25.0, key="v2_tab")
    
    v1_calculado = calculos.calcular_volumen_dilucion(c_stock, c_final, v_target)
    if v1_calculado > 0:
        st.success(f"Resultado: Necesitas agregar exactamente {v1_calculado:.2f} uL del stock por cada tubo.")
    else:
        st.warning("Verifica los valores: la concentracion final no puede superar a la concentracion stock.")
