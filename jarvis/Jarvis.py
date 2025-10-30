from openai import OpenAI
import json
import time
import functools
import subprocess
import inspect
import threading
import webbrowser

class Jarvis:
    groq_access_key = "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"
    openrouter_access_key = "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"
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
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "vscode": r"C:\Users\anant\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "spotify": r"C:\Program Files\WindowsApps\SpotifyAB.SpotifyMusic_1.265.255.0_x64__zpdnekdrzrea0\Spotify.exe", # needs fixing not right path or some admin error fix later
            "outlook" : r"C:\Program Files\WindowsApps\Microsoft.OutlookForWindows_1.2025.604.100_x64__8wekyb3d8bbwe\olk.exe",
            "whatsapp" : r"C:\Program Files\WindowsApps\5319275A.WhatsAppDesktop_2.2522.2.0_x64__cv1g1gvanyjgm\WhatsApp.exe"
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

                                            2. Be as consice and as clear as possible, don't add extra information, try aking your response as short as possible while still returning the overall message

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
    

    def open_application(self, app_name):
        if app_name not in self.app_registry:
            print(f"❌ Unknown app ID: '{app_name}'")
            return
        
        app_path = self.app_registry[app_name]

        try:
            print(f"🚀 Launching {app_name} -> {app_path}")
            subprocess.Popen(app_path, shell=True)
        except Exception as e:
            print(f"💥 Failed to launch {app_name}: {e}")

    def open_text_file(self, query, path):
        """
        Open a text file and maybe do something with 'query' inside it.
        For now, just opens the file and prints contents containing 'query'.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Example: print lines that contain the query
            print(f"Searching for '{query}' in {path}:")
            for line in content.splitlines():
                if query.lower() in line.lower():
                    print(line)
        except FileNotFoundError:
            print(f"⚠️ File not found at {path}")
        except Exception as e:
            print(f"❌ Error opening file: {e}")
    

    def change_file_loaction(self, current_path, new_path):
        """
        Move or rename a file from current_path to new_path.
        """
        import os
        try:
            os.rename(current_path, new_path)
            print(f"✅ Successfully moved/renamed file from {current_path} to {new_path}")
        except FileNotFoundError:
            print(f"⚠️ Current file not found at {current_path}")
        except FileExistsError:
            print(f"⚠️ Target file already exists at {new_path}")
        except Exception as e:
            print(f"❌ Error changing file location: {e}")


    def search_something_on_google(self, query):
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)

 
    def powershell_query(self, query):
        """
        Run a PowerShell command normally and print the output.
        """
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
        """
        Run a PowerShell command as Administrator (UAC prompt will appear).
        """
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
            print("✅ PowerShell command launched as Administrator.")
        except Exception as e:
            print(f"❌ Failed to run PowerShell as Administrator: {e}")


    def respond(self, user_input):
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
        
        return response
        
            
    
    def conversate(self):
        print("Chat with Jarvis — type 'exit' to bail.\n")
        while True:
            user = input("You: ")
            if user.lower() in ("exit", "quit"):
                print("Jarvis: Later, skater!")
                break

            
            start = time.perf_counter()
            reply = self.respond_and_act(user)
            elapsed = time.perf_counter() - start   

            
            print(f"\nJarvis: {reply['text']}")
            print(f"Action: {reply['action']}")
            print(f"Reasoning: {reply['reasoning']}")
            print(f"(Response time: {elapsed:.3f}s)\n")

# have a conversation with Jarvis
if __name__ == "__main__": 
    jarvis = Jarvis()
    jarvis.conversate()