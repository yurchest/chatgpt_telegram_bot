from decouple import config
import openai

API_KEY = config("OPENAI_API_KEY")
openai.api_key = API_KEY
model_id = 'gpt-3.5-turbo'

conversations = []


def get_response(conversation_log):
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation_log
    )
    return response


def chatgpt_conversation(user_text: str):
    global conversations
    conversations.append({'role': 'user', 'content': user_text})
    response = get_response(conversations)
    conversations.append({
        'role': response.choices[0].message.role,
        'content': response.choices[0].message.content.strip()
    })
    return conversations[-1]['content'].strip()


def init_conversation():
    global conversations
    # system, user, assistant
    conversations = [{'role': 'system', 'content': 'Сможешь мне помочь?'}]
    response = get_response(conversations)
    conversations.append({
        'role': response.choices[0].message.role,
        'content': response.choices[0].message.content.strip()
    })
    return conversations


def delete_last_el():
    conversations.pop()
