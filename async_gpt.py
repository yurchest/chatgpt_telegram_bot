import openai_async
from decouple import config
from exceptions import CustomRateLimitError

API_KEY = config("OPENAI_API_KEY")
model_id = 'gpt-3.5-turbo'
import asyncio

conversations = []

async def get_response(conversation_log):
    response = await openai_async.chat_complete(
        API_KEY,
        timeout=2,
        payload={
            "model": model_id,
            "messages": conversation_log,
        },
    )
    return response


async def chatgpt_conversation(user_text: str):
    global conversations
    conversations.append({'role': 'user', 'content': user_text})
    response = await get_response(conversations)
    if "error" in response.json() and "Rate limit" in response.json()["error"]["message"]:
        raise CustomRateLimitError()
    conversations.append({
        'role': response.json()["choices"][0]["message"]["role"],
        'content': response.json()["choices"][0]["message"]["content"].strip()
    })
    return conversations[-1]['content'].strip()


async def init_conversation():
    global conversations
    # system, user, assistant
    conversations = [{'role': 'system', 'content': 'Сможешь мне помочь?'}]
    response = await get_response(conversations)
    conversations.append({
        'role': response.json()["choices"][0]["message"]["role"],
        'content': response.json()["choices"][0]["message"]["content"].strip()
    })
    return conversations


def delete_last_el():
    conversations.pop()


if __name__ == "__main__":
    response = asyncio.run(get_response([{'role': 'user', 'content': "Расскажи шутку"}]))
    print(response.json()["choices"][0]["message"])
