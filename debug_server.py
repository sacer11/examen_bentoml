# debug_server.py
import uvicorn
from src.service import svc

if __name__ == "__main__":
    uvicorn.run(svc.asgi_app, host="127.0.0.1", port=3000)