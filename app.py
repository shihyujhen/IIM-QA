# -*- coding: utf-8 -*-
"""app

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16b7JniidU-N4rMDkIg3tGSHXuPrXSshG
"""

from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, Document
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import Settings
#======python的函數庫==========
import tempfile, os
import datetime
import time
import traceback
import pandas as pd
import pickle
import shutil
import requests
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
#openai.api_key = os.getenv('GEMINI_API_KEY')
GOOGLE_API_KEY = "AIzaSyDHdddKwG41Ig3p5bVfIUQ2w-X6bOZI3gk"  #input API key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-zh-v1.5")
#csv_file_path = 'output1.csv'
#data = pd.read_csv(csv_file_path) #讀文件儲存於變量


def GPT_response(text):
    # 改接收回應
   ##################
   # Google Drive 文件 ID
    file_id = '1XIaDpOLEw03KgFSjYPMG_tbEcs7AKunL'
    index_url = f'https://drive.google.com/uc?export=download&id={file_id}'
    local_index_path = 'vector_store_index.pkl'

    # 檢查本地文件是否存在
    if not os.path.isfile(local_index_path):
        print("Index file not found. Downloading...")
        # 下載文件
        response = requests.get(index_url)
        if response.status_code == 200:
            with open(local_index_path, 'wb') as f:
                f.write(response.content)
        else:
            print("Failed to download the file.")
    else:
        print("Index file already exists. Skipping download.")




    # 設定 index.pkl 的路徑
    #index_path = '/content/drive/MyDrive/vector_store_index.pkl'

    # 從 Google Drive 讀取 index.pkl 文件
    with open(local_index_path, 'rb') as f:
        index = pickle.load(f)

        #print(index)
        print("以讀取")


    Settings.llm = Gemini()
    retriever = VectorIndexRetriever(index=index,similarity_top_k=3,)
    response_synthesizer = get_response_synthesizer(response_mode="tree_summarize", llm=Gemini())
    query_engine = RetrieverQueryEngine(retriever=retriever,response_synthesizer=response_synthesizer)
    response=query_engine.query(text)
    #############

    #response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。','')
    return answer


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


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
