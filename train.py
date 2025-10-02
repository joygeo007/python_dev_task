import pandas as pd
import argparse
import re
import string
import logging
from gensim.models import Word2Vec

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Preprocessing Logic ---

# Define stop words outside the function for efficiency.
STOP_WORDS = {
    'a', 'an', 'are', 'as', 'at', 'be', 'but', 'by', 'if',
    'into', 'is', 'it', 'no', 'of', 'on',  'such', 'that', 'the',
    'their', 'then', 'there', 'these', 'they', 'this', 'to', 'was', 'will', 'with'
}

# Define punctuation to strip from the end of tokens once.
# Underscore and angle brackets are preserved as they are common in code.
PUNCTUATION_TO_STRIP = string.punctuation.replace('_', '').replace('>', '')


def code_aware_tokenizer(text):
    """
    Tokenizes text with an awareness for code-specific syntax,
    applying strict filtering to produce clean tokens for model training.

    Args:
        text (str): The raw text string to process.

    Returns:
        list: A list of processed string tokens.
    """
    if not isinstance(text, str):
        return []

    # Regex to find words, code entities (like module.function), or any non-whitespace character
    tokens = re.findall(r'[\w._]+|\S', text)

    processed_tokens = []
    for token in tokens:
        candidate_token = None

        # Rule 1: Preserve code-like tokens.
        # - Contains '_' or '.' and at least one letter (e.g., 'user_id', 'np.array')
        # - Contains both digits and letters (e.g., 'utf8', 'h2')
        if (
            (len(token) > 1 and any(c in '_.' for c in token) and any(c.isalpha() for c in token)) or
            (any(c.isdigit() for c in token) and any(c.isalpha() for c in token))
        ):
            # Strip trailing punctuation once, if present
            if len(token) > 1 and token.endswith(tuple(PUNCTUATION_TO_STRIP)):
                candidate_token = token[:-1]
            else:
                candidate_token = token

        # Rule 2: Process natural language tokens.
        # - Must be purely alphabetic.
        elif token.isalpha():
            lower_token = token.lower()
            # Filter out stop words
            if lower_token not in STOP_WORDS:
                candidate_token = lower_token

        # Rule 3: Apply final filters to ALL candidate tokens before appending.
        if candidate_token:
            # - Must be 3 or more characters long.
            # - Must not be a standalone number (checked by previous rules).
            # - Filter out tokens that are mostly digits (e.g., long hex strings).
            if len(candidate_token) > 2 and len(re.findall(r'\d', candidate_token)) < 5:
                processed_tokens.append(candidate_token)

    return processed_tokens


def main(dataset_path, model_path):
    """
    Main function to load data, preprocess it, and train the Word2Vec model.
    """
    # --- Load Dataset ---
    logging.info(f"Loading dataset from: {dataset_path}")
    try:
        df = pd.read_parquet(dataset_path)
        if 'answer' not in df.columns:
            logging.error("Dataset must contain an 'answer' column.")
            return
    except Exception as e:
        logging.error(f"Failed to load or read the parquet file: {e}")
        return

    # --- Preprocess Text ---
    logging.info("Starting text preprocessing...")
    # The .values attribute is used for a potential performance gain with large datasets
    preprocessed_text = df['answer'].apply(code_aware_tokenizer).values
    logging.info("Preprocessing complete.")

    # --- Train Word2Vec Model ---
    logging.info("Training Word2Vec model...")
    # sg=1 uses the Skip-gram model, which often works better for infrequent words.
    model = Word2Vec(sentences=preprocessed_text, vector_size=100, window=5, min_count=1, workers=4, sg=1)
    logging.info("Model training complete.")

    # --- Save Model ---
    try:
        model.save(model_path)
        logging.info(f"Model successfully saved to: {model_path}")

        # Optional: Check model functionality
        if 'main' in model.wv:
            similar_words = model.wv.most_similar('main', topn=5)
            logging.info(f"Example: 5 most similar words to 'main' are: {similar_words}")
        else:
            logging.warning("Word 'main' not in vocabulary, could not run similarity check.")

    except Exception as e:
        logging.error(f"Failed to save the model: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train a Word2Vec model on code-related text data.")
    parser.add_argument(
        '--dataset-path',
        type=str,
        required=True,
        help="Path to the input dataset (must be a .parquet file with an 'answer' column)."
    )
    parser.add_argument(
        '--model-path',
        type=str,
        required=True,
        help="Path where the trained Word2Vec model will be saved."
    )
    args = parser.parse_args()

    main(dataset_path=args.dataset_path, model_path=args.model_path)
