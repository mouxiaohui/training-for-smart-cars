from enum import Enum
from time import sleep
from typing import Sequence
from pynput import keyboard
import RPi.GPIO as GPIO
import cv2
import Adafruit_PCA9685

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
channelA = 5  # 底座舵机通道
channelB = 4  #顶部舵机通道

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


# 图像二值化
def image2binary(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    mask = cv2.erode(thresh, None, iterations=2)  # type: ignore
    return cv2.dilate(mask, None, iterations=2)  # type: ignore


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
    speed: Speed  # 运动速度
    model: Model  # 运动模式
    offset: Offset  # 控制转弯角度
    cap: cv2.VideoCapture
    cap_pwm: Adafruit_PCA9685.PCA9685  # 摄像头舵机

    def __init__(self):
        info = """
-------------------------------------------------------------
控制: ('w'前进, 's'后退, 'a'左转, 'd'右转, 'q'停止, 'esc'退出)
速度: ('1'低速, '2'中速, '3'高速)
模式: ('8'实时控制, '9'固定轨迹)               
偏移: (','向左, '.'向右, '/'取消)
避障前进: ('i'开启, 'q'退出)
循迹: ('o'单线循迹, 'p'双开启线循迹, 'q'退出)
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

        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)  #视频流宽度
        self.cap.set(4, 480)  #视频流高度
        self.cap.set(10, 100)  #视频流亮度

        self.cap_pwm = Adafruit_PCA9685.PCA9685()
        # 频率设置为50hz，适用于舵机系统。
        self.cap_pwm.set_pwm_freq(50)

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

    # def __init_cap_steering_engine():

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
    # TODO (未测试，左红外传感器损坏)
    def avoid_obstacles_up(self):
        print("=== 避障前进 启动 ===")
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

    # 辅助功能，使设置舵机角度更简单
    def __set_servo_angle(self, channel, angle):
        angle = 4096 * ((angle * 11) + 500) / 20000 + 0.5
        self.cap_pwm.set_pwm(channel, 0, int(angle))

    # 单线循迹
    def single_line_tracking(self):
        print("=== 单线循迹 启动 ===")
        self.change_speed(1)
        self.__set_servo_angle(channelA, 90)  # 底座舵机 90
        self.__set_servo_angle(channelB, 90)  # 顶部舵机 90
        #等待舵机完成运动
        sleep(0.5)
        self.cap_pwm.set_all_pwm(0, 0)  # 停止所有PWM信号

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            crop_img = frame[60:120, 0:170]
            # 图像二值化
            img = image2binary(crop_img)

            contours = cv2.findContours(
                img, 1,
                cv2.CHAIN_APPROX_NONE)[1]  # 小车上opencv版本与本机不一致，代码根据小车上3.4版本编写
            if len(contours) > 0 and len(contours[0]) > 0:
                c = max(contours, key=lambda x: cv2.contourArea(x))
                M = cv2.moments(c)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                cv2.line(crop_img, (cx, 0), (cx, 720), (255, 0, 0), 1)
                cv2.line(crop_img, (0, cy), (1280, cy), (255, 0, 0), 1)
                cv2.drawContours(crop_img, contours, -1, (0, 255, 0), 1)
                if cx >= 120:
                    self.right()
                if cx < 120 and cx > 50:
                    self.up()
                if cx <= 50:
                    self.left()

            cv2.namedWindow("result", 0)
            cv2.resizeWindow("result", 400, 300)
            cv2.imshow("result", crop_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):  #按q键退出
                self.stop()
                break

        cv2.destroyAllWindows()

    # 双线循迹
    def dual_line_tracking(self):
        print("=== 双线循迹 启动 ===")
        self.change_speed(1)
        self.__set_servo_angle(channelA, 78)  # 底座舵机
        self.__set_servo_angle(channelB, 35)  # 顶部舵机
        #等待舵机完成运动
        sleep(0.5)
        self.cap_pwm.set_all_pwm(0, 0)  # 停止所有PWM信号

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # 图像二值化
            b_img = image2binary(frame)

            # 定义提取车道线内侧点的函数
            def extract_lane_points(binary_image, rows):
                left_points = []
                right_points = []
                mid = binary_image.shape[1] // 2
                width = binary_image.shape[1]
                for row in rows:
                    for col in range(width):  # 遍历每一列
                        if binary_image[row, col] == 0:  # 检测到黑色像素点
                            if col < mid:  # 左侧车道线
                                left_points.append((col, row))
                            else:  # 右侧车道线
                                right_points.append((col, row))
                return left_points, right_points

            # 运动决策
            def make_decision(left_lane_points, right_lane_points):
                # 设置容错范围
                tolerance = 20  # 根据实际情况调整

                # 定义一个函数来安全地计算中心点
                def safe_center(points):
                    if points:
                        return sum(point[0] for point in points) // len(points)
                    else:
                        return None

                # 安全地计算左右车道线的中心点
                left_center = safe_center(left_lane_points)
                right_center = safe_center(right_lane_points)

                # 检查车道线中心点是否存在
                if left_center is not None and right_center is not None:
                    # 如果两条车道线都检测到，计算中点
                    mid_line = (left_center + right_center) // 2
                elif left_center is not None:
                    # 如果只检测到左侧车道线，使用左侧车道线的中心点作为中点
                    mid_line = left_center
                elif right_center is not None:
                    # 如果只检测到右侧车道线，使用右侧车道线的中心点作为中点
                    mid_line = right_center
                else:
                    # 如果没有检测到任何车道线，设置 mid_line 为 None
                    mid_line = None

                # 获取图像宽度
                width = frame.shape[1]

                # 根据 mid_line 的值来做出决策
                if mid_line is not None:
                    error = width // 2 - mid_line

                    # 根据误差和容错范围做出决策
                    if abs(error) <= tolerance:
                        self.up()  # 小车在容错范围内，保持直线行驶
                    elif error > tolerance:
                        self.right()  # 小车偏左超出容错范围，向右转
                    elif error < -tolerance:
                        self.left()  # 小车偏右超出容错范围，向左转
                else:
                    # 如果没有检测到车道线，采取保守策略，例如减速或停止
                    self.stop()  # 确保 stop 函数能够安全地停止小车
                    print("未检测到车道线，小车已停止。")

            # 定义提取行
            rows = [
                b_img.shape[0] // 4, b_img.shape[0] // 2,
                (3 * b_img.shape[0]) // 4
            ]

            # 提取车道线内侧点
            left_lane_points, right_lane_points = extract_lane_points(
                b_img, rows)
            make_decision(left_lane_points, right_lane_points)

            # 绘制车道线点
            for point in left_lane_points:
                cv2.circle(frame, point, 5, (0, 255, 0), -1)  # 绿色点表示左侧车道线
            for point in right_lane_points:
                cv2.circle(frame, point, 5, (0, 0, 255), -1)  # 红色点表示右侧车道线

            cv2.namedWindow("result", 0)
            cv2.resizeWindow("result", 600, 400)
            cv2.imshow("result", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  #按q键退出
                self.stop()
                break

        cv2.destroyAllWindows()

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
            elif c == 'o':
                self.single_line_tracking()
            elif c == 'p':
                self.dual_line_tracking()
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
                # 资源释放
                GPIO.cleanup()
                self.cap.release()  #释放摄像头设备资源

                return False


if __name__ == '__main__':
    car = Car()

    with keyboard.Listener(
            on_press=car.command_handler_for_press,
            on_release=car.command_handler_for_release  # type: ignore
    ) as listener:
        listener.join()
