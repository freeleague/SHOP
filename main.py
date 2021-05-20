#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import menu
import settings
import functions as func
import telebot
from telebot import types
import time
import datetime
import random
import traceback

catalog_dict = {}
product_dict = {}
download_dict = {}
balance_dict = {}
admin_sending_messages_dict = {}
edit_price_dict = {}

def start_bot():
    bot = telebot.TeleBot(settings.bot_token)

    # Command start
    @bot.message_handler(commands=['start'])
    def handler_start(message):
        chat_id = message.chat.id
        func.first_join(user_id=chat_id, name=message.from_user.username)
        bot.send_message(chat_id,
                         text='Добро пожаловать {}!'.format(message.from_user.first_name),
                         reply_markup=menu.cities)

    # Command admin
    @bot.message_handler(commands=['admin'])
    def handler_admin(message):
        chat_id = message.chat.id
        if chat_id == settings.admin_id:
            bot.send_message(chat_id, 'Вы перешли в меню админа', reply_markup=menu.admin_menu)
            
    # Обработка данных
    @bot.callback_query_handler(func=lambda call: True)
    def handler_call(call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id

        # Main menu
        if call.data == 'edit_price':
            msg = bot.send_message(
                chat_id=chat_id,
                text=f'Выберите каталог:\n{func.edit_price_list_c()}'
            )

            bot.register_next_step_handler(msg, edit_price)

        if '🇷🇺' in call.data or '🇺🇦' in call.data or '🇰🇿' in call.data:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f'Добро пожаловать в меню, вы выбрали город {call.data}',
                reply_markup=menu.main_menu
            )

        if call.data in 'ruuakz':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Выберите город',
                reply_markup=func.cities(call.data)
            )

        if call.data == 'catalog':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Каталог',
                reply_markup=func.menu_catalog()
            )

        if call.data == 'exit_from_catalog':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы вернулись назад',
                reply_markup=menu.main_menu
            )

        if call.data == 'admin_address':
            bot.send_message(
                chat_id=chat_id,
                text=func.admin_address(),
                reply_markup=menu.to_close
            )


        if call.data in func.list_sections():
            name = call.data
            product = func.Product(chat_id)
            product_dict[call.message.chat.id] = product
            product.section = name

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f'❕ Выберите нужный товар',
                reply_markup=func.menu_section(call.data)
            )

        if call.data in func.list_product():
            product = func.Product(chat_id)
            product_dict[chat_id] = product
            product = product_dict[chat_id]

            info = func.menu_product(call.data, product)
            product.product = info[1].product
            product.section = info[1].section
            product.amount_MAX = info[1].amount_MAX
            product.price = info[1].price

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=info[0],
                reply_markup=menu.btn_purchase
            )


        try:
            if call.data == 'buy':
                product = product_dict[chat_id]
                msg = bot.send_message(chat_id=chat_id,
                                       text=f'❕ Введите кол-во товара\n❕ От 1 - 15')
                bot.register_next_step_handler(msg, buy)
        except: pass
        
        try:
            if call.data == 'info':
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=settings.info,
                    reply_markup=menu.main_menu
                )
        except: pass

        if call.data == 'exit_to_menu':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы вернулись в главное меню',
                reply_markup=menu.main_menu
            )

        if call.data == 'btn_ok':
            bot.delete_message(chat_id, message_id)
        
        try:
            if call.data == 'profile':
                info = func.profile(chat_id)
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=settings.profile.format(
                                          id=info[0],
                                          login=f'@{info[1]}',
                                          data=info[2][:19],
                                          balance=info[5]
                                      ),
                                      reply_markup=menu.main_menu)
        except: pass

        # Admin menu
        try:
            if call.data == 'admin_info':
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=func.admin_info(),
                    reply_markup=menu.admin_menu
                )
        except: pass

        if call.data == 'add_section_to_catalog':
            if chat_id == settings.admin_id:
                msg = bot.send_message(chat_id=chat_id,
                                       text='Введите название раздела')
                bot.register_next_step_handler(msg, create_section)

        if call.data == 'del_section_to_catalog':
            if chat_id == settings.admin_id:
                conn = sqlite3.connect("base_ts.sqlite")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM catalog')
                row = cursor.fetchall()
                cursor.close()
                conn.close()

                text = ''
                num = 0

                for i in row:
                    text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                    num += 1

                msg = bot.send_message(
                    chat_id=chat_id,
                    text='Введите номер раздела\n\n'
                         f'{text}'
                )
                bot.register_next_step_handler(msg, del_section)

        if call.data == 'add_product_to_section':
            if chat_id == settings.admin_id:
                conn = sqlite3.connect("base_ts.sqlite")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM catalog')
                row = cursor.fetchall()

                text = ''
                num = 0

                for i in row:
                    text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                    num += 1

                msg = bot.send_message(chat_id=chat_id,
                                       text='Введите номер раздела в которы вы хотите добавить товар\n\n'
                                            f'{text}')
                bot.register_next_step_handler(msg, create_product)

        if call.data == 'del_product_to_section':
            if chat_id == settings.admin_id:
                conn = sqlite3.connect("base_ts.sqlite")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM catalog')
                row = cursor.fetchall()

                text = ''
                num = 0

                for i in row:
                    text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                    num += 1

                msg = bot.send_message(chat_id=chat_id,
                                       text='Введите номер раздела из которого вы хотите удалить товар\n\n'
                                            f'{text}')
                bot.register_next_step_handler(msg, del_product)

        if call.data == 'download_product':
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM catalog')
            row = cursor.fetchall()

            text = ''
            num = 0

            for i in row:
                text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                num += 1

            msg = bot.send_message(chat_id=chat_id,
                                   text='Введите номер раздела\n\n'
                                        f'{text}')
            bot.register_next_step_handler(msg, download_product)

        if call.data == 'exit_admin_menu':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы покинули меню админа',
                reply_markup=menu.main_menu
            )

        if call.data == 'back_to_admin_menu':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы перешли в меню админа',
                reply_markup=menu.admin_menu
            )

        if call.data == 'catalog_control':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы перешли в управление каталогом',
                reply_markup=menu.admin_menu_control_catalog
            )

        if call.data == 'section_control':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы перешли в управление разделами',
                reply_markup=menu.admin_menu_control_section
            )

        if call.data == 'replenish_balance':
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=func.replenish_balance(chat_id),
                                  reply_markup=menu.replenish_balance)

        if call.data == 'cancel_payment':
            func.cancel_payment(chat_id)
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text='❕ Добро пожаловать!',
                                  reply_markup=menu.main_menu)

        if call.data == 'check_payment':
            check = func.check_payment(chat_id)
            if check[0] == 1:
                bot.edit_message_text(chat_id=chat_id,
                                      message_id=message_id,
                                      text=f'✅ Оплата прошла\nСумма - {check[1]} руб',
                                      reply_markup=menu.main_menu)

                bot.send_message(chat_id=settings.admin_id,
                                 text='💰 Пополнение баланса\n'
                                      f'🔥 От - {chat_id}/{call.message.from_user.username}/{call.message.from_user.first_name}\n'
                                      f'🔥 Сумма - {check[1]} руб')

                try:
                    bot.send_message(chat_id=f'-100{settings.CHANNEL_ID}',
                                     text='💰 Пополнение баланса\n'
                                          f'🔥 Бот пренадлежит - {settings.LOGIN_ADMIN}'
                                          f'🔥 От - {chat_id}/{call.message.from_user.username}/{call.message.from_user.first_name}\n'
                                          f'🔥 Сумма - {check[1]} руб')
                except: pass

            if check[0] == 0:
                bot.send_message(chat_id=chat_id,
                                 text='❌ Оплата не найдена',
                                 reply_markup=menu.to_close)

        if call.data == 'to_close':
            bot.delete_message(chat_id=chat_id,
                               message_id=message_id)

        if call.data == 'give_balance':
            msg = bot.send_message(chat_id=chat_id,
                                   text='Введите id человека, которому будет изменён баланс')

            bot.register_next_step_handler(msg, give_balance)

        if call.data == 'admin_sending_messages':
            msg = bot.send_message(chat_id,
                                   text='Введите текст рассылки')
            bot.register_next_step_handler(msg, admin_sending_messages)

    def edit_price(message):
        try:
            edit_price = func.Edit_price(message.chat.id)
            edit_price_dict[message.chat.id] = edit_price
            edit_price = edit_price_dict[message.chat.id]
            edit_price.catalog = message.text

            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'Выберите товар:\n{func.edit_price_list_p(edit_price.catalog)}')

            bot.register_next_step_handler(msg, edit_price_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def edit_price_2(message):
        try:
            edit_price = edit_price_dict[message.chat.id]
            edit_price.product = message.text

            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'Введите сумму')

            bot.register_next_step_handler(msg, edit_price_3)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def edit_price_3(message):
        try:
            edit_price = edit_price_dict[message.chat.id]
            edit_price.sum = message.text

            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'{func.edit_price(edit_price)}',
                                   reply_markup=menu.admin_menu)

        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def give_balance(message):
        try:
            balance = func.GiveBalance(message.text)
            balance_dict[message.chat.id] = balance

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Введите сумму на которую изменится баланс(к балансу не добавится эта сумма, а баланс изменится на неё)')

            bot.register_next_step_handler(msg, give_balance_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def give_balance_2(message):
        try:
            balance = balance_dict[message.chat.id]
            balance.balance = message.text
            code = random.randint(111, 999)
            balance.code = code
            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'Логин - {balance.login}\n'
                                        f'Баланс изменится на - {balance.balance}\n'
                                        f'Для подтверждения введите {code}')

            bot.register_next_step_handler(msg, give_balance_3)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def give_balance_3(message):
        try:
            balance = balance_dict[message.chat.id]
            if int(message.text) == balance.code:
                func.give_balance(balance)
                bot.send_message(chat_id=message.chat.id,
                                 text='✅ Баланс успешно изменён')
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def create_section(message):
        try:
            name = message.text
            catalog = func.Catalog(name)
            catalog_dict[message.chat.id] = catalog
            msg = bot.send_message(chat_id=message.chat.id,
                                   text=name + '\n\n Создать?',
                                   reply_markup=menu.markup)
            bot.register_next_step_handler(msg, create_section_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def buy(message):
        try:
            product = product_dict[message.chat.id]
            if int(message.text) in range(1, int(product.amount_MAX)+1):
                product.amount = int(message.text)

                code = random.randint(111, 999)
                product.code = code

                msg = bot.send_message(chat_id=message.chat.id,
                    text=f'❕ Вы выбрали - {product.product}\n'
                       f'❕ Кол-во - {product.amount}\n'
                       f'❕ Цена - {float(product.price) * int(product.amount)} руб\n'
                       f'👉 Для подтверждения покупки отправьте {code}')
                bot.register_next_step_handler(msg, buy_2)
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='❌ Неверное кол-во',
                                 reply_markup=menu.main_menu)
        except:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def buy_2(message):
        try:
            product = product_dict[message.chat.id]
            if int(message.text) == product.code:
                check = func.check_balance(product.user_id, (float(product.price)*int(product.amount)))

                if check == 1:

                    func.buy(product)

                    if func.check_settings()[0][1] == '1':

                        msg = bot.send_message(chat_id=message.chat.id,
                                     text=f'⚠️ Введите адрес доставки или напишите в поддержку о встрече с дропом (+100р)')

                        bot.register_next_step_handler(msg, address)
                    else:

                        bot.send_message(chat_id=message.chat.id,
                                        text=f'✅ Вы успешно купили товар',
                                        reply_markup=menu.main_menu)

                    bot.send_message(chat_id=settings.admin_id,
                                     text=f'✅ Куплен товар\n\n'
                                          f'❕ Купил - {message.chat.id}/{message.from_user.username}/{message.from_user.first_name}\n'
                                          f'❕ Сумма покупки - {float(product.price) * int(product.amount)}\n'
                                          f'❕ Дата покупки - {datetime.datetime.now()}\n')

                    try:
                        bot.send_message(chat_id=f'-100{settings.CHANNEL_ID}',
                                         text=f'✅ Куплен товар\n\n'
                                              f'❕ Купил - {message.chat.id}/{message.from_user.username}/{message.from_user.first_name}\n'
                                              f'❕ Сумма покупки - {float(product.price) * int(product.amount)}\n'
                                              f'❕ Дата покупки - {datetime.datetime.now()}\n')

                    except: pass

                if check == 0:
                    bot.send_message(chat_id=message.chat.id,
                                     text='❌ На балансе недостаточно средств',
                                     reply_markup=menu.main_menu)

            else:
                bot.send_message(chat_id=message.chat.id,
                                 text='❌ Покупка отменина',
                                 reply_markup=menu.main_menu)
        except:
            bot.send_message(chat_id=message.chat.id,
                             text='⚠️ Что-то пошло не по плану',
                             reply_markup=menu.main_menu)

    def address(message):
        bot.send_message(chat_id=message.chat.id,
                             text=f'Ващ адрес доставки\n{message.text}')

        bot.send_message(chat_id=message.chat.id,
                                        text=f'✅ Вы успешно купили товар',
                                        reply_markup=menu.main_menu)

    def create_section_2(message):
        try:
            if message.text == 'Yes':
                catalog = catalog_dict[message.chat.id]
                func.add_section_to_catalog(catalog.name)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'✅Раздел: {catalog.name}\n'
                         f'✅Успешно добавлен в каталог',
                    reply_markup=menu.admin_menu
                )
        except Exception as e:
            print(e)

    def del_section(message):
        try:
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM catalog')
            row = cursor.fetchall()
            cursor.close()
            conn.close()

            name = row[int(message.text)][1]
            nm = row[int(message.text)][0]
            num_catalog = func.Catalog(name)
            catalog_dict[message.chat.id] = num_catalog

            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Yes', 'No')

            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'{nm}\nУдалить этот каталог?',
                                   reply_markup=menu.markup)

            bot.register_next_step_handler(msg, del_section_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def del_section_2(message):
        try:
            if message.text == 'Yes':
                catalog = catalog_dict[message.chat.id]
                func.del_section_to_catalog(catalog.name)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'✅Раздел: {catalog.name}\n'
                         f'✅Успешно удален из каталог',
                    reply_markup=menu.admin_menu
                )
            if message.text == 'No':
                bot.send_message(chat_id=message.chat.id,
                                 text='Вы вернулись в меню админа',
                                 reply_markup=menu.admin_menu)
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def create_product(message):
        try:
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM catalog')
            row = cursor.fetchall()
            cursor.close()
            conn.close()

            name = row[int(message.text)][1]
            num_catalog = func.Product(name)
            product_dict[message.chat.id] = num_catalog

            addproduct = product_dict[message.chat.id]
            addproduct.section = name

            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'{name}\nВведите название товара')

            bot.register_next_step_handler(msg, create_product_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def create_product_2(message):
        try:
            product_name = message.text
            product = product_dict[message.chat.id]
            product.product = product_name

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Введите цены на товар')
            bot.register_next_step_handler(msg, create_product_3)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def create_product_3(message):
        try:
            price = message.text
            product = product_dict[message.chat.id]
            product.price = price

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Введите описание товара')

            bot.register_next_step_handler(msg, create_product_4)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def create_product_4(message):
        try:
            product = product_dict[message.chat.id]
            product.info = message.text
            
            product_name = f'{product.product} | {product.price} руб'
            msg = bot.send_message(chat_id=message.chat.id,
                                   text=f'{product_name}\n\n'
                                        'Создать?',
                                   reply_markup=menu.markup)
            bot.register_next_step_handler(msg, create_product_5)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def create_product_5(message):
        try:
            if message.text == 'Yes':
                product = product_dict[message.chat.id]
                product_name = f'{product.product} | {product.price} руб'

                func.add_product_to_section(product_name, product.price, product.section, product.info)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'✅Товар: {product_name}\n'
                         f'✅Успешно добавлен в раздел',
                    reply_markup=menu.admin_menu
                )
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def del_product(message):
        try:
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM catalog')
            row = cursor.fetchall()
            cursor.close()
            conn.close()

            name = row[int(message.text)][1]
            product = func.AddProduct(name)
            product_dict[message.chat.id] = product

            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM "{name}"')
            row = cursor.fetchall()
            cursor.close()
            conn.close()

            text = ''
            num = 0

            for i in row:
                text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                num += 1

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Выберите номер товара который хотите удалить\n\n'
                                        f'{text}')
            bot.register_next_step_handler(msg, del_product_2)
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def del_product_2(message):
        try:
            product = product_dict[message.chat.id]

            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM '{product.section}'")
            row = cursor.fetchall()

            name_product = row[int(message.text)][0]
            product.product = name_product

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='❕Удалить ⬇️\n'
                                        f'❕{product.product}\n\n'
                                        '❕из раздела ⬇️\n'
                                        f'❕{product.section}  ?',
                                   reply_markup=menu.markup)
            bot.register_next_step_handler(msg, del_product_3)
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def del_product_3(message):
        try:
            if message.text == 'Yes':
                product = product_dict[message.chat.id]

                func.del_product_to_section(product.product, product.section)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=f'✅Товар: {product.product}\n'
                         f'✅Успешно удален из раздела',
                    reply_markup=menu.admin_menu
                )
            if message.text == 'No':
                bot.send_message(chat_id=message.chat.id,
                                 text='Вы вернулись в меню админа',
                                 reply_markup=menu.admin_menu)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def download_product(message):
        try:
            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM catalog')
            row = cursor.fetchall()

            name_section = row[int(message.text)][1]
            download = func.DownloadProduct(name_section)
            download_dict[message.chat.id] = download

            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM "{name_section}"')
            row = cursor.fetchall()

            cursor.close()
            conn.close()

            text = ''
            num = 0

            for i in row:
                text = text + '№ ' + str(num) + '   |  ' + str(i[0]) + '\n'
                num += 1

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Выберите номер товара\n\n'
                                        f'{text}')

            bot.register_next_step_handler(msg, download_product_2)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def download_product_2(message):
        try:
            product = download_dict[message.chat.id]

            conn = sqlite3.connect("base_ts.sqlite")
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM "{product.name_section}"')
            row = cursor.fetchall()

            product.name_product = row[int(message.text)][2]

            msg = bot.send_message(chat_id=message.chat.id,
                                   text='Вы хотите добавить товар в ⬇️\n\n'
                                        f'ID - {product.name_product}',
                                   reply_markup=menu.markup)

            bot.register_next_step_handler(msg, download_product_3)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def download_product_3(message):
        try:
            if message.text == 'Yes':
                msg = bot.send_message(chat_id=message.chat.id,
                                       text='❕Отправьте txt файл с товаром\n\n'
                                            '❗️ 1 строчка = 1 товару!!!\n\n'
                                            '❗️ ПРИМЕР ФАЙЛА:\n'
                                            'main@mail.ru:password\n'
                                            'QWERT-QWERY-QWERY\n'
                                            'какая-то_ссылка.ru')

                bot.register_next_step_handler(msg, download_product_4)

            if message.text == 'No':
                bot.send_message(chat_id=message.chat.id,
                                 text='Вы вернулись в меню админа',
                                 reply_markup=menu.admin_menu)
        except Exception as e:
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

    def admin_sending_messages(message):
        dict = func.Admin_sending_messages(message.chat.id)
        admin_sending_messages_dict[message.chat.id] = dict

        dict = admin_sending_messages_dict[message.chat.id]
        dict.text = message.text

        msg = bot.send_message(message.chat.id,
                               text='Отправьте "ПОДТВЕРДИТЬ" для подтверждения')
        bot.register_next_step_handler(msg, admin_sending_messages_2)

    def admin_sending_messages_2(message):
        conn = sqlite3.connect('base_ts.sqlite')
        cursor = conn.cursor()
        dict = admin_sending_messages_dict[message.chat.id]
        if message.text == 'ПОДТВЕРДИТЬ':
            cursor.execute(f'SELECT * FROM users')
            row = cursor.fetchall()

            for i in range(len(row)):
                try:
                    time.sleep(1)
                    bot.send_message(row[i][0], dict.text)

                except:
                    pass
        else:
            bot.send_message(message.chat.id, text='Рассылка отменена', reply_markup=menu.admin_menu)

    @bot.message_handler(content_types=['document'])
    def download_product_4(message):
        try:
            file_name = message.document.file_name.encode('UTF-8').decode('UTF-8')
            chat_id = message.chat.id

            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            download = download_dict[message.chat.id]

            with open(file_name, 'wb') as doc:
                doc.write(downloaded_file)

            func.download_product(file_name, download.name_product)

            bot.send_message(chat_id=chat_id,
                             text='❕ Товар загружен 👍')
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id,
                             text='Упсс, что-то пошло не по плану',
                             reply_markup=menu.admin_menu)

            


    bot.polling(none_stop=True)



start_bot()
