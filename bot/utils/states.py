"""All FSM states in one place."""
from aiogram.fsm.state import State, StatesGroup


class StartFlow(StatesGroup):
    choosing_language   = State()
    waiting_sub_check   = State()
    reading_offer       = State()
    entering_name       = State()
    entering_city       = State()


class ExpenseStates(StatesGroup):
    adding              = State()
    converting          = State()


class ReminderStates(StatesGroup):
    adding_text         = State()   # "YYYY-MM-DD HH:MM text" or "HH:MM text"
    choosing_repeat     = State()


class DailyPlanStates(StatesGroup):
    adding              = State()   # "HH:MM text"


class WeatherStates(StatesGroup):
    waiting_city        = State()


class CurrencyStates(StatesGroup):
    waiting_input       = State()


class ProfileStates(StatesGroup):
    editing_name        = State()
    editing_city        = State()


class AIStates(StatesGroup):
    chatting            = State()
    waiting_prompt      = State()   # generic prompt for any AI function


class BalanceStates(StatesGroup):
    reading_offer       = State()
    choosing_method     = State()
    entering_amount     = State()
    waiting_receipt     = State()
    waiting_stars       = State()


class TariffStates(StatesGroup):
    choosing_tariff     = State()
    choosing_period     = State()
    payment             = State()


class SettingsStates(StatesGroup):
    choosing_language   = State()


class AdminStates(StatesGroup):
    # broadcast
    broadcast_text      = State()
    # ad
    ad_choose_lang      = State()
    ad_input            = State()
    ad_schedule_time    = State()
    # mandatory sub
    sub_choose_lang     = State()
    sub_input           = State()
    # motivational quote
    quote_choose_lang   = State()
    quote_input         = State()
    quote_time          = State()
    # edit welcome
    welcome_choose_lang = State()
    welcome_input       = State()
    # edit button text
    btn_text_lang       = State()
    btn_text_choose     = State()
    btn_text_input      = State()
    # edit offer
    offer_choose_lang   = State()
    offer_input         = State()
    # edit admin contact text
    admin_txt_lang      = State()
    admin_txt_input     = State()
    # banned words
    banned_word_input   = State()
    # manual warning
    warn_user_id        = State()
    warn_text           = State()
    # block / unblock
    block_user_id       = State()
    unblock_user_id     = State()
