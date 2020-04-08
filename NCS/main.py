

import serial
import serial.tools.list_ports
from time import sleep
import tkinter.messagebox
import tkinter

import readConfig

from HslCommunication import SiemensS7Net
from HslCommunication import SiemensPLCS


class Com():
    def __init__(self, port='COM7', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=60):
        self.ser = serial.Serial()
        self.port = port  # 端口
        self.baudrate = baudrate  # 波特率
        self.bytesize = bytesize  # 数据位
        self.parity = parity  # 奇偶校验
        self.stopbits = stopbits  # 停止位
        self.timeout = timeout  # 超时
        self.data = bytes()  # 存放读取的串口数据
        
    def check_com(self):
        port_lists = list(serial.tools.list_ports.comports())
        if len(port_lists) == 0:
            print("无可用串口!")
            return False
        else:
            print('发现串口:')
            for i in range(len(port_lists)):
                print(port_lists[i])
            return True

    # 打开串口
    def open_com(self):        
        self.ser.port = self.port
        self.ser.baudrate = self.baudrate  # 波特率
        self.ser.bytesize = self.bytesize  # 数据位
        self.ser.parity = self.parity  # 奇偶校验
        self.ser.stopbits = self.stopbits  # 停止位
        self.ser.timeout = self.timeout  # 超时
        self.ser.open()
        if self.ser.isOpen():
            print("成功打开串口，当前串口为:%s" % self.ser.name)
            return True
        else:
            return False

    # 发送数据
    def send_data(self, data_to_send):
        self.ser.write(data_to_send)
        self.ser.flush()

    # 读取数据
    def read_data(self):
        count = self.ser.inWaiting()
        self.data = self.ser.read(count)
        # 清空缓存区
        self.ser.flushInput()
        return int(self.data[1:len(self.data)-1].decode())

"""*********************************
   *         全局变量初始化         *
   *********************************"""
# 串口数据
port = readConfig.port
bautrate = readConfig.bautrate
bytesize = readConfig.bytesize
parity = readConfig.parity
stopbits = readConfig.stopbits
timeout = readConfig.timeout
lux = readConfig.lux    
 

# 创建PLC实例
siemens = SiemensS7Net(SiemensPLCS.S200Smart, "192.168.2.1")

# 自定义报错消息框
def error_message_box(message_type, message):
    root = tkinter.Tk()
    root.withdraw()
    tkinter.messagebox.showerror(message_type, message)
    root.destroy()

def main():
    count = 0
    #创建串口实例
    ct = Com(port=port, baudrate=bautrate, bytesize=bytesize, parity=parity, stopbits=stopbits, \
                    timeout=timeout)  # 创建串口类实例
    has_com = ct.check_com()
    data_to_send = b'Get CH00.Lux\r'
    # data_to_send = "47 65 74 20 43 48 30 30 2E 4C 75 78 0D"
    if has_com and ct.open_com(): # 若存在串口 # 若成功打开串口
        if siemens.ConnectServer().IsSuccess:
            print("与PLC成功建立长连接")
            while True:
                if siemens.ReadBool("M2.2").Content:  # 若收到PLC接收数据命令
                    
                    data = 0
                    print("开始检测")
                    print("M2.2置为False")
                    siemens.WriteBool("M2.2", False)  # 信号置为假
                    print("向光度传感器发送信息")
                    try:
                        count += 1
                        ct.send_data(data_to_send)
                            
                    except Exception as e:
                        print("********************")
                        print("**发送数据发生异常**")
                        print("********************")
                        print("异常:%s" % str(e))
                        print("串口已打开? %s" % ct.ser.isOpen())
                        print("停止写")
                        ct.ser.flushOutput()
                        print("停止写结束")
                        print("关闭串口实例")
                        ct.ser.close()
                        print("串口已打开? %s" % ct.ser.isOpen())
                        print("打开串口实例")
                        print("串口已打开? %s" % ct.ser.isOpen())
                        
                    sleep(1)
                    print("接收光强传感器信息")
                    try:
                        data = ct.read_data()
                    except Exception as e:
                        print("********************")
                        print("**接收数据发生异常**")
                        print("********************")
                        print("异常:%s" % str(e))
                        print("串口已打开? %s" % ct.ser.isOpen())
                        print("关闭串口实例")
                            
                        ct.ser.close()
                        print("串口已打开? %s" % ct.ser.isOpen())
                        print("打开串口实例")
                        print("串口已打开? %s" % ct.ser.isOpen())
                    if data>=lux:
                        siemens.WriteBool("M2.0", True)
                        siemens.WriteBool("M2.1", False)
                        print("阈值为%s，实测为%s。 OK 第%s个" % (lux, data, count))
                    else:
                        siemens.WriteBool("M2.0", False)
                        siemens.WriteBool("M2.1", True)
                        print("********************************")
                        print("*        ！！错误！！          *")
                        print("*                              *")
                        print("*      光强度应>%s,实测值%s      *" % (lux, data))
                        print("*                              *")
                        print("*        ！！错误！！          *")
                        print("********************************")
                        print("阈值为3，实测为%s。 NG 第%s个" % (data, count))
                        error_message_box("错误", "光强度不够，检查把手LED灯是否异常")

                else:
                    pass
        else:
            error_message_box("错误", "与PLC连接失败")
    else:
        error_message_box("错误", "打开串口失败")
        input('按任意键退出!')
                
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        
        siemens.ConnectClose()
        print(e)
        error_message_box("错误", e)
        
