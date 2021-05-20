

bot_token = '1895662227:AAE5r4BVeFJSpeqHa5iuW51YW9N3KnCbnEY' # токен бота
LOGIN_BOT = '@sakhshop_bot' # логин бота
CHANNEL_ID = 1297563696 # id канала куда будет отсылаться информация, ид без -100 в начале (например: 124873248)

admin_id = 1783544652 # id админа

LOGIN_ADMIN = '@sakh7_bot' # тг логин спамера, нужен для информации

QIWI_NUMBER = '+79621080800'    # номер киви
QIWI_TOKEN = '7a46607dded191dd89429f5cdc8e95dc'            # токен киви


PERCENT_SPAM = 0.9  # Процент спамеру (0.5 = 50%) #не работает в версии без спамеров
PERCENT_OWN = 0.1   # Процент вам (0.5 = 50%)

main_bd = '/home/TiredCat/Admin bot/main.db'


info = 'Информация\n' \
'Telegram поддержки @login' \

text_purchase = '❕ Вы выбрали: ' \
                '{name}\n\n' \
                '{info}\n\n' \
                '💠 Цена: {price} рублей\n' \
                '💠 Товар: {amount}\n' \
  '💠 Введите ваш адрес после оплаты' \


replenish_balance = '➖➖➖➖➖➖➖➖➖➖➖\n' \
                    '💰 Пополнение баланса\n\n' \
                    '🥝 Оплата киви: \n\n' \
                    '👉 Номер  {number}\n' \
                    '👉 Комментарий  {code}\n' \
                    '👉 Сумма  от 1 до 15000 рублей\n' \
                    '➖➖➖➖➖➖➖➖➖➖➖\n' \

profile = '🧾 Профиль\n\n' \
          '❕ Ваш id - {id}\n' \
          '❕ Ваш логин - {login}\n' \
          '❕ Дата регистрации - {data}\n\n' \
          '💰 Ваш баланс - {balance} рублей'
