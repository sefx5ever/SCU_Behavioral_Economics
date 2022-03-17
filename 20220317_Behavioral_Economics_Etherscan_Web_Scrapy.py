#!/usr/bin/env python
# coding: utf-8

# ## STEP 1：套件匯入

# In[ ]:


import requests # API 請求
import pandas as pd # Excel 輸出
from lxml import etree # HTML 定位路徑語言
from time import sleep # 爬蟲休息
from datetime import date # 檔案匯出名稱格式


# ## STEP 2：爬取 Etherscan Transaction Data

# In[ ]:


STOP = False 
# While 暫停條件，用於爬取頁面完畢，暫停爬蟲使用

PAGE_NUM = 1 
# 爬取內容之起始頁面

ADDRESS = "0x99dc81489b75268baad66e2eb2301371d1ce235a" 
# 合約地址 / 錢包地址

base_link = "https://etherscan.io/txs?a={}&p={}"
# 請求 API 

headers = {"user-agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}
# API 請求攜帶 Headers 內容

data_to_df = []
# 用於爬取內容儲存空間

# 本次實作範例地址
## 錢包地址 0x99dc81489b75268baad66e2eb2301371d1ce235a
## 合約地址 0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb


# #### 爬取 單一用戶 or 智能合約 所有交易記錄

# In[ ]:


# 由於不清楚爬取地址總頁數，因此採用 while 迴圈進行爬蟲
while(not STOP): # 當爬取頁面已達到需求，則出發 Boolean 轉換暫停迴圈
    res = requests.get(base_link.format(ADDRESS,PAGE_NUM),headers=headers)
    # 透過 Get 攜帶 Headers 內容進行請求，可透過切換 PAGE_NUM 爬取其他頁面
    raw_data = etree.HTML(res.text)
    # 初始化路徑語言套件
    rows_loc = "//table/tbody/tr"
    # 所需爬取資料之路徑
    total_rows = len(raw_data.xpath(rows_loc))+1
    # 本次爬蟲總頁數
    total_page = raw_data.xpath("(//span[@class='page-link text-nowrap'])[1]/strong[2]")[0].text
    # 顯示目前的下載進度
    print(f"【Etherscan Crawling】Downloading... {PAGE_NUM}/{total_page}")
    # 藉由判斷總行數進行迴圈，爬取所需內容
    for num in range(1,total_rows):
        try:
            temp = {
                'txn' : raw_data.xpath(rows_loc + f"[{num}]/td[2]//a")[0].text,
                'method' : raw_data.xpath(rows_loc + f"[{num}]/td[3]/span")[0].text,
                'block' : raw_data.xpath(rows_loc + f"[{num}]/td[4]/a")[0].text,
                'age' : raw_data.xpath(rows_loc + f"[{num}]/td[6]/span")[0].attrib['title'],
                'value' : raw_data.xpath(rows_loc + f"[{num}]/td[10]")[0].text,
                'fee' : raw_data.xpath(rows_loc + f"[{num}]/td[11]/span")[0].text
            }
            
            try:
                temp_from = raw_data.xpath(rows_loc + f"[{num}]/td[7]/a")[0].text
            except IndexError:
                temp_from = raw_data.xpath(rows_loc + f"[{num}]/td[7]/span")[0].text
            except Exception as err:
                print(f"--->【Row：{num}】temp_from is {err}.")
            finally:
                temp['from'] = temp_from

            
            
            try:
                if raw_data.xpath(rows_loc + f"[{num}]/td[9]/span/span"):
                    temp_to = raw_data.xpath(rows_loc + f"[{num}]/td[9]/span/span")[-1].attrib['title']
                elif raw_data.xpath(rows_loc + f"[{num}]/td[9]/span/span/a/text()"):
                    temp_to = raw_data.xpath(rows_loc + f"[{num}]/td[9]/span/span/text()")[-1]
                elif raw_data.xpath(rows_loc + f"[{num}]/td[9]/span/a/text()"):
                    temp_to = raw_data.xpath(rows_loc + f"[{num}]/td[9]/span/a/text()")[-1]
                elif raw_data.xpath(rows_loc + f"[{num}]/td[9]/a/text()"):
                    temp_to = raw_data.xpath(rows_loc + f"[{num}]/td[9]/a/text()")[-1]
            except Exception as err:
                print(f"--->【Row：{num}】temp_to is {err}.")
            finally:
                temp['to'] = temp_to
                           
        except Exception as err:
            print(f"---->【Row：{num}】{err}")
        
        data_to_df.append(temp)
    # 若當前頁數大於或等於本次爬蟲總頁數時，開啟迴圈終止條件
    if PAGE_NUM >= int(total_page):
        STOP = True
    # 每次迴圈處理完後，頁數 +1
    PAGE_NUM+=1
    # 休息 1 秒，以免被 Etherscan 判斷為程式爬蟲
    sleep(1)
        
# ethblower.eth 
# https://opensea.io/assets/0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85/105638605602537123420675670083706176451217545169624515749079534262618711227914


# ## STEP 3：匯出檔案

# In[ ]:


today = date.today()
current_date = today.strftime("%Y_%m_%d")

columns = ['txn','method','block','age','value','fee','from','to']
df = pd.DataFrame(data_to_df,columns=columns)

file_name = f"{current_date}_Etherscan_Data_{ADDRESS[-5:]}.csv"
df.to_csv(file_name,encoding='utf-8')

print(f'Export file name: {file_name}, Data {df.shape}')


# In[ ]:




