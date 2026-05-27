import utils
import calculos
from typing import Dict, Any

def configurar_reactivos() -> Dict[str, float]:
    """
    Gestiona la interfaz de selección de reactivos moleculares.
    Permite alternar entre el estándar operativo de GenMol o la carga de 
    un protocolo modificado manteniendo la integridad de las unidades (uL).
    """
    print("\n[?] CONFIGURACIÓN DE REACTIVOS (Volumen por reacción):")
    print(" 1. Usar volúmenes estándar de GenMol (Buffer 10x, dNTPs, Primers, Taq)")
    print(" 2. Ingresar volúmenes personalizados (Protocolo alternativo)")
    opcion = utils.obtener_numero("Seleccioná una opción (1 o 2): ", tipo=int, minimo=1)
    
    if opcion == 2:
        print("\n--- CONFIGURACIÓN PERSONALIZADA (Carga de Microvolúmenes) ---")
        return {
            "Buffer PCR (uL)": utils.obtener_numero("• Buffer PCR (uL): ", minimo=0.0),
            "dNTPs (uL)": utils.obtener_numero("• dNTPs (uL): ", minimo=0.0),
            "Primer Forward (uL)": utils.obtener_numero("• Primer Forward (uL): ", minimo=0.0),
            "Primer Reverse (uL)": utils.obtener_numero("• Primer Reverse (uL): ", minimo=0.0),
            "Taq Polimerasa (uL)": utils.obtener_numero("• Taq Polimerasa (uL): ", minimo=0.0)
        }
    else:
        # Perfil analítico por defecto del laboratorio GenMol (CONICET-CENPAT)
        return {
            "Buffer PCR (10x)": 2.5,
            "dNTPs (10mM)": 0.5,
            "Primer Forward (10 uM)": 1.0,
            "Primer Reverse (10 uM)": 1.0,
            "Taq Polimerasa": 0.2
        }

def iniciar_programa() -> None:
    """
    Orquestador principal de la aplicación GenMol-PCR Tools.
    Maneja el ciclo de vida de la ejecución, captura flujos, gestiona excepciones
    de volumen físico y acopla los módulos de cálculo y persistencia.
    """
    while True:
        utils.limpiar_pantalla()
        print("============================================================================")
        print("   GENMOL-PCR: CORE ENTORNO DISTRIBUIDO v1.0 (CONICET - CENPAT)             ")
        print("============================================================================\n")
        
        # 1. Captura controlada de variables críticas del ensayo
        n_muestras = utils.obtener_numero("🧬 Cantidad de muestras biológicas a procesar: ", tipo=int, minimo=1)
        vol_final = utils.obtener_numero("🧪 Volumen total FINAL de la PCR por tubo (uL): ", minimo=0.1)
        vol_adn = utils.obtener_numero("💧 Volumen de ADN molde/template asignado por tubo (uL): ", minimo=0.0)
        porcentaje_error = utils.obtener_numero("📉 Colchón de pipeteo - Porcentaje de error extra (ej. 10): ", minimo=0.0)
        
        # 2. Configuración del set de reactivos
        reactivos = configurar_reactivos()
        
        # 3. Procesamiento analítico mediante el módulo matemático estricto
        res = calculos.calcular_componentes(n_muestras, vol_final, vol_adn, porcentaje_error, reactivos)
        
        # 4. Manejo avanzado de excepciones de mesada y volumen
        if res["error"]:
            print("\n❌ ¡ERROR DE CONSISTENCIA EN EL PROTOCOLO!")
            print(f" Motivo: {res['motivo_error']}")
            
            # Desglose específico si el error es por saturación física de masa líquida
            if not res.get("critico", True):
                print(f" • Sumatoria de reactivos cargados: {res.get('reactivos_fijos')} uL")
                print(f" • ADN template a ingresar:         {vol_adn} uL")
                print(f" • Capacidad excedida en el tubo:   {res.get('exceso_uL')} uL por encima del volumen final ({vol_final} uL).")
                
            print("\nOperación interrumpida. Ningún componente fue escalado.")
            input("Presioná Enter para reconfigurar los parámetros de mesada...")
            continue
            
        # 5. Generación y renderizado de outputs formateados
        tabla_str, alertas_str = utils.generar_tabla_y_alertas(n_muestras, porcentaje_error, res, reactivos)
        
        print(f"\n[PROCESAMIENTO EXITOSO] Lote proyectado para {n_muestras} muestras ({res['n_total_rxs']:.2f} reacciones calculadas):")
        print(tabla_str)
        print(alertas_str)
        print("=" * 78)
        
        # 6. Módulo de persistencia y trazabilidad digital
        guardar = input("\n💾 ¿Deseás exportar este registro de lote a un archivo de texto (.txt)? (s/n): ").lower()
        if guardar == 's':
            utils.exportar_reporte(tabla_str, alertas_str, n_muestras)
            
        # 7. Gestión del bucle de continuidad de la aplicación
        print("\n¿Qué acción deseás realizar a continuación?")
        print(" 1. Calcular un nuevo lote de Master Mix")
        print(" 2. Finalizar sesión y cerrar el entorno")
        opcion_final = utils.obtener_numero("Seleccioná una opción (1-2): ", tipo=int, minimo=1)
        
        if opcion_final == 2:
            print("\n👋 Entorno cerrado correctamente. ¡Éxitos en la mesada de GenMol!")
            break

if __name__ == "__main__":
    iniciar_programa()
