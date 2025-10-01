import uvicorn
import nest_asyncio
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from gensim.models import Word2Vec

# checking the model path
MODEL_PATH = "word2vec.model"
if not os.path.exists(MODEL_PATH):
    print(f"Error: Model file not found at '{MODEL_PATH}'")
    exit()

# Loading the trained Word2Vec model
model = Word2Vec.load(MODEL_PATH)

# Creating an instance of the FastAPI application
app = FastAPI()

# --- Pydantic Model with Input Validation ---
class WordInput(BaseModel):
    word: str

    @field_validator('word')
    def validate_word(cls, v):
        # strip whitespace
        clean_v = v.strip()

        # Checking if the word is empty or contains whitespace
        if not clean_v:
            raise ValueError("Input word cannot be empty or just whitespace.")

        # Checking if the word consists only of digits
        if clean_v.isdigit():
            raise ValueError("Numeric-only input is not allowed. Please provide an alphanumeric word.")

        # Return the cleaned version of the word
        return clean_v

# --- API Endpoint ---
@app.post("/similar_words")
async def get_similar_words(item: WordInput):
    try:
        similar_words = model.wv.most_similar(item.word, topn=5)
        return {"similar_words": [word for word, _ in similar_words]}
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Word '{item.word}' not found in vocabulary."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An internal server error occurred: {e}"
        )

# --- Main Execution Block ---
if __name__ == "__main__":
    nest_asyncio.apply()
    uvicorn.run(app, host="0.0.0.0", port=8000)