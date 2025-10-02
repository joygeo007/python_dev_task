import streamlit as st
import requests

st.title("Word Similarity Finder")

# Get user input
input_word = st.text_input("Enter a single word (e.g., computer, human, graph):", key="word_input")

if st.button("Find Similar Words"):
    if input_word:
        try:
            # Make a POST request to the FastAPI endpoint
            api_url = "https://word-similarity-api.onrender.com/similar_words"
            response = requests.post(api_url, json={"word": input_word})

            # Check the response status code
            if response.status_code == 200:
                # Success case
                data = response.json()
                st.success("Similar words found:")
                for word in data.get("similar_words", []):
                    st.write(f"- {word}")
            else:
                # Handle HTTP errors (like 404, 422, 500)
                error_data = response.json()
                error_message = error_data.get("detail", "An unknown error occurred.")
                st.error(f"Error: {error_message[0]['msg'] if isinstance(error_message, list) else error_message}")

        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the API server. Please ensure it is running at http://localhost:8000.")
        except Exception as e:
            # Catch any other exceptions
            st.error(f"A critical error occurred: {e}")
    else:
        st.warning("Please enter a word.")
