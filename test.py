import json

text = """{ 
    "text" : "hello",
    "action" : null,
    "reasoning" : "user needs to be said hi too"
}"""

# Convert the JSON string to a Python dictionary
data = json.loads(text)

# Print the type of the variable 'data'
print(type(data))
