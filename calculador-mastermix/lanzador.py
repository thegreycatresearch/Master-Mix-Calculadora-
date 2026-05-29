import os
import sys
import streamlit.web.cli as stcli

# 1. Bloquea la solicitud de email de Streamlit para cualquier usuario
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

if __name__ == "__main__":
    # 2. Si se ejecuta como .exe, obliga al programa a pararse en su carpeta temporal
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
        sys.path.append(sys._MEIPASS)
    else:
        # Si se ejecuta en modo desarrollo local
        ruta_actual = os.path.dirname(os.path.abspath(__file__))
        os.chdir(ruta_actual)
        sys.path.append(ruta_actual)
    
    # 3. Inicia Streamlit buscando 'app_web.py' directamente en el lugar correcto
    sys.argv = ["streamlit", "run", "app_web.py", "--global.developmentMode=false"]
    sys.exit(stcli.main())
