from config import *
import openai
import aiogram

openai.api_key = API_KEY1
model_id = 'gpt-3.5-turbo'


def get_response(conversation_log):
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation_log
    )
    return response


def chatgpt_conversation(user_text: str, conversation: list):
    if conversation:
        conversation.append({'role': 'user', 'content': user_text})
    else:
        conversation = [{'role': 'user', 'content': user_text}]
    response = get_response(conversation)
    conversation.append({
        'role': response.choices[0].message.role,
        'content': response.choices[0].message.content.strip()
    })
    return conversation


def init_conversation():
    conversation = [{'role': 'system', 'content': 'Сможешь мне помочь?'}]
    # system, user, assistant
    response = get_response(conversation)
    conversation.append({
        'role': response.choices[0].message.role,
        'content': response.choices[0].message.content.strip()
    })
    return conversation


def generate_img(prompt: str) -> str:
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return image_url
