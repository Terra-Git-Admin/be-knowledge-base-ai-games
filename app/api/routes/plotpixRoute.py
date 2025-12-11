from fastapi import APIRouter
from typing import List, Dict
from app.core.services.plotpixServices import plotPixServices



plotpixRouter = APIRouter(
    prefix="/files",
    tags=["plot_pix"]
)

@plotpixRouter.get("/plotpix")
def get_homescreen_data():
    result = plotPixServices.get_homescreen_data()
    return result

@plotpixRouter.get("/stage/plotpix")
def get_stage_homescreen_data():
    result = plotPixServices.get_stage_homescreen_data()
    return result

@plotpixRouter.put("/update/plotpix")
def update_homescreen_data(data: dict):
    return plotPixServices.update_homescreen_data(data)

@plotpixRouter.put("/update/stage/plotpix")
def update_stage_homescreen_data(data: dict):
    return plotPixServices.update_stage_homescreen_data(data)
