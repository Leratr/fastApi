from app.dash_app import dash_app
from app.measurements import cpu, update_msts, CPU_COUNT
from fastapi import FastAPI, Depends, HTTPException, Request, status, Form
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from typing import Union
import psutil 
import shutil
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount('/dash/', WSGIMiddleware(dash_app.server))
templates = Jinja2Templates(directory="/home/sirius/Загрузки/new_proj/app/templates")
SECRET_KEY = '3dbc746b37592b90efe1b5b5d31adbfec98d7c390e7451a047d5bb86e9e4223b'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
HASHED_PASSWORD = "$2b$12$DK4AqecIREPKTNXLKASL6OA7v0x6qzeSnbYJ/UP.7/ho3h.otH6wq"


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

@app.get("/", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    ram_info = {
        "total": psutil.virtual_memory().total,
        "available": psutil.virtual_memory().available,
        "used": psutil.virtual_memory().used,
        "percent": psutil.virtual_memory().percent
    }

    memory_info = {
        "total": psutil.disk_usage('/').total,
        "used": psutil.disk_usage('/').used,
        "free": psutil.disk_usage('/').free,
        "percent": psutil.disk_usage('/').used / psutil.disk_usage('/').total * 100
    }

    swap_info = {
        "total": psutil.swap_memory().total,
        "used": psutil.swap_memory().used,
        "free": psutil.swap_memory().free,
        "percent": psutil.swap_memory().percent
    }

    partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in partitions:
        usage = shutil.disk_usage(partition.mountpoint)
        disk_info[partition.device] = {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": usage.used / usage.total * 100
        }

    network_info = {
        "bytes_sent": psutil.net_io_counters().bytes_sent,
        "bytes_received": psutil.net_io_counters().bytes_recv,
        "packets_sent": psutil.net_io_counters().packets_sent,
        "packets_received": psutil.net_io_counters().packets_recv
    }

    connections = psutil.net_connections()
    connection_info = []
    for conn in connections:
        connection_info.append({
            "local_address": conn.laddr,
            "remote_address": conn.raddr,
            "status": conn.status
        })

    temperature_info = psutil.sensors_temperatures()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "ram_info": ram_info,
        "memory_info": memory_info,
        "swap_info": swap_info,
        "disk_info": disk_info,
        "network_info": network_info,
        "connection_info": connection_info,
        "temperature_info": temperature_info
    })

def verify_pwd(plain_pwd, hashed_pwd):
    return pwd_context.verify(plain_pwd, hashed_pwd)

def auth_user(pwd: str):
    if not verify_pwd(pwd, HASHED_PASSWORD):
        return False
    return 'admin'

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post('/token')
@app.get('/token')
async def login_for_access_token(password: str = Form(...)):
    user = auth_user(password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user},
        expires_delta=access_token_expires
    )

    response = RedirectResponse(url='/dash/', status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key='access_token', value=access_token, httponly=True)
    return response

@app.get('/ram')
async def get_ram_info():
    ram_info = {
        "total": psutil.virtual_memory().total,
        "available": psutil.virtual_memory().available,
        "used": psutil.virtual_memory().used,
        "percent": psutil.virtual_memory().percent
    }
    return ram_info

# Эндпоинт для получения информации о памяти
@app.get('/memory')
async def get_memory_info():
    memory_info = {
        "total": psutil.disk_usage('/').total,
        "used": psutil.disk_usage('/').used,
        "free": psutil.disk_usage('/').free,
        "percent": psutil.disk_usage('/').percent
    }
    return memory_info

# Эндпоинт для получения информации о Swap
@app.get('/swap')
async def get_swap_info():
    swap_info = {
        "total": psutil.swap_memory().total,
        "used": psutil.swap_memory().used,
        "free": psutil.swap_memory().free,
        "percent": psutil.swap_memory().percent
    }
    return swap_info


@app.get('/disk')
async def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in partitions:
        usage = shutil.disk_usage(partition.mountpoint)
        total = usage.total
        used = usage.used
        free = usage.free
        percent = (used / total) * 100  # Вычисляем процент использования диска
        disk_info[partition.device] = {
            "total": total,
            "used": used,
            "free": free,
            "percent": percent
        }
    return disk_info

# Эндпоинт для получения информации о сети
@app.get('/network')
async def get_network_info():
    network_info = {
        "bytes_sent": psutil.net_io_counters().bytes_sent,
        "bytes_received": psutil.net_io_counters().bytes_recv,
        "packets_sent": psutil.net_io_counters().packets_sent,
        "packets_received": psutil.net_io_counters().packets_recv
    }
    return network_info

# Эндпоинт для получения списка подключений
@app.get('/connections')
async def get_connections():
    connections = psutil.net_connections()
    connection_info = []
    for conn in connections:
        connection_info.append({
            "local_address": conn.laddr,
            "remote_address": conn.raddr,
            "status": conn.status
        })
    return connection_info

# Эндпоинт для получения информации о температуре
@app.get('/temperature')
async def get_temperature_info():
    temperature_info = psutil.sensors_temperatures()
    return temperature_info