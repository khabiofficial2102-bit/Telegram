# ===================== TÜRKÇE =====================
TR = {
    "choose_language":       "🌐 Dilinizi seçin / Choose your language:",
    "mandatory_sub_text":    "📢 Botu kullanmak için lütfen şu kanal/gruba abone olun:",
    "check_sub_btn":         "✅ Aboneliği kontrol et",
    "not_subscribed":        "❌ Henüz abone olmadınız. Abone olup tekrar kontrol edin.",
    "offer_text":            (
        "📋 <b>Kullanım Şartları (Kamu Teklifi)</b>\n\n"
        "1. Bu bot yalnızca kişisel kullanım içindir.\n"
        "2. Bot üzerinden yapılan ödemeler iade edilmez.\n"
        "3. Ödemeler yalnızca gerçek makbuz gönderildikten sonra onaylanır.\n"
        "4. Botu kötüye kullanmak hesabınızın askıya alınmasına yol açabilir.\n"
        "5. Kişisel verileriniz üçüncü taraflarla paylaşılmaz.\n\n"
        "Devam etmek için şartları kabul edin."
    ),
    "accept_offer_btn":      "✅ Kabul ediyorum",
    "welcome_new":           "🎉 <b>Hoş geldiniz!</b>\nBotu kullanmaya başlayabilirsiniz.",
    "enter_name":            "👤 Adınızı girin:",
    "enter_city":            "🏙 Şehrinizi girin:",
    "onboard_done":          "✅ Bilgileriniz kaydedildi! Artık botu tam olarak kullanabilirsiniz.",

    "menu_btn":              "📋 Menü",
    "main_menu":             "🏠 <b>Ana Menü</b>\nBir bölüm seçin:",
    "back_btn":              "⬅️ Geri",
    "back_main_btn":         "🏠 Ana Menü",

    "btn_expenses":          "💸 Harcamalar",
    "btn_reminders":         "⏰ Hatırlatıcılar",
    "btn_currency":          "💱 Döviz",
    "btn_daily_plan":        "📅 Günlük Plan",
    "btn_weather":           "🌤 Hava Durumu",
    "btn_profile":           "👤 Profil",
    "btn_ai":                "🤖 YZ Asistan",
    "btn_balance":           "💰 Bakiye",
    "btn_tariff":            "⭐ Tarife",
    "btn_referral":          "🎁 Referans",
    "btn_settings":          "⚙️ Ayarlar",
    "btn_admin_contact":     "📞 Yönetici",

    "expenses_info":         (
        "💸 <b>Harcamalar Bölümü</b>\n\n"
        "Harcama eklemek için şu biçimde yazın:\n"
        "<code>miktar para_birimi açıklama</code>\n\n"
        "📌 Örnekler:\n"
        "• <code>50 dolar yiyecek</code>\n"
        "• <code>100 TL kıyafet</code>\n"
        "• <code>200 USD ulaşım</code>"
    ),
    "expense_added":         "✅ Harcama eklendi: <b>{amount} {currency}</b> — {desc}",
    "expense_invalid":       "❌ Geçersiz format. Yazın: <code>miktar para_birimi açıklama</code>",
    "btn_today":             "📆 Bugün",
    "btn_week":              "📅 Hafta",
    "btn_month":             "🗓 Ay",
    "btn_year":              "📊 Yıl",
    "btn_convert":           "💱 Çevir",
    "btn_clear_expenses":    "🗑 Temizle",
    "expense_report_empty":  "📭 Bu dönem için harcama bulunamadı.",
    "expense_report_title":  "📊 <b>{period} Harcama Raporu:</b>\n\n",
    "expense_report_total":  "\n💰 <b>Toplam: {total} {currency}</b>",
    "expense_convert_ask":   "Hangi para birimine dönüştürmek istiyorsunuz?\n(Örn: dolar, EUR, Rusya, som)",
    "expense_convert_result":"✅ Toplam harcamalarınız: <b>{amount} {currency}</b>",
    "clear_confirm":         "⚠️ Tüm harcamaları silmek istediğinizden emin misiniz?",
    "btn_confirm":           "✅ Onayla",
    "btn_cancel":            "❌ İptal",
    "cleared_success":       "🗑 Tüm harcamalar silindi.",
    "cancelled":             "❌ İptal edildi.",

    "reminders_info":        (
        "⏰ <b>Hatırlatıcılar Bölümü</b>\n\n"
        "Hatırlatıcı eklemek için:\n"
        "<code>YYYY-MM-DD HH:MM metin</code>\n\n"
        "📌 Örnekler:\n"
        "• <code>2024-12-25 09:00 Noel tebriği</code>\n"
        "• <code>14:30 İlaç almak</code> (bugün)"
    ),
    "reminder_ask_repeat":   "🔄 Bu hatırlatıcı nasıl çalışsın?",
    "btn_once":              "1️⃣ Bir kez",
    "btn_daily":             "🔁 Her gün",
    "reminder_added":        "✅ Hatırlatıcı eklendi: <b>{time}</b> — {text}",
    "reminder_fired":        "⏰ <b>Hatırlatıcı:</b> {text}",
    "reminder_invalid":      "❌ Geçersiz format. Belirtilen şablonu kullanın.",
    "reminders_empty":       "📭 Hiç hatırlatıcınız yok.",
    "btn_list_reminders":    "📋 Hatırlatıcıları gör",
    "btn_clear_reminders":   "🗑 Hatırlatıcıları temizle",
    "reminders_cleared":     "🗑 Tüm hatırlatıcılar silindi.",

    "currency_info":         (
        "💱 <b>Döviz Dönüştürücü</b>\n\n"
        "Format:\n"
        "<code>miktar kaynak_para hedef_para</code>\n\n"
        "📌 Örnekler:\n"
        "• <code>100 dolar som</code>\n"
        "• <code>50 EUR TRY</code>"
    ),
    "currency_result":       "💱 <b>{amount} {from_cur}</b> = <b>{result} {to_cur}</b>",
    "currency_error":        "❌ Para birimi bulunamadı. Farklı bir ad deneyin.",

    "plan_info":             (
        "📅 <b>Günlük Plan</b>\n\n"
        "Format:\n"
        "<code>SS:DD plan metni</code>\n\n"
        "📌 Örnekler:\n"
        "• <code>07:00 Sabah egzersizi</code>\n"
        "• <code>09:00 İşe başla</code>"
    ),
    "plan_added":            "✅ Plan eklendi: <b>{time}</b> — {text}",
    "plan_fired":            "📅 <b>Günlük planınız:</b> {text}",
    "plan_invalid":          "❌ Geçersiz format. Yazın: <code>SS:DD metin</code>",
    "plans_empty":           "📭 Hiç günlük planınız yok.",
    "btn_list_plans":        "📋 Planları gör",
    "btn_clear_plans":       "🗑 Planları temizle",
    "plans_cleared":         "🗑 Tüm planlar silindi.",

    "weather_info":          "🌤 Hava durumunu kontrol etmek için şehir veya ülke adını girin:",
    "weather_result":        (
        "🌤 <b>{city} Hava Durumu:</b>\n\n"
        "🌡 Sıcaklık: <b>{temp}°C</b>\n"
        "💧 Nem: <b>{humidity}%</b>\n"
        "💨 Rüzgar: <b>{wind} m/s</b>\n"
        "☁️ Durum: <b>{description}</b>"
    ),
    "weather_error":         "❌ Şehir bulunamadı. Farklı bir ad deneyin.",

    "profile_text":          (
        "👤 <b>Profiliniz:</b>\n\n"
        "📛 Ad: <b>{name}</b>\n"
        "🏙 Şehir: <b>{city}</b>\n"
        "🌐 Dil: <b>{lang}</b>\n"
        "⭐ Tarife: <b>{tariff}</b>\n\n"
        "📊 <b>İstatistikler:</b>\n"
        "💸 Harcamalar: <b>{expenses}</b>\n"
        "⏰ Hatırlatıcılar: <b>{reminders}</b>\n"
        "📅 Günlük planlar: <b>{plans}</b>"
    ),
    "btn_edit_name":         "✏️ Adı düzenle",
    "btn_edit_city":         "✏️ Şehri düzenle",
    "enter_new_name":        "✏️ Yeni adınızı girin:",
    "enter_new_city":        "✏️ Yeni şehrinizi girin:",
    "profile_updated":       "✅ Bilgiler güncellendi!",

    "ai_info":               "🤖 <b>YZ Asistan</b>\nBir bölüm seçin:",
    "ai_chat":               "💬 Sohbet",
    "ai_no_balance":         "❌ Yetersiz bakiye. Bakiyenizi doldurun veya abonelik satın alın.",
    "ai_processing":         "⏳ Yanıt hazırlanıyor...",
    "ai_error":              "❌ Hata oluştu. Lütfen tekrar deneyin.",
    "ai_ask_prompt":         "✏️ İsteğinizi girin:",
    "ai_deducted":           "💳 {amount} som düşüldü.",

    "balance_text":          "💰 <b>Bakiyeniz:</b> <b>{amount} som</b>",
    "balance_topup_btn":     "➕ Bakiye yükle",
    "balance_offer":         (
        "⚠️ <b>Ödeme Teklifi</b>\n\n"
        "• Yatırılan tutarlar iade edilmez.\n"
        "• Ödeme yalnızca gerçek makbuz ile onaylanır.\n"
        "• Sahte makbuz hesabın askıya alınmasına yol açar.\n\n"
        "Şartları kabul ediyor musunuz?"
    ),
    "choose_payment":        "Ödeme yöntemini seçin:",
    "btn_pay_stars":         "⭐ Telegram Stars",
    "btn_pay_card":          "💳 Kartla ödeme",
    "enter_amount":          "💰 Ne kadar yüklemek istiyorsunuz? (yalnızca rakam)",
    "card_payment_info":     (
        "💳 <b>Kartla Ödeme</b>\n\n"
        "Tutarı şu karta aktarın:\n"
        "<code>{card_number}</code>\n"
        "<b>{card_holder}</b>\n\n"
        "Tutar: <b>{amount} som</b>\n\n"
        "Ödeme sonrası makbuzu (ekran görüntüsü) gönderin."
    ),
    "receipt_received":      "✅ Makbuzunuz alındı. Onay bekleniyor (5–30 dk).",
    "balance_added":         "✅ Bakiyenize <b>{amount} som</b> eklendi!",
    "payment_rejected":      "❌ Ödemeniz reddedildi. Sorular için yöneticiyle iletişime geçin.",

    "tariff_info":           (
        "⭐ <b>Tarifeler</b>\n\n"
        "🆓 <b>Ücretsiz:</b> YZ işlevlerinden 1 kez kullanım\n\n"
        "📦 <b>Standard:</b>\n"
        "   • Aylık: 49.900 som\n"
        "   • Yıllık: 499.900 som\n\n"
        "💎 <b>Premium:</b>\n"
        "   • Aylık: 99.900 som\n"
        "   • Yıllık: 999.900 som\n\n"
        "Tarife seçin:"
    ),
    "btn_standard":          "📦 Standard",
    "btn_premium":           "💎 Premium",
    "btn_monthly":           "📅 Aylık",
    "btn_yearly":            "📆 Yıllık",
    "tariff_activated":      "✅ <b>{tariff}</b> tarifesi etkinleştirildi! Bitiş: {expires}",

    "referral_info":         (
        "🎁 <b>Referans Programı</b>\n\n"
        "Bu linki arkadaşlarınızla paylaşın:\n"
        "{link}\n\n"
        "👥 Referanslarınız: <b>{count}</b>\n\n"
        "🎯 <b>İndirimler:</b>\n"
        "• 5 referans → Standard -%20, Premium -%5\n"
        "• 10 referans → Standard -%37, Premium -%10\n\n"
        "💡 Kullanılmayan indirimler sonraki aya aktarılır."
    ),

    "settings_lang":         "⚙️ Dil seçin:",

    "admin_contact_text":    (
        "📞 <b>Yönetici ile İletişim</b>\n\n"
        "Öneri, soru veya şikayetler için:\n"
        "👤 @{admin_username}\n\n"
        "❤️ Botu bağış yaparak destekleyin:\n"
        "{donation_link}"
    ),

    "blocked_msg":           "🚫 Hesabınız engellendi. İletişim: @{admin_username}",
    "unblocked_msg":         "✅ Hesabınızın engeli kaldırıldı. Botu kullanabilirsiniz.",
    "banned_word_warning":   "⚠️ Uyarı: yasaklı kelime kullandınız. ({count}/{max} kez)",
    "banned_word_blocked":   "🚫 Yasaklı kelimeleri tekrar kullandığınız için hesabınız engellendi.",
    "must_subscribe":        "📢 Botu kullanmak için önce abone olun:",
    "morning_quote":         "☀️ <b>Günün ilhamı:</b>\n\n{quote}",

    "help_text":             (
        "ℹ️ <b>Yardım</b>\n\n"
        "/start — Botu yeniden başlat\n"
        "/menu — Ana menü\n"
        "/profile — Profiliniz\n"
        "/offer — Kullanım şartları\n"
        "/settings — Ayarlar\n"
        "/help — Yardım\n"
        "/balance — Bakiye\n"
        "/tariff — Tarifeler\n"
        "/referral — Referans programı\n"
        "/ai — YZ Asistan\n"
        "/expenses — Harcamalar\n"
        "/reminders — Hatırlatıcılar\n"
        "/plans — Günlük plan\n"
        "/weather — Hava durumu\n"
        "/currency — Döviz"
    ),

    "period_today":          "Bugünkü",
    "period_week":           "Haftalık",
    "period_month":          "Aylık",
    "period_year":           "Yıllık",
    "tariff_free":           "Ücretsiz",
    "tariff_standard":       "Standard",
    "tariff_premium":        "Premium",
    "tariff_expires":        "Bitiş: {date}",
    "tariff_no_expire":      "Sınırsız",
}
