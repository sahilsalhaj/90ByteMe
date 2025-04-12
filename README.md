# MyFi Hackathon Project

## Overview
Welcome to my MyFi Hackathon project! 🎉  
This Flask-based web application lets you query and analyze a variety of financial data, including Indian equities, mutual funds, and ETFs. The system uses machine learning techniques to process natural language queries and fetch relevant results from large datasets. 

This project leverages powerful tools like FAISS for vector-based search, SentenceTransformers for embeddings, and Mistral for query classification. Whether you're interested in analyzing stock performance, mutual fund returns, or sector allocation, this app has got you covered!

## What Does It Do?
- **Natural Language Query Handling**: You can type queries in natural language (e.g., "Which mutual funds have the highest returns in the last 5 years?") and get accurate results.
- **Query Classification**: Queries are classified using Mistral, ensuring that your question is understood, whether it's about stock data, mutual funds, or ETFs.
- **Vector Search with FAISS**: Once your query is classified, it's converted into a vector using SentenceTransformers and searched in large datasets using FAISS. This makes searches fast and accurate.
- **Financial Data**: It works with a set of datasets including Indian stock data, mutual funds, and ETF holdings to answer a variety of financial questions.

## Tech Stack
- Flask: Web framework for the backend.
- SentenceTransformers: To generate vector embeddings for query understanding.
- FAISS: For fast similarity search in large datasets.
- Mistral: Used for classifying and categorizing queries into specific financial topics.
- Python 3.x: The language used for all the backend development.

## How It Works
1. **User Input**: The user enters a query like "Which mutual funds have the highest returns in the last 5 years?" in the search box on the homepage.
2. **Query Classification**: The query is passed to query_classifier.py, where Mistral classifies it into categories like "performance", "sector", or "fund".
3. **Embedding Generation**: The query is then passed to embedder.py, which uses SentenceTransformers to generate an embedding (vector).
4. **FAISS Search**: The generated vector is used to search the relevant dataset (stocks, mutual funds, etc.) using FAISS for a quick search and retrieval of similar entries.
5. **Reranking**: Results are reranked to ensure the most relevant ones appear at the top (based on things like returns, risk, etc.).
6. **Display Results**: The results are returned and displayed on the user interface in a clean and understandable format.

## Setting Up Locally
1. **Clone the Repo**:
    ```
    git clone https://github.com/yourusername/myfi-hackathon.git
    cd myfi-hackathon
    ```

2. **Create a Virtual Environment** (Optional but recommended):
    ```
    python3 -m venv venv
    source venv/bin/activate   # On Windows, use: venv\Scripts\activate
    ```

3. **Install Dependencies**:
    ```
    pip install -r requirements.txt
    ```

4. **Run the Application**:
    ```
    python app.py
    ```
    This will start the Flask server, and you can access the application at http://localhost:5000/.

## Datasets
The application uses the following datasets:
1. **cleaned_stock_data.json**: Contains data on Indian equities like stock names, market caps, P/E ratios, volatility, returns, and more.
2. **mutual_funds_cleaned.json**: Contains data on Indian mutual funds, such as their names, AUM (Assets Under Management), returns, asset allocation, and financial metrics.
3. **mutual_holdings_cleaned.json**: Contains information about the stocks within various mutual funds, including stock names, sectors, and their respective weightings in the fund.

## How Query Classification Works
We use Mistral to classify user queries into different categories. Here's an example:
- **Entity Query**: "Show me mutual funds by XYZ Fund House."
- **Sector Query**: "Which funds invest in the technology sector?"
- **Performance Query**: "What are the top-performing funds in the last 3 years?"
- **Tax Query**: "What is the tax impact of investing in a Fixed Maturity Plan?"

Mistral classifies each query, which helps the system decide which dataset to search and how to present the results.

## Customizing the App
- You can easily add more datasets by following the format of the existing data files and updating indexer.py to create FAISS indexes for them.
- To adjust how the app ranks and filters results, look into the reranking logic inside query.py.

## Future Improvements
- **User Interface**: Add more interactive visualizations to make the app more user-friendly.
- **Better Ranking**: Experiment with different ranking algorithms to improve the quality of the search results.
- **Extended Data**: Integrate more financial data sources, such as debt funds, ETFs, or international stocks.

## License
Feel free to use and modify this code for personal or educational purposes! For commercial use, you may want to check the licensing of the third-party libraries used in the project.

## Contact
If you have any questions or suggestions, feel free to reach out to me:

- Email: youremail@example.com
- GitHub: https://github.com/yourusername

Hope you enjoy exploring the project! 😄🚀
