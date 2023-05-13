import os
import psycopg2, re, csv, ast, io
import shlex
#from dotenv import load_dotenv

#ВЫБЕРИ БОТА ДЛЯ ЗАПУСКА
CONFIG_BOT = 'MASTER'

#Определяем статические переменные
ID_CONCEPTION = 123
ID_OBJECT = 1
ID_CLASS_PROP = 0
VAL_TEXT = 10

# Получаем значение пароля из переменной окружения
host = os.getenv('HOST_GPT')
database = os.getenv('DATABASE_GPT')
port = os.getenv('PORT_GPT')
user = os.getenv('USER_GPT')
password = os.getenv('PASSWORD_GPT') 

# Подключение к БД с использованием пароля из системной переменной окружения
conn = psycopg2.connect(host=host, port=port, dbname=database, user=user, password=password, )

# Создание объекта-курсора
cur = conn.cursor()
#84217
OPENAI_API_KEY_BOT = None
TELEGRAM_BOT_TOKEN_BOT = None
ASSISTANT_PROMPT = None
NAME_BOT = None

def convert_property(data: str) -> []:
    """
    Преобразование данных в список кортежей
    """
    if not isinstance(data, str) or not data:
        return []
    #regex = r'\((' + r'(?:[^,(]|\([^()]*\))+?' + r')\)'
    regex = r'\(([^()]*)\)'
    #regex = r"\(([^()]|(\(([^()]+)\))*)\)"
    response_data = re.findall(regex, data)
    result = []
    for match in response_data:
        new_match = match.replace('\\', '')
        # Разбиваем строку на поля, используя csv.reader для обработки текстовых полей
        # и удаляем кавычки внутри полей
        tuple_elements = [i.strip('"') for i in csv.reader([new_match], delimiter=',', quotechar='"', doublequote=True).__next__()]
        # Преобразуем список элементов в кортеж и добавляем его в результат
        # Проверяем, что список элементов не пустой
        if all(tuple_elements):
            result.append(tuple(tuple_elements))
    return result

def convert_property2(data: str) -> []:
    """
    Преобразование данных в список кортежей.
    Игнорирует символы в кавычках при составлении кортежей.
    """
    if not isinstance(data, str) or not data:
        return []

    data = data.replace('{', '[').replace('}', ']')
    #regex = r'(?:[^(),"]+|"[^"]*")+' # регулярное выражение для поиска элементов в строке, игнорируя символы в кавычках
    regex = r'\(([^()]*)\)'
    response_data = re.findall(regex, data)
    
    result = []
    for match in response_data:
        tuple_elements = [i.strip('"') for i in match.split(',')] # разделение `match` на элементы кортежа
        result.append(tuple(tuple_elements))
        
    return result

def convert_property3(data: str) -> []:
    # обработка экранирования символов в строках с кавычками
    data = re.sub(r"\\(.)", lambda x: x.group(1) + '\u0000', data)
    
    # конвертация данных в кортежи
    split_tuple = re.compile(r'\((?:\\.|[^\\()]*)*\)')
    tuples = [split_tuple.findall(d) for d in data.split(",")]
    
    # обработка экранированных символов в кортежах
    result = []
    for t in tuples:
        r = []
        for i in t:
            r.append(i.replace('\u0000', '\\'))
        result.append(tuple(x.strip() for x in r))
    return result

def convert_property4(data: str) -> []:
    if not isinstance(data, str) or not data:
        return []
    result = []
    data = data.replace('{', '[').replace('}', ']')
    # разбиваем данные на строки по символу ";"
    for line in data.split(';'):
        # парсим строку на отдельные аргументы с учетом кавычек
        args = shlex.split(line.strip())
        # конвертируем аргументы в кортеж и добавляем его в результат
        result.append(tuple(args))
    return result

