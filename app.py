from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import time
import traceback
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


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
    questions_answers = {
        '台數': {
            "莊家": "1台",
            "莊連一": "3台",
            "莊連二": "5台",
            "莊連三": "7台",
            "莊連四": "9台",
            "莊連五": "2N+1，N是連莊數，答案是11台，連六以後依此類推",
            "三元牌": "1台",
            "四風牌": "1台",
            "三暗刻": "2台",
            "四暗刻": "5台",
            "五暗刻": "8台",
            "碰碰胡": "4台",
            "混一色": "4台",
            "清一色": "8台",
            "小三元": "4台",
            "大三元": "8台",
            "小四喜": "8台",
            "大四喜": "16台",
            "七搶一": "8台",
            "八仙過海": "8台",
            "平胡": "2台",
            "單吊": "1台",
            "中洞": "1台",
            "邊張": "1台",
            "全求人": "2台",
            "門清": "1台",
            "門清一摸三": "3台",
            "MIGI": "8台",
            "門風台": "1台",
            "圈風台": "1台",
            "花台": "1台",
            "花槓": "2台",
            "海底撈月": "1台",
            "槓上開花": "1台",
            "搶槓胡": "1台",
        },
         '定義': {
            "台麻": "手牌16張。",
            "碰牌": "三家丟出的牌可與手牌中的對子而形成刻子，即可碰牌；若兩家同時碰牌與吃牌，則以碰牌者為優先。",
            "吃牌": "只有上家丟出的牌可與手牌而形成順子，即可吃牌。",
            "莊家": "做莊者，無論胡牌或放炮(打出的牌被別人胡)都多算一台。",
            "莊連一": "連續做莊者，無論胡牌或放炮(打出的牌被別人胡)都多算三台。",
            "莊連二": "連續做莊者，無論胡牌或放炮(打出的牌被別人胡)都多算五台。",
            "莊連三": "連續做莊者，無論胡牌或放炮(打出的牌被別人胡)都多算七台。",
            "莊連四": "連續做莊者，無論胡牌或放炮(打出的牌被別人胡)都多算九台。",
            "莊連五": "連續做莊者，無論胡牌或放炮(打出的牌被別人胡)都多算三2N+1台，N是連莊數，連六以後依此類推。",
            "對子": "2張相同花色與數字的牌，例如「七筒、七筒」。",
            "刻子": "3張相同花色與數字的牌，例如「六條、六條、六條」。",
            "順子": "3張相同花色且順序接連的牌，例如「一萬、一萬、一萬」。",
            "三元牌": "以任何方式拿到一副中/發/白的刻子。",
            "四風牌": "以任何方式拿到一副東/南/西/北的刻子。",
            "三暗刻": "有3副自己摸到的刻子，不是碰出來的。",
            "四暗刻": "有4副自己摸到的刻子，不是碰出來的。",
            "五暗刻": "有5副自己摸到的刻子，不是碰出來的。",
            "碰碰胡": "全部都是刻子，沒有順子。",
            "混一色": "整副牌由字牌及另外單一花色組成，例如萬/筒/條。",
            "清一色": "整副牌由同一花色組成，例如萬/筒/條。",
            "字一色": "整副牌由字牌組成，例如四風牌/三元牌。",
            "小三元": "胡牌者將中、發、白，組成2組刻子與1組對子。",
            "大三元": "胡牌者將中、發、白，組成3組刻子",
            "小四喜": "胡牌者將東、南、西、北，組成3組刻子，1組對子。",
            "大四喜": "胡牌者將東、南、西、北，組成4組刻子",
            "七搶一": "四人當中有某家摸進7張花牌時，另三家之一牌面前有1張花牌，可以立刻喊胡，而那位拿到1張花的仁兄，要付給7張花牌者一底八台。",
            "八仙過海": "當某家拿到全部8張花牌，可立即喊胡，，三家通賠一底八台。",
            "平胡": "全部都是順子而沒有刻子，未有任何字牌或花牌，且聽牌為雙頭，不能為獨聽或自摸。",
            "單吊": "聽牌只聽一張牌。",
            "中洞": "聽牌只聽一張牌，且為順子中間那張；例如在「一萬、二萬、三萬」中，聽二萬即是中洞。",
            "邊張": "聽牌只聽一張牌，且為順子邊邊那張；例如在「一萬、二萬、三萬」中，聽三萬即是中洞。",
            "全求人": "胡牌時，手牌裡只剩一張單吊牌，其餘全為吃、碰或明槓，且不與單吊重複計台。",
            "門清": "沒有吃也沒有碰，全部牌都是自己摸到的。",
            "門清一摸三": "為門清、自摸加上不求人共三台。",
            "MIGI": "起牌後海底打進八張牌內，且四家沒有碰牌吃牌時的情況下聽牌。",
            "門風台": "以開牌位置開始計算風位，逆時針依次為東、南、西、北。",
            "圈風台": "視本局風圈為何即是該風圈，需有該風牌的刻子。",
            "花台": "以開牌位置開始計算風位，逆時針依次為1花(春/梅)、2花(夏/蘭)、3花(秋/竹)、4花(冬/菊)。",
            "花槓": "花牌湊滿春夏秋冬/梅蘭竹菊。",
            "海底撈月": "海底前最後一張而自摸。",
            "槓上開花": "因家槓、暗槓、摸到花牌而補牌，補牌後又剛好胡牌。",
            "搶槓胡": "當對手加槓時，加槓的那一張牌剛好是胡牌者所要胡的牌，胡牌者可以選擇搶槓胡牌，視為加槓者放槍。",
        }
    }
    
    
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()
    
    if user_id not in user_state:
        user_state[user_id] = None
    
    if msg == '牌型的台數或定義':
        line_bot_api.reply_message(event.reply_token, TextSendMessage("想查詢台數還是定義?"))
    elif msg == '台數':
        user_state[user_id] = '台數'
        line_bot_api.reply_message(event.reply_token, TextSendMessage("請輸入想查詢的牌型台數"))
    elif msg == '定義':
        user_state[user_id] = '定義'
        line_bot_api.reply_message(event.reply_token, TextSendMessage("請輸入想查詢的牌型定義"))
    else:
        current_state = user_state[user_id]
        if current_state and msg in questions_answers[current_state]:
            reply = questions_answers[current_state][msg]
            line_bot_api.reply_message(event.reply_token, TextSendMessage(reply))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage("未找到相關答案，請重新輸入相對應的關鍵字"))

       
         

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
