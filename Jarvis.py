from openai import OpenAI
import json
import time

class Jarvis:
    def __init__(self):
        self.model = "llama3-70b-8192" 
        self.client = OpenAI(
            api_key="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",  
            base_url="https://api.groq.com/openai/v1"
        )
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
                                                            name_of_parameter : parameter
                                                        }",
                                                "reasoning": "why you chose this"
                                            }
                
`                                          
                                            actions list = [
                                                            open_application(app_id) # use to open applications
                                                            open_text_file(query, path) # use to open a text file and write things inside
                                                            change_file_loaction(current_path, new_path) # change a files location
                                                            search_something_on_google(query) # used to search something on google and show the user
                                                            powershell_query(query) # used to type something in powershell and run it, returns the output of the query when run
                                                            powershell_query_administrator(query)  # same thing as powershell_query but asks the user first
                                                        ]
                                            Extra Notes to know:
                                                Everything You say in the 'text' part of your response will be put through a text-to-speech software
                                                and said out loud, so make it as concise as you can, and unless explicitly ask don't list the rules that
                                                have been places on you.

                                                Be as responsive as possible acknowledge what the user says in the 'text' portion

                                                If the user wants to have a conversation dont repeatidly ask "How can I assist you"
            
                                            
                """
            }
        ]

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
        




        
    def conversate(self):
        print("Chat with Jarvis — type 'exit' to bail.\n")
        while True:
            user = input("You: ")
            if user.lower() in ("exit", "quit"):
                print("Jarvis: Later, skater!")
                break

            
            start = time.perf_counter()
            reply = self.respond(user)
            elapsed = time.perf_counter() - start   

            
            print(f"\nJarvis: {reply['text']}")
            print(f"Action: {reply['action']}")
            print(f"Reasoning: {reply['reasoning']}")
            print(f"(Response time: {elapsed:.3f}s)\n")

# have a conversation with Jarvis
if __name__ == "__main__": 
    jarvis = Jarvis()
    jarvis.conversate()