import logging
import os
import psycopg2, re, csv

from dotenv import load_dotenv
from openai_helper import OpenAIHelper, default_max_tokens
from telegram_bot import ChatGPTTelegramBot

#ВЫБЕРИ БОТА ДЛЯ ЗАПУСКА
CONFIG_BOT = 'MASTER'

def convert_property(data: str) -> []:
    """
    Преобразование данных в список кортежей
    """
    if not isinstance(data, str) or not data:
        return []
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

def main():
    #Получение настроек из базы данных
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
    conn = psycopg2.connect(host=host, port=port, dbname=database, user=user, password=password)

    # Создание объекта-курсора
    cur = conn.cursor()
    
    OPENAI_API_KEY_BOT = None
    TELEGRAM_BOT_TOKEN_BOT = None
    ASSISTANT_PROMPT = None
    ADMIN_USER_IDS = None
    ALLOWED_TELEGRAM_USER_IDS = None
    NAME_BOT = None
    
    #Получение данных бота
    cur.callproc('bpd.object_ext_by_name', [CONFIG_BOT, ID_CONCEPTION, False])
    data = cur.fetchone()

    bot_propertys = convert_property(data[35])
    for bot_property in bot_propertys:
        #Запрашиваем данные значения свойства
        if len(bot_property)>11:
            cur.callproc('bpd.object_prop_user_big_val_by_id_prop', [bot_property[ID_OBJECT], bot_property[ID_CLASS_PROP]])
            prop_val = cur.fetchone()
    
            #Получаем значение переменных бота
            if bot_property[11] == 'OPENAI_API_KEY_BOT':
                OPENAI_API_KEY_BOT = prop_val[VAL_TEXT]
            elif bot_property[11] == 'TELEGRAM_BOT_TOKEN_BOT':        
                TELEGRAM_BOT_TOKEN_BOT =  prop_val[VAL_TEXT]
            elif bot_property[11] == 'ASSISTANT_PROMPT':        
                ASSISTANT_PROMPT =  prop_val[VAL_TEXT]    
            elif bot_property[11] == 'ADMIN_USER_IDS':        
                ADMIN_USER_IDS =  prop_val[VAL_TEXT]
            elif bot_property[11] == 'ALLOWED_TELEGRAM_USER_IDS':        
                ALLOWED_TELEGRAM_USER_IDS =  prop_val[VAL_TEXT]        
            elif bot_property[11] == 'NAME_BOT':        
                NAME_BOT =  prop_val[VAL_TEXT]

        # Read .env file
        load_dotenv()

    # Закрытие курсора и соединения с БД
    cur.close()
    conn.close()

    # Setup logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Check if the required environment variables are set
    required_values = [TELEGRAM_BOT_TOKEN_BOT, OPENAI_API_KEY_BOT]
    missing_values = [value for value in required_values if required_values is None]
    if len(missing_values) > 0:
        logging.error(f'The following environment values are missing in your .env: {", ".join(missing_values)}')
        exit(1)

    # Setup configurations
    model = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    max_tokens_default = default_max_tokens(model=model)
    openai_config = {
        'api_key': OPENAI_API_KEY_BOT,
        'show_usage': os.environ.get('SHOW_USAGE', 'false').lower() == 'true',
        'stream': os.environ.get('STREAM', 'true').lower() == 'true',
        'proxy': os.environ.get('PROXY', None),
        'max_history_size': int(os.environ.get('MAX_HISTORY_SIZE', 15)),
        'max_conversation_age_minutes': int(os.environ.get('MAX_CONVERSATION_AGE_MINUTES', 180)),
        'assistant_prompt': ASSISTANT_PROMPT if ASSISTANT_PROMPT is not None else 'You are a helpful assistant.',
        'max_tokens': int(os.environ.get('MAX_TOKENS', max_tokens_default)),
        'n_choices': int(os.environ.get('N_CHOICES', 1)),
        'temperature': float(os.environ.get('TEMPERATURE', 1.0)),
        'image_size': os.environ.get('IMAGE_SIZE', '512x512'),
        'model': model,
        'presence_penalty': float(os.environ.get('PRESENCE_PENALTY', 0.0)),
        'frequency_penalty': float(os.environ.get('FREQUENCY_PENALTY', 0.0)),
        'bot_language': os.environ.get('BOT_LANGUAGE', 'ru'),
    }

    # log deprecation warning for old budget variable names
    # old variables are caught in the telegram_config definition for now
    # remove support for old budget names at some point in the future
    if os.environ.get('MONTHLY_USER_BUDGETS') is not None:
        logging.warning('The environment variable MONTHLY_USER_BUDGETS is deprecated. '
                        'Please use USER_BUDGETS with BUDGET_PERIOD instead.')
    if os.environ.get('MONTHLY_GUEST_BUDGET') is not None:
        logging.warning('The environment variable MONTHLY_GUEST_BUDGET is deprecated. '
                        'Please use GUEST_BUDGET with BUDGET_PERIOD instead.')

    telegram_config = {
        'token': TELEGRAM_BOT_TOKEN_BOT,
        'admin_user_ids': ADMIN_USER_IDS if ADMIN_USER_IDS is not None else '-',
        'allowed_user_ids': ALLOWED_TELEGRAM_USER_IDS if ALLOWED_TELEGRAM_USER_IDS is not None else '*',
        'enable_quoting': os.environ.get('ENABLE_QUOTING', 'true').lower() == 'true',
        'enable_image_generation': os.environ.get('ENABLE_IMAGE_GENERATION', 'true').lower() == 'true',
        'enable_transcription': os.environ.get('ENABLE_TRANSCRIPTION', 'true').lower() == 'true',
        'budget_period': os.environ.get('BUDGET_PERIOD', 'monthly').lower(),
        'user_budgets': os.environ.get('USER_BUDGETS', os.environ.get('MONTHLY_USER_BUDGETS', '*')),
        'guest_budget': float(os.environ.get('GUEST_BUDGET', os.environ.get('MONTHLY_GUEST_BUDGET', '100.0'))),
        'stream': os.environ.get('STREAM', 'true').lower() == 'true',
        'proxy': os.environ.get('PROXY', None),
        'voice_reply_transcript': os.environ.get('VOICE_REPLY_WITH_TRANSCRIPT_ONLY', 'false').lower() == 'true',
        'voice_reply_prompts': os.environ.get('VOICE_REPLY_PROMPTS', '').split(';'),
        'ignore_group_transcriptions': os.environ.get('IGNORE_GROUP_TRANSCRIPTIONS', 'true').lower() == 'true',
        'group_trigger_keyword': os.environ.get('GROUP_TRIGGER_KEYWORD', ''),
        'token_price': float(os.environ.get('TOKEN_PRICE', 0.002)),
        'image_prices': [float(i) for i in os.environ.get('IMAGE_PRICES', "0.016,0.018,0.02").split(",")],
        'transcription_price': float(os.environ.get('TOKEN_PRICE', 0.006)),
        'bot_language': os.environ.get('BOT_LANGUAGE', 'ru'),
    }

    # Setup and run ChatGPT and Telegram bot
    openai_helper = OpenAIHelper(config=openai_config)
    telegram_bot = ChatGPTTelegramBot(config=telegram_config, openai=openai_helper)
    telegram_bot.run()


if __name__ == '__main__':
    main()
