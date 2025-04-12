# from flask import Flask, request, jsonify, render_template
# from query import search_fund  # Assuming this performs the actual fund search logic
# from utils import format_fund_result  # Make sure this function is in the utils module

# app = Flask(__name__)

# @app.route("/")
# def home():
#     return render_template("index.html")

# @app.route("/query", methods=["POST"])
# def query():
#     data = request.get_json()  # Get JSON data from the frontend
#     user_query = data.get("query")
    
#     if not user_query:
#         return jsonify({"error": "Missing 'query' field"}), 400

#     # Search for funds based on the user's query
#     matches = search_fund(user_query)  # This function should return a list of fund results
#     print("Raw result:", matches)
#     # Format each result using the format_fund_result function
#     results = [format_fund_result(f) for f in matches]
    
#     # Return the formatted results in JSON format
#     return jsonify({"results": results})

# if __name__ == "__main__":
#     app.run(debug=True)
from flask import Flask, request, jsonify, render_template
from query import search_fund  # Assuming this performs the actual fund search logic
from utils import format_fund_result  # Make sure this function is in the utils module

# ✅ START: Ensure Ollama is running and model is pulled
import subprocess
import requests
import time

def ensure_ollama_running():
    try:
        # Check if Ollama server is running
        requests.get("http://localhost:11434", timeout=2)
        print("✅ Ollama is already running.")
    except requests.exceptions.RequestException:
        print("🟡 Starting Ollama server...")
        subprocess.Popen(["ollama", "serve"])
        time.sleep(2)  # Let it start

    try:
        # Check if mistral model is available
        models = requests.get("http://localhost:11434/api/tags").json()
        model_names = [m["name"] for m in models.get("models", [])]
        if "mistral" not in model_names:
            print("⬇️ Pulling mistral model...")
            subprocess.run(["ollama", "pull", "mistral"], check=True)
        else:
            print("✅ Mistral model already pulled.")
    except Exception as e:
        print("❌ Could not verify or pull mistral model:", e)

# Run this once before starting Flask
ensure_ollama_running()
# ✅ END

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()  # Get JSON data from the frontend
    user_query = data.get("query")
    
    if not user_query:
        return jsonify({"error": "Missing 'query' field"}), 400

    # Search for funds based on the user's query
    matches = search_fund(user_query)  # This function should return a list of fund results
    print("Raw result:", matches)

    # Format each result using the format_fund_result function
    results = [format_fund_result(f) for f in matches]
    
    # Return the formatted results in JSON format
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True)
