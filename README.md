# IIM-QA
一、簡介: 透過加入Line好友，使用者得以透過此頁面詢問關於成功大學工業與資訊管理學系相關資訊。

二、開發背景: 
大型語言的發展越來越完善，除了可以回答已有的知識，也能透過一些特定的提示詞搜尋網路上的資料以回應使用者。然而，在我使用此技術時，卻發現大型語言的網路搜尋技術並沒有那麼好，在問題較小眾的情況下，多數回應皆有幻覺的情況。例如: 當我詢問現今成大校長，語言模型可以給我正確的回應，然而當我詢問現今成大工業與資訊管理學系系主任時，ChatGPT 4.0的回應卻完全錯誤。此問題是大型語言較無法解決的，因為網路資訊多且雜，語言模型未必能正確提取到使用者想要知道的回饋。另外，因為開發時間正處於大學部新生欲入學的階段，但系上頁面許多資訊並沒有統整的非常好，導致新生有時無法找到正確的資訊(如: 選課規定與時程等等)。在這樣的背景下，我便想到了RAG(檢索增強生成)技術，並透過結合Line頁面創造使用者友善的環境，讓使用者僅需透過聊天室輸入問題，便可容易地獲取正確回饋。

三、技術簡介: 
RAG技術為在大型語言模型發展越趨於成熟的現在最熱門的應用之一，開發者透過RAG技術可以將特定資料先存放於資料庫，在使用者輸入問題時，先搜尋資料庫內容檢索是否有符合的答案，再將問題與答案作為提示詞輸入大型語言模型，模型會將集合的答案輸出給使用者。對於企業來說，在許多機密資料的情況下，RAG技術可以在不將這些資料洩漏的情況下打造企業專屬的聊天機器人；對於一般人來說，也能透過大型語言模型打造特定的回應機器人。
此專案以成功大學工業與資訊管理學系的系網作為資料來源，將資料爬蟲且統整後放入MongoDB資料庫管理系統，並利用Render部屬網站結合Github主程式與MongoDB。使用者輸入問題時會透過嵌入模型轉為向量，再放入MongoDB進行向量搜索。檢索完成的答案群將與問題一起放入gemini-pro模型進行整理，再將回應輸出給使用者。
