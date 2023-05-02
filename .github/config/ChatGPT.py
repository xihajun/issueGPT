import os
import openai
import sys
import json
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens*2

# load comments
with open("comments.json", 'r') as data_file:
    json_data = data_file.read()

data = json.loads(json_data)

# Generate the desired format
conversations = [{"role": "system","content": "Assume that you are a IT assistant to help people to generate the code to run the simple script and create files"}]
for item in data:
    if item["user"]["login"] != "github-actions[bot]":
        conversations.append({"role": "user", "content": item["body"]})
    else:
        conversations.append({"role": "assistant", "content": item["body"]})

if True: #num_tokens_from_string(conversations,"cl100k_base") < 2000:
    # Run gpt3.5
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=conversations
    )
    answer = completion.choices[0].message.content
else:
    answer = "信息太长了啦，请关闭这个issue重来，都怪你！"

print(answer)

with open(".github/comment-template.md", 'a') as f:
    f.write(answer)
