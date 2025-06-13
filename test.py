import webbrowser

def search_something_on_google(query):
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)

actions_list = [
                    "open_application",               # use to open application
                    "open_text_file",                 # use to open a text file and write things inside
                    "change_file_loaction"            # change a files location
                    "search_something_on_google",     # used to search something on google and show the user
                    "powershell_query",               # used to type something in powershell and run it, returns the output of the query when run
                    "powershell_query_administrator"  # same thing as powershell_query but asks the user first
                    ]


print("search_something_on_google" in actions_list)