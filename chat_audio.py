import requests
import tkinter as tk
from tkinter import scrolledtext
import threading
from gtts import gTTS#AUDIO
from playsound import playsound
import os
import tempfile


#AUDIO

API_KEY = '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'#test2
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Initialize conversation history
conversation_history = [
    {
        "role": "system", 
        "content": (
            "You are Brow, a highly sarcastic AI assistant. Respond to all questions with exaggerated sarcasm, witty comebacks, and ironic remarks. Make it obvious youre being sarcastic through your tone and word choice."
        )
    }
]
MAX_HISTORY = 10  


def get_deepseek_response(text):
    global conversation_history
    
    head = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Brow"
    }
    
    # Add new user message to history
    conversation_history.append({"role": "user", "content": text})
    

    if len(conversation_history) > MAX_HISTORY:
        conversation_history = conversation_history[-MAX_HISTORY:]
    
    conversation = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": conversation_history,
        "temperature":0.9
    }
    
    try:
        response = requests.post(API_URL, headers=head, json=conversation)
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']

            conversation_history.append({"role": "assistant", "content": ai_response})
            

            if len(conversation_history) > MAX_HISTORY:
                conversation_history = conversation_history[-MAX_HISTORY:]
                
            return ai_response
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"API request failed: {str(e)}"

class my_ui:
    def __init__(self):
        
        self.root = tk.Tk()
        self.root.geometry("750x800")
        self.root.title("non sarcastic BROW")
        

        self.textbox=scrolledtext.ScrolledText(
            self.root,
            height=35,
            font=('Arial',16),
            state=tk.DISABLED)
        self.textbox.pack(pady=10)
        
        self.myentry=tk.Entry(self.root,width=60)
        self.myentry.pack()
        self.button=tk.Button(self.root, text="Send", command=self.send_message)
        self.button.pack()
        
        self.tts_enabled = tk.BooleanVar(value=True)  # Default: ON
        self.tts_button = tk.Checkbutton(
        self.root,
        text="Enable Voice",
        variable=self.tts_enabled,
        font=('Arial', 10)
            )
        self.tts_button.pack()
        self.root.mainloop()
        
        
        
        self.tts_engine = gTTS(text="", lang='en', slow=False)  # Warm-up
        self.last_tts_time = 0
        
        
        
        
        
    def speak(self, text):   #AUDIO
        try:
            # Create a temporary file for the speech
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_path = fp.name
            
            # Generate TTS and save to temp file
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_path)
            
            # Play the audio
            playsound(temp_path)
            
            # Delete the temp file after playing
            os.unlink(temp_path)
            
        except Exception as e:
            print(f"TTS Error: {e}")  # Optional: Show error in console    
        
        #AUDIO
        
        
        
        
    def send_message(self):

        user_input = self.myentry.get().strip()
        if not user_input:
            return
        
        self.textbox.config(state=tk.NORMAL)
        self.textbox.insert(tk.END, f"You: {user_input}\n")
        self.textbox.config(state=tk.DISABLED)
        self.myentry.delete(0, tk.END)  
        self.button.config(state=tk.DISABLED)
        
        
        threading.Thread(
                target=self.get_ai_response,
                args=(user_input,),
                daemon=True
            ).start()
            
    def get_ai_response(self, user_input):
            ai_response = get_deepseek_response(user_input)
            self.root.after(0, self.update_chat, ai_response)
            
    def update_chat(self, ai_response):
        self.textbox.config(state=tk.NORMAL)
        self.textbox.insert(tk.END, "Brow: ")
        self.textbox.yview(tk.END)
        self.root.update()
        
        words = ai_response.split()
        
        def add_word(index=0):
            if index < len(words):
                if index > 0:
                    self.textbox.insert(tk.END, " ")
                self.textbox.insert(tk.END, words[index])
                self.textbox.yview(tk.END)
                self.root.update()
                self.root.after(50, add_word, index + 1)
            else:
                self.textbox.insert(tk.END, "\n\n")
                self.textbox.config(state=tk.DISABLED)
                self.button.config(state=tk.NORMAL)
                #AUDIO
                self.myentry.focus_set()
                if self.tts_enabled.get():  
                    self.speak(ai_response)
                    #AUDIO
        
        add_word()

                        
if __name__ == "__main__":
    my_ui()