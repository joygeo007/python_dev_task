# Word Similarity Finder API & Streamlit App

## Overview

This project provides a simple web application for finding similar words using a `gensim` Word2Vec model. It consists of two main components:

1.  **FastAPI Backend (`api.py`):** A robust REST API that loads a Word2Vec model, accepts a word as input, and returns a list of the 5 most similar words. It includes input validation and graceful error handling.
2.  **Streamlit Frontend (`app.py`):** A user-friendly web interface that allows users to enter a word, interact with the FastAPI backend, and view the results or any error messages.

Additionally, code has been provided for training the model (at the end).


## Project Structure

```
/word-similarity-app
|-- api.py            # FastAPI backend server
|-- app.py            # Streamlit frontend application
|-- train.py          # model training file
|-- requirements.txt  # Project dependencies
|-- word2vec.model    # (Generated) Word2Vec model file
|-- README.md         # This file
```

## Prerequisites

Before you begin, ensure you have the following installed:

  * Python 3.8+
  * pip (Python package installer)
  * Git

-----

## Setup and Installation

Follow these steps to set up the project locally.

### 1\. Clone the Repository

First, clone the repository to your local machine using Git.

```bash
git clone https://github.com/joygeo007/python_dev_task.git
cd python-dev-task
```

### 2\. Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

  * **On macOS / Linux:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

  * **On Windows:**

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

### 3\. Install Dependencies

Install all the required Python packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

#### `requirements.txt` contents:

```
fastapi
uvicorn
gensim
streamlit
requests
nest_asyncio
pandas
pyarrow
nltk
argparse
```

-----

## Running the Application

You will need to run two processes in two separate terminal windows: the API server and the Streamlit app.

### Step 1: Start the FastAPI Backend

In your **first terminal**, run the following command to start the Uvicorn server for the API. The `--reload` flag will automatically restart the server when you make changes to the code.

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

You should see output indicating that the server is running, typically on `http://127.0.0.1:8000`.



#### API Usage Examples

You can interact with the API directly using tools like `curl` or Postman. The server must be running on `http://localhost:8000`.

##### 1\. Successful Request (200 OK)

This is an example of a valid request where the word exists in the model's vocabulary.

**Request:**

```bash
curl -X POST "http://localhost:8000/similar_words" \
-H "Content-Type: application/json" \
-d '{"word": "computer"}'
```

**Expected Response:**

```json
{
  "similar_words": [
    "user",
    "interface",
    "system",
    "time",
    "graph"
  ]
}
```

*(Note: The exact words will depend on the training data of your Word2Vec model.)*

##### 2\. Word Not Found (404 Not Found)

This happens when the word is valid but is not present in the model's vocabulary.

**Request:**

```bash
curl -X POST "http://localhost:8000/similar_words" \
-H "Content-Type: application/json" \
-d '{"word": "hellow"}'
```

**Expected Response:**

```json
{
  "detail": "Word 'hellow' not found in the vocabulary."
}
```

##### 3\. Invalid Input (422 Unprocessable Entity)

This error occurs when the input fails the validation rules (e.g., it contains only numbers, punctuation, or is empty).

**Request:**

```bash
curl -X POST "http://localhost:8000/similar_words" \
-H "Content-Type: application/json" \
-d '{"word": "123"}'
```

**Expected Response:**

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "word"
      ],
      "msg": "Numeric-only input is not allowed. Please provide an alphanumeric word.",
      "type": "value_error"
    }
  ]
}
```

### Step 2: Run the Streamlit Frontend

In a **second terminal** (ensure your virtual environment is still active), run the following command to launch the Streamlit application.

```bash
streamlit run app.py
```

Streamlit will automatically open a new tab in your web browser. If it doesn't, navigate to the URL shown in the terminal (usually `http://localhost:8501`).

## Usage

1.  Make sure both the FastAPI server and the Streamlit app are running.
2.  Open your web browser and go to the Streamlit URL (`http://localhost:8501`).
3.  Enter a single, alphabetic word into the input box (e.g., "computer", "human", "graph").
4.  Click the "Find Similar Words" button.
5.  The results or any relevant error messages will be displayed on the page. 


## Model Training Guidelines

The `train.py` script is designed to process text data that contains a mix of natural language and source code. It uses a 'code-aware' preprocessing pipeline to generate high-quality tokens before training a `gensim` Word2Vec model.

The preprocessing logic is specifically tuned to:

* Preserve important code entities like function_names, variable_names, and module.method calls.
* Convert natural language to lowercase while maintaining the original case for code.
* Remove common stop words and standalone numbers that add little value.
* Filter out very short words and variables.

### Dataset Requirements

To use this script, your dataset must meet the following criteria:

1. File Format: The dataset must be a Parquet file (.parquet).
2. Column Name: The data must be loadable into a pandas DataFrame that contains a column named exactly "answer". This column should hold the raw text documents (strings) you want to train the model on.

### How to Run the Training Script

You can run the script from your terminal. It requires two command-line arguments to specify the locations of your dataset and where to save the final model.
Command-line Arguments

*    `--dataset-path` (Required): The full path to your input .parquet dataset file.

*    `--model-path` (Required): The full path where the trained model file will be saved. It's conventional to name this file word2vec.model.

Example Usage

Here is an example command to run the script. Make sure you have activated your Python environment and installed the necessary dependencies.

```bash
python train.py --dataset-path /path/to/your/tech_dataset.parquet --model-path ./word2vec.model
```
After running, the script will log its progress to the console, and upon completion, the trained word2vec.model file will be available at the specified output path.
