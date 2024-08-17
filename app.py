from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from translate import Translator
from langdetect import detect

app = Flask(__name__)
CORS(app)

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'speech_app_db'
}

# Function to connect to the database
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# Test database connection route
@app.route('/test-db')
def test_db_connection():
    connection = get_db_connection()
    if connection and connection.is_connected():
        return "Successfully connected to the database"
    else:
        return "Failed to connect to the database"

# Translation function using MyMemory API via translate package
def translate_text(text, target_language='en'):
    translator = Translator(to_lang=target_language)
    translation = translator.translate(text)
    return translation

# Route to handle transcription submission
@app.route('/submit', methods=['POST'])
def submit_transcription():
    data = request.json
    user_id = data.get('user_id')
    transcription = data.get('transcription')
    language = data.get('language', 'en')
    
    # Error handling for missing data
    if not user_id or not transcription:
        return jsonify({"error": "Missing user_id or transcription"}), 400
    
    # Detect language and translate if necessary
    try:
        detected_language = detect(transcription)
        translation = transcription if detected_language == 'en' else translate_text(transcription, target_language='en')
    except Exception as e:
        return jsonify({"error": "Language detection or translation failed", "details": str(e)}), 500

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor()

    try:
        # Insert transcription
        query = "INSERT INTO transcriptions (user_id, transcription, translated_transcription, language) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (user_id, transcription, translation, detected_language))
        connection.commit()

        # Calculate word frequencies for the user
        words = translation.split()
        for word in words:
            cursor.execute("SELECT frequency FROM word_frequencies WHERE user_id = %s AND word = %s", (user_id, word))
            result = cursor.fetchone()
            if result:
                cursor.execute("UPDATE word_frequencies SET frequency = frequency + 1 WHERE user_id = %s AND word = %s", (user_id, word))
            else:
                cursor.execute("INSERT INTO word_frequencies (user_id, word, frequency) VALUES (%s, %s, 1)", (user_id, word))

        connection.commit()
    except Error as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return jsonify({"message": "Transcription submitted successfully!"})

# Route to calculate word frequencies
@app.route('/frequencies/<int:user_id>', methods=['GET'])
def get_word_frequencies(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT word, frequency FROM word_frequencies WHERE user_id = %s ORDER BY frequency DESC", (user_id,))
        user_frequencies = cursor.fetchall()

        cursor.execute("SELECT word, SUM(frequency) AS frequency FROM word_frequencies GROUP BY word ORDER BY frequency DESC")
        global_frequencies = cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return jsonify({"user_frequencies": user_frequencies, "global_frequencies": global_frequencies})

# Route to identify top 3 unique phrases
@app.route('/unique_phrases/<int:user_id>', methods=['GET'])
def get_unique_phrases(user_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT phrase FROM unique_phrases WHERE user_id = %s ORDER BY frequency DESC LIMIT 3", (user_id,))
        top_phrases = cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return jsonify({"top_phrases": top_phrases})

# Add the similarity detector route here (if implemented)

if __name__ == '__main__':
    app.run(debug=True)
