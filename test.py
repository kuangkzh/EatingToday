#时间戳转换
import time
t = time.time()
print(t)
timeArray = time.localtime(t)
print(timeArray)
TimeFormat = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
print(TimeFormat)

#session操作
'''
1、设置session值
　　　　request.session["session_name"]="admin"
2、获取session值
　　　　session_name = request.session("session_name")
3、删除session值
　　　　del request.session["session_name"]  删除一组键值对
　　　　request.session.flush()   删除一条记录
4、检测是否操作session值
　　　　if "session_name"  is request.session:
'''