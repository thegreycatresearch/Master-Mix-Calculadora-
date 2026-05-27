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

def calcular_parametros_ciclado(tm_primer_menor: float, longitud_bp: int) -> Dict[str, Any]:
    """
    Estima los parametros del programa del termociclador.
    Aplica la regla empirica Ta = Tm - 5 para anillamiento y 1 min/kb para extension con Taq.
    """
    if tm_primer_menor <= 0 or longitud_bp <= 0:
        return {"ta": 0.0, "tiempo_ext_seg": 0}
    
    ta = tm_primer_menor - 5.0
    # 60 segundos por cada 1000 pares de bases, con un minimo de 15 segundos
    tiempo_ext = max(15, round((longitud_bp / 1000.0) * 60.0))
    
    return {
        "ta": round(ta, 1),
        "tiempo_ext_seg": tiempo_ext
    }

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
    Suma reactivos fijos y calcula de forma cinetica el agua libre de nucleasas remanente.
    """
    es_valido, mensaje_error = validar_entradas(n_muestras, vol_final, vol_adn, porcentaje_error)
    if not es_valido:
        return {
            "error": True, 
            "motivo_error": mensaje_error, 
            "critico": True
        }

    n_total = n_muestras * (1 + (porcentaje_error / 100))
    reactivos_fijos = sum(reactivos.values())
    vol_agua = vol_final - vol_adn - reactivos_fijos
    
    if vol_agua < 0:
        return {
            "error": True,
            "motivo_error": "Saturacion de volumen",
            "critico": False,
            "reactivos_fijos": round(reactivos_fijos, 2),
            "exceso_uL": round(abs(vol_agua), 2)
        }
        
    master_mix_totales = {comp: round(vol * n_total, 2) for comp, vol in reactivos.items()}
    master_mix_totales["Agua libre de nucleasas"] = round(vol_agua * n_total, 2)
    
    vol_mm_por_tubo = vol_final - vol_adn
    total_tubo_master = vol_mm_por_tubo * n_total
    volumen_total_ensayo = vol_final * n_total
    
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
