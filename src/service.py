import bentoml
import jwt as pyjwt  # Alias für PyJWT
from fastapi import Request
from fastapi.responses import JSONResponse
from bentoml.io import JSON
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
import numpy as np
import uuid
import time
from typing import Dict

JWT_SECRET = "supersecret"
JWT_ALGORITHM = "HS256"

# Lade beide Modelle als Runner
lr_runner = bentoml.sklearn.get("admissions_lr:latest").to_runner()
rf_runner = bentoml.sklearn.get("admissions_rf:latest").to_runner()

# Erstelle Service mit beiden Runnern
svc = bentoml.Service("admissions_service", runners=[lr_runner, rf_runner])

class AdmissionInput(BaseModel):
    gre_score: int
    toefl_score: int
    university_rating: int
    sop: float
    lor: float
    cgpa: float
    research: int

class LoginInput(BaseModel):
    username: str
    password: str

class BatchPredictionRequest(BaseModel):
    instances: list[AdmissionInput]

class BatchStatusRequest(BaseModel):
    job_id: str

batch_jobs: Dict[str, Dict] = {}

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path != "/login":
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            try:
                pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except Exception:
                return {"error": "Invalid token", "status_code": 401}
        return await call_next(request)

svc.add_asgi_middleware(JWTAuthMiddleware)

@svc.api(input=JSON(pydantic_model=LoginInput), output=JSON())
def login(input_data: LoginInput):
    if input_data.username == "admin" and input_data.password == "admin":
        token = pyjwt.encode({"user": input_data.username}, JWT_SECRET, algorithm=JWT_ALGORITHM)
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        return {"token": token}
    else:
        return {"error": "Invalid credentials", "status_code": 401}

@svc.api(input=JSON(pydantic_model=AdmissionInput), output=JSON())
async def predict(input_data: AdmissionInput):
    try:
        input_df = [[
            input_data.gre_score,
            input_data.toefl_score,
            input_data.university_rating,
            input_data.sop,
            input_data.lor,
            input_data.cgpa,
            input_data.research
        ]]
        lr_result = await lr_runner.async_run(input_df)
        rf_result = await rf_runner.async_run(input_df)

        return {
            "lr_prediction": lr_result.tolist(),
            "rf_prediction": rf_result.tolist()
        }
    except Exception as e:
        return {"error": f"Prediction error: {str(e)}", "status_code": 400}

@svc.api(input=JSON(pydantic_model=BatchPredictionRequest), output=JSON())
async def batch_predict(request: BatchPredictionRequest):
    job_id = str(uuid.uuid4())
    batch_jobs[job_id] = {"status": "pending", "predictions": None}

    try:
        data = np.array([[
            ins.gre_score,
            ins.toefl_score,
            ins.university_rating,
            ins.sop,
            ins.lor,
            ins.cgpa,
            ins.research
        ] for ins in request.instances])
        # Optional: Du kannst hier z.B. beide Modelle parallel laufen lassen oder nur eins
        predictions = await lr_runner.async_run(data)
        batch_jobs[job_id] = {"status": "completed", "predictions": predictions.tolist()}
    except Exception as e:
        batch_jobs[job_id] = {"status": "failed", "error": str(e)}

    return {"job_id": job_id}

@svc.api(input=JSON(pydantic_model=BatchStatusRequest), output=JSON())
def batch_status(request: BatchStatusRequest):
    job = batch_jobs.get(request.job_id)
    if not job:
        return {
            "error": f"Job {request.job_id} not found",
            "status_code": 404
        }
    return job