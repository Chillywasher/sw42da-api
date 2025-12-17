import asyncio
import json
import os

from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from cached_status import CachedStatus
from models import CommandString
from sw42da import Sw42da
from sw42da_utility import Sw42daUtility

load_dotenv()
FASTAPI_LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

ON = "On"
OFF = "Off"
MUTE = "Mute"
VOLUME = "Volume"

cs = CachedStatus(expires_seconds=30)
su = Sw42daUtility()
sc = Sw42da()

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(cache_updater_loop())
    yield

app = FastAPI(docs_url="/", lifespan=lifespan)

@app.exception_handler(404)
async def custom_404_handler(_, __):
    response_404 = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <title>Not Found</title>
                        <script> location.href='/' </script>
                    </head>
                    <body>
                        <p>The file you requested was not found.</p>
                    </body>
                    </html>
                    """
    return HTMLResponse(response_404)

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def cache_updater_loop():
    count = 0
    while True:
        count +=1
        # print(f"Refreshing cache [{count}]")
        await asyncio.sleep(3)
        await cs.get_cache()

@app.get("/status")
async def get_status():
    cache = await cs.get_cache()
    json_formatted = json.dumps(cache["AudioOut"][0], indent=2)
    print(json_formatted)
    return cache

@app.post("/send_command")
async def send_command(cmd: CommandString):
    return await sc.send_command(cmd.command)

@app.get("/volume/up/{volume}")
async def volume_up(volume: int):
    resp = await sc.send_command(f"VOL+{volume}")
    if response_success(resp):
        vol = await parse_volume_response(resp)
        await update_cache(VOLUME, vol)
    return resp

@app.get("/volume/down/{volume}")
async def volume_down(volume: int):
    resp = await sc.send_command(f"VOL-{volume}")
    if response_success(resp):
        vol = await parse_volume_response(resp)
        await update_cache(VOLUME, vol)
    return resp

@app.get("/volume/set/{volume}")
async def volume_up(volume: int):
    resp = await sc.send_command(f"VOL {volume}")
    if response_success(resp):
        vol = await parse_volume_response(resp)
        await update_cache(VOLUME, vol)
    return resp

@app.get("/volume/mute/on")
async def mute_on():
    resp = await sc.send_command("MUTE ON")
    if response_success(resp):
        await update_cache(MUTE, ON)
        return resp
    else:
        raise HTTPException(status_code=500, detail="Mute on unsucessful")

@app.get("/volume/mute/off")
async def mute_off():
    resp = await sc.send_command("MUTE OFF")
    if response_success(resp):
        await update_cache(MUTE, OFF)
        return resp
    else:
        raise HTTPException(status_code=500, detail="Mute off unsucessful")

@app.get("/volume/mute/toggle")
async def mute_toggle():

    status = await get_status()

    if status["AudioOut"][0][MUTE] == ON:
        print("Mute is On so setting Mute to Off")
        update_flag = OFF
    else:
        print("Mute is Off so setting Mute to On")
        update_flag = ON

    if update_flag == ON:
        resp = await mute_off()
    else:
        resp = await mute_on()

    if response_success(resp):
        await update_cache(MUTE, update_flag)
        return resp
    else:
        raise HTTPException(status_code=500, detail="Mute toggle unsucessful")

async def parse_volume_response(resp: list) -> int:
    vol = resp[1].split(" ")[-1].replace(".", "")
    return int(vol)

async def update_cache(key: str, value: str | int):
    status = await get_status()
    status["AudioOut"][0][key] = value
    await cs.set_cache(status)

def response_success(resp: list):
    if len(resp) < 4:
        return False
    if not resp[1].startswith("[SUCCESS]"):
        return False
    return True

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8030, log_level=FASTAPI_LOG_LEVEL, reload=True)


