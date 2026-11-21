# InkSpark

InkSpark is a Streamlit-powered AI writing assistant that transforms any topic into a structured, engaging blog post in seconds.
Students and creators can customize the tone and word count, preview the formatted post, and download the output as a Markdown file.

## Setup

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a Gemini API Key:**
   Get a free API key from Google AI Studio at:
   https://aistudio.google.com/app/apikey

4. **Configure your environment:**
   Copy `.env.example` to `.env` and paste your API key:
   ```bash
   # On Windows (cmd/PowerShell):
   copy .env.example .env
   # On macOS/Linux:
   cp .env.example .env
   ```
   Open `.env` and replace `your_gemini_api_key_here` with your actual key:
   ```env
   GEMINI_API_KEY=AIzaSy...
   ```

## Running the App

Start the Streamlit development server:
```bash
streamlit run app.py
```

The app will automatically open in your default browser at `http://localhost:8501`.

## Example to Try

- **Topic:** `How to start learning Python`
- **Tone:** `Friendly`
- **Approximate word count:** `600`
- Click **Generate Post** to create the blog post, then click **Download as Markdown** to save it locally.
