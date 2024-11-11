import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from groq import Groq
import re

# Cargar variables de entorno
load_dotenv()

# Crear aplicación Flask
app = Flask(__name__)

# Cliente de Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Historial de mensajes
messages = []

# Cargar el system prompt desde archivo
def load_system_prompt():
    try:
        with open("system_prompt.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "No se encontró el archivo system_prompt.txt."

# Función para extraer bloques de código
def extract_code_blocks(text):
    pattern = r"```[\w]*\n(.*?)```"
    code_blocks = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
    return code_blocks, "\n\n".join(code_blocks)

# Función para hacer una solicitud a Groq
def ask_groq(messages):
    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-70b-versatile",
            temperature=1,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error connecting to Groq API: {e}"

@app.route("/ask", methods=["POST"])
def ask():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Añadir mensaje del usuario al historial
    if not messages:
        messages.append({"role": "system", "content": load_system_prompt()})
    messages.append({"role": "user", "content": user_message})

    # Pedir respuesta al modelo Groq
    response = ask_groq(messages)
    code_blocks, code_content = extract_code_blocks(response)

    # Guardar respuesta y actualizar historial
    messages.append({"role": "assistant", "content": response})

    return jsonify({
        "response": response,
        "code": code_content
    })

if __name__ == "__main__":
    app.run(debug=True)
