import os
import sys
import streamlit.web.cli as stcli

# 1. Bloquea el cartel molesto del email de raíz
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

if __name__ == "__main__":
    # 2. Si es el .exe, lo obliga a pararse en su carpeta temporal para no perder los archivos
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    
    # 3. Arranca Streamlit buscando 'app_web.py' directamente en el lugar correcto
    sys.argv = ["streamlit", "run", "app_web.py", "--global.developmentMode=false"]
    sys.exit(stcli.main())
