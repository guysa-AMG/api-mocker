from fastapi import FastAPI

app = FastAPI(title="apiMocker")

@app.api_route("/",description="says hello")
def index():
    
    return "Hi"