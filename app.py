# (через Terminal окно)
    #  python.exe -m pip install --upgrade pip
    #  pip install Jinja2
    #  pip install Flask
    #  pip install requests
    # наличие requirements.txt при выгрузке на хостинг
from jinja2 import Template, Environment, FileSystemLoader
from flask import Flask, render_template, redirect, url_for, request, session, app


app = Flask(__name__)
app.secret_key = 'ваш_очень_секретный_ключ'

# Словарь продуктов (оставляем как константу, он общий)
l0 = {
    'Молоко': 60, 'Кефир': 53, 'Творог': 145, 'Яйцо куриное': 157, 'Макароны': 333, 'Йогурт': 68,
    'Мороженое пломбир': 232, 'Сметана': 206, 'Сыр твердый': 344, 'Скумбрия': 191, 'Щука': 84,
    'Кальмар': 100, 'Икра красная': 249, 'Батон': 262, 'Крупа рисовая': 333, 'Мука': 329,
    'Печенье': 417, 'Хлеб': 201, 'Сушки': 339, 'Сухари': 399, 'Фасоль': 298, 'Арахис': 552,
    'Миндаль': 609, 'Фундук': 653, 'Кабачки': 24, 'Капуста белокочанная': 28, 'Капуста брокколи': 34,
    'Капуста пекинская': 16, 'Картофель': 77, 'Морковь': 35, 'Огурец': 14, 'Помидор': 24,
    'Редис': 20, 'Свекла': 42, 'Спаржа': 21, 'Тыква': 22, 'Чеснок': 149, 'Шпинат': 23,
    'Абрикос': 44, 'Авокадо': 160, 'Ананас': 52, 'Апельсин': 43, 'Банан': 96, 'Виноград': 72,
    'Гранат': 72, 'Грейпфрут': 35, 'Груша': 47, 'Ежевика': 34, 'Лимон': 34, 'Киви': 47,
    'Мандарин': 38, 'Персик': 45, 'Яблоки': 47, 'Курага': 32, 'Чернослив': 256, 'Финики': 292,
    'Грибы белые': 34, 'Грибы шампиньоны': 27, 'Сок апельсиновый': 45, 'Сок виноградный': 70,
    'Сок морковный': 56, 'Масло подсолнечное': 899, 'Масло оливковое': 898, 'Майонез': 629,
    'Колбаса сервелат': 461, 'Колбаски охотничьи': 463
}
l_keys = ["--выбирите продукт--"] + list(l0.keys())


def is_part_in_list(str_, words):
    return any(word in str_ for word in words)


@app.route('/')
@app.route('/main')
def main():
    # Извлекаем данные из сессии (если их нет - подставляем пустые значения)
    user_messages = session.get('user_messages', [])
    mes_massa = session.get('mes_massa', "")

    # Считаем сумму калорий на лету из списка в сессии
    total_kkal = round(sum(msg['kkal'] for msg in user_messages), 2)

    return render_template('main.html',
                           messages=user_messages,
                           summa=total_kkal,
                           products=l_keys,
                           mes_massa=mes_massa,
                           username=session.get('username'))


@app.route('/add_message', methods=['POST'])
def add_message():
    text = request.form.get('text')
    massa = request.form.get('massa', "")

    # Инициализируем список сообщений в сессии
    if 'user_messages' not in session:
        session['user_messages'] = []

    error_msg = ""

    if text == "--выбирите продукт--":
        error_msg = "вы не выбрали тип продукта"
    else:
        if massa == "":
            error_msg = "вы не выбрали вес продукта"
        elif "-" in massa:
            error_msg = "вы ввели вес меньше 0"
        elif massa == "0":
            error_msg = "вы ввели вес равный 0"
        elif is_part_in_list(massa, [",", "."]):
            error_msg = "введите целое число грамм"
        elif not massa.isdigit():
            error_msg = "вы ввели не число"
        elif int(massa) > 10000:
            error_msg = "ведрами есть нельзя)"
        else:
            # УСПЕШНОЕ ДОБАВЛЕНИЕ
            kkal = round(int(massa) / 100 * l0.get(text, 0), 2)

            # Работаем с сессией (сохраняем как список словарей)
            temp_list = session['user_messages']
            temp_list.append({'text': text, 'massa': massa, 'kkal': kkal})
            session['user_messages'] = temp_list
            session.modified = True
            error_msg = ""

    session['mes_massa'] = error_msg
    return redirect(url_for('main'))


@app.route('/login', methods=['POST'])
def login():
    session['username'] = request.form.get('user_input')
    # При логине можно сразу очистить старый список или оставить
    return redirect(url_for('main'))


@app.route('/logout')
def logout():
    session.clear()  # Полная очистка сессии
    return redirect(url_for('main'))


@app.route('/del_messages', methods=['POST'])
def del_messages():
    session['user_messages'] = []
    session['mes_massa'] = ""
    return redirect(url_for('main'))


# JSON - Postman

# 1. Очистка списка (API-запрос)
@app.route('/del_messages_req', methods=['POST'])
def del_messages_req():
    # Очищаем только данные текущего пользователя в сессии
    session.pop('user_messages', None)
    session.pop('mes_massa', None)

    # Возвращаем JSON-ответ
    return {
        "Список обнулён!": True,
        "Список выбранных продуктов": []
    }


# 2. Показать накопленный список (API-запрос)
@app.route('/show_messages_req', methods=['POST'])
def show_messages_reg():
    # Достаем список из сессии (если пусто — возвращаем [])
    user_messages = session.get('user_messages', [])

    # Считаем сумму калорий только для этого пользователя
    total_kkal = round(sum(msg['kkal'] for msg in user_messages), 2)

    return {
        'Список выбранных продуктов': user_messages,
        'Сумма калорий в выбранных продуктах(ККал)': str(total_kkal)
    }


# 3. Вывод справочника (не зависит от сессии, отдаем общий словарь)
@app.route('/list', methods=['GET'])
def list_food():
    return {'Справочник калорийности продуктов': l0}


# 4. Поиск калорийности (не зависит от сессии)
@app.route('/search', methods=['GET'])
def search():
    food = request.args.get('food', '').strip()

    if not food:
        return 'Вы не ввели в запросе параметр "food"!', 400

    # Проверка на кириллицу (упрощенно)
    if not any(c.isalpha() for c in food):
        return 'Введите буквенное значение на русском языке!', 400

    # Ищем в объединенном словаре (регистронезависимо)
    food_lower = food.lower()
    if food_lower in l_full:
        return {food: l_full[food_lower]}
    else:
        return 'Данный тип продукта не найден в списке!', 404

if __name__ == '__main__':
    app.run(debug=True)
