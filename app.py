# -*- coding: utf-8 -*-
#new1227
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage
print("line東西完成yaaaaaaaaaaaaaaaaaaaaaaaaa")

from pymongo import MongoClient
from pymongo.server_api import ServerApi
import google.generativeai as genai

print("非內建import 完成yaaaaaaaaaaaaaaaaaaaaaaaaa")

##################################

import psutil

def check_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    ram_usage_mb = mem_info.rss / (1024 ** 2)  # 将字节转换为MB
    print(f"Current RAM usage: {ram_usage_mb:.2f} MB")
    return ram_usage_mb
#################################


#======python的函數庫==========
import tempfile
import datetime
import time
import traceback
import numpy as np
import pandas as pd
import os
import requests
#======python的函數庫==========
print("import 完成yaaaaaaaaaaaaaaaaaaaaaaaaa")

uri = "mongodb+srv://h34106054:Alice0813@test0819.46rp0.mongodb.net/?retryWrites=true&w=majority&appName=test0819"
client = MongoClient(uri, server_api=ServerApi('1'))
dbName = "linebot"
collectionName = "0819-small"
collection = client[dbName][collectionName]
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

app = Flask(__name__)
#static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
######################################################################
#google and llm setting
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

############################################################################
#huggingface api
API_URL = "https://api-inference.huggingface.co/models/BAAI/bge-small-zh-v1.5"
HUGGING_FACE_API = os.getenv("HUGGING_FACE_API")
headers = {"Authorization": f"Bearer {HUGGING_FACE_API}"}
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

################################################################################

print("感覺可以開始接收回應嘞yaaaaaaaaaaaaaaaaaaaaaaaaa")
check_memory_usage()

def GPT_response(question):
    print("已接收到訊息yaaaaaaaaaaaaaaaaaaaaaaaaa")
    
    #############
    
    texts = [question]
    output = query({"inputs": texts,})
    #print("API Response:", output)
    embedding_vector = output[0][0][0]
    print(embedding_vector)
    check_memory_usage()
        
    
    print("嵌入完yaaaaaaaaaaaaaaaaaaaaaaaaa")
    check_memory_usage()
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",  # 替换为您的索引名称
                "path": "embedding",       # 替换为您的字段名称
                "queryVector": embedding_vector,  # 替换为您的查询向量
                "numCandidates": 1,  # 设置候选项数量
                "limit": 1  # 设置结果限制
            }}]
    print("pipeline完yaaaaaaaaaaaaaaaaaaaaaaaaa")
    check_memory_usage()
    try:
        results = list(collection.aggregate(pipeline))
        print("collection完yaaaaaaaaaaaaaaaaaaaaaaaaa")
        check_memory_usage()
    except Exception as e:
        print(f"An error occurred: {e}")
        ErrorMessage="我不太清楚，An error occurred."
        return ErrorMessage
    print("有收到訊息並查詢完yaaaaaaaaaaaaaaaaaaaaaaaaa")
    
    # 提取 detail 部分
    for doc in results:
        text = doc.get('text', '')
        # 找到 detail 的起始位置
        start_index = text.find('detail: ')
        if start_index != -1:
            # 提取 detail 部分
            detail = text[start_index + len('detail: '):]
            # 找到详细信息的结束位置（通常是下一行的开始位置）
            end_index = detail.find('\n')
            if end_index != -1:
                detail = detail[:end_index].strip()
            #print(f"Detail: {detail}")
        else:
            print("Detail not found")
    print("提取提示細節完成yaaaaaaaaaaaaaaaaaaaaaaaaa")
        

    ##############
    prompt = f"查詢: {question}\n回答提示: {detail}\n你是協助回答問題的助手，請根據以上信息使用繁體中文\"活潑親切\"的回答。"
    print("準備丟入LLMyaaaaaaaaaaaaaaaaaaaaaaaaa")
    response = model.generate_content(prompt)
    
    #return response.text
    check_memory_usage()
    print("要印出了yaaaaaaaaaaaaaaaaaaaaaaaaa")
    print(prompt)
    #print(response)
    return response.text


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    print("收到消息")
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("找到你嘞")
        abort(400)
    return 'OK'

processed_events = set()
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.id in processed_events: 
        print("出事了阿北")
        return 
    processed_events.add(event.message.id)
    msg = event.message.text
    user_id = event.source.user_id   # 获取用户的 user_id
    
    try:
        GPT_answer = GPT_response(msg)
        print(GPT_answer)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
    except:
        print(traceback.format_exc())
        #line_bot_api.reply_message(event.reply_token, TextSendMessage('系統正在忙碌幫您找資料中，請耐心等待喔'))
        #print(traceback.format_exc())
        
        #GPT_answer = None  
        #del msg  
        #line_bot_api.reply_message(event.reply_token, TextSendMessage('已啟動 請重新輸入'))
        line_bot_api.push_message(user_id, TextSendMessage(text="系统忙碌，请稍后再试。"))
                

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
