from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import F
from config import BOT_TOKEN
from database import create_db, add_user
import asyncio


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


class Register(StatesGroup):
    first_name = State()
    last_name = State()
    gender = State()
    phone = State()


@dp.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
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
        keyboard=[
            [KeyboardButton(text="Erkak"), KeyboardButton(text="Ayol")]
        ],
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
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True
    )
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_kb)
    await state.set_state(Register.phone)


@dp.message(Register.phone, F.contact)
async def get_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_user(
        user_id=message.from_user.id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        gender=data['gender'],
        phone=message.contact.phone_number
    )
    await show_menu(message)
    await state.clear()


@dp.message(Register.phone, F.text)
async def get_phone_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_user(
        user_id=message.from_user.id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        gender=data['gender'],
        phone=message.text
    )
    await show_menu(message)
    await state.clear()


# ✅ Show only one button after registration
async def show_menu(message: types.Message):
    menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Kurs haqida ma'lumot", callback_data="info")]
    ])
    await message.answer("Quyidagilardan birini tanlang:", reply_markup=menu)


# ✅ When press 'info', show text + admin buttons
@dp.callback_query(F.data == "info")
async def show_info(callback: types.CallbackQuery):
    text = """
" 📣 Tabiiy Ovoz Sirlari Kursi haqida to‘liq ma’lumot

Assalamu alaykum, hurmatli tilovat va ovoz san’atiga qiziqadigan birodar va opa-singillar!

Sizni “Tabiiy Ovoz Sirlari” onlayn kursimizga qiziqish bildirganingiz uchun chin dildan minnatdorchilik bildiramiz.

🎙 Bu kurs kimlar uchun?
▫️ Qur’on tilovati chog‘ida tez charchab qoladiganlar uchun
▫️ Ovozining tabiiy, jozibali va barakali bo‘lishini istaganlar uchun
▫️ Masjid muazzinlari, xatib va imomlar uchun
▫️ O‘z ustida ishlamoqchi bo‘lgan erkak va ayollar uchun

📚 Kurs davomida siz nimalarga ega bo‘lasiz?

✅ Ovozdan to‘g‘ri va sog‘lom foydalanish sirlarini o‘rganasiz
✅ Tabiiy va sof ovoz chiqarishni shakllantirasiz
✅ Qur’on tilovatini charchamasdan uzoq davom ettirishga o‘rganasiz
✅ Tilovat va azon san’atida ishlatiladigan 8 ta maqom haqida chuqur tushunchaga ega bo‘lasiz
✅ Maqomlar orasidagi farqlarni eshitib ajrata olasiz
✅ Ovoz sifati doimiy bo‘lishi uchun maxsus mashqlar, tavsiyalar va amaliyotlar taqdim etiladi

👩‍🦰 Ayollar ham qatnasha oladimi?
Albatta! Kursimiz ham ayollar, ham erkaklar uchun maxsus moslashtirilgan.

🧒 Yosh chegarasi:
Kursimizga 16 yoshdan 40 yoshgacha bo‘lgan barcha ishtiyoqmandlar qatnasha oladi.

💳 Kurs tariflari:

🟢 1. Individual yondashuv tarifi
🔹 8 ta jonli dars (haftasiga 2 marta)
🔹 Har bir dars Abdulloh Hasaniy tomonidan o‘tiladi
🔹 Yakka tartibda topshiriqlar, ovoz tahlili, shaxsiy maslahatlar
🔹 Talabaga xos individual yondashuv
🔹 Faol va mas’uliyatli qatnashuvchilarga 100% natija kafolati
🔹 Kurs yakunida sertifikat va 50% gacha pul qaytishi imkoniyati
🔹 Iqtidorli ayollarga Misrda mashhur hofiza Zaxro Loyiq xonim bilan maxsus maqomat guruhi imkoniyati
🔹 Iqtidorli yigitlarga Abdulloh Hasaniy jamoasida Ustoz yordamchisi bo‘lib qolish imkoniyati
🔹 Ijobiy natija kafolatlanadi

📌 Bu tarifda o‘rinlar soni cheklangan. Ulgurib qoling!

💰 Narx:
▫️ Erkaklar uchun — 899 000 so‘m
▫️ Ayollar uchun — 699 000 so‘m

🟡 2. Video darsliklar tarifi
🔹 8 ta video darslik (30 kun ichida)
🔹 Individual tarifdagi barcha mavzularni o‘z ichiga oladi
🔹 Mustaqil ishlash uchun mo‘ljallangan
🔹 Jonli dars va yakka maslahatlar mavjud emas
🔹 Sertifikat berilmaydi
🔹 Natija kafolatlanmaydi

📌 Ushbu tarif mustaqil ravishda o‘qishni istagan, vaqtiga egalik qiluvchi va arzon narxda sifatli ilm olishni xohlaganlar uchun juda qulay.

💰 Narx:
▫️ Umumiy: 249 000 so‘m

👥 Har ikki tarifda ham ayollar qatnashishi mumkin.

🕋 Bu kurs sizning Qur’on tilovati, azon ijrosi va ovoz tarbiyangizdagi yangi bosqich bo‘lishi mumkin.
Noyob ilmiy imkoniyat va amaliy mashg‘ulotlardan bahramand bo‘lishni istasangiz — bugunoq ro‘yxatdan o‘ting!

📌 Agar kursimiz sizga maqul bo‘lgan va uni sotib olishga tayyor bo‘lsangiz, iltimos, quyida ko‘rsatilgan adminlarimiz bilan bog‘laning.
Ular sizga barcha zarur ma’lumotlarni taqdim etishadi va ro‘yxatdan o‘tish jarayonida yordam berishadi, inshaAlloh.
    """

    admin_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Admin 1", url="https://t.me/hasaniy_admin1")],
        [InlineKeyboardButton(text="👤 Admin 2", url="https://t.me/hasaniy_admin2")]
    ])

    await callback.message.answer(text, reply_markup=admin_buttons)
    await callback.answer()


async def main():
    await create_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
