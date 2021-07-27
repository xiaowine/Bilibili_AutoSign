from logging import INFO, DEBUG, getLogger, Formatter, StreamHandler
from logging import handlers
from os import system, path, mkdir
from random import choice
from re import findall
from sys import argv
from time import time, sleep

from requests import get, post
from yaml import safe_load, YAMLError

initialization = '''# 获取Cookie教程
# （此处使用谷歌浏览器举例）打开电脑浏览器无痕模式并登录 bilibili 网站
# 按 F12 打开 「开发者工具」 在最上方找到 应用程序/Application -> 存储 -> Cookies
# 找到 SESSDATA DedeUserID bili_jct 三项，并复制值。


举例用户1: # 此处名字随意填写，只是用于自己区分账号使用
  SESSDATA: 'xyz321' # 值需要用引号括上，单引号双引号都行
  DedeUserID: 654321 # 这里不能用引号括住
  bili_jct: 'xyz321' # 值需要用引号括上，单引号双引号都行
  history: True # 关闭历史(签到的视频不会增加到Bilibili观看历史)
  autoSign: True # 自动签到
  autoWatch: True # 自动观看
  autoShare: True # 自动分享视频
  autoCoin: True # 自动投币
  lowestCoin: 0 # 硬币数低于停止自动投币 值大于等于0
  likeWhenCoin: True # 投币同时点赞
  autoSign_live: True # 自动直播签到
  silverToCoin: True # 直播银瓜子换硬币



举例用户2:
  SESSDATA: 'abc123'
  DedeUserID: 123456
  bili_jct: 'abc123'
  history: True # 关闭历史(签到的视频不会增加到Bilibili观看历史)
  autoSign: True # 自动签到
  autoWatch: True # 自动观看
  autoShare: True # 自动分享视频
  autoCoin: True # 自动投币
  lowestCoin: 0 # 硬币数低于停止自动投币
  likeWhenCoin: True # 投币同时点赞
  autoSign_live: True # 自动直播签到
  silverToCoin: True # 直播银瓜子换硬币
'''


def config():
    if path.isfile('config.yml'):
        with open('config.yml', encoding='UTF-8') as file:
            try:
                configFile = safe_load(file.read())
                for key in configFile.keys():
                    ikey = configFile[key]
                    if type(ikey['SESSDATA']) is str and \
                            type(ikey['DedeUserID']) is int and \
                            type(ikey['bili_jct']) is str:
                        if type(ikey['lowestCoin']) is int and ikey['lowestCoin'] >= 0:
                            if type(ikey['history']) is bool and type(ikey['autoSign']) is bool and \
                                    type(ikey['autoSign_live']) is bool and type(ikey['autoWatch']) is bool and \
                                    type(ikey['autoShare']) is bool and type(ikey['autoCoin']) is bool and \
                                    type(ikey['likeWhenCoin']) is bool and type(ikey['silverToCoin']) is bool:
                                pass
                            else:
                                log.logger.error('“功能开关” 参数错误 请检查配置文件')
                                system('PAUSE')
                                quit()
                        else:
                            log.logger.error('“硬币数低于停止自动投币”参数错误 请检查配置文件')
                            system('PAUSE')
                            quit()
                    else:
                        log.logger.error('“Cookie”参数错误 请检查配置文件')
                        system('PAUSE')
                        quit()
                return configFile
            except YAMLError as error:
                where = error.args
                for e in where:
                    log.logger.error(e)
                log.logger.info('请检查配置文件，删除文件恢复默认配置')
                system('PAUSE')
                quit()
    else:
        with open('config.yml', 'w', encoding='UTF-8') as file:
            file.write(initialization)
            log.logger.error('请退出程序，使用记事本 “config.yml”配置文件')
            system('PAUSE')
            quit()


class Logger:
    def __init__(self, filename, grade=INFO):
        if not path.exists('logs'):
            mkdir('logs')
        self.logger = getLogger(filename)
        format_str = Formatter('[%(asctime)s] %(message)s'.format(''), '%Y-%m-%d %H:%M:%S')
        self.logger.setLevel(grade)
        sh = StreamHandler()
        sh.setFormatter(format_str)
        th = handlers.TimedRotatingFileHandler(filename=filename, when='D', encoding='utf-8')
        th.setFormatter(format_str)
        self.logger.addHandler(sh)
        self.logger.addHandler(th)


