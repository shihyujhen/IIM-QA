# -*- coding: utf-8 -*-
#new1227
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
print("line東西完成yaaaaaaaaaaaaaaaaaaaaaaaaa")

from pymongo import MongoClient
from pymongo.server_api import ServerApi
import google.generativeai as genai
#from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
print("非內建import 完成yaaaaaaaaaaaaaaaaaaaaaaaaa")


#======python的函數庫==========
import tempfile
import datetime
import time
import traceback

import numpy as np
import pandas as pd
import os
#======python的函數庫==========
print("import 完成yaaaaaaaaaaaaaaaaaaaaaaaaa")

uri = "mongodb+srv://h34106054:Alice0813@test0819.46rp0.mongodb.net/?retryWrites=true&w=majority&appName=test0819"
client = MongoClient(uri, server_api=ServerApi('1'))
dbName = "linebot"
collectionName = "0819"
collection = client[dbName][collectionName]
embed_model = HuggingFaceEmbeddings(model_name="BAAI/bge-large-zh-v1.5")
print("embedding_vector 完成yaaaaaaaaaaaaaaaaaaaaaaaaa")

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
######################################################################
#google and llm setting

GOOGLE_API_KEY="AIzaSyDUuA4pHGNTWyUWp2xK63ifGwUgv0x43ho"
genai.configure(api_key = GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')


print("感覺可以開始接收回應嘞yaaaaaaaaaaaaaaaaaaaaaaaaa")

def GPT_response(query):
    
    #############
    embedding_vector  = embed_model.embed_query(query)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",  # 替换为您的索引名称
                "path": "embedding",       # 替换为您的字段名称
                "queryVector": embedding_vector,  # 替换为您的查询向量
                "numCandidates": 100,  # 设置候选项数量
                "limit": 1  # 设置结果限制
            }}]
    
    try:
        results = list(collection.aggregate(pipeline))
    except Exception as e:
        print(f"An error occurred: {e}")
        ErrorMessage="我不太清楚，An error occurred."
        return ErrorMessage
    
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
    
        

    ##############
    prompt = f"查詢: {query}\n回答提示: {detail}\n請根據以上信息使用繁體中文回答。"
    response = model.generate_content(prompt)
    return response.text


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    try:
        GPT_answer = GPT_response(msg)
        print(GPT_answer)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
    except:
        print(traceback.format_exc())
        line_bot_api.reply_message(event.reply_token, TextSendMessage('你所使用的OPENAI API key額度可能已經超過，請於後台Log內確認錯誤訊息'))


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
