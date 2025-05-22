FROM bentoml/model-server:latest

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt