# -*- coding: utf-8 -*-
#new1227


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
import psutil
#======python的函數庫==========

def print_memory_usage(message):
    """打印当前内存使用量"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    print(f"{message} - RSS: {mem_info.rss / (1024 ** 2):.2f} MB, VMS: {mem_info.vms / (1024 ** 2):.2f} MB")

# OPENAI API Key初始化設定
print("開始跑了")
print_memory_usage("開始跑了")
#openai.api_key = os.getenv('GEMINI_API_KEY')
GOOGLE_API_KEY = "AIzaSyDHdddKwG41Ig3p5bVfIUQ2w-X6bOZI3gk"  #input API key
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
#embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-zh-v1.5")
print("嵌入模型下載中")
print_memory_usage("嵌入模型下載中")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")
csv_file_path = 'output1.csv'
print("讀文件儲存於變量")
print_memory_usage("讀文件儲存於變量")
data = pd.read_csv(csv_file_path) #讀文件儲存於變量
print("讀完文件")
print_memory_usage("讀完文件")
documents = []
skipNUM = 0
print("1")
for index, row in data.iterrows():
    if pd.isna(row['title']): #跳過title空的行
        print(f"Skipping row {index-skipNUM} due to empty 'title' field")
        skipNUM += 1
        continue
    if pd.notna(row['title']):
        content = (f"title: {row['title']}\n" f"detail: {row['detail']}")

        #print(f"Content for row {index-skipNUM}: {content}")
        #改!
        documents.append(Document(id=str(index-skipNUM),text=content))# 索引作为ID       # 將detail的東西存入
    else:
        print(f"Skipping row {index-skipNUM} due to missing data in other fields")

if not documents:
    raise ValueError("No valid documents found. Ensure your CSV file has content.")

index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
print("index轉換完成")
def GPT_response(text):
    # 改接收回應
    
    print("2")
    Settings.llm = Gemini()
    retriever = VectorIndexRetriever(index=index,similarity_top_k=3,)
    response_synthesizer = get_response_synthesizer(response_mode="tree_summarize", llm=Gemini())
    query_engine = RetrieverQueryEngine(retriever=retriever,response_synthesizer=response_synthesizer)
    response=query_engine.query(text)
    #############

    #response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    print("3")
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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
