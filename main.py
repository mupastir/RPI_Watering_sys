import RPi.GPIO as GPIO
import datetime
import time
import telebot
import config

init = False

GPIO.setmode(GPIO.BOARD) # Broadcom pin-numbering scheme

token = 'your_token'
bot = telebot.TeleBot(token)
authorized_users = [207216763, 579192114]   # id of my users


def get_status(pin=8):
    GPIO.setup(pin, GPIO.IN)
    return GPIO.input(pin)


def init_output(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HUGH)
    GPIO.output(pin, GPIO.LOW)


def auto_water(delay=5, pump_pin=7, water_sensor_pin=8):
    consecutive_water_count = 0
    init_output(pump_pin)
    print("Here we go! Press CTRL+C to exit")
    try:
        while 1 and consecutive_water_count < 10:
            time.sleep(delay)
            wet = get_status(pin=water_sensor_pin) == 0
            if not wet:
                if consecutive_water_count < 5:
                    pump_on(pump_pin, 1)
                consecutive_water_count += 1
            else:
                consecutive_water_count = 0
    except KeyboardInterrupt:  # If CTRL+C is pressed, exit cleanly:
        GPIO.cleanup()  # cleanup all GPI


def pump_on(pump_pin=7, delay=1):
    init_output(pump_pin)
    f = open("last_watered.txt", "w")
    f.write("Last watered {}".format(datetime.datetime.now()))
    f.close()
    GPIO.output(pump_pin, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(pump_pin, GPIO.LOW)


@bot.message_handler(commands=['info'])
def get_last_watered(message):
    bot.send_message(message.chat.id, message.from_user.id)
    try:
        f = open("last_watered.txt", "r")
        return bot.send_message(message.chat.id, f.readline())
    except:
        return bot.send_message(message.chat.id, 'It was NEVER water!')


@bot.message_handler(commands=['start', 'help'])
def get_last_watered(message):
    bot.send_message(message.chat.id, 'This is bot, which controls of watering your plant at home. '
                     'Enter /info to get information about last watering or /water if you think that it has not'
                     ' enough water in the soil.')


@bot.message_handler(commands=['water'])
def once_water(message):
    if message.from_user.id in authorized_users:  # if the id exists in our database
        pump_on(pump_pin, 1)
        bot.send_message(message.chat.id, 'It has watered once just a moment.')
    else:
        bot.send_message(message.chat.id, 'I have no clue who you are...')


if __name__ == '__main__':
    bot.polling(none_stop=True)
