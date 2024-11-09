from typing import Annotated
from pydantic import BaseModel
from fastapi import FastAPI, Body
from llama_cpp import Llama

class SummarizeBody(BaseModel):
    input: str

app = FastAPI()

model = Llama(
    model_path='/weights/model.gguf',
    n_threads=8,  # Number of threads to use
    n_ctx=768,  # Context size
    verbose=False,
    n_gpu_layers=25,
)


def inference(model, text):
    text = text[:400]

    summarization = model(
        f"{text}\n Сокращенный текст на Русском:",
        max_tokens=170,
    )

    return summarization


@app.post("/summarize", tags="Predict")
def predict(predict_body: Annotated[SummarizeBody, Body()]):
    summary = inference(model, predict_body.input)

    responce = {
        "input": predict_body.input,
        "summary": ' '.join(summary['choices'][0]['text'].strip().replace('\n\n', '\n').split('\n')[:2]),
    }

    return responce