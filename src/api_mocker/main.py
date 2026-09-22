from fastapi import FastAPI,requests,responses,Form,UploadFile,Response
from scalar_fastapi import add_scalar_reference
from pydantic import BaseModel
app = FastAPI(title="apiMocker")
add_scalar_reference(app)



@app.api_route("/",description="says hello")
def index():
    return "Hi"

@app.post("/register")
async def register(name :str = Form(...), file :UploadFile = Form(...)):

    fname = file.filename
    if fname.endswith(".yaml") or fname.endswith("yml") or fname.endswith("json") :
        if await process(name,file):
            return Response(status_code=200)
    else:
        return Response(status_code=401)

import os   
from datetime import datetime
async def process(name: str, file: UploadFile):
    if not os.path.isdir("api_doc"):
        os.mkdir("api_doc")
    file_name = file.filename
    prefix = "_".join(name.split(" "))
   
    file_name=f"{datetime.now().strftime("%Y%m%d%H%M%S")}#{file_name}"

    file_name=("_".join(file_name.split(" ")))
    if not os.path.isdir("api_doc/"+prefix):
            os.mkdir("api_doc/"+prefix)
    with open(f"api_doc/{prefix}/"+file_name,"wb") as f:
        data=await file.read()
        f.write(data)
    return True


