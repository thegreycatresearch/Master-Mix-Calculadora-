import os
import sys
import streamlit.web.cli as stcli

def obtener_ruta_recurso(ruta_relativa):
    """ Permite acceder a los archivos empaquetados dentro del ejecutable """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)

if __name__ == "__main__":
    # Localiza el script principal de la interfaz dentro del paquete compilado
    ruta_aplicacion = obtener_ruta_recurso("app_web.py")
    
    # Configura los argumentos del sistema para iniciar el servidor local de forma automática
    sys.argv = ["streamlit", "run", ruta_aplicacion, "--global.developmentMode=false"]
    sys.exit(stcli.main())
