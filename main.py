# -*- coding: utf-8 -*-
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import BOT_TOKEN
from database import create_db, add_user


CHANNEL_USERNAME = '@abdulloh_hasaniy'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ✅ Subscription check
async def check_subscription(user_id):
    member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
    return member.status in ["member", "administrator", "creator"]


async def ask_subscription(message: types.Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")]
        ]
    )
    await message.answer("Siz Abdulloh Hasaniy kanaliga obuna bo'lganmisiz?", reply_markup=kb)


# ✅ FSM States
class Register(StatesGroup):
    first_name = State()
    last_name = State()
    gender = State()
    phone = State()


# ✅ Handlers
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer("Ismingizni kiriting:")
    await state.set_state(Register.first_name)


@dp.message(Register.first_name)
async def get_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(Register.last_name)


@dp.message(Register.last_name)
async def get_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    gender_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Erkak"), KeyboardButton(text="Ayol")]],
        resize_keyboard=True
    )
    await message.answer("Jinsingizni tanlang:", reply_markup=gender_kb)
    await state.set_state(Register.gender)


@dp.message(Register.gender)
async def get_gender(message: types.Message, state: FSMContext):
    if message.text not in ["Erkak", "Ayol"]:
        await message.answer("Iltimos, 'Erkak' yoki 'Ayol' deb yozing.")
        return
    await state.update_data(gender=message.text)
    phone_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_kb)
    await state.set_state(Register.phone)


@dp.message(Register.phone, F.contact)
async def get_phone_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_user(
        user_id=message.from_user.id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        gender=data["gender"],
        phone=message.contact.phone_number
    )
    await ask_subscription(message)
    await state.clear()


@dp.message(Register.phone, F.text)
async def get_phone_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_user(
        user_id=message.from_user.id,
        first_name=data["first_name"],
        last_name=data["last_name"],
        gender=data["gender"],
        phone=message.text
    )
    await ask_subscription(message)
    await state.clear()


@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(user_id):
        await show_menu(callback.message)
        await callback.answer("✅ Obuna tekshirildi!")
    else:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Kanalga obuna bo'lish", url="https://t.me/abdulloh_hasaniy")],
                [InlineKeyboardButton(text="🔄 Qayta tekshirish", callback_data="check_sub")]
            ]
        )
        await callback.message.answer(
            "❌ Iltimos, Abdulloh Hasaniy kanaliga obuna bo'ling.", reply_markup=kb
        )
        await callback.answer("❗ Hali obuna emassiz!")


async def show_menu(message: types.Message):
    menu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Kurs haqida ma'lumot", callback_data="info")]
        ]
    )
    await message.answer("Quyidagilardan birini tanlang:", reply_markup=menu)


@dp.callback_query(F.data == "info")
async def show_info(callback: types.CallbackQuery):
    text = """
📣 Tabiiy Ovoz Sirlari Kursi haqida to‘liq ma’lumot...

💳 Kurs tariflari:
🟢 Individual jonli dars:
🔸 Erkaklar — 899,000 so'm
🔸 Ayollar — 699,000 so'm

🟡 Video dars:
🔸 249,000 so'm

👤 Adminlar:
👉 @hasaniy_admin1
👉 @hasaniy_admin2
    """
    await callback.message.answer(text)
    await callback.answer()


# ✅ Main runner
async def main():
    await create_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
