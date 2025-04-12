from flask import Flask, request, jsonify, render_template
from query import search_fund  # Assuming this performs the actual fund search logic
from utils import format_fund_result  # Make sure this function is in the utils module

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
