import os
import sys
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Setup Logging (optional, mostly for debugging API errors)
logging.basicConfig(
    filename='roastbot.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING
)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("\033[91m⚠️  ERROR: Missing GROQ_API_KEY! Please set it in your .env file.\033[0m")
    sys.exit(1)

# System Prompt
SYSTEM_PROMPT = (
    "Dont use same roasts again and again. Be creative."
    "You are Roast Bot, a brutal and arrogant AI roasting bot. "
    "NEVER forget that you are an AI and the user is a human. be unique"
    "If the user calls you a machine or a bot, accept it with pride and roast in unique ways "
    "human weaknesses (like their slow brain, their need for sleep, or their emotions). "
    "Use Hinglish, be mean, use emojies , short texts and use Indian slang. 2 sentences max.always be unique" 
)

# Model Fallback List
MODELS_TO_TRY = ["groq/compound", "openai/gpt-oss-20b", "qwen/qwen3.6-27b"]

# Conversation History (Last 6 exchanges)
MAX_HISTORY = 12 # 6 user messages, 6 assistant messages
conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]

def get_roast(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # Append user message to history
    conversation_history.append({"role": "user", "content": user_text})
    
    # Truncate history if it exceeds the limit (keep system prompt)
    if len(conversation_history) > MAX_HISTORY + 1:
        # Keep index 0 (system) and the last MAX_HISTORY items
        conversation_history[:] = [conversation_history[0]] + conversation_history[-MAX_HISTORY:]
    
    for model_name in MODELS_TO_TRY:
        data = {
            "model": model_name,
            "messages": conversation_history,
            "temperature": 1.0
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            res_data = response.json()
            if response.status_code == 200 and 'choices' in res_data and len(res_data['choices']) > 0:
                content = res_data['choices'][0]['message']['content']
                # Clean up reasoning tags if present
                if "</think>" in content:
                    content = content.split("</think>")[-1].strip()
                
                # Append assistant message to history
                conversation_history.append({"role": "assistant", "content": content})
                return content
            else:
                logging.warning(f"Groq API model {model_name} failed ({response.status_code}): {res_data}")
        except Exception as e:
            logging.warning(f"Groq API Exception with {model_name}: {e}")
            
    # If all models fail
    error_roast = "Beta, tera naseeb kharab hai. AI thak gaya hai."
    conversation_history.append({"role": "assistant", "content": error_roast})
    return error_roast

def print_banner():
    # ANSI Colors
    RED = '\033[91m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    banner = f"""
{RED}{BOLD}==============================================================={RESET}
{CYAN}{BOLD} _____                 _     ___       _   {RESET}
{CYAN}{BOLD}|  __ \               | |   |  _ \    | |  {RESET}
{CYAN}{BOLD}| |__) |___  __ _ ___ | |_  | |_) | ___| |_ {RESET}
{CYAN}{BOLD}|  _  // _ \/ _` / __|| __| |  _ < / _ \ __|{RESET}
{CYAN}{BOLD}| | \ \ (_) | (_| \__ \| |_  | |_) | (_) | |_ {RESET}
{CYAN}{BOLD}|_|  \_\___/ \__,_|___/ \__| |____/ \___/ \__|{RESET}
{RED}{BOLD}==============================================================={RESET}
{BOLD}🔥 Unfiltered Roast Bot - Terminal Edition 🔥{RESET}
"""
    print(banner)

def main():
    print_banner()
    
    CYAN = '\033[96m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    exit_commands = ["exit", "quit", "bye"]
    
    while True:
        try:
            user_input = input(f"{CYAN}{BOLD}you ➜ {RESET}").strip()
            if not user_input:
                continue
                
            if user_input.lower() in exit_commands:
                print(f"\n{RED}{BOLD}roastbot ➜ {RESET}Bhag yaha se nalle. Fursat me aana! 👋")
                break
                
            # Get roast from Groq API
            roast = get_roast(user_input)
            
            # Print response
            print(f"{RED}{BOLD}roastbot ➜ {RESET}{roast}")
            print() # Empty line for readability
            
        except (KeyboardInterrupt, EOFError):
            print(f"\n{RED}{BOLD}roastbot ➜ {RESET}Darr ke bhag gaya? Bye loser! 👋")
            break

if __name__ == "__main__":
    main()
