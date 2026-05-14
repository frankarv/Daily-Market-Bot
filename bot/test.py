from anthropic import Anthropic
import os

client = Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

models = client.models.list()

for m in models.data:
    print(m.id)