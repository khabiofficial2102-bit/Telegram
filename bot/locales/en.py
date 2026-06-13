# ===================== ENGLISH =====================
EN = {
    "choose_language":       "🌐 Choose your language / Tilni tanlang:",
    "mandatory_sub_text":    "📢 Please subscribe to the following channel/group to use the bot:",
    "check_sub_btn":         "✅ Check subscription",
    "not_subscribed":        "❌ You haven't subscribed yet. Please subscribe and check again.",
    "offer_text":            (
        "📋 <b>Terms of Use (Public Offer)</b>\n\n"
        "1. This bot is intended for personal use only.\n"
        "2. Payments made through the bot are non-refundable.\n"
        "3. Payments are only confirmed after a valid receipt is submitted.\n"
        "4. Misuse of the bot may result in account suspension.\n"
        "5. Your personal data will not be shared with third parties.\n\n"
        "Please accept the terms to continue."
    ),
    "accept_offer_btn":      "✅ Accept",
    "welcome_new":           "🎉 <b>Welcome!</b>\nYou can now start using the bot.",
    "enter_name":            "👤 Please enter your name:",
    "enter_city":            "🏙 Please enter your city:",
    "onboard_done":          "✅ Your information has been saved! You can now use the bot fully.",

    "menu_btn":              "📋 Menu",
    "main_menu":             "🏠 <b>Main Menu</b>\nSelect a section:",
    "back_btn":              "⬅️ Back",
    "back_main_btn":         "🏠 Main Menu",

    "btn_expenses":          "💸 Expenses",
    "btn_reminders":         "⏰ Reminders",
    "btn_currency":          "💱 Currency",
    "btn_daily_plan":        "📅 Daily Plan",
    "btn_weather":           "🌤 Weather",
    "btn_profile":           "👤 Profile",
    "btn_ai":                "🤖 AI Assistant",
    "btn_balance":           "💰 Balance",
    "btn_tariff":            "⭐ Tariff",
    "btn_referral":          "🎁 Referral",
    "btn_settings":          "⚙️ Settings",
    "btn_admin_contact":     "📞 Admin",

    "expenses_info":         (
        "💸 <b>Expenses Section</b>\n\n"
        "To add an expense, write in the following format:\n"
        "<code>amount currency description</code>\n\n"
        "📌 Examples:\n"
        "• <code>50 dollar food</code>\n"
        "• <code>10 USD clothes</code>\n"
        "• <code>100 uzbekistan transport</code>\n\n"
        "You can enter the currency as a name, abbreviation, or country name."
    ),
    "expense_added":         "✅ Expense added: <b>{amount} {currency}</b> — {desc}",
    "expense_invalid":       "❌ Invalid format. Please write: <code>amount currency description</code>",
    "btn_today":             "📆 Today",
    "btn_week":              "📅 Week",
    "btn_month":             "🗓 Month",
    "btn_year":              "📊 Year",
    "btn_convert":           "💱 Convert",
    "btn_clear_expenses":    "🗑 Clear",
    "expense_report_empty":  "📭 No expenses found for this period.",
    "expense_report_title":  "📊 <b>{period} Expense Report:</b>\n\n",
    "expense_report_total":  "\n💰 <b>Total: {total} {currency}</b>",
    "expense_convert_ask":   "Which currency do you want to convert to?\n(e.g.: dollar, EUR, Russia, som)",
    "expense_convert_result":"✅ Your total expenses: <b>{amount} {currency}</b>",
    "clear_confirm":         "⚠️ Are you sure you want to delete all expenses?",
    "btn_confirm":           "✅ Confirm",
    "btn_cancel":            "❌ Cancel",
    "cleared_success":       "🗑 All expenses have been deleted.",
    "cancelled":             "❌ Cancelled.",

    "reminders_info":        (
        "⏰ <b>Reminders Section</b>\n\n"
        "To add a reminder, write in the following format:\n"
        "<code>YYYY-MM-DD HH:MM text</code>\n\n"
        "📌 Examples:\n"
        "• <code>2024-12-25 09:00 Christmas greeting</code>\n"
        "• <code>14:30 Take medicine</code> (today)\n\n"
        "If only time is entered, it will be set for today."
    ),
    "reminder_ask_repeat":   "🔄 How should this reminder work?",
    "btn_once":              "1️⃣ One-time",
    "btn_daily":             "🔁 Daily",
    "reminder_added":        "✅ Reminder added: <b>{time}</b> — {text}",
    "reminder_fired":        "⏰ <b>Reminder:</b> {text}",
    "reminder_invalid":      "❌ Invalid format. Please use the format shown.",
    "reminders_empty":       "📭 You have no reminders.",
    "btn_list_reminders":    "📋 View reminders",
    "btn_clear_reminders":   "🗑 Clear reminders",
    "reminders_cleared":     "🗑 All reminders have been deleted.",

    "currency_info":         (
        "💱 <b>Currency Converter</b>\n\n"
        "Write in the following format:\n"
        "<code>amount from_currency to_currency</code>\n\n"
        "📌 Examples:\n"
        "• <code>100 dollar som</code>\n"
        "• <code>50 EUR UZS</code>\n"
        "• <code>1000 uzbekistan russia</code>"
    ),
    "currency_result":       "💱 <b>{amount} {from_cur}</b> = <b>{result} {to_cur}</b>",
    "currency_error":        "❌ Currency not found. Please try a different name.",

    "plan_info":             (
        "📅 <b>Daily Plan</b>\n\n"
        "Write your plan in the following format:\n"
        "<code>HH:MM plan text</code>\n\n"
        "📌 Examples:\n"
        "• <code>07:00 Morning exercise</code>\n"
        "• <code>09:00 Start work</code>"
    ),
    "plan_added":            "✅ Plan added: <b>{time}</b> — {text}",
    "plan_fired":            "📅 <b>Your daily plan:</b> {text}",
    "plan_invalid":          "❌ Invalid format. Write: <code>HH:MM text</code>",
    "plans_empty":           "📭 You have no daily plans.",
    "btn_list_plans":        "📋 View plans",
    "btn_clear_plans":       "🗑 Clear plans",
    "plans_cleared":         "🗑 All plans have been deleted.",

    "weather_info":          "🌤 Enter the city or country name to check the weather:",
    "weather_result":        (
        "🌤 <b>Weather in {city}:</b>\n\n"
        "🌡 Temperature: <b>{temp}°C</b>\n"
        "💧 Humidity: <b>{humidity}%</b>\n"
        "💨 Wind: <b>{wind} m/s</b>\n"
        "☁️ Condition: <b>{description}</b>"
    ),
    "weather_error":         "❌ City not found. Please try a different name.",

    "profile_text":          (
        "👤 <b>Your Profile:</b>\n\n"
        "📛 Name: <b>{name}</b>\n"
        "🏙 City: <b>{city}</b>\n"
        "🌐 Language: <b>{lang}</b>\n"
        "⭐ Tariff: <b>{tariff}</b>\n\n"
        "📊 <b>Stats:</b>\n"
        "💸 Expenses: <b>{expenses}</b>\n"
        "⏰ Reminders: <b>{reminders}</b>\n"
        "📅 Daily plans: <b>{plans}</b>"
    ),
    "btn_edit_name":         "✏️ Edit name",
    "btn_edit_city":         "✏️ Edit city",
    "enter_new_name":        "✏️ Enter your new name:",
    "enter_new_city":        "✏️ Enter your new city:",
    "profile_updated":       "✅ Information updated!",

    "ai_info":               "🤖 <b>AI Assistant</b>\nSelect a section:",
    "ai_chat":               "💬 Chat",
    "ai_no_balance":         "❌ Insufficient balance. Please top up your balance or purchase a subscription.",
    "ai_processing":         "⏳ Preparing response...",
    "ai_error":              "❌ An error occurred. Please try again.",
    "ai_ask_prompt":         "✏️ Enter your request:",
    "ai_deducted":           "💳 {amount} UZS deducted.",

    "balance_text":          "💰 <b>Your balance:</b> <b>{amount} UZS</b>",
    "balance_topup_btn":     "➕ Top up balance",
    "balance_offer":         (
        "⚠️ <b>Payment Offer</b>\n\n"
        "• Deposited funds are non-refundable.\n"
        "• Payment is confirmed only after a valid receipt is submitted.\n"
        "• Submitting a fake receipt will result in account suspension.\n\n"
        "Do you accept the terms?"
    ),
    "choose_payment":        "Choose a payment method:",
    "btn_pay_stars":         "⭐ Telegram Stars",
    "btn_pay_card":          "💳 Card payment",
    "enter_amount":          "💰 How much do you want to top up? (numbers only)",
    "card_payment_info":     (
        "💳 <b>Card Payment</b>\n\n"
        "Transfer the amount to the following card:\n"
        "<code>{card_number}</code>\n"
        "<b>{card_holder}</b>\n\n"
        "Amount: <b>{amount} UZS</b>\n\n"
        "After payment, send the receipt (screenshot)."
    ),
    "receipt_received":      "✅ Your receipt has been received. Awaiting confirmation (5–30 min).",
    "balance_added":         "✅ <b>{amount} UZS</b> has been added to your balance!",
    "payment_rejected":      "❌ Your payment was rejected. Contact admin for questions.",

    "tariff_info":           (
        "⭐ <b>Tariffs</b>\n\n"
        "🆓 <b>Free:</b> 1 AI function use\n\n"
        "📦 <b>Standard:</b>\n"
        "   • Monthly: 49,900 UZS\n"
        "   • Yearly: 499,900 UZS\n\n"
        "💎 <b>Premium:</b>\n"
        "   • Monthly: 99,900 UZS\n"
        "   • Yearly: 999,900 UZS\n\n"
        "Select a tariff:"
    ),
    "btn_standard":          "📦 Standard",
    "btn_premium":           "💎 Premium",
    "btn_monthly":           "📅 Monthly",
    "btn_yearly":            "📆 Yearly",
    "tariff_activated":      "✅ <b>{tariff}</b> tariff activated! Expires: {expires}",

    "referral_info":         (
        "🎁 <b>Referral Program</b>\n\n"
        "Share this link with your friends:\n"
        "{link}\n\n"
        "👥 Your referrals: <b>{count}</b>\n\n"
        "🎯 <b>Discounts:</b>\n"
        "• 5 referrals → Standard -20%, Premium -5%\n"
        "• 10 referrals → Standard -37%, Premium -10%\n\n"
        "💡 Unused discounts are saved for the next month."
    ),

    "settings_lang":         "⚙️ Choose your language:",

    "admin_contact_text":    (
        "📞 <b>Contact Admin</b>\n\n"
        "For suggestions, inquiries, or complaints:\n"
        "👤 @{admin_username}\n\n"
        "❤️ Support the bot with a donation:\n"
        "{donation_link}"
    ),

    "blocked_msg":           "🚫 Your account is blocked. Contact: @{admin_username}",
    "unblocked_msg":         "✅ Your account has been unblocked. You can now use the bot.",

    "banned_word_warning":   "⚠️ Warning: you used a banned word. ({count}/{max} times)",
    "banned_word_blocked":   "🚫 Your account has been blocked for repeatedly using banned words.",

    "must_subscribe":        "📢 Please subscribe first to use the bot:",

    "morning_quote":         "☀️ <b>Daily inspiration:</b>\n\n{quote}",

    "help_text":             (
        "ℹ️ <b>Help</b>\n\n"
        "/start — Restart the bot\n"
        "/menu — Main menu\n"
        "/profile — Your profile\n"
        "/offer — Terms of use\n"
        "/settings — Settings\n"
        "/help — Help\n"
        "/balance — Your balance\n"
        "/tariff — Tariffs\n"
        "/referral — Referral program\n"
        "/ai — AI Assistant\n"
        "/expenses — Expenses\n"
        "/reminders — Reminders\n"
        "/plans — Daily plan\n"
        "/weather — Weather\n"
        "/currency — Currency"
    ),

    "period_today":          "Today's",
    "period_week":           "Weekly",
    "period_month":          "Monthly",
    "period_year":           "Yearly",

    "tariff_free":           "Free",
    "tariff_standard":       "Standard",
    "tariff_premium":        "Premium",
    "tariff_expires":        "Expires: {date}",
    "tariff_no_expire":      "Unlimited",
}
