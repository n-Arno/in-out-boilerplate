#!/usr/bin/env python3

import os
import uvicorn
import aiohttp
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
from typing import Any


# Composite logging for main application
# A standard FileHandler is not used to close the file after each write

class CompositeSender:
    def __init__(self, logFile: str) -> None:
        self.logFile = logFile

    def writeLog(self, logLine: str) -> None:
        with open(self.logFile, "a", encoding="utf-8") as f:
            f.write(f"{logLine}\n")


class CompositeHandler(logging.Handler):
    def __init__(self, logFile: str) -> None:
        logging.Handler.__init__(self)
        self.sender = CompositeSender(logFile)

    def emit(self, record) -> None:
        self.sender.writeLog(self.format(record))


class CompositeLogger(logging.Logger):
    def __init__(self, name, logFile, level=logging.INFO):
        super().__init__(name, level)
        handler = CompositeHandler(logFile)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s", "%H:%M")
        handler.setFormatter(formatter)
        self.addHandler(handler)


logger = CompositeLogger("main", "./logs/composite.log")


# Class definitions
class OutException(Exception):
    pass


class Status(BaseModel):
    status: str


class Hello(BaseModel):
    msg: str
    path: str


# Helper functions
async def get_weather(location: str) -> str:
    WEATHERURL = os.getenv("WEATHERURL", default="https://wttr.in")
    url = f"{WEATHERURL}/{location}?format=%C+%t"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                weather_data = await response.text()
                return weather_data
            else:
                raise OutException(f"Got {response.status} from {url}")


async def get_ip() -> Any:
    GETIPURL = os.getenv("GETIPURL", default="https://api4.my-ip.io")
    url = f"{GETIPURL}/v2/ip.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                my_ip = await response.json()
                return my_ip
            else:
                raise OutException(f"Got {response.status} from {url}")


async def call_hello(whatever: str) -> Hello:
    HELLOURL = os.getenv("HELLOURL", default="https://127.0.0.1:8443")
    url = f"{HELLOURL}/{whatever}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                hello = await response.json()
                return Hello(**hello)
            else:
                raise OutException(f"Got {response.status} from {url}")


# Load env values
load_dotenv()

# Build app, demo mounting api version as subapp
app = FastAPI(description="[v1 api](/v1/docs)")
api = FastAPI(root_path="/v1", description="[go back](/docs)")
app.mount("/v1", api)


# example: Return using a class object
@app.get("/", status_code=200)
async def health() -> Status:
    logger.info("status called")
    return Status(status="ok")


# example: Return text, use a path parameter
@api.get("/location/{location}", response_class=PlainTextResponse)
async def get_location(location: str):
    try:
        weather_data = await get_weather(location)
        return PlainTextResponse(weather_data, status_code=200)
    except OutException as e:
        raise HTTPException(status_code=500, detail=str(e))


# example: Return json
@api.get("/myip", response_class=JSONResponse)
async def get_myip():
    try:
        my_ip = await get_ip()
        return my_ip
    except OutException as e:
        raise HTTPException(status_code=500, detail=str(e))


# example: Get object from helper
@api.get("/hello/{whatever}", status_code=200)
async def get_hello(whatever: str) -> Hello:
    try:
        return await call_hello(whatever)
    except OutException as e:
        raise HTTPException(status_code=500, detail=str(e))


# Start app locally, ready for proxying
if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
