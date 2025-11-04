
import RPi.GPIO as GPIO
import socket
import time
import os

# LCD pin configuration (BCM numbering)
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18

LCD_WIDTH = 16
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LCD_E, GPIO.OUT)
GPIO.setup(LCD_RS, GPIO.OUT)
GPIO.setup(LCD_D4, GPIO.OUT)
GPIO.setup(LCD_D5, GPIO.OUT)
GPIO.setup(LCD_D6, GPIO.OUT)
GPIO.setup(LCD_D7, GPIO.OUT)

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
    for i in range(LCD_WIDTH):
        lcd_send_byte(ord(message[i]), True)

def lcd_display(ip):
    lcd_send_byte(LCD_LINE_1, False)
    lcd_message("IP Address:")
    lcd_send_byte(LCD_LINE_2, False)
    lcd_message(ip)

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No IP"

# Main loop
time.sleep(5)  # Delay after boot
lcd_init()

last_ip = ""
while True:
    current_ip = get_ip()
    if current_ip != last_ip:
        lcd_display(current_ip)
        last_ip = current_ip
    time.sleep(10)

