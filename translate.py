from flask import *
import openai
# import os
from google.cloud import translate

app = Flask(__name__)


# Configure Google Cloud Translation API client
# maybe need []
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\heman\MedScribe\Backend\credentials.json"

@app.route('/')
def main():
    return render_template('home.html')

# Reroute request to post with html boiler file
@app.route('/upload', methods=['POST', 'GET'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        languageDict = {
            "english": "en-US",
            "spanish": "es",
            "chinese": "zh",
            "german": "de",
            "telugu": "te",
            "french": "fr",
            "arabic": "ar"
        }
        inputLanguage = languageDict[request.form['InputL'].lower()]
        outputLanguage = languageDict[request.form['OutputL'].lower()]
        # Save uploaded file to Google Cloud Storage
        fileContent = file.read()
        fileContent = str(fileContent, 'utf-8') #Translates from bytes object to string with utf-8
        project_id = "medscribe-415400"
        client = translate.TranslationServiceClient()
        location = "global"
        parent = f"projects/{project_id}/locations/{location}"
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [fileContent],
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "source_language_code": inputLanguage, #en-US
                "target_language_code": outputLanguage, #hi
            }
        )
        #for translation in response.translations:
        #    print(f"Translated text: {translation.translated_text}")

        #FOR SUMMARIZING TEXT
        summary = abstract_summary_extraction(fileContent)
        summary = translateText(summary, inputLanguage, outputLanguage)

        #summary = 'temp'
        return render_template('display.html', 
            translated_text = response.translations[0].translated_text, 
            original_text = fileContent,
            summary = summary,
            #keyPoints = key_points_extraction(fileContent)
        )
        #return redirect(url_for('displayText', translated_text = response.translations[0].translated_text, original_text = fileContent))
        #return response.translations[0].translated_text
        #return fileContent
        # Analyze uploaded document (you can add analysis logic here)
        # For now, let's just return a success message
        #return url_for('translate_document', fileContent = fileContent)
def translateText(fileContent, inputLanguage, outputLanguage):
    project_id = "medscribe-415400"
    client = translate.TranslationServiceClient()
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [fileContent],
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "source_language_code": inputLanguage, #en-US
            "target_language_code": outputLanguage, #hi
        }
    )
    return response.translations[0].translated_text

def abstract_summary_extraction(transcription):
    client = openai.Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the following text and summarize it into a concise abstract paragraph. Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points."
            },
            {
                "role": "user",
                "content": transcription
            }
        ]
    )
    # Return the content of the completion
    return response.choices[0].message.content

def key_points_extraction(transcription):
    client = openai.Client()
    response = client.chat.completions.create(
        model="gpt-4",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are an AI expert in analyzing conversations and extracting action items. Please review the text and identify any tasks, assignments, or actions that were agreed upon or mentioned as needing to be done. These could be tasks assigned to specific individuals, or general actions that the group has decided to take. Please list these action items clearly and concisely."
            },
            {
                "role": "user",
                "content": transcription
            }
        ]
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=True)