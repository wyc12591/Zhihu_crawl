from __future__ import unicode_literals

import json
import time

import cv2
import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options


class Zhihu:

    def __init__(self):
        self.url = 'https://www.zhihu.com/signin?next=%2F'
        self.options = Options()
        self.options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        # self.chrome_options = webdriver.ChromeOptions
        # self.chrome_options.add_experimental_option('excludeSwitches', 'enable-automation', )
        self.driver = webdriver.Chrome(options=self.options)
        # self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #     "source": """
        #     Object.defineProperty(navigator, 'webdriver', {
        #     get: () => false
        #     })
        #     """
        # })
        # self.driver.implicitly_wait(1)
        self.k = 1
        self.userid = ''

    def login(self):
        use_pwd = self.driver.find_element_by_xpath(
            '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[1]/div[@class="SignFlow-tab"]')
        use_pwd.click()

        self.driver.implicitly_wait(3)
        username = self.driver.find_element_by_xpath(
            '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[2]/div/label/input')
        self.driver.implicitly_wait(3)
        password = self.driver.find_element_by_xpath(
            '//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[3]/div/label/input')
        self.driver.implicitly_wait(3)
        time.sleep(2)
        username.send_keys('17520486329')
        time.sleep(2)
        password.send_keys('SEj5lAySsxCZVzUwBiiLzIo0vG')
        time.sleep(2)
        login_button = self.driver.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/button')
        login_button.click()

    def close_window(self):
        self.driver.quit()

    def get_image(self):
        self.driver.switch_to.frame('tcaptcha_iframe')
        time.sleep(2)
        bg_img = self.driver.find_element_by_xpath('//*[@id="slideBg"]')
        block_img = self.driver.find_element_by_xpath('//*[@id="slideBlock"]')
        print(bg_img)
        print(block_img)
        # response = requests.get(bg_img.get_attribute('src'))
        # print(response.content)
        with open("bg.jpg", "wb") as f:
            f.write(requests.get(bg_img.get_attribute('src')).content)
            f.close()
        with open("block.jpg", "wb") as f:
            f.write(requests.get(block_img.get_attribute('src')).content)
            f.close()

    def deal_with_image(self):
        bj = cv2.imread('./bg.jpg')  # 打开待处理图片
        xhd = cv2.imread('./block.jpg')

        bj = cv2.cvtColor(bj, cv2.COLOR_BGR2GRAY)  # 灰度处理
        xhd = cv2.cvtColor(xhd, cv2.COLOR_BGR2GRAY)

        time.sleep(3)

        # 去掉滑块黑色部分
        xhd = xhd[xhd.any(1)]  # 0表示黑色，1表示高亮部分

        time.sleep(3)

        # 匹配->cv图像匹配算法
        result = cv2.matchTemplate(bj, xhd, cv2.TM_CCOEFF_NORMED)  # match匹配,Template模板;精度高，速度慢的方法
        index_max = np.argmax(result)  # 返回的是一维的位置，最大值索引

        time.sleep(3)

        # 反着推最大值的二维位置，和opencv是相反的
        x, y = np.unravel_index(index_max, result.shape)
        print("二维中坐标的位置：", x, y)
        print("正在进行第%s次滑动验证" % self.k)
        drop = self.driver.find_element_by_xpath('/html/body/div/div[3]/div[2]/div[2]/div[2]/div')
        ActionChains(self.driver).drag_and_drop_by_offset(drop, xoffset=x + 26, yoffset=0).perform()
        time.sleep(1)

    def get_data(self, userid):
        self.driver.get('https://www.zhihu.com/people/' + userid)

        data = {}

        basic_info = {}
        nickname = self.driver.find_element_by_xpath(
            '//*[@id="ProfileHeader"]/div/div[2]/div/div[2]/div[1]/h1/span[1]').text
        basic_info['昵称'] = nickname

        try:
            gender = self.driver.find_element_by_xpath(
                '//*[@id="ProfileHeader"]/div/div/div/div/div/div/div/div/div//*[@width=24]').get_attribute(
                'class')
            if gender == 'Zi Zi--Male':
                basic_info['性别'] = '男'
            else:
                basic_info['性别'] = '女'
        except:
            basic_info['性别'] = '秘密'

        one_sentence = self.driver.find_element_by_xpath('//span[@class="ztext ProfileHeader-headline"]').text
        basic_info['一句话介绍'] = one_sentence

        time.sleep(2)

        detail_button = self.driver.find_element_by_xpath(
            '//*[@class="Button ProfileHeader-expandButton Button--plain"]')
        detail_button.click()

        time.sleep(2)

        try:
            place_of_residence = self.driver.find_element_by_xpath(
                '//span[contains(text(),"居住地")]/../div/span').text
            basic_info['居住地'] = place_of_residence
        except:
            basic_info['居住地'] = '无'

        try:
            profession = self.driver.find_element_by_xpath(
                '//span[contains(text(),"所在行业")]/../div').text
            basic_info['所在行业'] = profession
        except:
            basic_info['所在行业'] = '无'

        try:
            professional_history = self.driver.find_element_by_xpath(
                '//span[contains(text(),"职业经历")]/../div/div').text
            basic_info['职业经历'] = professional_history
        except:
            basic_info['职业经历'] = '无'

        try:
            individual_resume = self.driver.find_element_by_xpath(
                '//span[contains(text(),"个人简介")]/../div').text
            basic_info['个人简介'] = individual_resume
        except:
            basic_info['个人简介'] = '无'

        print(basic_info)

        data['基本属性信息'] = basic_info

        print(data)

        social_info = {}
        follow_button = self.driver.find_element_by_xpath(
            '//main//*[@class="Tabs-item Tabs-item--noMeta"]/*[contains(text(),"关注")]')
        follow_button.click()

        time.sleep(2)

        guanzhu_info_list = []
        guanzhu_list = self.driver.find_elements_by_xpath('//*[@class="List-item"]//*[@class="ContentItem-head"]')
        guanzhu_info_list = self.get_followers(guanzhu_list)
        data['关注人'] = guanzhu_info_list

        fensi_button = self.driver.find_element_by_xpath('//*[@id="Profile-following"]/div[@class="List-header"]//a[2]')
        fensi_button.click()
        time.sleep(1)

        fensi_list = self.driver.find_elements_by_xpath('//*[@class="List-item"]//*[@class="ContentItem-head"]')
        fensi_info_list = self.get_followers(fensi_list)
        data['粉丝'] = fensi_info_list

        huida_button = self.driver.find_element_by_xpath('//main//a[contains(text(),"回答")]')
        huida_button.click()

        time.sleep(2)

        huida_list = self.driver.find_elements_by_xpath('//*[@id="Profile-answers"]//div[@class="List-item"]')
        huida_info_list = self.get_huida(huida_list)
        data['回答'] = huida_info_list

        tiwen_button = self.driver.find_element_by_xpath('//div[@class="Profile-main"]//a[contains(text(),"提问")]')
        action = ActionChains(self.driver)
        action.move_to_element(tiwen_button).click().perform()
        time.sleep(1)

        tiwen_list = self.driver.find_elements_by_xpath('//div[@class="List-item"]')
        tiwen_info_list = self.get_tiwen(tiwen_list)
        data['提问'] = tiwen_info_list
        return data

    def get_huida(self, huida_list):
        huida_info_list = []
        for huida in huida_list:
            if len(huida_info_list) >= 10:
                break
            huida_detail = {}
            huida_detail['问题'] = huida.find_element_by_xpath('.//h2[@class="ContentItem-title"]/div').text
            yue_du_quan_wen = huida.find_element_by_xpath('.//*[@class="Button ContentItem-more Button--plain"]')
            yue_du_quan_wen.click()
            huida_detail['回答内容'] = huida.find_element_by_xpath(
                './/*[@class="RichText ztext CopyrightRichText-richText"]').text
            # print(huida_detail['回答'])
            huida_detail['回答时间'] = huida.find_element_by_xpath('.//div[@class="ContentItem-time"]//span').text
            huida_detail['评论数'] = huida.find_element_by_xpath('.//button[contains(text(),"评论")]').text
            huida_detail['点赞数'] = huida.find_element_by_xpath(
                './/button[@class="Button VoteButton VoteButton--up"]').text
            huida_detail['评论'] = []

            ping_lun_button = huida.find_element_by_xpath('.//button[contains(text(),"评论")]')
            ping_lun_button.click()
            time.sleep(3)
            while True:
                try:
                    zhan_kai_ping_lun = huida.find_element_by_xpath('.//button[contains(text(),"展开其他")]')
                    zhan_kai_ping_lun.click()
                    time.sleep(1)
                except:
                    break

            ping_lun_main_list = huida.find_elements_by_xpath('.//ul')
            for ping_lun_zu in ping_lun_main_list:
                ping_lun_list = ping_lun_zu.find_elements_by_xpath('.//li')
                for single_ping_lun in ping_lun_list:
                    if len(huida_detail['评论']) >= 10:
                        break
                    single_ping_lun_detail = {}
                    single_ping_lun_detail['评论人地址'] = single_ping_lun.find_element_by_xpath(
                        './/span[@class="UserLink"][1]').get_attribute('href')
                    single_ping_lun_detail['评论人昵称'] = single_ping_lun.find_element_by_xpath(
                        './/span[@class="UserLink"][1]').text
                    single_ping_lun_detail['评论时间'] = single_ping_lun.find_element_by_xpath(
                        './/span[@class="CommentItemV2-time"]').text
                    single_ping_lun_detail['评论内容'] = single_ping_lun.find_element_by_xpath(
                        './/div[@class="CommentItemV2-metaSibling"]//div[@class="RichText ztext"]').text
                    single_ping_lun_detail['点赞次数'] = single_ping_lun.find_element_by_xpath(
                        './/button[@class="Button CommentItemV2-likeBtn Button--plain"]').text
                    if single_ping_lun_detail['点赞次数'] == '赞':
                        single_ping_lun_detail['点赞次数'] = '0'
                    huida_detail['评论'].append(single_ping_lun_detail)
            huida_info_list.append(huida_detail)
            shou_qi_ping_lun_button = huida.find_element_by_xpath('.//button[contains(text(),"收起评论")]')
            # self.driver.execute_script("arguments[0].scrollIntoView();", shou_qi_ping_lun_button)
            # time.sleep(1)
            # shou_qi_ping_lun_button.click()
            action = ActionChains(self.driver)
            action.move_to_element(shou_qi_ping_lun_button).click().perform()
            time.sleep(1)
        return huida_info_list

    def get_followers(self, people_list):
        people_info_list = []
        for guanzhu in people_list:
            if len(people_info_list) >= 10:
                break
            try:
                people_info = {'昵称': guanzhu.find_element_by_xpath('.//a[@class="UserLink-link"]').text,
                               '链接地址': guanzhu.find_element_by_xpath('.//a[@class="UserLink-link"]').get_attribute(
                                   'href')}
            except:
                people_info = {'昵称': '知乎用户（已注销）', '链接地址': '无'}
            try:
                people_info['回答数'] = guanzhu.find_element_by_xpath(
                    './/div[@class="ContentItem-status"]/span[contains(text(),"回答")]').text
            except:
                people_info['回答数'] = '无'
            try:
                people_info['文章数'] = guanzhu.find_element_by_xpath(
                    './/div[@class="ContentItem-status"]/span[contains(text(),"文章")]').text
            except:
                people_info['文章数'] = '无'
            try:
                people_info['关注者数'] = guanzhu.find_element_by_xpath(
                    './/div[@class="ContentItem-status"]/span[contains(text(),"关注")]').text
            except:
                people_info['关注者数'] = '无'
            people_info_list.append(people_info)
        print(len(people_info_list))
        return people_info_list

    def run(self):
        # # url
        # # driver
        # # get
        # self.driver.get(self.url)
        #
        # # login
        # self.login()
        # time.sleep(10)
        # cookies_list = self.driver.get_cookies()
        # cookies = {}
        # for cookie in cookies_list:
        #     cookies[cookie['name']] = cookie['value']
        # json_cookies = json.dumps(cookies)
        # with open("zhihu_cookies.txt", "w") as f:
        #     f.write(json_cookies)
        #     f.close()
        #
        # print('自动登录成功')

        self.userid = 'shui-yue-95-77'  # input('请输入用户id')
        # while True:
        # self.get_image()
        # self.deal_with_image()
        # self.driver.switch_to.default_content()
        # if '首页' in self.driver.title:
        #     break
        # else:
        #     print('第%s次验证失败...' % self.k, '\n')
        # self.k = self.k + 1
        # time.sleep(5)
        # get user_info
        data = self.get_data(self.userid)
        with open("result.json", "w", encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))  # parse
        # save
        # next

    def get_tiwen(self, tiwen_list):
        tiwen_info_list = []
        for tiwen in tiwen_list:
            if len(tiwen_info_list) >= 10:
                break
            tiwen_detail = {}
            tiwen_detail['问题'] = tiwen.find_element_by_xpath('.//a').text
            tiwen_detail['提问时间'] = tiwen.find_element_by_xpath('.//span[@class="ContentItem-statusItem"][1]').text
            tiwen_detail['回答数'] = tiwen.find_element_by_xpath('.//span[@class="ContentItem-statusItem"][2]').text
            tiwen_detail['关注数'] = tiwen.find_element_by_xpath('.//span[@class="ContentItem-statusItem"][3]').text
            tiwen_info_list.append(tiwen_detail)
        return tiwen_info_list


if __name__ == '__main__':
    zhihu = Zhihu()
    zhihu.run()
    # zhihu.close_window()
