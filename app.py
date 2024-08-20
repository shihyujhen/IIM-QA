# -*- coding: utf-8 -*-
#new1227
from pymongo import MongoClient
from pymongo.server_api import ServerApi

import google.generativeai as genai
from langchain.embeddings.huggingface import HuggingFaceEmbeddings


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
embedding_vector  = embed_model.embed_query("碩士入學申請?")

print("embedding_vector 完成yaaaaaaaaaaaaaaaaaaaaaaaaa")



def GPT_response(text):
    # 改接收回應
    
    #print("2")
    #Settings.llm = Gemini()
    #retriever = VectorIndexRetriever(index=index,similarity_top_k=3,)
    #response_synthesizer = get_response_synthesizer(response_mode="tree_summarize", llm=Gemini())
    #query_engine = RetrieverQueryEngine(retriever=retriever,response_synthesizer=response_synthesizer)
    #response=query_engine.query(text)
    #############

    #response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=text, temperature=0.5, max_tokens=500)
    #print(response)
    # 重組回應
    #print("3")
    #answer = response['choices'][0]['text'].replace('。','')
    return text


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
