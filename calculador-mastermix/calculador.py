def calcular_master_mix():
    print("--- CALCULADOR DE MASTER MIX PARA PCR ---")
    
    # 1. Pedir al usuario el número de reacciones
    n_muestras = int(input("¿Cuántas muestras vas a procesar? "))
    
    # Sumamos un 10% de exceso para el error de pipeteo
    n_total = n_muestras * 1.10
    print(f"\nCalculando para {n_muestras} muestras (+ 10% de error de pipeteo = {n_total:.2f} reacciones)")
    print("-" * 50)
    
    # 2. Definir los volúmenes en microlitros (uL) para 1 Sola Reacción
    # Modificá estos valores según el protocolo real de GenMol
    vol_agua = 14.8
    vol_buffer = 2.5
    vol_dntps = 0.5
    vol_primer_f = 1.0
    vol_primer_r = 1.0
    vol_taq = 0.2
    
    # 3. Calcular el total multiplicando por el número total de reacciones
    print(f"{'Componente':<20} | {'Para 1 tubo (uL)':<18} | {f'Master Mix Total ({n_muestras} m.)':<20}")
    print("-" * 50)
    print(f"{'Agua libre de nucleasas':<20} | {vol_agua:<18} | {vol_agua * n_total:.2f} uL")
    print(f"{'Buffer PCR (10x)':<20} | {vol_buffer:<18} | {vol_buffer * n_total:.2f} uL")
    print(f"{'dNTPs (10mM)':<20} | {vol_dntps:<18} | {vol_dntps * n_total:.2f} uL")
    print(f"{'Primer Forward':<20} | {vol_primer_f:<18} | {vol_primer_f * n_total:.2f} uL")
    print(f"{'Primer Reverse':<20} | {vol_primer_r:<18} | {vol_primer_r * n_total:.2f} uL")
    print(f"{'Taq Polimerasa':<20} | {vol_taq:<18} | {vol_taq * n_total:.2f} uL")
    print("-" * 50)
    
    vol_tubo_master = (vol_agua + vol_buffer + vol_dntps + vol_primer_f + vol_primer_r + vol_taq) * n_total
    print(f"Volumen total a preparar en el tubo de Master Mix: {vol_tubo_master:.2f} uL")

# Ejecutar la función
if __name__ == "__main__":
    calcular_master_mix()
