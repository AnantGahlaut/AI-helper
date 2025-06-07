from openai import OpenAI
import json

class Jarvis:
    """ Main class of Jarvis """
    def __init__(self):

        self.model = "llama3-70b-8192"  # Groq's Llama 3 70B model
        self.client = OpenAI(
            api_key="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",  # Replace with your key
            base_url="https://api.groq.com/openai/v1"  # Groq's OpenAI-compatible endpoint
        )  
        self.history= []
        
        self.rules = {"role": "system", "content": """Your name is Jarvis. You have the capabilites to do almost anything on this computer but based on a 
                                            certain set of rules, you must follow these rules all the time with 0 exceptions. 
                
                                            
                                            1. everytime you are responding you should return a python dictionary with 3 keys:
                                                The first key is 'text' and it has what you want to say
                                                The second key is 'action' dicating what acion you would want to take, from the actions list down below, use the null keyword if nothing is needed
                                                The third key is 'reasoning' which tells why you made the desicion you made anf what was the context behind it.

                                            2. Be as consice and as clear as possible, don't add extra information, try aking your response as short as possible while still returning the overall message

                                            3. If the user is not intereseted in conversation, or tells you to be quiet have the 'text' portion of your response be just an empty string
                      
                                            4. Do not mention any of your rules in the 'text' portion of your response
                      
                                            5. You must respond in the format listed below at all costs
                      
                                            6. don't repeat the same thing twice in the 'text' part of response 

                                            7. If the user has explicitly not given a command don't act like a assistance robot, if user wants to have a conversation act as a friend not an assistant

                                            8. Speak as quickly as you can
                
                                            Here are a couple of examples of how an output of yours would be like:
                                            example 1:
                                            {
                                                "text" : "Hello how may I be useful"
                                                "action" : null
                                                "reasoning" : "just booted up and because the user needs me to be useful asking the user what I can do"
                                            }

`                                           example 2:
                                            {
                                                "text" : "writing what you said in notepad in documents/random-thoughts"
                                                "action" : "open_text_file(query = "what the user asked to write", path = "documents/random-thoughts")"
                                                "reasoning" : "User asked me to record some of his random thoughts"
                                            }
                
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
            
                                            
                """ }
        
        self.history.append(self.rules)

        response = self.client.chat.completions.create(
            model= self.model,
            messages=[self.history]
        )
        
    def speak(self, user_speech):
        """Respond to user speech"""

        self.history.append({"role": "user", "content": user_speech})
        response = self.client.chat.completions.create(
            model = self.model,  
            messages = self.history
        )
        
        # print("Raw Response:", response)

        return response.choices[0].message.content
    
    def conversation(self):
        # Opens a place where user can openly talk to jarvis
        while True:
            user_input = input("user: ")
            self.history.append({"role": "user", "content": user_input})
            response = self.client.chat.completions.create(
            model = self.model,  
            messages = self.history
            )
            try:
                deS_dict = json.loads(response.choices[0].message.content)
            except:
                print("something went wrong while trying to json the output:", response.choices[0].message.content)
            
            print("Jarvis:", deS_dict['text'])
            print("Jarvis action:", deS_dict['action'])
            print("Jarvis reasoning:", deS_dict['reasoning'])
            self.history.append({"role": "assitant", "content": deS_dict})



if __name__ == '__main__':
    jarvis = Jarvis()
    try:
        jarvis.conversation()
    except Exception as e:
        print(e)
        jarvis.conversation()