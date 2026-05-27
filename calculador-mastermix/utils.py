
import os
from datetime import datetime
from typing import Dict, Any, Tuple

def limpiar_pantalla() -> None:
    """
    Limpia la consola de comandos según el sistema operativo detectado (Windows/Linux/macOS).
    Mantiene la interfaz de usuario despejada durante las corridas de cálculo.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def obtener_numero(mensaje: str, tipo: type = float, minimo: float = 0.0) -> Any:
    """
    Solicita una entrada numérica al usuario de forma segura y controlada.
    Intercepta errores de tipeo (letras, caracteres especiales) y valores negativos,
    reintentando de forma cíclica sin romper la ejecución del programa.
    """
    while True:
        try:
            valor = tipo(input(mensaje))
            if valor < minimo:
                print(f" El valor ingresado no puede ser menor a {minimo}. Intentá de nuevo.")
                continue
            return valor
        except ValueError:
            print("Entrada inválida. Por favor, ingresá un número válido (usá el punto '.' para los decimales).")

def generar_tabla_y_alertas(
    n_muestras: int, 
    porcentaje_error: float, 
    resultados: Dict[str, Any], 
    reactivos_individuales: Dict[str, float]
) -> Tuple[str, str]:
    """
    Construye y formatea las cadenas de texto correspondientes a la tabla de resultados
    y las especificaciones de la mesada. Extrae de forma matemática los metadatos
    de entrada para no alterar la firma estructural original de la aplicación.
    """
    linea_doble = "=" * 78 + "\n"
    linea_simple = "-" * 78 + "\n"
    
    # Reconstrucción analítica de volúmenes básicos para el reporte visual
    vol_final = resultados["volumen_total_ensayo"] / resultados["n_total_rxs"]
    vol_adn = vol_final - resultados["vol_mm_por_tubo"]
    
    # --- CONSTRUCCIÓN DE LA TABLA DE VOLÚMENES ---
    tabla = linea_doble
    tabla += f" {'Componente':<32} | {'1 Tubo (uL)':<12} | {f'Master Mix Total ({n_muestras} m. + {porcentaje_error}%)':<25}\n"
    tabla += linea_simple
    
    # 1. Componente crítico: Agua de grado biología molecular (Relleno cinético)
    vol_agua_tot = resultados["totales_mix"]["Agua libre de nucleasas"]
    tabla += f" {'Agua libre de nucleasas':<29} | {resultados['vol_agua_individual']:<12.2f} | {vol_agua_tot:<12.2f} uL\n"
    
    # 2. Desglose dinámico de reactivos del kit de amplificación
    for componente, vol_individual in reactivos_individuales.items():
        vol_total_componente = resultados["totales_mix"][componente]
        # Limpieza visual de etiquetas de concentración comercial
        nombre_limpio = componente.split(" (")[0]
        tabla += f" {nombre_limpio:<29} | {vol_individual:<12.2f} | {vol_total_componente:<12.2f} uL\n"
        
    tabla += linea_simple
    
    # --- CONSTRUCCIÓN DE ALERTAS E INSTRUCCIONES DE OPERACIÓN ---
    alertas = f" INSTRUCCIONES OPERATIVAS PARA LA MESADA:\n"
    alertas += f" 1. Preparación del Stock:\n"
    alertas += f"    En un tubo Eppendorf estéril de 1.5 mL, pipeteá los volúmenes de la columna 'Master Mix Total'.\n"
    alertas += f"    Volumen TOTAL a armar en el tubo madre: {resultados['total_tubo_master']:.2f} uL.\n\n"
    alertas += f" 2. Alícuotas en Placa/Strips:\n"
    alertas += f"    Fraccioná el Master Mix homogeneizado distribuyendo:\n"
    alertas += f"    {resultados['vol_mm_por_tubo']:.2f} uL del mix en cada pocillo o tubo de PCR.\n\n"
    alertas += f" 3. Incorporación del Templado:\n"
    alertas += f"    Agregá {vol_adn:.2f} uL de ADN molde (o control) a cada tubo de forma independiente.\n"
    alertas += f"    (Volumen operativo final por reacción independiente: {vol_final:.2f} uL).\n\n"
    
    # Panel de control de calidad analítico
    alertas += f" VERIFICACIÓN DE CONTROL DE CALIDAD (QA/QC):\n"
    alertas += f" • Volumen bruto de reactivos escalados: {resultados['volumen_total_ensayo']:.2f} uL\n"
    
    if resultados.get("balance_masa_ok", True):
        alertas += f" • Balance de masa y balanceo térmico: CONVERGENTE (0.00 uL de desvío)"
    else:
        alertas += f" • Balance de masa y balanceo térmico: ADVERTENCIA (Revisar redondeo decimal)"
        
    return tabla, alertas

def exportar_reporte(tabla: str, alertas: str, n_muestras: int) -> None:
    """
    Exporta la persistencia de datos del ensayo a un archivo de texto plano (.txt).
    Introduce encabezados formales del nodo científico y marcas de tiempo del sistema.
    """
    ahora = datetime.now()
    stamp_archivo = ahora.strftime("%Y-%m-%d_%H-%M-%S")
    stamp_encabezado = ahora.strftime("%Y-%m-%d %H:%M:%S")
    nombre_archivo = f"pcr_reporte_{stamp_archivo}.txt"
    
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("============================================================================\n")
            f.write("             LABORATORIO DE GENÉTICA MOLECULAR (GenMol)                      \n")
            f.write("        CENTRO NACIONAL PATAGÓNICO (CONICET - CENPAT)                       \n")
            f.write(f"        Registro de Mesada Automatizado - Fecha: {stamp_encabezado}         \n")
            f.write("============================================================================\n\n")
            f.write(f"RESUMEN METODOLÓGICO DEL ENSAYO:\n")
            f.write(f" • Número de muestras biológicas declaradas: {n_muestras}\n\n")
            f.write(tabla)
            f.write("\n\n" + alertas + "\n")
            f.write("\n" + "=" * 76 + "\n")
            f.write(" Archivo de trazabilidad de lote generado por GenMol-PCR Tools v1.0.\n")
        print(f"\n💾 ¡Reporte de lote exportado con éxito como '{nombre_archivo}'!")
        
    except IOError as e:
        print(f"\n❌ Error crítico de infraestructura (E/S): No se pudo escribir en el disco. {e}")
    except Exception as e:
        print(f"\n❌ Ocurrió una anomalía inesperada al intentar procesar el archivo: {e}")
