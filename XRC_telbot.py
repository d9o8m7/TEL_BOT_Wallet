import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from web3 import Web3
import sqlite3

# Configura tu token de acceso al bot de Telegram
TOKEN = "TuTokenDeTelegram"

# Configura tu dirección de nodo XinFin y web3
XINFIN_NODE_URL = "https://rpc.xinfin.network"

# Inicializa el bot de Telegram
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Inicializa la conexión a la red XinFin
w3 = Web3(Web3.HTTPProvider(XINFIN_NODE_URL))

# Inicializa la base de datos SQLite para guardar direcciones y movimientos de tokens
conn = sqlite3.connect('wallets.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS wallets (user_id INTEGER, wallet_address TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS token_movements (user_id INTEGER, wallet_address TEXT, token_contract_address TEXT, movement TEXT)')

# Manejador del comando /start
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        fr"Hola {user.mention_html()}!\n"
        "Puedes usar los comandos /addwallet para guardar una dirección de billetera y /movimientos para ver los movimientos de tokens.",
    )

# Manejador del comando /addwallet para guardar una dirección de billetera
def add_wallet(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if len(context.args) == 0:
        update.message.reply_text("Por favor, proporciona una dirección de billetera.")
        return

    wallet_address = context.args[0]

    # Verifica si la dirección de billetera ya está en la base de datos
    cursor.execute('SELECT wallet_address FROM wallets WHERE user_id = ? AND wallet_address = ?', (user_id, wallet_address))
    existing_wallet = cursor.fetchone()

    if existing_wallet:
        update.message.reply_text("Esta dirección de billetera ya está guardada.")
    else:
        cursor.execute('INSERT INTO wallets (user_id, wallet_address) VALUES (?, ?)', (user_id, wallet_address))
        conn.commit()
        update.message.reply_html(f"La dirección de billetera {wallet_address} ha sido guardada.")

# Manejador del comando /movimientos para ver los movimientos de tokens
def movements(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Obtén las direcciones de billetera guardadas por el usuario
    cursor.execute('SELECT wallet_address FROM wallets WHERE user_id = ?', (user_id,))
    wallet_addresses = cursor.fetchall()

    if not wallet_addresses:
        update.message.reply_text("Aún no has guardado ninguna dirección de billetera.")
    else:
        keyboard = [
            [InlineKeyboardButton(wallet[0], callback_data=f'address:{wallet[0]}') for wallet in wallet_addresses]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Selecciona una dirección de billetera para ver sus movimientos:", reply_markup=reply_markup)

# Manejador de los botones de dirección de billetera
def button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data.startswith("address:"):
        wallet_address = data[len("address:"):]
        user_id = query.from_user.id

        # Aquí puedes agregar la lógica para obtener y mostrar los movimientos de tokens XRC-20/XRC-721 para la dirección de billetera seleccionada
        # Utiliza la biblioteca web3 para interactuar con los contratos inteligentes de tokens y obtener los movimientos.

        # Por ejemplo, puedes usar la función w3.eth.getPastLogs para obtener los eventos de transferencia de tokens en la dirección especificada.

        # Luego, muestra los movimientos de tokens en la conversación de Telegram.
        # query.answer(f"Mostrando movimientos de tokens para la dirección {wallet_address}")

# Agrega comandos y manejadores al bot
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("addwallet", add_wallet, pass_args=True))
dispatcher.add_handler(CommandHandler("movimientos", movements))
dispatcher.add_handler(CallbackQueryHandler(button))

# Inicia el bot
updater.start_polling()
updater.idle()

