import RPi.GPIO as GPIO
import time

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

#对使能引脚开启pwm控制,并启动pwm
L_Motor = GPIO.PWM(PWMA, 100)
L_Motor.start(0)
R_Motor = GPIO.PWM(PWMB, 100)
R_Motor.start(0)


# 停止
def t_stop(t_time):
    L_Motor.ChangeDutyCycle(0)
    GPIO.output(AIN1, False)
    GPIO.output(AIN2, False)
    R_Motor.ChangeDutyCycle(0)
    GPIO.output(BIN1, False)
    GPIO.output(BIN2, False)
    time.sleep(t_time)


# 后退
def t_down(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN1, True)
    GPIO.output(AIN2, False)
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN1, True)
    GPIO.output(BIN2, False)
    time.sleep(t_time)


# 前进
def t_up(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN1, False)
    GPIO.output(AIN2, True)
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN1, False)
    GPIO.output(BIN2, True)
    time.sleep(t_time)


# 左转
def t_left(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN1, False)
    GPIO.output(AIN2, True)
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN1, True)
    GPIO.output(BIN2, False)
    time.sleep(t_time)


# 右转
def t_right(speed, t_time):
    L_Motor.ChangeDutyCycle(speed)
    GPIO.output(AIN1, True)
    GPIO.output(AIN2, False)
    R_Motor.ChangeDutyCycle(speed)
    GPIO.output(BIN1, False)
    GPIO.output(BIN2, True)
    time.sleep(t_time)


def keysacn():
    while True:
        # 获取用户输入
        key = input(
            "请输入指令 ('w'前进, 's'后退, 'a'左转, 'd'右转, 'q'停止, 'e'退出): ").lower()

        if key == 'w':
            # 前进
            t_up(50, 1)
        elif key == 's':
            # 后退
            t_down(50, 1)
        elif key == 'a':
            # 左转
            t_left(50, 1)
        elif key == 'd':
            # 右转
            t_right(50, 1)
        elif key == 'q':
            # 停止
            t_stop(1)
        elif key == 'e':
            # 退出循环
            t_stop(1)
            print("退出程序。")
            break
        else:
            # 无效输入
            print("无效的指令，请重新输入。")


# 调用函数，运行主程序
try:
    keysacn()
except KeyboardInterrupt:
    t_stop(1)
    GPIO.cleanup()
