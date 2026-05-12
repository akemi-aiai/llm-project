from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()


def token_key(user_id: int) -> str:
    return f"token:{user_id}"


def extract_token(text: str) -> str | None:
    parts = text.strip().split(maxsplit=1)
    if len(parts) != 2:
        return None
    return parts[1].strip()


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Сначала получи JWT в Auth Service через Swagger, "
        "затем отправь мне команду:\n\n/token <jwt>"
    )


@router.message(Command("token"))
async def token_handler(message: Message) -> None:
    if message.from_user is None:
        await message.answer("Не удалось определить Telegram user_id.")
        return

    token = extract_token(message.text or "")
    if not token:
        await message.answer("Отправь токен в формате:\n/token <jwt>")
        return

    try:
        decode_and_validate(token)
    except ValueError as exc:
        await message.answer(f"Я отказываюсь принимать этот токен: {exc}")
        return

    redis = await get_redis()
    await redis.set(token_key(message.from_user.id), token)
    await message.answer("Этот токен мне нравится, я сохранил.")


@router.message(F.text)
async def text_handler(message: Message) -> None:
    if message.from_user is None:
        await message.answer("Не удалось определить Telegram user_id.")
        return

    text = (message.text or "").strip()
    if not text:
        return

    redis = await get_redis()
    token = await redis.get(token_key(message.from_user.id))

    if not token:
        await message.answer(
            "Дальше дороги нет. Сначала авторизуйся через Auth Service и отправь:\n\n/token <jwt>"
        )
        return

    try:
        decode_and_validate(token)
    except ValueError as exc:
        await redis.delete(token_key(message.from_user.id))
        await message.answer(f"Сохранённый токен недействителен: {exc}. Получи новый JWT.")
        return

    llm_request.delay(message.chat.id, text)
    await message.answer("Я отправил ваш запрос своему коллеге LLM, ожидайте.")
