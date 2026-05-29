import os
import sys
import streamlit.web.cli as stcli

# 1. Evita que Streamlit pida el email al usuario
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

if __name__ == "__main__":
    # 2. Determina dónde están realmente los archivos (.exe o desarrollo)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 3. Fuerza a Python y a la terminal a pararse en esa carpeta
    os.chdir(base_path)
    sys.path.append(base_path)
    
    # 4. Ruta absoluta al archivo app_web.py para que no haya margen de error
    script_path = os.path.join(base_path, "app_web.py")
    
    # 5. Lanza Streamlit apuntando directo al archivo mapeado
    sys.argv = ["streamlit", "run", script_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())