class Bilibili:
    def __init__(self, url='https://api.bilibili.com/x/web-interface/nav', data=None):
        if data is None:
            data = {}
        self.url = url
        self.data = data
        log.logger.debug('{} {}'.format(self.url, self.data))

    def get(self):
        res = get(self.url, headers=cookies)
        if res.status_code == 200 and res.json()['code'] in [0, 1011040, -101]:
            if res.json()['code'] == -101:
                log.logger.error('Cookie 错误，请检查')
                system('PAUSE')
                quit()
            else:
                log.logger.debug(res.json())
                return res.json()
        else:
            log.logger.debug(res.text)
            log.logger.error('程序错误,请检查配置文件')
            system('PAUSE')
            quit()

    def post(self):
        res = post(url=self.url, data=self.data, headers=cookies)
        if res.status_code == 200 and res.json()['code'] in [0, 71000]:
            log.logger.debug(res.json())
            return res.json()
        else:
            log.logger.debug(res.text)
            log.logger.error('程序错误,请检查配置文件')
            system('PAUSE')
            quit()


def main(args):
    got_xp = 0
    log.logger.info('{}'.format('*' * 50))
    nav = Bilibili().get()

    verification_status = True
    if nav['data']['email_verified'] == 0:
        verification_status = False
        log.logger.info('［提示］建议账号绑定邮箱')
    if nav['data']['mobile_verified'] == 0:
        verification_status = False
        log.logger.info('［提示］建议账号绑定手机号')
    if Bilibili('https://api.bilibili.com/x/member/realname/apply/status').get()['data']['status'] == 3:
        verification_status = False
        log.logger.info('［提示］建议账号实名认证')
    if not verification_status:
        log.logger.info('{} 建议完成以上事件,可增加经验值,提前LV.6 {}'.format('*' * 5, '*' * 5))

    log.logger.info('［主站］B站用户名：{}'.format(nav['data']['uname']))
    log.logger.info('［主站］B站MID：{}'.format(nav['data']['mid']))
    log.logger.info('［主站］B站B币数：{}'.format(nav['data']['wallet']['bcoin_balance']))

    vip = nav['data']['vipType']
    if vip == 1:
        vipStatus = '月度大会员'
    elif vip == 2:
        vipStatus = '年度及以上大会员'
    else:
        vipStatus = '无会员'
    log.logger.info('［主站］B站会员类型：{}'.format(vipStatus))

    xp = [nav['data']['level_info']['current_level'], nav['data']['level_info']['current_exp'],
          nav['data']['level_info']['next_exp'] - nav['data']['level_info']['current_exp']]
    log.logger.info('［主站］现等级 LV.{0} ,现经验 {1} ,升级还需经验{2}'.format(*xp))
    reward = Bilibili('https://api.bilibili.com/x/member/web/exp/reward').get()

    if args['autoSign']:
        if reward['data']['login']:
            log.logger.info('［主站］签到失败(今日已签到),现有硬币:{}'.format(Bilibili().get()['data']['money']))
        else:
            log.logger.info('［主站］签到成功,现有硬币:{}'.format(Bilibili().get()['data']['money']))
            got_xp += 5

    else:
        log.logger.info('［主站］签到功能已关闭')

    shadow = Bilibili('https://api.bilibili.com/x/v2/history/shadow').get()['data']
    log.logger.info('［主站］当前历史状态：关闭' if shadow else '［主站］当前历史状态：开启')
    if args['history']:
        Bilibili('https://api.bilibili.com/x/v2/history/shadow/set', {'switch': True, 'csrf': args['bili_jct']}).post()
        log.logger.info('［主站］关闭当前历史')
    else:
        log.logger.info('［主站］保留当前历史状态')

    loc = Bilibili('https://api.bilibili.com/x/web-show/res/loc?id=34').get()
    spread_show = [show['url'] for show in loc['data'] if findall('^http://www.bilibili.com/video/BV', show['url'])]
    spread_bv = choice(spread_show).split('/')[-1]
    view = Bilibili('https://api.bilibili.com/x/web-interface/view?bvid={}'.format(spread_bv)).get()
    if args['autoWatch']:
        if reward['data']['watch']:
            log.logger.info('［主站］观看失败(今日已观看)')
        else:
            Bilibili('https://api.bilibili.com/x/v2/history/report',
                     {'csrf': args['bili_jct'], 'aid': view['data']['aid'], 'cid': view['data']['cid']}).post()
            log.logger.info('［主站］观看 {}, BV号 :{}'.format(view['data']['title'], view['data']['bvid']))
            got_xp += 5
    else:
        log.logger.info('［主站］观看功能已关闭')
    if args['autoShare']:
        if reward['data']['share']:
            log.logger.info('［主站］分享失败(今日已分享)')
        else:
            while True:
                share = Bilibili('https://api.bilibili.com/x/web-interface/share/add',
                                 data={'aid': view['data']['aid'], 'csrf': args['bili_jct']}).post()
                if share['code'] == 71000:
                    spread_bv = choice(spread_show).split('/')[-1]
                    view = Bilibili('https://api.bilibili.com/x/web-interface/view?bvid={}'.format(spread_bv)).get()
                else:
                    log.logger.info('［主站］分享成功 {}, BV号 :{}'.format(view['data']['title'], view['data']['bvid']))
                    got_xp += 5
                    break

    else:
        log.logger.info('［主站］分享功能已关闭')
    if args['autoCoin']:
        exp = Bilibili('https://www.bilibili.com/plus/account/exp.php').get()
        if exp['number'] != 50:
            related = Bilibili(
                'https://api.bilibili.com/x/web-interface/archive/related?bvid={}'.format(spread_bv)).get()
            bv = [bv['bvid'] for bv in related['data']]
            while Bilibili('https://www.bilibili.com/plus/account/exp.php').get()['number'] != 50 and \
                    Bilibili().get()['data']['money'] // 1 > args['lowestCoin']:
                bv_ = choice(bv)
                if Bilibili('https://api.bilibili.com/x/web-interface/archive/coins?bvid={}'.format(bv_)).get()[
                    'data']['multiply'] == 0:
                    Bilibili('https://api.bilibili.com/x/web-interface/coin/add',
                             {'bvid': bv_, 'multiply': 1, 'select_like': 1, 'csrf': args['bili_jct']}).post()
                    log.logger.info('［主站］成功投币：{}'.format(bv_))
                    got_xp += 10
            log.logger.info('［主站］投币完成,剩余硬币: {}'.format(Bilibili().get()['data']['money']))

        else:
            log.logger.info('［主站］投币失败(今日已投币5颗)')
    else:
        log.logger.info('［主站］投币功能已关闭')
    Bilibili('https://api.bilibili.com/x/v2/history/shadow/set', {'switch': False, 'csrf': args['bili_jct']}).post()
    log.logger.info('［主站］恢复当前历史状态')

    nav = Bilibili().get()
    if got_xp == 0:
        log.logger.info('［主站］本次运行没有获得经验')
    else:
        log.logger.info(
            '［主站］本次运行获得经验 {} 还需运行{}天 到达 LV.{}'.format(got_xp, nav['data']['level_info']['current_exp'] // int(got_xp),
                                                      nav['data']['level_info']['current_level'] + 1))

    log.logger.info('{}'.format('*' * 50))

    if args['autoSign_live']:
        DoSign = Bilibili('https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign').get()
        log.logger.info(
            '［直播］{}'.format(DoSign if (DoSign['message'].strip() == 0) else DoSign['message']))
    else:
        log.logger.info('［直播］签到功能已关闭')

    if args['silverToCoin']:
        if Bilibili('https://api.live.bilibili.com/xlive/web-ucenter/user/get_user_info').get() \
                ['data']['silver'] // 1 >= 700:
            Bilibili('https://api.live.bilibili.com/pay/v1/Exchange/silver2coin', {'csrf': args['bili_jct']}).post()
        else:
            log.logger.info('［直播］银瓜子兑换硬币失败(银瓜子不足)')
    else:
        log.logger.info('［直播］银瓜子兑换硬币功能已关闭')

    log.logger.info('{}'.format('*' * 50))


if __name__ == '__main__':

    if len(argv) == 2:
        if argv[1].upper() == 'DEBUG':
            log = Logger('logs/logs.log', DEBUG)
        else:
            log = Logger('logs/logs.log')
    else:
        log = Logger('logs/logs.log')
    config = config()

    while True:
        start = time()
        for i in config.keys():
            cookies = {'Cookie': 'DedeUserID={};SESSDATA={}'.format(config[i]['DedeUserID'], config[i]['SESSDATA']),
                       "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/63.0.3239.108"}
            log.logger.info(cookies)
            main(config[i])
        log.logger.info('当前任务完成，暂停24小时')
        sleep(60 * 60 * 24 - time() + start)
