import os
import sys

# Parche de rutas para evitar el error 'Not Found' en el ejecutable compilado
if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
    sys.path.append(sys._MEIPASS)
else:
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    os.chdir(ruta_actual)
    sys.path.append(ruta_actual)

# ... (Acá abajo sigue todo tu código de Streamlit normal, con tus imports de streamlit, pandas, etc.)

# 1. Configuración de página básica
st.set_page_config(
    page_title="Asistente Digital de PCR",
    layout="centered"
)

# 2. Inyección de diseño con st.html (Estética Claridad Molecular)
st.html("""
    <style>
    /* Ocultar la barra superior de decoración y el encabezado por defecto */
    [data-testid="stHeader"], header, .stDecoration {
        display: none !important;
        height: 0px !important;
        opacity: 0 !important;
    }
    
    /* Ajustar el espacio superior para compensar la falta de encabezado */
    .block-container {
        padding-top: 2rem !important;
    }

    /* Fondo principal de la aplicación (Gris Platino Claro) */
    .stApp, .stMain, .stAppViewContainer {
        background-color: #f4f6f9 !important;
    }
    
    /* Fondo del panel lateral (Azul Hielo tenue para separar secciones) */
    [data-testid="stSidebar"] {
        background-color: #e5ecf4 !important;
    }
    
    /* TODAS las letras del sistema en color Negro Absoluto (Máxima legibilidad) */
    h1, h2, h3, h4, p, label, span, .stMarkdown p, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #000000 !important;
    }
    
    /* Forzar texto negro también dentro de la barra lateral */
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #000000 !important;
    }
    
    /* Botones y descargas (Violeta Pastel Claro con letras NEGRAS para que resalten) */
    button {
        background-color: #e9d5ff !important;
        color: #000000 !important;
        border: 2px solid #c084fc !important; /* Borde violeta UV */
        border-radius: 8px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px;
        transition: all 0.2s ease !important;
    }
    
    /* Efecto Hover al pasar el mouse por los botones */
    button:hover {
        background-color: #d8b4fe !important;
        border-color: #a855f7 !important;
        color: #000000 !important;
    }
    
    /* --- TOQUES DE CONTRASTE (Violeta Amatista UV) --- */
    /* Línea inferior y texto de la solapa activa (Tabs) */
    button[data-baseweb="tab"] div[aria-selected="true"] {
        color: #a855f7 !important;
        font-weight: 700 !important;
    }
    
    /* Líneas divisorias de la aplicación (st.write("---")) */
    hr {
        border-color: #a855f7 !important;
        opacity: 0.6;
    }
    
    /* Texto de las pestañas inactivas (Gris oscuro para mantener la jerarquía) */
    button[data-baseweb="tab"] {
        color: #475569 !important;
    }
    
    /* Contenedores de información especiales (st.info, st.warning, st.error) */
    div[data-testid="stNotification"] {
        background-color: #ffffff !important;
        border-left: 5px solid #a855f7 !important;
        border-top: 1px solid #e2e8f0 !important;
        border-right: 1px solid #e2e8f0 !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    </style>
""")

# 3. Encabezado institucional de la aplicación
st.title("Asistente Digital de PCR")
st.markdown("#### *Herramienta analítica para la preparación, validación y optimización de ensayos moleculares*")
st.write("---")

# 4. Estructuración en solapas funcionales
tab_mix, tab_ciclado, tab_dilucion, tab_diagnostico = st.tabs([
    "Cálculo de Master Mix", 
    "Optimización de Ciclado Térmico", 
    "Asistente de Diluciones",
    "Diagnóstico y Optimización"
])

