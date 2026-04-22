import mlflow

mlflow.set_experiment(experiment_id='1')
mlflow.set_tracking_uri('http://localhost:5000')
# mlflow.openai.autolog()

import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Load the Iris dataset
X, y = datasets.load_iris(return_X_y=True)

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the model hyperparameters
params = {
    'solver': 'lbfgs',
    'max_iter': 1000,
    'random_state': 8888
}

# Enable autologging for scikit-learn
mlflow.sklearn.autolog()

# Just train the model normally
lr = LogisticRegression(**params)
lr.fit(X_train, y_train)

# MLFlow abilities:
# Saving the trained model.
# Recording the model's performance metrics during training, such as accuracy, precision, AUC curve.
# Logging hyperparameter values used to train the model.
# Track metadata such as input data format, user, timestamp, etc.

y_pred = lr.predict(X_test)

with mlflow.start_run():
    # mlflow.log_metrics({
    #     "accuracy": accuracy_score(y_test, y_pred),
    #     "precision": precision_score(y_test, y_pred, average='weighted'),
    #     "recall": recall_score(y_test, y_pred, average='weighted'),
    #     "f1": f1_score(y_test, y_pred, average='weighted'),
    # })
    mlflow.log_params(params=params)

    # Train the model
    lr = LogisticRegression(**params)
    lr.fit(X_train, y_train)

    # Log the model
    model_info = mlflow.sklearn.log_model(sk_model=lr, name = "iris-model")

    # Predict on the test set, compute and log the loss metric
    y_pred = lr.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    mlflow.log_metric('accuracy',accuracy)
    mlflow.set_tag('Training info', 'Basic LR model for iris data')