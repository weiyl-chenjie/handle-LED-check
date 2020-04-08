import configparser
import os

# curpath = os.path.dirname(os.path.abspath(__file__))  # 本文件所在的目录
# cfgpath = os.path.join(curpath, "Config.ini")  # 配置文件路径
curpath = os.getcwd()  # 本文件所在的目录
cfgpath = os.path.join(curpath, "Config.ini")  # 配置文件路径
print("配置文件路径:"+cfgpath)

# 创建管理对象
conf = configparser.ConfigParser()

# 读取ini文件
conf.read(cfgpath, encoding="utf-8")

# 获取SATO_COM配置
port = conf.get('COM', 'port')
bautrate = int(conf.get('COM', 'bautrate'))
bytesize = int(conf.get('COM', 'bytesize'))
parity = conf.get('COM', 'parity')
stopbits = int(conf.get('COM', 'stopbits'))
timeout = int(conf.get('COM', 'timeout'))
lux = int(conf.get('LUX', 'lux'))
