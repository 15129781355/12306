import requests
from cons  import station_names
from  settings  import *
from user import *
import re
import urllib
import urllib3
urllib3.disable_warnings()

dict_station={}
tem_list=station_names.split('@')
for i in tem_list:
    temp_list = i.split('|')
    if len(temp_list) > 2:
        dict_station[temp_list[1]] = temp_list[2]

from_station = dict_station[FROM_STATION]
to_station = dict_station[TO_STATION]
#创建标签  代表是同一个用户申请的图片和输入的验证码
req = requests.Session()
req.verify=False

def login():
    #读取图片
    response = req.get('https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand')
    ff = response.content
    f = open('code.png','wb')
    f.write(ff)
    f.close()
    #输入验证码
    url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
    data={
    'answer':input('>>>>'),
    'login_site':'E',
    'rand':'sjrand'
    }
    response = req.post(url=url , data = data , headers = header)
    if response.json()['result_code'] != '4':
        login()
        return
    user = {
        'username':userr,
        'password': pwd,
        'appid': 'otn'}
    response = req.post(url='https://kyfw.12306.cn/passport/web/login',data = user,headers=header)
    if response.json()['result_code'] != 0:
        login()
        return
    #登陆的传参,检查登陆是否真的成功
    request = req.post('https://kyfw.12306.cn/passport/web/auth/uamtk', headers=header,data={'appid':'otn'})
    TK =request.json()['newapptk']
    request = req.post('https://kyfw.12306.cn/otn/uamauthclient', headers=header, data={'tk': TK})
    request = req.get('https://kyfw.12306.cn/otn/index/initMy12306', headers=header)
    code = re.findall(r'<span style="width:50px;">(.*?)</span>',request.text)[0]
    if code =='朱昭苇':
        print('登陆成功')

def order():
    #下单第一步
    request = req.post('https://kyfw.12306.cn/otn/login/checkUser', headers=header, data={'_json_att': ''})
    code = request.json()['data']['flag']
    if code == True:
        print('下单第一步完成')
        print(request.json())
    else:
        print('下单第一步失败',request.json())
        return
    # 下单第二步
    global sorce  ####sorce是经过python编码的 应该解码下
    sorce = urllib.parse.unquote(sorce)
    data = {
        'back_train_date':NOW_TIME,
        'purpose_codes':'ADULT',
        'query_from_station_name':FROM_STATION,
        'query_to_station_name':TO_STATION,
        'secretStr':sorce,
        'tour_flag':'dc',     ###一定注意检查参数对不对
        'train_date' :TRAIN_DATE,
        'undefined':''}
    request = req.post('https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest', headers=header, data=data)
    code = request.json()['httpstatus']
    if code ==200:
        print('下单第二步完成')
        print(request.json())
    else:
        print('下单第二步失败')
        return
    # 获取登陆验证码
    request1 = req.post('https://kyfw.12306.cn/otn/confirmPassenger/initDc',headers=header ,data={'_json_att':''} )
    repeat_submit_token = re.findall(r"var globalRepeatSubmitToken = '(.*?)'",request1.text)[0]      #r"'key_check_isChange':'(.*?)'"
    #bug有时找不到liftTicket 服务器的问题 直接在 车票信息那找
    liftTicket = re.findall(r"'leftTicketStr':'(.*?)'",request1.text)[0]
    key_check_ischange = re.findall(r"'key_check_isChange':'(.*?)'",request1.text)[0]
    print('成功获取登陆验证码')
    #下单第三步
    data = {'_json_att':'',
    'REPEAT_SUBMIT_TOKEN':repeat_submit_token}
    request = req.post('https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs',headers=header , data=data)
    code = request.json()['data']['isExist']
    if code:
        print('下单第三步完成')
        print(request.json())
    else:
        print('下单第三步失败')
        return
    #下单第四步
    data = {'_json_att': '',
            'bed_level_order_num':'000000000000000000000000000000',
            'cancel_flag':2,
            'oldPassengerStr':'写死的',
        'passengerTicketStr':'写死的',
            'randCode':'',
            'REPEAT_SUBMIT_TOKEN': repeat_submit_token,
            'tour_flag': 'dc',
            'whatsSelect':1}
    request = req.post('https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo', headers=header, data=data)
    code = request.json()['status']
    if code:
        print('下单第四步成功')
        print(request.json())
    else:
        print('下单第四步失败')
        return
    #下单第五步
    data = {'_json_att':'',
            'fromStationTelecode':fromStation,
            'leftTicket':liftTicket,
            'purpose_codes':'00',
            'REPEAT_SUBMIT_TOKEN':repeat_submit_token,
            'seatType':'4',
            'tationTrainCode':count_taxi,
            'toStationTelecode':to_station,
            'train_date':'Thu Mar 29 2018 00:00:00 GMT+0800 (中国标准时间)',
            'train_location':train_location,
            'train_no':train_no}
    request = req.post('https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount', headers=header, data=data) #这一步感觉没作用count不能正常返回就是这个问题
    code = request.json()['status']
    # for i in data.items():
    #     print(i)
    if code:
        print('下单第五步成功')
        print(request.json())
    else:
        print('下单第五步失败')
        return
    #购票第一步
    data = {
        'passengerTicketStr':'写死的',
        'oldPassengerStr':'写死的',
        'randCode':'',
        'purpose_codes':'00',
        'key_check_isChange':key_check_ischange,
        'leftTicketStr':liftTicket,
        'train_location':train_location,
        'choose_seats':'',
        'seatDetailType':'000',
        'whatsSelect':'1',
        'roomType':'00',
        'dwAll':'N',
        '_json_att':'',
        'REPEAT_SUBMIT_TOKEN': repeat_submit_token}
    request = req.post('https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue', headers=header, data=data)
    print(request.text)


def check_stamp():
    '''查找软卧是否有票'''
    req.get('http://www.12306.cn/mormhweb/',headers =header)
    response=req.get('https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(TRAIN_DATE,from_station,to_station),headers=header)
    result = response.json()
    # print(response.url)
    # print(result)
    return result['data']['result']

'''1预定  3车次 8出发时间 9到达时间 10历时 21 高级软卧 23软卧  25,32商务座特等座
 31一等座  30二等座 26无座 29 硬座 28硬卧 33 动卧  27 软座'''
for i in check_stamp():
    tem_list = i.split('|')
    set = tem_list[SET]
    sorce = tem_list[0]
    count_taxi = tem_list[3]
    train_location = tem_list[15]
    train_no = tem_list[2]
    fromStation = tem_list[4]
    #liftTicket = tem_list[12]
    if set == '' or set == '无':
        print('无票',tem_list[3])
    else:
        print('有票', tem_list[3],set)
        #有票后登陆 然后 预定
        login()
        order()
        break







