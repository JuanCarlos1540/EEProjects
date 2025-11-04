import RPi.GPIO as GPIO
import socket
import time
import uuid

# LCD pin config
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18

# Button pin (updated from GPIO 17 to GPIO 16)
BUTTON_PIN = 16

# LCD constants
LCD_WIDTH = 16
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup([LCD_E, LCD_RS, LCD_D4, LCD_D5, LCD_D6, LCD_D7], GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# LCD functions
def lcd_toggle_enable():
    time.sleep(0.0005)
    GPIO.output(LCD_E, True)
    time.sleep(0.0005)
    GPIO.output(LCD_E, False)
    time.sleep(0.0005)

def lcd_send_byte(bits, mode):
    GPIO.output(LCD_RS, mode)
    GPIO.output(LCD_D4, bool(bits & 0x10))
    GPIO.output(LCD_D5, bool(bits & 0x20))
    GPIO.output(LCD_D6, bool(bits & 0x40))
    GPIO.output(LCD_D7, bool(bits & 0x80))
    lcd_toggle_enable()
    GPIO.output(LCD_D4, bool(bits & 0x01))
    GPIO.output(LCD_D5, bool(bits & 0x02))
    GPIO.output(LCD_D6, bool(bits & 0x04))
    GPIO.output(LCD_D7, bool(bits & 0x08))
    lcd_toggle_enable()

def lcd_init():
    lcd_send_byte(0x33, False)
    lcd_send_byte(0x32, False)
    lcd_send_byte(0x28, False)
    lcd_send_byte(0x0C, False)
    lcd_send_byte(0x06, False)
    lcd_send_byte(0x01, False)

def lcd_message(message):
    message = message.ljust(LCD_WIDTH, " ")
    for char in message:
        lcd_send_byte(ord(char), True)

def lcd_display(line1, line2):
    lcd_send_byte(LCD_LINE_1, False)
    lcd_message(line1)
    lcd_send_byte(LCD_LINE_2, False)
    lcd_message(line2)

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No IP"

def get_mac():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(40, -1, -8)])
    return mac

def format_mac_for_lcd(mac):
    parts = mac.split(":")
    line1 = ":".join(parts[:2])           # First two pairs
    line2 = ":".join(parts[2:])           # Remaining four
    return line1.ljust(16), line2.ljust(16)

# Main loop
time.sleep(5)  # Delay after boot
lcd_init()

last_display = ""
while True:
    if GPIO.input(BUTTON_PIN) == GPIO.HIGH:
        mac = get_mac()
        line1, line2 = format_mac_for_lcd(mac)
        if last_display != mac:
            lcd_display(line1, line2)
            last_display = mac
    else:
        ip = get_ip()
        if last_display != ip:
            lcd_display("IP Address:", ip)
            last_display = ip
    time.sleep(1)
