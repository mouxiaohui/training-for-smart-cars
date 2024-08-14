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
# 左右红外传感器
SensorRight = 16
SensorLeft = 12

# 设备初始化，开启引脚并设置模式
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(AIN2, GPIO.OUT)
GPIO.setup(AIN1, GPIO.OUT)
GPIO.setup(PWMA, GPIO.OUT)
GPIO.setup(BIN1, GPIO.OUT)
GPIO.setup(BIN2, GPIO.OUT)
GPIO.setup(PWMB, GPIO.OUT)
GPIO.setup(SensorRight, GPIO.IN)
GPIO.setup(SensorLeft, GPIO.IN)

# 红外避障传感器, 将两个引脚设置为输入模式
SensorRight = 16
SensorLeft = 12
GPIO.setup(SensorRight, GPIO.IN)
GPIO.setup(SensorLeft, GPIO.IN)


# 小车速度
class Speed(Enum):
    SLOW = 35.0
    MEDIUM = 50.0
    HIGH = 70.0


# 小车运动模式
class Model(Enum):
    REAL_TIME_CONTROL = "实时控制"
    FIXED_TRAJECTORY = "固定轨迹"


# 弧线偏移
class Offset:
    value: int
    direction: int  # ('0'没有', '1'向左, '2'向右)

    def __init__(self):
        self.cancel()

    def inc(self):
        self.value += 2

    def add(self, v):
        self.value += v

    def cancel(self):
        self.value = 1
        self.direction = 0

    def left(self):
        if self.direction != 1:
            self.direction = 1

    def right(self):
        if self.direction != 2:
            self.direction = 2


# 小车
class Car:
    l_motor: GPIO.PWM
    r_motor: GPIO.PWM
    speed: Speed
    model: Model
    offset: Offset

    def __init__(self):
        info = """
-------------------------------------------------------------
控制: ('w'前进, 's'后退, 'a'左转, 'd'右转, 'q'停止, 'esc'退出)
速度: ('1'低速, '2'中速, '3'高速)
模式: ('8'实时控制, '9'固定轨迹)               
偏移: (','向左, '.'向右, '/'取消)
避障前进: ('i'开启)
-------------------------------------------------------------
"""
        print(info)

        # 对使能引脚开启pwm控制,并启动pwm
        self.l_motor = GPIO.PWM(PWMA, 100)
        self.l_motor.start(0)
        self.r_motor = GPIO.PWM(PWMB, 100)
        self.r_motor.start(0)

        self.model = Model.REAL_TIME_CONTROL
        self.speed = Speed.MEDIUM
        self.offset = Offset()
        self.__set_duty_cycle()

    # 更新左右轮转动速度
    def __set_duty_cycle(self):
        l = self.speed.value
        r = self.speed.value
        if self.offset.direction == 1:
            r /= self.offset.value
        elif self.offset.direction == 2:
            l /= self.offset.value

        self.l_motor.ChangeDutyCycle(l)
        self.r_motor.ChangeDutyCycle(r)

    def __set_output(self, ain1, ain2, bin1, bin2):
        GPIO.output(AIN1, ain1)
        GPIO.output(AIN2, ain2)
        GPIO.output(BIN1, bin1)
        GPIO.output(BIN2, bin2)

    # 改变速度
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
        self.__set_duty_cycle()
        print(f"速度=>{speed_str}")

    # 改变运动模式
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

    # 避障前进
    def avoid_obstacles_up(self):
        listener = keyboard.Listener(
            on_release=self.command_handler_for_release)  # type: ignore
        listener.start()
        self.up()
        while listener.running == True:
            SR_2 = GPIO.input(SensorRight)
            SL_2 = GPIO.input(SensorLeft)
            if SR_2 == 1 and SL_2 == 1:  # 传感器检测到障碍物时返回0，没有障碍时返回1
                self.offset.cancel()
            elif SL_2 == 1:  # 左边没有障碍
                self.offset.left()
                self.offset.inc()
            elif SR_2 == 1:  # 右边没有障碍
                self.offset.right()
                self.offset.inc()
            else:
                self.stop()
                break
            self.__set_duty_cycle()

    # 按下指令处理
    def command_handler_for_press(self, key):
        try:
            c: str = key.char
            if c == 'w':
                self.up()  # 向前
            elif c == 's':
                self.down()  # 向后
            elif c == 'a':
                self.left()  # 向左
            elif c == 'd':
                self.right()  # 向右
            elif c == ',':
                self.offset.left()
                self.offset.inc()
                self.__set_duty_cycle()
                print(f"偏移=>向左{self.offset.value}")
            elif c == '.':
                self.offset.right()
                self.offset.inc()
                self.__set_duty_cycle()
                print(f"偏移=>向右{self.offset.value}")
            elif c == '/':
                self.offset.cancel()
                self.__set_duty_cycle()
                print("偏移=>取消")
            elif c == 'i':
                self.avoid_obstacles_up()
            elif c.isdigit():  # 速度与模式切换
                num = int(c)
                if num <= 3:
                    self.change_speed(num)
                else:
                    self.change_model(num)
        except AttributeError:
            pass

    # 松开指令处理
    def command_handler_for_release(self, key):
        if car.model == Model.REAL_TIME_CONTROL:
            car.stop()
        try:
            c: str = key.char
            if c == 'q':
                self.stop()
        except AttributeError:
            if key == keyboard.Key.esc:
                print("退出程序!")
                car.stop()
                return False


if __name__ == '__main__':
    car = Car()

    with keyboard.Listener(
            on_press=car.command_handler_for_press,
            on_release=car.command_handler_for_release  # type: ignore
    ) as listener:
        listener.join()
