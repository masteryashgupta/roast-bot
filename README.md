# Unfiltered Roast Bot

An unfiltered roast bot. Chat for fun in the terminal, completely unfiltered.

### Setup Checklist:

1. **Environment Variables**: Copy `.env.example` to a new file named `.env` and fill in the values:
   - **Groq**: Get `GROQ_API_KEY` from console.groq.com.
2. **Install Dependencies**: 
   ```bash
   pip install -r requirements.txt
   ```
3. **Run**: 
   ```bash
   python main.py
   ```

### Features:
- Terminal-based REPL chat loop.
- Colored ANSI aesthetic with JetBrains Mono style vibes.
- Short conversational memory.
- Uses Groq API for rapid response.
