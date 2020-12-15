import os
import logging

from vkbottle import Text
from vkbottle import Keyboard
from vkbottle import CtxStorage
from vkbottle import BaseStateGroup
from vkbottle.bot import Bot
from vkbottle.bot import Message

from myrsa import make_key_pair, encoding

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

start_message = "Привет! Я бот-помощник, который может кодировать информацию с помощью простейшего RSA алгоритма."
back_message = "Выберите действие:"
unknown_message = "Извини, я тебя не понимаю, попробуй еще раз."
error_message = "Что-то пошло не так, попробуйте еще раз"

generate_message = "Сгенерирован публичный ключ: {}; приватный ключ: {}."

decrypt_key_message = "Введите приватный ключ (2 числа через пробел): "
decrypt_text_message = "Введите зашифрованный текст: "
decrypt_out_message = "Расшифрованный текст: {}"
wrong_message = "Некоректный ответ, попробуй еще раз:"

encrypt_key_message = "Введите публичный ключ (2 числа через пробел): "
encrypt_text_message = "Введите текст: "
encrypt_out_message = "Зашифрованный текст: {}"

bot = Bot(os.environ["TOKEN"])
ctx_storage = CtxStorage()

keyboard_main = Keyboard(one_time=True)
keyboard_main.add(Text("Сгенерировать", {"cmd": "generate"}))
keyboard_main.row()
keyboard_main.add(Text("Зашифровать", {"cmd": "encrypt"}))
keyboard_main.add(Text("Расшифровать", {"cmd": "decrypt"}))

keyboard_decrypt = Keyboard(one_time=True)
keyboard_decrypt.add(Text("Назад", {"cmd": "back"}))


class MenuState(BaseStateGroup):
    INFO = 1
    ENCRYPT_KEY = 2
    ENCRYPT_TEXT = 3
    DECRYPT_KEY = 4
    DECRYPT_TEXT = 5


@bot.on.message(state=None)
async def start_handler(message: Message):
    await message.answer(start_message, keyboard=keyboard_main.get_json())
    await bot.state_dispenser.set(message.peer_id, MenuState.INFO)


@bot.on.message(payload={"cmd": "back"})
async def back_handler(message: Message):
    await message.answer(back_message, keyboard=keyboard_main.get_json())
    await bot.state_dispenser.set(message.peer_id, MenuState.INFO)


@bot.on.message(state=MenuState.INFO, payload={"cmd": "generate"})
@bot.on.message(state=MenuState.INFO, text=["/generate", "/сгенерировать", "сгенерировать"])
async def generate_handler(message: Message):
    try:
        public, private = make_key_pair(20)
    except Exception as e:
        logger.exception(e)
        await message.answer(error_message, keyboard=keyboard_main.get_json())
        return
    await message.answer(generate_message.format(public, private), keyboard=keyboard_main.get_json())


@bot.on.message(state=MenuState.INFO, payload={"cmd": "decrypt"})
@bot.on.message(state=MenuState.INFO, text=["/decrypt", "/расшифровать", "расшифровать"])
async def decrypt_handler(message: Message):
    await message.answer(decrypt_key_message, keyboard=keyboard_decrypt.get_json())
    await bot.state_dispenser.set(message.peer_id, MenuState.DECRYPT_KEY)


@bot.on.message(state=MenuState.DECRYPT_KEY)
async def decrypt_key_handler(message: Message):
    try:
        n, d = [int(x) for x in message.text.split()]
        ctx_storage.set(f"{message.peer_id}n", n)
        ctx_storage.set(f"{message.peer_id}d", d)
    except ValueError:
        await message.answer(wrong_message, keyboard=keyboard_decrypt.get_json())
        return
    await message.answer(decrypt_text_message, keyboard=keyboard_decrypt.get_json())
    await bot.state_dispenser.set(message.peer_id, MenuState.DECRYPT_TEXT)


@bot.on.message(state=MenuState.DECRYPT_TEXT)
async def decrypt_text_handler(message: Message):
    try:
        d = int(ctx_storage.get(f"{message.peer_id}d"))
        n = int(ctx_storage.get(f"{message.peer_id}n"))
        await message.answer(decrypt_out_message.format(encoding(key=(n, d), text=message.text)),
                             keyboard=keyboard_main.get_json())
    except Exception as e:
        logger.exception(e)
        return
    await bot.state_dispenser.set(message.peer_id, MenuState.INFO)


@bot.on.message(state=MenuState.INFO, payload={"cmd": "encrypt"})
@bot.on.message(state=MenuState.INFO, text=["/encrypt", "/зашифровать", "зашифровать"])
async def encrypt_handler(message: Message):
    await message.answer(encrypt_key_message, keyboard=keyboard_decrypt.get_json())
    await bot.state_dispenser.set(message.peer_id, MenuState.ENCRYPT_KEY)


@bot.on.message(state=MenuState.ENCRYPT_KEY)
async def encrypt_key_handler(message: Message):
    # TODO: Make 'generate' button in encrypt keyboard
    try:
        n, d = [int(x) for x in message.text.split()]
        ctx_storage.set(f"{message.peer_id}n", n)
        ctx_storage.set(f"{message.peer_id}d", d)
    except ValueError:
        await message.answer(wrong_message, keyboard=keyboard_decrypt.get_json())
        return
    await message.answer(encrypt_text_message, keyboard=keyboard_decrypt.get_json())
    await bot.state_dispenser.set(message.peer_id, MenuState.ENCRYPT_TEXT)


@bot.on.message(state=MenuState.ENCRYPT_TEXT)
async def encrypt_text_handler(message: Message):
    try:
        d = int(ctx_storage.get(f"{message.peer_id}d"))
        n = int(ctx_storage.get(f"{message.peer_id}n"))
        await message.answer(encrypt_out_message.format(encoding(key=(n, d), text=message.text)),
                             keyboard=keyboard_main.get_json())
    except Exception as e:
        logger.exception(e)
        return
    await bot.state_dispenser.set(message.peer_id, MenuState.INFO)


@bot.on.message(state=MenuState.INFO)
async def keyboard_handler(message: Message):
    await message.answer(unknown_message, keyboard=keyboard_main.get_json())


if __name__ == "__main__":
    try:
        bot.run_forever()
    except Exception as e:
        logger.exception(e)
        exit(-1)
