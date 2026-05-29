import os
import sys
import threading
import time
import webbrowser
import streamlit.web.cli as stcli

# 1. Configuración de entorno
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_PORT"] = "8501"

def abrir_navegador():
    """Espera a que el servidor de Streamlit inicie para abrir el navegador."""
    time.sleep(3)  # Da tiempo a que el servidor levante
    url = "http://localhost:8501"
    
    # Intenta abrir con Edge primero, si no, usa el predeterminado del sistema
    edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
    if os.path.exists(edge_path):
        try:
            webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))
            webbrowser.get('edge').open(url)
            return
        except:
            pass
    webbrowser.open(url)

if __name__ == "__main__":
    # 2. Configuración de rutas (crítico para --onedir)
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(base_path)
    sys.path.append(base_path)
    
    # 3. Iniciar el navegador en un hilo separado para no bloquear el inicio
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    # 4. Lanzar la aplicación
    script_path = os.path.join(base_path, "app_web.py")
    sys.argv = ["streamlit", "run", script_path, "--global.developmentMode=false"]
    sys.exit(stcli.main())
