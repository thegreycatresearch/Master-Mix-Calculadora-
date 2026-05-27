import os
from datetime import datetime

def limpiar_pantalla():
    """Limpia la terminal según el sistema operativo para mantener el orden."""
    os.system('cls' if os.name == 'nt' else 'clear')

def obtener_numero_valido(mensaje, tipo=float, minimo=0.0):
    """Garantiza que el usuario ingrese un número válido y no rompa el programa con texto."""
    while True:
        try:
            valor = tipo(input(mensaje))
            if valor < minimo:
                print(f"❌ El valor no puede ser menor a {minimo}. Intentá de nuevo.")
                continue
            return valor
        except ValueError:
            print("❌ Entrada inválida. Por favor, ingresá un número válido (usá el punto para los decimales).")

def exportar_reporte(datos_tabla, alertas, n_muestras):
    """Guarda automáticamente los resultados en un archivo de texto para el cuaderno digital."""
    fecha_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"pcr_reporte_{fecha_actual}.txt"
    
    try:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write("=============================================\n")
            f.write("   REPORTE DE MESADA - GENMOL CONICET-CENPAT \n")
            f.write(f"   Fecha y Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=============================================\n\n")
            f.write(f"Muestras reales a procesar: {n_muestras}\n")
            f.write(datos_tabla)
            f.write("\n" + alertas + "\n")
            f.write("\n=============================================\n")
            f.write("Reporte generado automáticamente por GenMol-PCR Tools.\n")
        print(f"\n💾 ¡Reporte guardado con éxito como '{nombre_archivo}'!")
    except Exception as e:
        print(f"❌ No se pudo guardar el archivo de reporte: {e}")

def ejecutar_calculadora():
    limpiar_pantalla()
    print("=============================================")
    print("   GENMOL-PCR: CALCULADOR PROFESIONAL V3     ")
    print("=============================================\n")
    
    # 1. Entrada segura de datos básicos
    n_muestras = obtener_numero_valido("🧬 ¿Cuántas muestras vas a procesar? ", tipo=int, minimo=1)
    vol_final_pcr = obtener_numero_valido("🧪 Volumen FINAL de la PCR en cada tubo (uL): ", tipo=float, minimo=1.0)
    vol_adn = obtener_numero_valido("💧 Volumen de ADN molde por tubo (uL): ", tipo=float, minimo=0.0)
    
    # Margen de error modificable (por defecto 10%)
    porcentaje_error = obtener_numero_valido("📉 % de error de pipeteo extra (ej. 10): ", tipo=float, minimo=0.0)
    n_total = n_muestras * (1 + (porcentaje_error / 100))
    
    # 2. Configuración de reactivos (Estándar vs Personalizado)
    print("\n[?] Configuración de reactivos para 1 reacción:")
    print(" 1. Usar volúmenes estándar de GenMol (Buffer, dNTPs, Primers, Taq)")
    print(" 2. Ingresar volúmenes personalizados de reactivos")
    opcion = obtener_numero_valido("Seleccioná una opción (1 o 2): ", tipo=int, minimo=1)
    
    if opcion == 2:
        print("\n--- Ingresá los volúmenes para UN SOLO tubo ---")
        vol_buffer = obtener_numero_valido("• Buffer PCR (uL): ", float)
        vol_dntps = obtener_numero_valido("• dNTPs (uL): ", float)
        vol_primer_f = obtener_numero_valido("• Primer Forward (uL): ", float)
        vol_primer_r = obtener_numero_valido("• Primer Reverse (uL): ", float)
        vol_taq = obtener_numero_valido("• Taq Polimerasa (uL): ", float)
    else:
        # Valores estándar del laboratorio
        vol_buffer = 2.5   # Buffer 10x
        vol_dntps = 0.5    # dNTPs 10mM
        vol_primer_f = 1.0 # Forward 10uM
        vol_primer_r = 1.0 # Reverse 10uM
        vol_taq = 0.2      # Taq Polimerasa
        print("\nℹ️ Usando volúmenes estándar cargados.")

    # 3. Cálculo de agua (relleno) y validación matemática
    reactivos_fijos = vol_buffer + vol_dntps + vol_primer_f + vol_primer_r + vol_taq
    vol_agua = vol_final_pcr - vol_adn - reactivos_fijos
    
    if vol_agua < 0:
        print("\n❌ ¡ERROR CRÍTICO! Los reactivos y el ADN superan el volumen final de la PCR.")
        print(f"Suma de reactivos + ADN: {reactivos_fijos + vol_adn:.2f} uL vs Volumen Final: {vol_final_pcr:.2f} uL")
        print("Operación cancelada. Revisá tus volúmenes.")
        input("\nPresioná Enter para volver a empezar...")
        return

    # 4. Construcción de la tabla de resultados
    linea_separadora = "-" * 70 + "\n"
    tabla = linea_separadora
    tabla += f"{'Componente':<28} | {'1 Tubo (uL)':<12} | {f'Master Mix Total ({n_muestras} m. + {porcentaje_error}%)':<25}\n"
    tabla += linea_separadora
    tabla += f"{'Agua libre de nucleasas':<28} | {vol_agua:<12.2f} | {vol_agua * n_total:.2f} uL\n"
    tabla += f"{'Buffer PCR':<28} | {vol_buffer:<12.2f} | {vol_buffer * n_total:.2f} uL\n"
    tabla += f"{'dNTPs':<28} | {vol_dntps:<12.2f} | {vol_dntps * n_total:.2f} uL\n"
    tabla += f"{'Primer Forward':<28} | {vol_primer_f:<12.2f} | {vol_primer_f * n_total:.2f} uL\n"
    tabla += f"{'Primer Reverse':<28} | {vol_primer_r:<12.2f} | {vol_primer_r * n_total:.2f} uL\n"
    tabla += f"{'Taq Polimerasa':<28} | {vol_taq:<12.2f} | {vol_taq * n_total:.2f} uL\n"
    tabla += linea_separadora
    
    vol_mm_por_tubo = vol_final_pcr - vol_adn
    total_tubo_master = vol_mm_por_tubo * n_total
    
    alertas =  f"👉 En cada tubo de PCR vaciarás: {vol_mm_por_tubo:.2f} uL de este Master Mix.\n"
    alertas += f"👉 Luego agregarás a cada uno:   {vol_adn:.2f} uL de tu ADN molde.\n"
    alertas += f"👉 Volumen TOTAL a armar en el tubo Eppendorf de Master Mix: {total_tubo_master:.2f} uL"

    # Mostrar en pantalla
    print(f"\n[RESULTADOS] Calculado para {n_muestras} muestras (+ {porcentaje_error}% error = {n_total:.2f} rxs):")
    print(tabla)
    print(alertas)
    print("-" * 70)

    # 5. Exportar los datos
    guardar = input("\n💾 ¿Querés exportar estos resultados a un archivo de texto? (s/n): ").lower()
    if guardar == 's':
        exportar_reporte(tabla, alertas, n_muestras)
        
    input("\nPresioná Enter para continuar...")

def main():
    """Bucle principal para mantener la aplicación corriendo si se desea."""
    while True:
        ejecutar_calculadora()
        limpiar_pantalla()
        print("¿Qué deseas hacer ahora?")
        print("1. Calcular otro Master Mix")
        print("2. Salir del programa")
        opcion = obtener_numero_valido("Seleccioná una opción: ", tipo=int, minimo=1)
        if opcion == 2:
            print("\n👋 ¡Éxitos en el GenMol! Nos vemos.")
            break

if __name__ == "__main__":
    main()
