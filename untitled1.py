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
        try:
            close_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="關閉登入的資訊。"]')
        
            # 點選關閉按鈕
            close_button.click()
        except:
            pass
        # 使用 BeautifulSoup 解析網頁內容
        soup = BeautifulSoup(page_content, 'html.parser')
        class_name = 'f6431b446c a23c043802'  # 请将此处替换为您要查找的class值
        elements_with_class = soup.find_all('div', class_=class_name)
        
        # 確認首間是要查詢的飯店
        for id,element in enumerate(elements_with_class):
            if id==0:
                print(element.get_text(),hotel_name)
                if element.get_text()!=hotel_name:
                    return 
            else:
                break
        # 假設您已經獲取了網頁內容並存儲在 page_content 變數中
        # page_content = ...
        
        # 使用 BeautifulSoup 解析網頁內容
        soup = BeautifulSoup(page_content, 'html.parser')
    
        target_element = driver.find_element(By.CLASS_NAME, 'a78ca197d0[data-testid="title-link"]')
    
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
        check_roomnumber=0
        for ids,name in enumerate(ans):
            if (ids+1)<len(ans) and '最多人數:' in ans[ids+1]: #如果下一個不是 最多人數的話 代表是新的房間
                for j in range(len(ans[ids])):
                    if ans[ids][j]==' ':
                        room=ans[ids][0:j+1]
                        check_roomnumber+=1
                        #room=ans[ids]
                        #print(room)
                        break
            if '選擇客房01' in ans[ids]:
                try:
                    check_roomnumber+=1
                    roomtype.append(room)
                    location_list.append(location)
                    haveroom.append('')
                    hotel_name_list.append(hotel_name)
                    for i in range(len(ans[ids])):
                        if ans[ids][i]=='(':
                            first=i+5
                        elif ans[ids][i]==')':
                            price_or=ans[ids][first:i].replace(',','')
                            price.append(int(price_or))
                            break
                    alldate.append(start_date)                
                    if '含早餐' in ans[ids-1]:
                        breakfast.append('含早餐')
                    else:
                        breakfast.append('不含早餐')
                except:
                    pass
        if check_roomnumber==0:
            roomtype.append('')
            location_list.append(location)
            hotel_name_list.append(hotel_name)
            haveroom.append('X')
            price.append('')
            alldate.append(start_date) 
            breakfast.append('')
        driver.quit()
        
if __name__ == "__main__":
    #location = input('請輸入縣市: ') #台北 'JR東日本大飯店 台北'
    #hotel_name = input('請輸入旅館名稱:  （請輸入全名）')
    start_date = datetime.now().date()
    period=1
    end_date = start_date + timedelta(days=period)
    hotel_info=pd.read_excel('hotel_name_location.xlsx')
    location_list=[]
    hotel_name_list=[]
    roomtype=[]
    price=[]
    breakfast=[]
    alldate=[]
    haveroom=[]
    # 定义每两天为一组
    days_per_group = 2
    for i in range(len(hotel_info)):
        start_date_obj = start_date
        end_date_obj = end_date
        while start_date_obj <end_date_obj:
            # 计算下一组的结束日期
            next_end_date_obj = start_date_obj + timedelta(days=days_per_group - 1)
            # 格式化日期字符串
            formatted_start_date = start_date_obj.strftime("%Y/%m/%d")
            formatted_end_date = next_end_date_obj.strftime("%Y/%m/%d")
            # 输出日期范围
            scrape_hotel_info(hotel_info['location'][i], hotel_info['name'][i], formatted_start_date, formatted_end_date)
            print(formatted_start_date,'-',formatted_end_date)
            # 更新起始日期到下一组的开始日期
            start_date_obj = next_end_date_obj 
            print(len(price))
            print(len(alldate))
            print(len(breakfast))
            print(len(roomtype))
        if  i==len(hotel_info)-1 or hotel_info['location'][i]!=hotel_info['location'][i+1] :
            df=pd.DataFrame()
            df['地區']=location_list
            df['旅館名稱']=hotel_name_list
            df['日期']=alldate
            df['房型']=roomtype
            df['房型1']=''
            df['房型2']=''
            df['房型3']=''
            df['房型4']=''
            df['房型5']=''
            df['房價']=price
            df['有無含早餐']=breakfast
            df['房價變動']=''
            df['有無房']=haveroom
            filename = str(hotel_info['location'][i]) + '旅館房價調查' + str(start_date) + '.xls'
            df.to_excel(filename, sheet_name='sheet1', index=0, engine='openpyxl')
            location_list=[]
            hotel_name_list=[]
            roomtype=[]
            price=[]
            breakfast=[]
            alldate=[]
    
    
    
    
    
