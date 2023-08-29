#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 19:14:51 2023

@author: yxwu
"""
import pandas as pd
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
def scrape_hotel_info(location, hotel_name, start_date, end_date):
    driver = webdriver.Edge()
    search_url = f"https://www.booking.com/searchresults.zh-tw.html?ss={hotel_name}&checkin_year={start_date[:4]}&checkin_month={start_date[5:7]}&checkin_monthday={start_date[8:10]}&checkout_year={end_date[:4]}&checkout_month={end_date[5:7]}&checkout_monthday={end_date[8:10]}"
    displaynames = []
    # 載入網頁
    driver.get(search_url)

    # 等待網頁完全載入（可以根據實際情況調整等待時間）
    driver.implicitly_wait(10)

    # 獲取網頁內容
    page_content = driver.page_source
    #print(page_content)
    # 假設登入提示的元素帶有 aria-label 屬性
    close_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="關閉登入的資訊。"]')

    # 點選關閉按鈕
    close_button.click()

    # 假設您已經獲取了網頁內容並存儲在 page_content 變數中
    # page_content = ...

    # 使用 BeautifulSoup 解析網頁內容
    soup = BeautifulSoup(page_content, 'html.parser')

    target_element = driver.find_element(By.CLASS_NAME, 'e13098a59f[data-testid="title-link"]')

    # 取得 href 屬性的值
    href_value = target_element.get_attribute('href')

    # 關閉瀏覽器視窗
    driver.quit()

    driver = webdriver.Edge()
    driver.get((href_value))
    driver.implicitly_wait(10)
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')

    # 找到所有的 <tr> 元素
    table_rows = soup.find_all('tr')
    ans=[]
    # 遍歷每個 <tr> 元素，然後提取其中的 <td> 資訊
    for row in table_rows:
        table_data = row.find_all('td')
        for data in table_data:
            if data.get_text()=='\xa0' or data.get_text()=='\n\n1—\n\n' or data.get_text()=='':
                continue
            else:
                clean_data=data.get_text().replace('\n','')
                ans.append(clean_data)
            #print(data.get_text())  # 印出 <td> 元素的文字內容
    room=''
    for ids,i in enumerate(ans):
        if ids==0:
            for i in range(len(ans[ids])):
                if ans[ids][i]==' ':
                    room=ans[ids][0:i+1]
                    #room=ans[ids]
                    #print(room)
                    break
        if '最多人數:' in ans[ids]:
            people.append(ans[ids])
        if '選擇客房01' in ans[ids]:
            try:
                location_list.append(location)
                hotel_name_list.append(hotel_name)
                roomtype.append(room)
                for i in range(len(ans[ids])):
                    if ans[ids][i]=='(':
                        first=i+1
                    elif ans[ids][i]==')':
                        price.append(ans[ids][first:i])
                        break
                alldate.append(start_date)                
                if '含早餐' in ans[ids-1]:
                    breakfast.append('含早餐')
                else:
                    breakfast.append('不含早餐')
                if '最多人數:' not in ans[ids+1]: #如果下一個不是 最多人數的話 代表是新的房間
                    for i in range(len(ans[ids+1])):
                        if ans[ids+1][i]==' ':
                            #room=ans[ids+1]
                            room=ans[ids+1][0:i+1]
                            break
            except:
                pass
            
    driver.quit()
    
if __name__ == "__main__":
    location = input('請輸入縣市: ') #台北 'JR東日本大飯店 台北'
    hotel_name = input('請輸入旅館名稱:  （請輸入全名）')
    start_date = input('請輸入開始日期:  ') #'2023/09/28'
    end_date = input('請輸入結束日期:  ') #'2023/09/29'
    start_date_obj = datetime.strptime(start_date, "%Y/%m/%d")
    end_date_obj = datetime.strptime(end_date, "%Y/%m/%d")
    # 定义每两天为一组
    days_per_group = 2
    location_list=[]
    hotel_name_list=[]
    people=[]
    roomtype=[]
    price=[]
    breakfast=[]
    alldate=[]
    while start_date_obj <end_date_obj:
        # 计算下一组的结束日期
        next_end_date_obj = start_date_obj + timedelta(days=days_per_group - 1)
        # 格式化日期字符串
        formatted_start_date = start_date_obj.strftime("%Y/%m/%d")
        formatted_end_date = next_end_date_obj.strftime("%Y/%m/%d")
        # 输出日期范围
        scrape_hotel_info(location, hotel_name, formatted_start_date, formatted_end_date)
        print(formatted_start_date,'-',formatted_end_date)
        # 更新起始日期到下一组的开始日期
        start_date_obj = next_end_date_obj 
    print(len(price))
    print(len(alldate))
    print(len(breakfast))
    print(len(roomtype))
    df=pd.DataFrame()
    df['地區']=location_list
    df['飯店名']=hotel_name_list
    df['日期']=alldate
    df['房型']=roomtype
    df['房價']=price
    df['有無早餐']=breakfast
    df.to_csv(hotel_name+'.csv',index=0)
    
    
    
    
    