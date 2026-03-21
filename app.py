# (через Terminal окно)
    #  python.exe -m pip install --upgrade pip
    #  pip install Jinja2
    #  pip install Flask
    #  pip install requests
    #  pip install Flask-Session
    # наличие requirements.txt при выгрузке на хостинг
from jinja2 import Template, Environment, FileSystemLoader
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_permanent_key_123'

# Настройка серверных сессий
app.config['SESSION_TYPE'] = 'filesystem'
# Чтобы папка с сессиями создалась в корне проекта
app.config['SESSION_FILE_DIR'] = './flask_session'
Session(app)

# Словарь продуктов
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

# Предварительно создаем словарь для поиска в нижнем регистре
l0_lookup = {k.lower(): (k, v) for k, v in l0.items()}
l_keys = list(l0.keys())

def is_part_in_list(str_, words):
    return any(word in str_ for word in words)

@app.route('/')
@app.route('/main')
def main():
    user_messages = session.get('user_messages', [])
    mes_massa = session.get('mes_massa', "")
    total_kkal = round(sum(msg.get('kkal', 0) for msg in user_messages), 2)

    return render_template('main.html',
                           messages=user_messages,
                           summa=total_kkal,
                           products=l_keys,
                           mes_massa=mes_massa,
                           username=session.get('username'))


@app.route('/add_message', methods=['POST'])
def add_message():
    text = request.form.get('text')
    massa = request.form.get('massa', "").strip()

    # Сохраняем ввод в сессию, чтобы он не сбросился в форме
    session['current_text'] = text
    session['current_massa'] = massa

    error_msg = ""

    # 1. Проверка на выбор продукта
    if not text or text == "" or text == "--выберите продукт--":
        error_msg = "вы не выбрали тип продукта"

    # 2. Проверка на пустое поле
    elif not massa:
        error_msg = "вы не ввели вес продукта"

    # 3. ПРОВЕРКА НА ДРОБНОЕ ЧИСЛО (точка или запятая)
    elif "." in massa or "," in massa:
        error_msg = "введите целое число грамм (без точек и запятых)"

    # 4. Проверка на отрицательное число (через минус)
    elif "-" in massa:
        error_msg = "вы ввели вес меньше 0"

    # 5. Проверка на буквы и спецсимволы
    elif not massa.isdigit():
        error_msg = "вы ввели не число"

    # 6. Проверка на логические границы
    elif int(massa) == 0:
        error_msg = "вы ввели вес равный 0"
    elif int(massa) > 10000:
        error_msg = "ведрами есть нельзя)"

    else:
        # Если все проверки пройдены — УСПЕХ
        kkal = round(int(massa) / 100 * l0.get(text, 0), 2)

        temp_list = session.get('user_messages', [])
        temp_list.append({'text': text, 'massa': massa, 'kkal': kkal})
        session['user_messages'] = temp_list

        # Очищаем временный ввод, так как данные успешно добавлены
        session.pop('current_text', None)
        session.pop('current_massa', None)
        session['mes_massa'] = ""
        session.modified = True
        return redirect(url_for('main'))

    # Если дошли сюда — значит есть ошибка
    session['mes_massa'] = error_msg
    session.modified = True
    return redirect(url_for('main'))


@app.route('/login', methods=['POST'])
def login():
    session['username'] = request.form.get('user_input')
    return redirect(url_for('main'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('main'))

@app.route('/del_messages', methods=['GET'])
def del_messages():
    session['user_messages'] = []
    session['mes_massa'] = ""
    return redirect(url_for('main'))


@app.route('/update_last', methods=['PUT'])
def update_last():
    # Получаем JSON данные из запроса (для PUT это стандарт)
    data = request.get_json()
    new_massa = data.get('new_massa', "").strip()


    user_messages = session.get('user_messages', [])

    if not user_messages:
        return jsonify({"error": "Список пуст"}), 400

    # Валидация веса
    if not new_massa.isdigit() or int(new_massa) <= 0:
        return jsonify({"error": "Введите положительное число"}), 400

    # Обновляем данные последнего элемента
    last_item = user_messages[-1]
    product_name = last_item['text']

    # Пересчитываем ккал (l0 — твой исходный словарь из начала кода)
    new_kkal = round(int(new_massa) / 100 * l0.get(product_name, 0), 2)

    last_item['massa'] = new_massa
    last_item['kkal'] = new_kkal

    session['user_messages'] = user_messages
    session.modified = True

    return jsonify({"success": True, "new_kkal": new_kkal}), 200




#Показать накопленный список (API-запрос)
@app.route('/show_messages_req', methods=['GET'])
def show_messages_reg():
    # Достаем список из сессии (если пусто — возвращаем [])
    user_messages = session.get('user_messages', [])

    # Считаем сумму калорий только для этого пользователя
    total_kkal = round(sum(msg['kkal'] for msg in user_messages), 2)

    return {
        'Список выбранных продуктов': user_messages,
        'Сумма калорий в выбранных продуктах(ККал)': str(total_kkal)
    }


# Вывод справочника (не зависит от сессии, отдаем общий словарь)
@app.route('/list', methods=['GET'])
def list_food():
    return {'Справочник калорийности продуктов': l0}


# Поиск по справочнику
# Создаём вспомогательный словарь: все ключи в нижнем регистре
l0_lookup = {k.lower(): v for k, v in l0.items()}

@app.route('/search', methods=['GET'])
def search():
    # Приводим ввод пользователя к нижнему регистру и убираем пробелы
    food_input = request.args.get('food', '').lower().strip()

    # Ищем в подготовленном словаре l0_lookup
    if food_input in l0_lookup:
        # Находим оригинальное название из основного словаря l0 для красоты ответа
        # (ищем ключ, который в нижнем регистре совпадает с вводом)
        original_key = next((k for k in l0.keys() if k.lower() == food_input), food_input)
        return jsonify({original_key: l0_lookup[food_input]}), 200

    return jsonify({"error": "Продукт не найден"}), 404


from flask import jsonify  # Добавь в импорты


@app.route('/delete_last', methods=['DELETE'])
def delete_last():
    user_messages = session.get('user_messages', [])

    if user_messages:
        user_messages.pop()
        session['user_messages'] = user_messages
        session.modified = True
        return jsonify({"status": "success", "remaining": len(user_messages)}), 200

    return jsonify({"status": "error", "message": "List is empty"}), 400


if __name__ == '__main__':
    app.run(debug=True)
