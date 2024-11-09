FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

EXPOSE 8000
COPY ./requirements.txt /model/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /model/requirements.txt

COPY ./ /model
COPY ./src/mistral-7b-instruct-v0.2.Q4_K_M.gguf /weights/model.gguf

WORKDIR /model

CMD ["python3", "-m", "src"]  