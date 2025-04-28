#Libraries
import RPi.GPIO as GPIO
import time
 
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    start_time = time.time()
    stop_time = time.time()
 
    # save start_time
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()
 
    # time difference between start and arrival
    time_elapsed = stop_time - start_time
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (time_elapsed * 34300) / 2
 
    return distance
 

import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_SSD1306

def display_text(text, *args):

    if len(args) < 2:
        FONT_SIZE = 15
    elif len(args) == 2:
        FONT_SIZE = 10
    else:
        FONT_SIZE = 8

    global disp
    disp = Adafruit_SSD1306.SSD1306_128_32(rst = 0)

    disp.begin()
    disp.clear()
    disp.display()

    width = disp.width
    height = disp.height

    # 1 bit pixel
    image = Image.new('1', (width, height))
    # Create a new image (all black) with the binary mode

    draw = ImageDraw.Draw(image)
    # Create an object that can be used to draw in the given image

    font = ImageFont.truetype("./ARIALUNI.TTF", FONT_SIZE)

    try:
        print('Press ^C to terminate')
        while True:

            draw.rectangle((0, 0, width, height), outline = 0, fill = 0)
            
            draw.text((0, 0), text, font = font, fill = 255)

            if len(args) > 0:
                for i, item in enumerate(args):
                    draw.text((0, (i + 1) * FONT_SIZE-1), item, font = font, fill = 255)

            disp.image(image)
            disp.display()
            time.sleep(0.2)

    except KeyboardInterrupt:
        print('terminated')

    finally:
        disp.clear()
        disp.display()



def main():
    # OLED 初始化
    global disp
    disp = Adafruit_SSD1306.SSD1306_128_32(rst=0)
    disp.begin()
    disp.clear()
    disp.display()

    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("./ARIALUNI.TTF", 15)



def wait_until_object_detected():
    try:
        print("開始測距，按 Ctrl+C 停止")
        while True:
            dist = distance()
            text = "Distance = %.1f cm" % dist
            print(text)
            
            if dist < 21:
                print(f"物體接近({dist:.1f} cm)，停止測距")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print("terminated")
        GPIO.cleanup()
        disp.clear()
        disp.display()

        return 0
    
    return 1


    
if __name__ == '__main__':
    main()