# --- SOLAPA 1: CALCULO DE MASTER MIX ---
with tab_mix:
    st.sidebar.header("Parámetros del Ensayo")
    
    formato_lote = st.sidebar.selectbox(
        "Configuración rápida de lote:", 
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
    porcentaje_error = st.sidebar.number_input("Margen de pipeteo (% error extra):", min_value=0.0, value=porcentaje_error_predeterminado, step=1.0)

    st.sidebar.write("---")
    st.sidebar.header("Configuración de Reactivos")
    tipo_protocolo = st.sidebar.radio("Seleccione el protocolo:", ["Configuración Estándar", "Personalizado (Carga manual)"])

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
    activar_aditivos = st.sidebar.checkbox("Añadir co-solventes (Plantillas complejas)")

    if activar_aditivos:
        tipo_aditivo = st.sidebar.selectbox("Seleccione el aditivo:", ["DMSO", "Glicerol", "Formamida"])
        vol_aditivo = st.sidebar.number_input(f"Volumen de {tipo_aditivo} por tubo (uL):", min_value=0.0, value=1.25, step=0.25)
        if vol_aditivo > 0:
            reactivos[f"Aditivo ({tipo_aditivo})"] = vol_aditivo

    res = calculos.calcular_componentes(n_muestras, vol_final, vol_adn, porcentaje_error, reactivos)

    if res["error"]:
        st.error("RESTRICCIÓN DE VOLUMEN DETECTADA")
        st.warning(f"Motivo: {res['motivo_error']}")
        if "reactivos_fijos" in res:
            st.info(f"La suma de reactivos fijos ({res['reactivos_fijos']} uL) más el ADN asignado ({vol_adn} uL) excede la capacidad total configurada ({vol_final} uL).")
    else:
        if formato_lote != "Manual":
            st.info(f"Modo automático activo: Configurado para {formato_lote}")
            
        st.subheader(f"Resultados del Lote (Calculado para {res['n_total_rxs']:.2f} reacciones)")
        
        # Panel métrico principal
        col1, col2, col3 = st.columns(3)
        col1.metric("Volumen Master Mix / Tubo", f"{res['vol_mm_por_tubo']:.2f} uL")
        col2.metric("ADN Template / Tubo", f"{vol_adn:.2f} uL")
        col3.metric("Total Tubo Madre", f"{res['total_tubo_master']:.2f} uL")

        # --- SECCIÓN NUEVA: AUDITORÍA DE VIABILIDAD EN MESADA (REALISMO) ---
        reactivos_criticos = []
        for comp, vol_tot in res['totales_mix'].items():
            if vol_tot < 1.0 and comp != "Agua libre de nucleasas":
                reactivos_criticos.append((comp, vol_tot))
        
        if reactivos_criticos:
            with st.container():
                st.warning(
                    "ALERTA DE VIABILIDAD TÉCNICA: Se han detectado volúmenes de pipeteo críticamente bajos en el tubo madre. "
                    "Para asegurar la reproducibilidad real en mesada, considere las siguientes recomendaciones:"
                )
                for item, vol in reactivos_criticos:
                    st.markdown(f"- **{item}**: El volumen consolidado es de solo {vol:.2f} uL. Pipetear menos de 1 uL introduce un error experimental elevado. Se sugiere incrementar el número de muestras reflejadas, elevar el margen de pipeteo, o realizar una predilución 1:10 del stock del reactivo.")
                st.write("")

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

        # --- SECCIÓN NUEVA: CONTROL DE CONCENTRACIONES FINALES TEÓRICAS ---
        with st.expander("Verificar Concentraciones Finales de la Reacción"):
            st.markdown("Auditoría analítica de la solución final en base a reactivos comerciales estándar:")
            c_buffer = (reactivos.get("Buffer PCR (10x)", 2.5) / vol_final) * 10 if "Buffer PCR (10x)" in reactivos else 1.0
            c_dntps = (reactivos.get("dNTPs (10mM)", 0.5) / vol_final) * 10 if "dNTPs (10mM)" in reactivos else 0.2
            c_fwd = (reactivos.get("Primer Forward (10 uM)", 1.0) / vol_final) * 10 if "Primer Forward (10 uM)" in reactivos else 0.4
            c_rev = (reactivos.get("Primer Reverse (10 uM)", 1.0) / vol_final) * 10 if "Primer Reverse (10 uM)" in reactivos else 0.4
            
            st.markdown(f"- **Concentración de Buffer:** {c_buffer:.2f}X *(Rango óptimo: 1X)*")
            st.markdown(f"- **Concentración de dNTPs totales:** {c_dntps:.2f} mM *(Rango óptimo: 0.2 - 0.25 mM)*")
            st.markdown(f"- **Concentración de Cebador Forward:** {c_fwd:.2f} uM *(Rango óptimo: 0.1 - 0.5 uM)*")
            st.markdown(f"- **Concentración de Cebador Reverse:** {c_rev:.2f} uM *(Rango óptimo: 0.1 - 0.5 uM)*")

        st.info(
            f"Guía de operación en mesada:\n\n"
            f"1. En un tubo de volumen adecuado, prepare el Master Mix combinando los volúmenes consolidados de la columna 'Master Mix Total' (Volumen total: {res['total_tubo_master']:.2f} uL).\n\n"
            f"2. Homogeneice por inversión suave y alícuote {res['vol_mm_por_tubo']:.2f} uL de la mezcla en cada pocillo.\n\n"
            f"3. Incorpore los {vol_adn:.2f} uL de la muestra de ADN de forma independiente en cada reacción."
        )

        st.write("---")
        if res["balance_masa_ok"]:
            st.success("Control de calidad: Balance de masa convergente. Los microvolúmenes coinciden correctamente.")
        else:
            st.warning("Control de calidad: Se detectó un desvío marginal en el redondeo decimal.")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reporte_txt = (
            f"=========================================================\n"
            f"        REPORTE DE PREPARACIÓN DE REACCIONES\n"
            f"        Fecha y Hora: {timestamp}\n"
            f"=========================================================\n\n"
            f"Muestras: {n_muestras} | Volumen Final: {vol_final} uL | ADN: {vol_adn} uL\n"
            f"Volumen total a preparar en tubo madre: {res['total_tubo_master']:.2f} uL\n"
            f"Distribución por pocillo: {res['vol_mm_por_tubo']:.2f} uL de Mix + {vol_adn:.2f} uL de ADN.\n"
        )

        st.download_button(
            label="Descargar Reporte de Lote (.txt)",
            data=reporte_txt,
            file_name=f"reporte_pcr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# --- SOLAPA 2: OPTIMIZACION DE CICLADO TERMICO ---
with tab_ciclado:
    st.subheader("Estimación de Perfil para Termociclador")
    st.markdown("Cálculo aproximado de las temperaturas y tiempos clave para la reacción en base a las propiedades de los cebadores y el amplicón.")
    
    col_tm, col_bp = st.columns(2)
    tm_input = col_tm.number_input("Tm del cebador con menor estabilidad (Grados C):", min_value=20.0, max_value=85.0, value=60.0, step=0.5)
    bp_input = col_bp.number_input("Longitud esperada del amplicón (Pares de bases - bp):", min_value=50, max_value=10000, value=500, step=50)
    
    ciclado_res = calculos.calcular_parametros_ciclado(tm_input, bp_input)
    
    st.write("---")
    st.markdown("### Perfil de Ciclado Recomendado (Polimerasa Estándar)")
    
    st.code(
        f"1. Desnaturalización Inicial : 95 C por 3:00 minutos\n"
        f"2. Desnaturalización (Ciclos): 95 C por 0:30 segundos\n"
        f"3. Anillamiento (Annealing)  : {ciclado_res['ta']} C por 0:30 segundos\n"
        f"4. Extensión (Ciclos)        : 72 C por {ciclado_res['tiempo_ext_seg']} segundos\n"
        f"5. Extensión Final           : 72 C por 5:00 minutos",
        language="text"
    )

# --- SOLAPA 3: ASISTENTE DE DILUCIONES ---
with tab_dilucion:
    st.subheader("Cálculo de Diluciones (C1 * V1 = C2 * V2)")
    st.markdown("Herramienta para determinar el volumen de reactivo stock necesario para alcanzar la concentración requerida.")
    
    col_c1, col_c2, col_v2 = st.columns(3)
    c_stock = col_c1.number_input("Concentración Stock (C1):", min_value=0.0, value=10.0, key="c1_tab")
    c_final = col_c2.number_input("Concentración Final (C2):", min_value=0.0, value=0.4, key="c2_tab")
    v_target = col_v2.number_input("Volumen Final del Tubo (V2 - uL):", min_value=0.0, value=25.0, key="v2_tab")
    
    v1_calculado = calculos.calcular_volumen_dilucion(c_stock, c_final, v_target)
    if v1_calculado > 0:
        st.success(f"Resultado: Es necesario añadir exactamente {v1_calculado:.2f} uL del reactivo stock por cada tubo.")
    else:
        st.warning("Verifique las variables introducidas: la concentración final no puede ser superior a la concentración del stock.")

# --- SOLAPA 4: NUEVA SOLAPA DE DIAGNÓSTICO (TROUBLESHOOTING) ---
with tab_diagnostico:
    st.subheader("Asistente de Optimización y Resolución de Problemas")
    st.markdown(
        "Si los resultados empíricos obtenidos en el ensayo no coinciden con las predicciones del modelo teórico, "
        "seleccione el patrón observado en el gel de electroforesis para acceder a las pautas de ajuste físico-químico:"
    )
    
    patron = st.selectbox(
        "Patrón anómalo observado en el gel de agarosa:",
        [
            "Seleccione una opción...",
            "Ausencia total de amplificación (No se observan bandas)",
            "Presencia de bandas inespecíficas (Bandas secundarias múltiples)",
            "Dímeros de cebadores (Bandas intensas de muy bajo peso molecular)",
            "Arrastre o degradación del amplicón (Efecto Smear en el carril)"
        ]
    )
    
    st.write("---")
    
    if patron == "Ausencia total de amplificación (No se observan bandas)":
        st.markdown("### Recomendaciones para Ausencia de Señal:")
        st.markdown("1. **Temperatura de Anillamiento (Ta):** Es posible que la temperatura calculada sea excesivamente restrictiva para la cinética de hibridación. Reduzca la Ta calculada en la Solapa 2 en intervalos de 2 °C.")
        st.markdown("2. **Calidad del ADN Molde:** La presencia de inhibidores de la polimerasa (sales, etanol) puede bloquear la reacción. Pruebe una dilución 1:10 o 1:100 de la muestra de ADN molde.")
        st.markdown("3. **Concentración de MgCl2:** Si está utilizando un protocolo personalizado, verifique que la concentración final de magnesio no sea inferior a 1.5 mM, ya que actúa como cofactor esencial de la enzima.")
        
    elif patron == "Presencia de bandas inespecíficas (Bandas secundarias múltiples)":
        st.markdown("### Recomendaciones para Bandas Inespecíficas:")
        st.markdown("1. **Incremento de Rigurosidad Térmica:** La temperatura de anillamiento actual es demasiado baja, permitiendo uniones inespecíficas en regiones parcialmente homólogas. Aumente la Ta de la Solapa 2 entre 1 °C y 3 °C.")
        st.markdown("2. **Reducción de Ciclos:** Disminuya el número de ciclos del termociclador (por ejemplo, de 35 a 30) para evitar la amplificación tardía de artefactos de fondo.")
        st.markdown("3. **Cebadores:** Reduzca la concentración final de los cebadores a 0.2 uM para disminuir la probabilidad de interacciones secundarias.")
        
    elif patron == "Dímeros de cebadores (Bandas intensas de muy bajo peso molecular)":
        st.markdown("### Recomendaciones para Dímeros de Cebadores:")
        st.markdown("1. **Cinética de Hibridación:** Ocurre cuando los cebadores tienen complementariedad en sus extremos 3'. Incremente la temperatura de anillamiento para desestabilizar estas estructuras débiles.")
        st.markdown("2. **Disminución de Concentración:** Reduzca el volumen asignado a los cebadores en la Solapa 1. Concentraciones superiores a 0.5 uM favorecen la autohibridación por sobre la unión a la secuencia blanco.")
        st.markdown("3. **Hot-Start:** Considere el uso de una polimerasa de tipo 'Hot-Start' para evitar la extensión de dímeros formados a temperatura ambiente durante la preparación de la mezcla.")
        
    elif patron == "Arrastre o degradación del amplicón (Efecto Smear en el carril)":
        st.markdown("### Recomendaciones para Efecto Arrastre (Smear):")
        st.markdown("1. **Exceso de ADN Molde:** Una cantidad desproporcionada de templado interfiere con la migración y agota prematuramente los dNTPs. Reduzca el volumen de ADN molde a 1 uL o realice una predilución.")
        st.markdown("2. **Actividad Enzimática Excesiva:** Demasiadas unidades de Taq polimerasa pueden generar extensiones aberrantes. Ajuste el volumen de la enzima al límite inferior recomendado (0.1 uL a 0.2 uL por tubo).")
        st.markdown("3. **Degradación:** Asegúrese de trabajar en condiciones libres de nucleasas externas y mantenga los reactivos estrictamente en cadena de frío.")
    else:
        st.info("Seleccione un patrón del menú desplegable para desplegar las sugerencias de optimización fisicoquímica.")
