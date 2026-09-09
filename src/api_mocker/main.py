from fastapi import FastAPI
from scalar_fastapi import add_scalar_reference

app = FastAPI(title="apiMocker")
add_scalar_reference(app)

@app.api_route("/",description="says hello")
def index():
    return "Hi"