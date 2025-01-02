from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from services.db_service import (
    create_table,
    get_all_samples,
    insert_sample,
    get_all_assets,
    get_all_categories,
    insert_category,
    insert_asset,
    get_category_attributes,
    insert_category_attributes
)
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil
from datetime import datetime
from dtos.category_dto import add_category
from dtos.asset_dto import add_asset
from dtos.category_attributes_dto import add_attributes, get_attributes

create_table()
# seed ?

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/samples")
def get_samples():
    return get_all_samples()
       
@app.post("/samples/upload")
async def upload(files: List[UploadFile] = File(...)):
    for file in files:
        try:

            tempFolder = 'data/temp/'
            if not os.path.exists(tempFolder):
                os.makedirs(tempFolder)

            tempPath = tempFolder + file.filename
            with open(tempPath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            insert_sample(file.filename, tempFolder + file.filename, datetime.now(), False)

        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            await file.close()  # Use await for closing FastAPI UploadFile

    return {"message": f"Successfully uploaded samples {[file.filename for file in files]}"}

@app.post("/samples/{sampleId}/analyze") 
async def analyze_sample(sampleId: int, backgroundTasks: BackgroundTasks):
    
    return {"message": "Accepted", "sampleId" : sampleId}

@app.get("/assets")
def get_assets():
    return get_all_assets() 

@app.post("/assets")
async def add_asset(addAssetObj: add_asset):

    added_date = datetime.now().timestamp()
    insert_asset(addAssetObj.name, addAssetObj.description, added_date, addAssetObj.category_id, addAssetObj.is_active)

    return {"message": "Successfully added asset"}

@app.get("/categories")
def get_categories():
    return get_all_categories()

@app.post("/categories")
async def add_category(addCategoryObj: add_category):

    added_date = datetime.now().timestamp()
    insert_category(addCategoryObj.name, addCategoryObj.description, added_date, addCategoryObj.is_active)

    return {"message": "Successfully added category"}

@app.get("/categories/{categoryId}/attributes")
def get_attributes(categoryId: int):
    return get_category_attributes(categoryId)

@app.post("/categories/{categoryId}/attributes")
async def add_attributes(categoryId: int, addAttributesObj: dict):

    insert_category_attributes(categoryId, addAttributesObj)

    return {"message": "Successfully added category attributes"}
