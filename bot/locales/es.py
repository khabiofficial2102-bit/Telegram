# ===================== ESPAÑOL =====================
ES = {
    "choose_language":       "🌐 Elige tu idioma / Choose your language:",
    "mandatory_sub_text":    "📢 Por favor suscríbete al siguiente canal/grupo para usar el bot:",
    "check_sub_btn":         "✅ Verificar suscripción",
    "not_subscribed":        "❌ Aún no te has suscrito. Suscríbete y verifica nuevamente.",
    "offer_text":            (
        "📋 <b>Términos de Uso (Oferta Pública)</b>\n\n"
        "1. Este bot es solo para uso personal.\n"
        "2. Los pagos realizados a través del bot no son reembolsables.\n"
        "3. Los pagos se confirman solo al enviar un recibo válido.\n"
        "4. El uso indebido del bot puede resultar en la suspensión de tu cuenta.\n"
        "5. Tus datos personales no se compartirán con terceros.\n\n"
        "Acepta los términos para continuar."
    ),
    "accept_offer_btn":      "✅ Acepto",
    "welcome_new":           "🎉 <b>¡Bienvenido!</b>\nYa puedes empezar a usar el bot.",
    "enter_name":            "👤 Ingresa tu nombre:",
    "enter_city":            "🏙 Ingresa tu ciudad:",
    "onboard_done":          "✅ ¡Tu información ha sido guardada! Ya puedes usar el bot completo.",

    "menu_btn":              "📋 Menú",
    "main_menu":             "🏠 <b>Menú Principal</b>\nSelecciona una sección:",
    "back_btn":              "⬅️ Atrás",
    "back_main_btn":         "🏠 Menú Principal",

    "btn_expenses":          "💸 Gastos",
    "btn_reminders":         "⏰ Recordatorios",
    "btn_currency":          "💱 Moneda",
    "btn_daily_plan":        "📅 Plan Diario",
    "btn_weather":           "🌤 Clima",
    "btn_profile":           "👤 Perfil",
    "btn_ai":                "🤖 Asistente IA",
    "btn_balance":           "💰 Saldo",
    "btn_tariff":            "⭐ Tarifa",
    "btn_referral":          "🎁 Referido",
    "btn_settings":          "⚙️ Configuración",
    "btn_admin_contact":     "📞 Admin",

    "expenses_info":         (
        "💸 <b>Sección de Gastos</b>\n\n"
        "Para agregar un gasto, escribe en el formato:\n"
        "<code>monto moneda descripción</code>\n\n"
        "📌 Ejemplos:\n"
        "• <code>50 dólares comida</code>\n"
        "• <code>100 USD ropa</code>\n"
        "• <code>200 uzbekistán transporte</code>"
    ),
    "expense_added":         "✅ Gasto agregado: <b>{amount} {currency}</b> — {desc}",
    "expense_invalid":       "❌ Formato inválido. Escribe: <code>monto moneda descripción</code>",
    "btn_today":             "📆 Hoy",
    "btn_week":              "📅 Semana",
    "btn_month":             "🗓 Mes",
    "btn_year":              "📊 Año",
    "btn_convert":           "💱 Convertir",
    "btn_clear_expenses":    "🗑 Limpiar",
    "expense_report_empty":  "📭 No se encontraron gastos en este período.",
    "expense_report_title":  "📊 <b>Reporte de gastos {period}:</b>\n\n",
    "expense_report_total":  "\n💰 <b>Total: {total} {currency}</b>",
    "expense_convert_ask":   "¿A qué moneda quieres convertir?\n(Ej: dólar, EUR, Rusia, sum)",
    "expense_convert_result":"✅ Tus gastos totales: <b>{amount} {currency}</b>",
    "clear_confirm":         "⚠️ ¿Estás seguro de que quieres eliminar todos los gastos?",
    "btn_confirm":           "✅ Confirmar",
    "btn_cancel":            "❌ Cancelar",
    "cleared_success":       "🗑 Todos los gastos han sido eliminados.",
    "cancelled":             "❌ Cancelado.",

    "reminders_info":        (
        "⏰ <b>Sección de Recordatorios</b>\n\n"
        "Para agregar un recordatorio:\n"
        "<code>YYYY-MM-DD HH:MM texto</code>\n\n"
        "📌 Ejemplos:\n"
        "• <code>2024-12-25 09:00 Feliz Navidad</code>\n"
        "• <code>14:30 Tomar medicamento</code> (hoy)"
    ),
    "reminder_ask_repeat":   "🔄 ¿Cómo debe funcionar este recordatorio?",
    "btn_once":              "1️⃣ Una vez",
    "btn_daily":             "🔁 Diariamente",
    "reminder_added":        "✅ Recordatorio agregado: <b>{time}</b> — {text}",
    "reminder_fired":        "⏰ <b>Recordatorio:</b> {text}",
    "reminder_invalid":      "❌ Formato inválido. Usa el formato indicado.",
    "reminders_empty":       "📭 No tienes recordatorios.",
    "btn_list_reminders":    "📋 Ver recordatorios",
    "btn_clear_reminders":   "🗑 Limpiar recordatorios",
    "reminders_cleared":     "🗑 Todos los recordatorios han sido eliminados.",

    "currency_info":         (
        "💱 <b>Conversor de Moneda</b>\n\n"
        "Formato:\n"
        "<code>monto moneda_origen moneda_destino</code>\n\n"
        "📌 Ejemplos:\n"
        "• <code>100 dólar sum</code>\n"
        "• <code>50 EUR UZS</code>"
    ),
    "currency_result":       "💱 <b>{amount} {from_cur}</b> = <b>{result} {to_cur}</b>",
    "currency_error":        "❌ Moneda no encontrada. Intenta con otro nombre.",

    "plan_info":             (
        "📅 <b>Plan Diario</b>\n\n"
        "Formato:\n"
        "<code>HH:MM texto del plan</code>\n\n"
        "📌 Ejemplos:\n"
        "• <code>07:00 Ejercicio matutino</code>\n"
        "• <code>09:00 Iniciar trabajo</code>"
    ),
    "plan_added":            "✅ Plan agregado: <b>{time}</b> — {text}",
    "plan_fired":            "📅 <b>Tu plan diario:</b> {text}",
    "plan_invalid":          "❌ Formato inválido. Escribe: <code>HH:MM texto</code>",
    "plans_empty":           "📭 No tienes planes diarios.",
    "btn_list_plans":        "📋 Ver planes",
    "btn_clear_plans":       "🗑 Limpiar planes",
    "plans_cleared":         "🗑 Todos los planes han sido eliminados.",

    "weather_info":          "🌤 Ingresa el nombre de la ciudad o país para ver el clima:",
    "weather_result":        (
        "🌤 <b>Clima en {city}:</b>\n\n"
        "🌡 Temperatura: <b>{temp}°C</b>\n"
        "💧 Humedad: <b>{humidity}%</b>\n"
        "💨 Viento: <b>{wind} m/s</b>\n"
        "☁️ Condición: <b>{description}</b>"
    ),
    "weather_error":         "❌ Ciudad no encontrada. Intenta con otro nombre.",

    "profile_text":          (
        "👤 <b>Tu Perfil:</b>\n\n"
        "📛 Nombre: <b>{name}</b>\n"
        "🏙 Ciudad: <b>{city}</b>\n"
        "🌐 Idioma: <b>{lang}</b>\n"
        "⭐ Tarifa: <b>{tariff}</b>\n\n"
        "📊 <b>Estadísticas:</b>\n"
        "💸 Gastos: <b>{expenses}</b>\n"
        "⏰ Recordatorios: <b>{reminders}</b>\n"
        "📅 Planes diarios: <b>{plans}</b>"
    ),
    "btn_edit_name":         "✏️ Editar nombre",
    "btn_edit_city":         "✏️ Editar ciudad",
    "enter_new_name":        "✏️ Ingresa tu nuevo nombre:",
    "enter_new_city":        "✏️ Ingresa tu nueva ciudad:",
    "profile_updated":       "✅ ¡Información actualizada!",

    "ai_info":               "🤖 <b>Asistente IA</b>\nSelecciona una sección:",
    "ai_chat":               "💬 Chat",
    "ai_no_balance":         "❌ Saldo insuficiente. Recarga tu saldo o compra una suscripción.",
    "ai_processing":         "⏳ Preparando respuesta...",
    "ai_error":              "❌ Ocurrió un error. Por favor intenta de nuevo.",
    "ai_ask_prompt":         "✏️ Ingresa tu solicitud:",
    "ai_deducted":           "💳 Se descontaron {amount} sum.",

    "balance_text":          "💰 <b>Tu saldo:</b> <b>{amount} sum</b>",
    "balance_topup_btn":     "➕ Recargar saldo",
    "balance_offer":         (
        "⚠️ <b>Oferta de Pago</b>\n\n"
        "• Los fondos depositados no son reembolsables.\n"
        "• El pago solo se confirma con recibo válido.\n"
        "• Enviar recibo falso resultará en suspensión de cuenta.\n\n"
        "¿Aceptas los términos?"
    ),
    "choose_payment":        "Elige el método de pago:",
    "btn_pay_stars":         "⭐ Telegram Stars",
    "btn_pay_card":          "💳 Pago con tarjeta",
    "enter_amount":          "💰 ¿Cuánto quieres recargar? (solo números)",
    "card_payment_info":     (
        "💳 <b>Pago con Tarjeta</b>\n\n"
        "Transfiere el monto a la siguiente tarjeta:\n"
        "<code>{card_number}</code>\n"
        "<b>{card_holder}</b>\n\n"
        "Monto: <b>{amount} sum</b>\n\n"
        "Después del pago, envía el recibo (captura de pantalla)."
    ),
    "receipt_received":      "✅ Tu recibo fue recibido. Esperando confirmación (5–30 min).",
    "balance_added":         "✅ ¡Se han añadido <b>{amount} sum</b> a tu saldo!",
    "payment_rejected":      "❌ Tu pago fue rechazado. Contacta al admin para preguntas.",

    "tariff_info":           (
        "⭐ <b>Tarifas</b>\n\n"
        "🆓 <b>Gratis:</b> 1 uso de funciones IA\n\n"
        "📦 <b>Standard:</b>\n"
        "   • Mensual: 49,900 sum\n"
        "   • Anual: 499,900 sum\n\n"
        "💎 <b>Premium:</b>\n"
        "   • Mensual: 99,900 sum\n"
        "   • Anual: 999,900 sum\n\n"
        "Selecciona una tarifa:"
    ),
    "btn_standard":          "📦 Standard",
    "btn_premium":           "💎 Premium",
    "btn_monthly":           "📅 Mensual",
    "btn_yearly":            "📆 Anual",
    "tariff_activated":      "✅ ¡Tarifa <b>{tariff}</b> activada! Vence: {expires}",

    "referral_info":         (
        "🎁 <b>Programa de Referidos</b>\n\n"
        "Comparte este enlace con tus amigos:\n"
        "{link}\n\n"
        "👥 Tus referidos: <b>{count}</b>\n\n"
        "🎯 <b>Descuentos:</b>\n"
        "• 5 referidos → Standard -20%, Premium -5%\n"
        "• 10 referidos → Standard -37%, Premium -10%\n\n"
        "💡 Los descuentos no usados se guardan para el próximo mes."
    ),

    "settings_lang":         "⚙️ Elige tu idioma:",

    "admin_contact_text":    (
        "📞 <b>Contactar al Admin</b>\n\n"
        "Para sugerencias, consultas o quejas:\n"
        "👤 @{admin_username}\n\n"
        "❤️ Apoya el bot con una donación:\n"
        "{donation_link}"
    ),

    "blocked_msg":           "🚫 Tu cuenta está bloqueada. Contacta: @{admin_username}",
    "unblocked_msg":         "✅ Tu cuenta ha sido desbloqueada. Puedes usar el bot.",
    "banned_word_warning":   "⚠️ Advertencia: usaste una palabra prohibida. ({count}/{max} veces)",
    "banned_word_blocked":   "🚫 Tu cuenta fue bloqueada por usar palabras prohibidas repetidamente.",
    "must_subscribe":        "📢 Por favor suscríbete primero para usar el bot:",
    "morning_quote":         "☀️ <b>Inspiración del día:</b>\n\n{quote}",

    "help_text":             (
        "ℹ️ <b>Ayuda</b>\n\n"
        "/start — Reiniciar el bot\n"
        "/menu — Menú principal\n"
        "/profile — Tu perfil\n"
        "/offer — Términos de uso\n"
        "/settings — Configuración\n"
        "/help — Ayuda\n"
        "/balance — Tu saldo\n"
        "/tariff — Tarifas\n"
        "/referral — Programa de referidos\n"
        "/ai — Asistente IA\n"
        "/expenses — Gastos\n"
        "/reminders — Recordatorios\n"
        "/plans — Plan diario\n"
        "/weather — Clima\n"
        "/currency — Moneda"
    ),

    "period_today":          "Hoy",
    "period_week":           "Semana",
    "period_month":          "Mes",
    "period_year":           "Año",
    "tariff_free":           "Gratis",
    "tariff_standard":       "Standard",
    "tariff_premium":        "Premium",
    "tariff_expires":        "Vence: {date}",
    "tariff_no_expire":      "Ilimitado",
}
