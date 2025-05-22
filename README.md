# Admissions Prediction Service

This project implements an Admission Prediction API using BentoML.  

The system uses two models (Linear Regression and Random Forest) to predict student admission chances.

---

## Requirements

- Python 3.10+  

- Docker  

- BentoML (version < 1.4 recommended)  

---

## 1. Project Setup

- docker load -i thoma_admissions_service.tar

### 1.1 Create and activate virtual environment

```bash
python -m venv venv_bento

source venv_bento/bin/activate    # Linux/Mac

venv_bento\Scripts\activate       # Windows PowerShell

pip install -r requirements.txt

1.2 Train and save models


python src/prepare_data.py


python src/train_model.py

2. optional rebuil Build Bento

bentoml build

3. Build and run Docker image

# Build Docker image (auto by bentoml build or manual)

bentoml containerize admissions_service:latest -t admissions_service_image

# Tag image (optional)

docker tag admissions_service_image:latest <your_name>_admissions_service:latest

# Run container

docker run -p 3000:3000 <your_name>_admissions_service:latest

 4. Test API



4.1 Login


curl -X POST http://localhost:3000/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin", "password":"admin"}'

get token

```powershell

$loginResponse = Invoke-RestMethod -Method Post -Uri "http://localhost:3000/login" -Body '{"username":"admin","password":"admin"}' -ContentType "application/json"

$token = $loginResponse.token

4.2 Predict with token

curl -X POST http://localhost:3000/predict \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer <TOKEN>" \
    -d '{
        "gre_score": 330,
        "toefl_score": 110,
        "university_rating": 4,
        "sop": 4.5,
        "lor": 4.5,
        "cgpa": 9.2,
        "research": 1
    }'

Linear Regression and Random Forest Prediction

```powershell

$token = (Invoke-RestMethod -Method Post -Uri "http://localhost:3000/login" -Body '{"username":"admin","password":"admin"}' -ContentType "application/json").token; Invoke-RestMethod -Method Post -Uri "http://localhost:3000/predict" -Headers @{Authorization = "Bearer $token"} -Body '{"gre_score":320,"toefl_score":110,"university_rating":4,"sop":4.5,"lor":4.0,"cgpa":9.1,"research":1}' -ContentType "application/json"


Invoke-RestMethod -Method Post -Uri "http://localhost:3000/predict" `
    -Headers @{Authorization = "Bearer $token"} `
    -Body '{"gre_score":320,"toefl_score":110,"university_rating":4,"sop":4.5,"lor":4.0,"cgpa":9.1,"research":1}' `
    -ContentType "application/json"



5. Run unit tests


pytest -v -s tests/test_endpoints.py

pytest tests/test_endpoints.py -v -s



Load image 

docker load -i thoma_admissions_service.tar

docker run -p 3000:3000 thoma_admissions_service:latest