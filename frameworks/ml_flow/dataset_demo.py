import openai

import mlflow
from mlflow.genai.scorers import Correctness

mlflow.set_tracking_uri('http://localhost:5000')
mlflow.set_experiment(experiment_id="1")

# Define your model's predict function
def my_model(question: str) -> str:
    response = openai.OpenAI().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
    )
    return response.choices[0].message.content

eval_dataset = [
    {
        "inputs": {"question": "How do I log a model with MLflow?"},
        "expectations": {
            "expected_response": "You can log a model by using the mlflow.<flavor>.log_model function."
        },
    },
]

# Run evaluation with built-in scorer Correctness
mlflow.genai.evaluate(
    data=eval_dataset,
    predict_fn=my_model,
    scorers=[Correctness()],
)