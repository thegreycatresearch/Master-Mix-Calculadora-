from typing import Dict, Any, Tuple

def calcular_volumen_dilucion(c_stock: float, c_final: float, v_final: float) -> float:
    """
    Calcula el volumen necesario de un stock concentrado usando la ecuacion C1*V1 = C2*V2.
    Retorna el volumen V1 en microlitros (uL) requerido por reaccion.
    """
    if c_stock <= 0 or c_final <= 0 or v_final <= 0:
        return 0.0
    if c_final > c_stock:
        return 0.0
    return (c_final * v_final) / c_stock

def validar_entradas(n_muestras: int, vol_final: float, vol_adn: float, porcentaje_error: float) -> Tuple[bool, str]:
    """
    Valida la consistencia fisica y biologica de los parametros de entrada.
    Evita ejecuciones fallidas o valores fisicamente imposibles en la mesada.
    """
    if n_muestras <= 0:
        return False, "El numero de muestras debe ser mayor o igual a 1."
    if vol_final <= 0:
        return False, "El volumen final de la PCR debe ser un valor positivo."
    if vol_adn < 0:
        return False, "El volumen de ADN molde no puede ser un valor negativo."
    if vol_adn >= vol_final:
        return False, f"El volumen de ADN ({vol_adn} uL) no puede ser igual o mayor al volumen final del tubo ({vol_final} uL)."
    if porcentaje_error < 0:
        return False, "El porcentaje de error de pipeteo no puede ser negativo."
    return True, ""

def calcular_componentes(
    n_muestras: int, 
    vol_final: float, 
    vol_adn: float, 
    porcentaje_error: float, 
    reactivos: Dict[str, float]
) -> Dict[str, Any]:
    """
    Realiza los calculos matematicos avanzados para el lote de Master Mix.
    Incluye tipado estricto, redondeo de precision para pipetas de microvolumen,
    validaciones de seguridad termica y verificacion de balance de masa.
    
    Args:
        n_muestras (int): Cantidad de tubos/muestras reales a procesar.
        vol_final (float): Volumen total final de la reaccion de PCR (uL).
        vol_adn (float): Volumen de ADN molde que se añade de forma independiente por tubo (uL).
        porcentaje_error (float): Porcentaje de exceso para el colchon de pipeteo (ej. 10 para 10%).
        reactivos (dict): Diccionario con {Nombre_Reactivo: Volumen_Individual_uL}.
        
    Returns:
        dict: Resultados del calculo listos para la interfaz o reportes, con flags de error.
    """
    # 1. Control de seguridad inicial sobre parametros basicos
    es_valido, mensaje_error = validar_entradas(n_muestras, vol_final, vol_adn, porcentaje_error)
    if not es_valido:
        return {
            "error": True, 
            "motivo_error": mensaje_error, 
            "critico": True
        }

    # 2. Factor de multiplicacion basado en el coeficiente de error humano/arrastre
    n_total = n_muestras * (1 + (porcentaje_error / 100))
    
    # 3. Sumatoria estricta de reactivos fijos provistos para un tubo
    reactivos_fijos = sum(reactivos.values())
    
    # 4. Calculo cinetico del agua libre de nucleasas (Buffer de volumen restante)
    vol_agua = vol_final - vol_adn - reactivos_fijos
    
    # 5. Control de saturacion (evita que el master mix supere la capacidad fisica configurada)
    if vol_agua < 0:
        return {
            "error": True,
            "motivo_error": "Saturacion de volumen",
            "critico": False,
            "reactivos_fijos": round(reactivos_fijos, 2),
            "exceso_uL": round(abs(vol_agua), 2)
        }
        
    # 6. Escalado de volumenes individuales al volumen total (lote), aplicando redondeo flotante a 2 decimales
    master_mix_totales = {comp: round(vol * n_total, 2) for comp, vol in reactivos.items()}
    master_mix_totales["Agua libre de nucleasas"] = round(vol_agua * n_total, 2)
    
    # 7. Volumenes operativos para la manipulacion en la campana de flujo laminar
    vol_mm_por_tubo = vol_final - vol_adn
    total_tubo_master = vol_mm_por_tubo * n_total
    volumen_total_ensayo = vol_final * n_total
    
    # 8. Control interno de calidad (Sanity Check de masa balanceada)
    suma_componentes_mix = sum(master_mix_totales.values())
    balance_masa_ok = abs(suma_componentes_mix - total_tubo_master) < 0.05

    return {
        "error": False,
        "n_total_rxs": round(n_total, 2),
        "vol_agua_individual": round(vol_agua, 2),
        "reactivos_fijos_individual": round(reactivos_fijos, 2),
        "totales_mix": master_mix_totales,
        "vol_mm_por_tubo": round(vol_mm_por_tubo, 2),
        "total_tubo_master": round(total_tubo_master, 2),
        "volumen_total_ensayo": round(volumen_total_ensayo, 2),
        "balance_masa_ok": balance_masa_ok
    }
