from fastapi import FastAPI
from backend.app.routes.test_route import router as test_router
from backend.app.routes.user_route import router as user_router

app = FastAPI()

# Registrar rutas
app.include_router(test_router)
app.include_router(user_router)

@app.get("/")
def root():
    return {"message": "API funcionando"}
