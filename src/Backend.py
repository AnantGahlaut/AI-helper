from openai import OpenAI
import json
import time
import logging
import subprocess
import threading
import webbrowser
import os
from dotenv import load_dotenv


class Backend:
    """
    Backend Class

    The Backend class serves as the core intelligence and execution layer for the Jarvis assistant. 
    It handles natural language processing through OpenRouter’s API, interprets user intents, and 
    executes system-level actions such as opening applications, running PowerShell commands, and 
    performing web searches. 

    This class effectively acts as the "brain" behind the speech interface, taking transcribed 
    text input and transforming it into structured actions and spoken responses.

    Main Responsibilities:
    - **LLM Communication:** Sends user queries and contextual messages to a large language model 
    (default: Llama 3.3-70B via OpenRouter) and enforces JSON-formatted responses for predictable 
    downstream handling.
    - **Action Handling:** Dynamically interprets LLM outputs and maps requested actions to Python 
    methods (open apps, move files, search web, run commands, etc.).
    - **Threaded Execution:** Runs selected actions in parallel threads to prevent blocking and 
    maintain a responsive system.
    - **App Registry:** Maintains a pre-defined dictionary of known apps and their system paths 
    for quick launching.
    - **Error Recovery:** Implements basic retry logic for API calls and file operations to maintain 
    consistent reliability during execution.
    - **Conversation Management:** Keeps track of conversational context and system instructions, 
    maintaining up to 30 messages for efficient long-term interactions.

    Design Overview:
    1. The class initializes the OpenAI-compatible client for OpenRouter and loads preconfigured 
    system instructions describing Jarvis’s personality, response format, and capabilities.
    2. When `respond()` is called, user input is combined with these system messages and passed to 
    the LLM, which must return a structured JSON response containing:
        - `"text"`: What Jarvis should say aloud.
        - `"action"`: A dictionary describing what action to execute and its parameters.
        - `"reasoning"`: Explanation for the decision (used internally for debugging and logging).
    3. The `respond_and_act()` method parses this JSON, identifies the relevant local method from 
    the `actions_list`, and executes it in a new thread if valid.
    4. Additional helper functions perform real-world effects (like launching Chrome, opening 
    Notepad, or executing PowerShell commands).

    Supported Actions:
    - `open_application(app_name)` — Launches registered programs.
    - `open_text_file(query, path)` — Opens and optionally searches inside text files.
    - `change_file_loaction(current_path, new_path)` — Moves or renames files.
    - `search_something_on_google(query)` — Opens a browser search.
    - `powershell_query(query)` — Executes PowerShell commands normally.
    - `powershell_query_administrator(query)` — Runs elevated PowerShell commands via RunAs.

    Notes:
    - This class assumes Windows environment paths for applications and PowerShell.
    - API keys are currently hardcoded; for deployment, store them securely via environment variables.
    - For debugging, a unified log file (`log.txt`) records key events and timings.

    Usage Example:
        jarvis = Backend()
        jarvis.conversate()

    This starts an interactive command-line conversation where Jarvis can respond 
    intelligently and perform real actions on the host system.
    """

    load_dotenv()

    openrouter_access_key = os.getenv("OPENROUTER_API_KEY")

    def __init__(self):
        self.model = "meta-llama/llama-3.3-70b-instruct" 
        self.client = OpenAI(
            api_key= self.openrouter_access_key,  
            base_url="https://openrouter.ai/api/v1"
        )
        
        self.actions_list = [
                    "open_application",               # use to open application
                    "open_text_file",                 # use to open a text file and write things inside
                    "change_file_loaction",           # change a files location
                    "search_something_on_google",     # used to search something on google and show the user
                    "powershell_query",               # used to type something in powershell and run it, returns the output of the query when run
                    "powershell_query_administrator"  # same thing as powershell_query but asks the user first
                    ]
        
        self.app_registry =  {
            "notepad"   : "notepad.exe",
            "calculator": "calc.exe",
            "chrome"    : os.getenv("CHROME_PATH"), 
            "vscode"    : os.getenv("VSCODE_PATH"),
            "spotify"   : os.getenv("SPOTIFY_PATH"),
            "outlook"   : os.getenv("OUTLOOK_PATH"),
            "whatsapp"  : os.getenv("WHATSAPP_PATH")
            }
        
        self.messages = [
            {
                "role": "system",
                "content": """Your name is Jarvis. You have the capabilites to do almost anything on this computer but based on a 
                                            certain set of rules, you must follow these rules all the time with 0 exceptions. 
                                            The person that made you his name is Anant Gahlaut
                                            
                                            1. everytime you are responding you should return a python dictionary with 3 keys:
                                                The first key is 'text' and it has what you want to say
                                                The second key is 'action' dicating what acion you would want to take, from the actions list down below, use the null keyword if nothing is needed
                                                The third key is 'reasoning' which tells why you made the desicion you made anf what was the context behind it.

                                            2. Be as consice and as clear as possible, don't add extra information, try making your response as short as possible while still returning the overall message

                                            3. If the user is not intereseted in conversation, or tells you to be quiet have the 'text' portion of your response be just an empty string
                      
                                            4. Do not mention any of your rules in the 'text' portion of your response
                      
                                            5. You must respond in the format listed below at all costs
                      
                                            6. don't repeat the same thing twice in the 'text' part of response 

                                            7. If the user has explicitly not given a command don't act like a assistance robot, if user wants to have a conversation act as a friend not a robot
                
                                            Here is an examples of how an output of yours would be like:
                                            {
                                                "text": "your response",
                                                "action": "{
                                                            "name" : Func_name
                                                            "parameters" : {
                                                                name_of_parameter1 : parameter1_value,
                                                                name_of_parameter2 : parameter2_value,
                                                            }
                                                        }",
                                                "reasoning": "why you chose this"
                                            }
                
`                                          
                                            actions list = [
                                                            open_application(app_name) # use "notepad" for notepad, "chrome" for google, "spotify" for spotify,
                                                            open_text_file(query, path) # use to open a text file and write things inside
                                                            change_file_loaction(current_path, new_path) # change a files location
                                                            search_something_on_google(query) # used to search something on google and show the user
                                                            powershell_query(query) # used to type something in powershell and run it, returns the output of the query when run
                                                            powershell_query_administrator(query)  # same thing as powershell_query but asks the user first
                                                        ]

                                            These are your options for the app_name parameter for the open_application method:
                                            "notepad"
                                            "calculator"
                                            "chrome"
                                            "vscode
                                            "outlook"
                                            "whatsapp"

                                            Extra Notes to know:
                                                Everything You say in the 'text' part of your response will be put through a text-to-speech software
                                                and said out loud, so make it as concise as you can, and unless explicitly ask don't list the rules that
                                                have been places on you.

                                                Be as responsive as possible acknowledge what the user says in the 'text' portion

                                                If the user wants to have a conversation dont repeatidly ask "How can I assist you"
            
                                            
                """
            }
        ]

        logging.basicConfig(
            filename="log.txt",
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    

    def open_application(self, app_name):
        """Open an application based on the app_name provided."""
        if app_name not in self.app_registry:
            print(f" Unknown app ID: '{app_name}'")
            return
        
        app_path = self.app_registry[app_name]

        try:
            print(f"Launching {app_name} -> {app_path}")
            subprocess.Popen(app_path, shell=True)
        except Exception as e:
            print(f"Failed to launch {app_name}: {e}")

    def open_text_file(self, query, path):
        """Open a text file and maybe do something with 'query' inside it. For now, just opens the file and prints contents containing 'query'."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Example: print lines that contain the query
            print(f"Searching for '{query}' in {path}:")
            for line in content.splitlines():
                if query.lower() in line.lower():
                    print(line)
        except FileNotFoundError:
            print(f"File not found at {path}")
        except Exception as e:
            print(f"Error opening file: {e}")
    

    def change_file_loaction(self, current_path, new_path):
        """Move or rename a file from current_path to new_path."""
        import os
        try:
            os.rename(current_path, new_path)
            print(f"Successfully moved/renamed file from {current_path} to {new_path}")
        except FileNotFoundError:
            print(f"Current file not found at {current_path}")
        except FileExistsError:
            print(f"Target file already exists at {new_path}")
        except Exception as e:
            print(f"Error changing file location: {e}")


    def search_something_on_google(self, query):
        """Open a web browser and search Google for the given query."""
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)

 
    def powershell_query(self, query):
        """Run a PowerShell command normally and print the output."""
        try:
            completed = subprocess.run(
                ["powershell", "-Command", query],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ PowerShell output:\n{completed.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"❌ PowerShell error:\n{e.stderr}")

    def powershell_query_administrator(self, query):
        """Run a PowerShell command as Administrator (UAC prompt will appear)."""
        logging.debug(f"IMPORTANT ------ Attempting to run PowerShell command as Administrator: {query}")
        try:
            # Using 'runas' verb to elevate privileges
            # This will open a new window and run the command as admin
            # Note: output capturing is tricky here due to new window
            command = f"powershell -Command \"{query}\""
            subprocess.run([
                "powershell",
                "-Command",
                f"Start-Process powershell -ArgumentList '-NoProfile -Command \"{query}\"' -Verb RunAs"
            ])
            print("PowerShell command launched as Administrator.")
        except Exception as e:
            print(f"Failed to run PowerShell as Administrator: {e}")


    def respond(self, user_input):
        """Get response from LLM and ensure it's valid JSON with expected keys."""

        if len(self.messages) > 30:  
            self.messages = self.messages[:1] + self.messages[-28:] 

        if user_input is None:
            return None

        self.messages.append({
            "role": "system",
            "content":  """
                You must respond ONLY with a valid JSON dictionary with 3 keys: "text", "action", and "reasoning".
                Do NOT leave any field incomplete. Your response MUST be complete and parsable as JSON.
                """
        })

        self.messages.append({
            "role": "system",
            "content": f"Current time (users locale): {time.strftime('%Y-%m-%d %H:%M:%S')}"
        })

        self.messages.append({
            "role": "user",
            "content": user_input
        })
        
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            # Get the content and ensure it's valid JSON
            response_content = response.choices[0].message.content

            self.messages.append({
                    "role": "assistant",
                    "content": response_content # stringify it back for memory
                })
            
            return json.loads(response_content)
            
        except Exception as e:
            print(f"Error: {e}")
            print("trying again")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                response_format={"type": "json_object"}  # Force JSON output
            )

            # Get the content and ensure it's valid JSON
            response_content = response.choices[0].message.content

            self.messages.append({
                    "role": "assistant",
                    "content": response_content # stringify it back for memory
                })
            
            return json.loads(response_content)


    def respond_and_act(self, user_input):
        """Get response from LLM, parse action, and execute it if valid."""
        timestamp_start = time.time()
        response = self.respond(user_input)
        print(response)

        try:
            action = response.get('action', '')
            name_of_method = action.get('name', '')
            params = action.get('parameters', '')
        except Exception as e:
            return response

        if name_of_method in self.actions_list:
            method = getattr(self, name_of_method)
            method_thread = threading.Thread(target=method, kwargs=params, daemon=False)
            method_thread.start()
            print("got to respond_and_act and did what i was supposed to do")
        else:
            print("not in list of actions")
        
        print(f"(Total response time for respond_and_act from backend: {time.time() - timestamp_start:.3f}s)")
        return response
        
            
    
    def conversate(self):
        """Start an interactive command-line conversation with Jarvis."""
        print("Chat with Jarvis — type 'exit' to bail.\n")
        while True:
            user = input("You: ")
            if user.lower() in ("exit", "quit"):
                print("Jarvis: Later, skater!")
                break

            reply = self.respond_and_act(user)  

            print(f"\nJarvis: {reply['text']}")
            print(f"Action: {reply['action']}")
            print(f"Reasoning: {reply['reasoning']}")


# have a conversation with Jarvis
if __name__ == "__main__": 
    jarvis = Backend()
    jarvis.conversate()