def convert_property5(data: str) -> []:
    
    if not isinstance(data, str) or not data:
        return []

    regex = r'\(([^,()]|(?R))*\)'
    response_data = re.findall(regex, data)
    result = []
    for match in response_data:
        match = match.strip()
        if match:
            tuple_elements = []
            # Loop through each character in the match string
            i = 0
            n = len(match)
            while i < n:
                # If the current character is a double-quote, find the next one and append everything in between
                # If no second double-quote is found, just append the remainder of the string
                if match[i] == '"':
                    j = i + 1
                    while j < n and match[j] != '"':
                        if match[j] == '\\' and j + 1 < n and match[j+1] == '"':
                            j += 1
                        j += 1
                    tuple_elements.append(match[i+1:j].replace('\\"', '"'))
                    i = j + 1
                # If the current character is not a comma or parenthesis, find the next one and append everything in between
                else:
                    j = i
                    while j < n and match[j] not in (',', '(' , ')'):
                        j += 1
                    tuple_elements.append(match[i:j])
                    i = j
            # Преобразуем список элементов в кортеж и добавляем его в результат
            # Проверяем, что список элементов не пустой
            if all(tuple_elements):
                result.append(tuple(tuple_elements))
    return result

def convert_property6(data: str) -> []:
    """
    Преобразование данных в список кортежей
    """
    if not isinstance(data, str) or not data:
        return []
    # заменяем символы фигурных скобок на квадратные скобки
    data = data.replace('{', '[').replace('}', ']')
    # Убираем '\' перед экранированными символами
    data = data.replace(r'\"', '"').replace(r"\'", "'").replace(r"\(", "(").replace(r"\)", ")")
    # используем csv.reader для обработки экранированных значений
    result = []
    for row in csv.reader(io.StringIO(data)):
        row = [str(ast.literal_eval(cell)) if cell else '' for cell in row]
        result.append(tuple(row))
    return result

def convert_property7(data: str) -> []:
    """
    Преобразование данных в список кортежей
    """
    if not isinstance(data, str) or not data:
        return []
    data = data.replace('{', '[').replace('}', ']')
    #data = data.replace('{"','[').replace('"}',']').repleace(')","(','),(')
    regex = r'\(([^()]*)\)'
    response_data = re.findall(regex, data)
    result = []
    for match in response_data:
        # Преобразуем строку-кортеж в список, используя csv.reader
        # и убираем лишние пробелы у значений
        tuple_elements = [i.strip() for i in csv.reader([match], delimiter=',', quotechar='"', doublequote=True).__next__()]
        # Преобразуем список элементов в кортеж и добавляем его в результат
        if len(tuple_elements) > 24 :
            result.append(tuple(tuple_elements))
    return result

#Получение данных бота
cur.callproc('bpd.object_ext_by_name', [CONFIG_BOT, ID_CONCEPTION, False])
data = cur.fetchone()

print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
print(data[35])
print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

bot_propertys = convert_property7(data[35])

print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
print(bot_propertys)
print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

for bot_property in bot_propertys:
    
    #Запрашиваем данные значения свойства

    #if len(bot_propertys)>11:
    cur.callproc('bpd.object_prop_user_big_val_by_id_prop', [bot_property[ID_OBJECT], bot_property[ID_CLASS_PROP]])
    prop_val = cur.fetchone()
    
    #Получаем значение переменных бота
    if bot_property[11] == 'OPENAI_API_KEY_BOT':
        OPENAI_API_KEY_BOT = prop_val[VAL_TEXT]
    elif bot_property[11] == 'TELEGRAM_BOT_TOKEN_BOT':        
        TELEGRAM_BOT_TOKEN_BOT =  prop_val[VAL_TEXT]
    elif bot_property[11] == 'ASSISTANT_PROMPT':        
        ASSISTANT_PROMPT =  prop_val[VAL_TEXT]    
    elif bot_property[11] == 'NAME_BOT':        
        NAME_BOT =  prop_val[VAL_TEXT]
     
    print('Result:',  bot_property[11], prop_val[VAL_TEXT])

print(OPENAI_API_KEY_BOT)
print(TELEGRAM_BOT_TOKEN_BOT)
print(ASSISTANT_PROMPT)
print(NAME_BOT)

# Закрытие курсора и соединения с БД
cur.close()
conn.close()
