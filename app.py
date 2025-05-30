# Import necessary modules
from flask import Flask, render_template, request, jsonify
from txtai.pipeline import Summary
from PyPDF2 import PdfReader
from googletrans import Translator
import os
import re

# Initialize Flask application
app = Flask(__name__)

# Initialize translator and text summarizer instances
translator = Translator()
summary = Summary()

# Utility Functions

# Function to generate summary of a given text


def text_summary(text, maxlength=None):
    result = summary(text)
    return result

# Function to extract text from a PDF file


def extract_text_from_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PdfReader(f)
            text = ""
            for page_number in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_number].extract_text()
        return text
    except Exception as e:
        return None


# Function to translate text to a target language


def translate_text(text, target_language):
    if not text:
        return ""  # Return empty string if text is empty

    translation = translator.translate(text, dest=target_language)
    return translation.text

# Flask Routes

# Route for the home page


@app.route('/')
def index():
    return render_template('index.html')

# Route for text summarization


@app.route('/summarize_text', methods=['GET', 'POST'])
def summarize_text():
    if request.method == 'POST':
        input_text = request.form['input_text']
        result = text_summary(input_text)
        return jsonify({'result': result})
    elif request.method == 'GET':
        return render_template('text-summary.html')

# Route for document summarization


@app.route('/summarize_document', methods=['GET', 'POST'])
def summarize_document():
    if request.method == 'POST':
        try:
            input_file = request.files['input_file']
            file_path = 'static/uploaded_docs/doc_file.pdf'

            # Ensure the 'static/uploaded_docs/' directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            input_file.save(file_path)

            extracted_text = extract_text_from_pdf(file_path)

            if extracted_text is None:
                return jsonify({'error': 'Empty or invalid PDF file.'}), 400

            doc_summary = text_summary(extracted_text)
            return jsonify({'extracted_text': extracted_text, 'doc_summary': doc_summary})

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return render_template('doc-summary.html')


# Route for text translation


@app.route("/translate", methods=["GET", "POST"])
def translate():
    if request.method == "POST":
        data = request.get_json()
        text = data.get("text")
        target_language = data.get("target_language", "mr")

        try:
            # Translate the text to the target language
            translated_text = translate_text(text, target_language)
            return jsonify({"result": translated_text}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif request.method == "GET":
        # Handle GET request if needed
        return jsonify({"error": "GET request not supported"}), 405


# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
