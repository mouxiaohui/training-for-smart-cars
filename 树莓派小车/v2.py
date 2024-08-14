from pynput import keyboard
import RPi.GPIO as GPIO
from enum import Enum

#定义引脚
PWMA = 18
AIN1 = 22
AIN2 = 27
PWMB = 23
BIN1 = 25
BIN2 = 24

# 设备初始化，开启引脚并设置模式
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(PWMA, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)
GPIO.setup(PWMB, GPIO.OUT)


# 小车速度
class Speed(Enum):
    SLOW = 35.0
    MEDIUM = 50.0
    HIGH = 70.0


# 小车运动模式
class Model(Enum):
    REAL_TIME_CONTROL = "实时控制"
    FIXED_TRAJECTORY = "固定轨迹"


# 小车
class Car:
    l_motor: GPIO.PWM
    r_motor: GPIO.PWM
    speed: Speed
    model: Model

    def __init__(self):
        info = """
-----------------------------------------------------
控制: ('w'前进, 's'后退, 'a'左转, 'd'右转, 'esc'退出)
速度: ('1'低速, '2'中速, '3'高速)
模式: ('8'实时控制, '9'固定轨迹)                     
-----------------------------------------------------
"""
        print(info)

        # 对使能引脚开启pwm控制,并启动pwm
        self.l_motor = GPIO.PWM(PWMA, 100)
        self.l_motor.start(0)
        self.r_motor = GPIO.PWM(PWMB, 100)
        self.r_motor.start(0)

        self.model = Model.REAL_TIME_CONTROL
        self.speed = Speed.MEDIUM
        self.__update_duty_cycle()

    # 更新小车速度
    def __update_duty_cycle(self):
        self.l_motor.ChangeDutyCycle(self.speed.value)
        self.r_motor.ChangeDutyCycle(self.speed.value)

    def __set_output(self, ain1, ain2, bin1, bin2):
        GPIO.output(AIN1, ain1)
        GPIO.output(AIN2, ain2)
        GPIO.output(BIN1, bin1)
        GPIO.output(BIN2, bin2)

    def change_speed(self, num: int):
        speed_str: str
        if num == 1:
            self.speed = Speed.SLOW
            speed_str = "低速"
        elif num == 2:
            self.speed = Speed.MEDIUM
            speed_str = "中速"
        elif num == 3:
            self.speed = Speed.HIGH
            speed_str = "高速"
        else:
            print("错误参数!")
            return
        self.__update_duty_cycle()
        print(f"速度=>{speed_str}")

    def change_model(self, num: int):
        if num == 8:
            self.model = Model.REAL_TIME_CONTROL
        elif num == 9:
            self.model = Model.FIXED_TRAJECTORY
        else:
            print("错误参数!")
            return
        print(f"模式=>{self.model.value}")

    # 停止
    def stop(self):
        self.__set_output(False, False, False, False)

    # 前进
    def up(self):
        self.__set_output(False, True, False, True)

    # 后退
    def down(self):
        self.__set_output(True, False, True, False)

    # 左转
    def left(self):
        self.__set_output(False, True, True, False)

    # 右转
    def right(self):
        self.__set_output(True, False, False, True)


if __name__ == '__main__':
    car = Car()

    def on_press(key):
        try:
            c: str = key.char
            if c == 'w':
                car.up()
            elif c == 's':
                car.down()
            elif c == 'a':
                car.left()
            elif c == 'd':
                car.right()
            elif c == 'r':
                car.right()
            elif c.isdigit():
                num = int(c)
                if num <= 3:
                    car.change_speed(num)
                else:
                    car.change_model(num)
        except AttributeError:
            pass

    def on_release(key):
        if key == keyboard.Key.esc:
            print("退出程序!")
            car.stop()
            return False
        else:
            if car.model == Model.REAL_TIME_CONTROL:
                car.stop()

    with keyboard.Listener(on_press=on_press,
                           on_release=on_release) as listener:  # type: ignore
        listener.join()
