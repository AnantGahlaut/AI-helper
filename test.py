from openai import OpenAI

client = OpenAI(api_key="sk_wRpyywMpqd5cZ47rPI8MWGdyb3FYnuN2oeT0546eQN7rl8QrZHcC")

models = client.models.list()

for model in models.data:
    print(model.id)
