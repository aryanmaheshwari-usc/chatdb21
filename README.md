# chatdb21
# 🧠 Natural Language Query Interface for MySQL and MongoDB (LLM-Powered) <br>

# This project is a Streamlit web application that allows users to interact with **MySQL** and **MongoDB** databases using **natural language queries**. The app uses **OpenAI's GPT-4 model** to convert user input into executable SQL or MongoDB queries, then displays the results. <br>

# It supports: <br>
# - Schema-aware SQL generation for structured market data (in MySQL) <br>
# - Structured MongoDB command generation for unstructured text collections (like news and earnings transcripts) <br>
# - Fully dynamic execution of generated queries <br>

# --- <br>

## ✅ Prerequisites <br>

### 📦 Software Requirements <br>
# Before running this app, make sure you have the following installed: <br>

# 1. **Python 3.8+** <br>
# 2. **MySQL Server** (ensure the `market_data` database is created and running) <br>
# 3. **MongoDB Server** (running locally on `localhost:27017`) <br>
# 4. **pip** for installing Python packages <br>

### 🔑 API Key <br>
# You must have an **OpenAI API key** (preferably with GPT-4 access). <br>

# Replace the API key placeholder in the script: <br>
# ```python  
# openai.api_key = 'sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' 