import os
import openai
import sys
import json
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

# load comments
with open("comments.json", 'r') as data_file:
    json_data = data_file.read()

data = json.loads(json_data)

with open("issue_content.txt", 'r') as issue_file:
    issue_content = issue_file.read().strip()

if issue_content:
    system_message = issue_content
else:
    system_message = "Assume that you are an IT assistant to help people generate the code to run simple scripts and create files"

conversations = [{"role": "system", "content": system_message}]
for item in data:
    if item["user"]["login"] != "github-actions[bot]":
        conversations.append({"role": "user", "content": item["body"]})
    else:
        conversations.append({"role": "assistant", "content": item["body"]})

token_length = num_tokens_from_messages(conversations, "gpt-3.5-turbo-0301")
if token_length <= 4000:
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=conversations
    )
    answer = completion.choices[0].message.content
else:
    answer = "信息太长了啦，请关闭这个issue[点此](https://github.com/xihajun/issueGPT/issues/new?assignees=&labels=GPT3.5&template=chatgpt.md&title=%5BCHAT%5D)重来，都怪你！"

with open(".github/comment-template.md", 'a') as f:
    f.write(answer)

print(answer)