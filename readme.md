# Discord Bot - 巴哈姆特動漫瘋更新通知

## 功能
- 從 [巴哈姆特動畫瘋](https://ani.gamer.com.tw/) 獲取最新的動漫更新資訊
- 訂閱指定動漫，當有新集數時收到通知
- 查看目前所有更新中的動漫列表
- 管理訂閱（訂閱/取消訂閱所有）
- 支援斜線指令
- 除了新增到伺服器外也可以新增應用程式, 用私人對話的方式使用機器人

## 需求條件
部屬機器人前，準備以下工具:
- Python 3.11.9
- Discord 機器人 Token (設置為環境變數 `BOT_TOKEN`)
- 你的Discord ID (設置為環境變數`BOT_AUTHOR_ID`)

## 安裝與部署
1. 下載此存儲庫：
   ```sh
   git clone https://github.com/Alone0506/DiscordBahamutAnimeSubBot.git
   ```
2. 安裝所需套件：
   ```sh
   pip install -r requirements.txt
   ```
3. 設置環境變數：
   
    windows: 環境變數 -> 系統變數 -> 新增
    ```
    BOT_TOKEN = 你的機器人Token
    BOT_AUTHOR_ID = 你的Discord ID
    ```
4. 啟動機器人：
   ```sh
   python bot.py
   ```

## 部屬到雲端
此機器人目前已上傳到 Docker Hub 並在 Synology Nas 上運作, 操作方式見下列文章:
1. 打包成 image 並上傳到 Docker Hub (還在寫)
2. 利用 Synology 的 Container Manager 下載 Docker Hub 的 image 後部屬 (也還在寫)

## 指令列表
| 指令                    | 功能                                      |
|-------------------------|-----------------------------------------|
| `/anime_help`         | 查看指令使用說明                         |
| `/anime_list`         | 查看所有更新中的動漫                     |
| `/anime_sub_list`     | 查看你的訂閱動漫列表                     |
| `/anime operation:<Subscribe/Unsubscribe> anime_name:<name>` | 訂閱或取消訂閱指定動漫 |
| `/anime_unsub_all`    | 取消訂閱所有動漫                         |
