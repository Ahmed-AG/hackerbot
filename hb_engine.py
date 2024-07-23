import asyncio
from ollama import AsyncClient

class hb_engine:
  async def chat():
    message = {'role': 'user', 'content': 'Why is the sky blue?'}
    response = await AsyncClient().chat(model='llama3', messages=[message])

  asyncio.run(chat())

  def request(user_input):
      prompt = "Answer only with the actual command. {}".format(user_input)

      return ai_response
