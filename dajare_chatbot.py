#21K0134 日置遼平 プロジェクト チャットボット製作
''' メモ
ダジャレを返すチャットボット
あらかじめ自分でダジャレのリストを作るようにする。
txtファイルからの読み込みでリストを作るようにすれば、
ユーザから入力されたダジャレを保存することもできる？
できる限り漢字やカタカナで入力させる
１．ユーザから単語（修飾語付き？）の入力
２．その単語がダジャレリストの文の中に含まれていればそれを出力候補にする(名詞限定？)
　　形態素解析？
　　まず入力された単語のままリストを探索
    単語が４つ以上の形態素で構成されていない前提
　　なかったら、入力の単語を分割して探索
    それでもないなら、入力もリストもカタカナに変換してそのまま探索
    ただし入力の漢字は変換しない
３．出力候補からランダムに出力
'''
from tkinter import *
from pykakasi import kakasi # 全てをカタカナに変換
import jaconv # 平仮名だけをカタカナに変換
import numpy as np
import random

botName = "おやじ"

kks = kakasi()
root = Tk()

root.geometry("600x450")
root.title("ダジャレボット")
frame = Frame(root)

sc = Scrollbar(frame)
sc.pack(side=RIGHT, fill=Y)

msgs = Listbox(frame, width=80, height=20, yscrollcommand=sc.set)
msgs.pack(side=LEFT, fill=BOTH, pady=10)

frame.pack()
mode = 1 # output mode

def eng2kana(dajare): # 英語をカタカナに変換
    word = ""
    for i in range(len(dajare)):
        if dajare[i] == "A":
            word += "エー"
        elif dajare[i] == "B":
            word += "ビー"
        elif dajare[i] == "C":
            word += "シー"
        elif dajare[i] == "D":
            word += "ディー"
        elif dajare[i] == "E":
            word += "イー"
        elif dajare[i] == "F":
            word += "エフ"
        elif dajare[i] == "G":
            word += "ジー"
        elif dajare[i] == "H":
            word += "エイチ"
        elif dajare[i] == "I":
            word += "アイ"
        elif dajare[i] == "J":
            word += "ジェー"
        elif dajare[i] == "K":
            word += "ケー"
        elif dajare[i] == "L":
            word += "エル"
        elif dajare[i] == "M":
            word += "エム"
        elif dajare[i] == "N":
            word += "エヌ"
        elif dajare[i] == "O":
            word += "オー"
        elif dajare[i] == "P":
            word += "ピー"
        elif dajare[i] == "Q":
            word += "キュー"
        elif dajare[i] == "R":
            word += "アール"
        elif dajare[i] == "S":
            word += "エス"
        elif dajare[i] == "T":
            word += "ティー"
        elif dajare[i] == "U":
            word += "ユー"
        elif dajare[i] == "V":
            word += "ヴイ"
        elif dajare[i] == "W":
            word += "ダブリュー"
        elif dajare[i] == "X":
            word += "エックス"
        elif dajare[i] == "Y":
            word += "ワイ"
        elif dajare[i] == "Z":
            word += "ゼット"
        else:
            word += dajare[i]
    return word

def isInclude(a, b): # aにbが含まれるかどうかを返す
    for i in range(len(a)-len(b)+1):
        word = ""
        for j in range(len(b)):
            word += a[i+j]
        if word == b:
            return True
    return False

# 文として成り立っているかを確認できるようになるとより良くなる？
def isDajare(a, b): # aがbを使ったダジャレかどうかを返す
    key = sen2read(b) # 読みに変換
    dajare = sen2read(a)
    #print(dajare)
    cnt = 0 # keyが文章に２回以上登場したらダジャレとする
    skip = 0 # 一致したところのダジャレは重複回避のためスキップ
    for i in range(len(dajare)): # ダジャレ1文字1文字に対して
        if skip == 0:
            #print(i)
            cutKey = []
            for j in range(len(key)):
                cutKey.append(key[j]) # bを１文字ずつに分けてリストに入れる
            #print(cutKey)
            index = 0 # 順序管理
            forRange = len(key) + int(len(key)/2) # key+keyの半分 の区間(緩め)
            if i + forRange > len(dajare):
                forRange = len(dajare) - i # rangeの上限はダジャレの長さ
            missCnt = 0 # どのくらい連続で一致しなかったか
            for j in range(i, i+forRange): # まだ読んでない一定の区間で
                missCnt += 1
                for k in range(len(cutKey)):
                    if (dajare[j] == cutKey[k] # aとbの文字が一致して
                        and k >= index): # 順番が適切なら(リストの左から順に一致するはず)
                        cutKey.pop(k) # 一致した文字を消す
                        #print(cutKey)
                        index = k # 消した文字の右側しか消せない
                        missCnt = 0
                        break
            if (len(key) - len(cutKey) > 1 # １文字一致はダメ
                and len(key) - len(cutKey) >= int(len(key)/2) + 1): # 半分よりも多く一致したら(緩め)
                cnt += 1
                skip = len(key) + int(len(key)/2) - missCnt - 1 # 読んだところは基本skipするが
                continue # missしたところはskipしない
        if skip > 0:
            skip = skip - 1
    if cnt >= 2:
        #print(cnt)
        return True
    else:
        return False

def outputRoop(word):
    option = []
    for dajare in dajareList: # 入力された単語のままリストを探索-----------
        if (isInclude(dajare, word) # ダジャレに含まれているか確認
            and isDajare(dajare, word)): # それがダジャレなのか確認
            option.append(dajare)
    if len(option) != 0:
        return option[random.randint(0, len(option) - 1)] # 出力候補からランダムに出力
    else: # 入力された単語を読みに変換して探索（漢字は変換しない）---------------------
        for dajare in dajareList:
            if (isInclude(dajare, jaconv.hira2kata(word))
                and isDajare(dajare, word)): # 平仮名はカタカナに変換
                option.append(dajare)
            elif (isInclude(dajare, jaconv.kata2hira(word))
                and isDajare(dajare, word)): # カタカナは平仮名に変換
                option.append(dajare)
        if len(option) != 0:
            return option[random.randint(0, len(option) - 1)] # 出力候補からランダムに出力
        else: # ダジャレも単語も読みに変換して探索（"入力"の漢字は変換しない）-------------------------
            for dajare in dajareList:
                if (isInclude(sen2read(dajare), jaconv.hira2kata(word))
                    and isDajare(dajare, word)):
                    option.append(dajare)
            if len(option) != 0:
                return option[random.randint(0, len(option) - 1)]
            else: # 見つからなかった場合-----------------------------------
                return "別の単語にして"

def inputRoop(word):
    if len(word) < 3:
        return "それダジャレじゃないでしょ"
    cnt = 0
    for i in range(len(word)):
        if i > 0 and word[i-1] == word[i]: # 同じ文字が続いたら
            cnt += 1
        else:
            cnt = 0
        if cnt >= 3: # ４回同じ文字が続いたら
            return "それダジャレじゃないでしょ"
    for dajare in dajareList:
        if word == dajare or sen2read(word) == sen2read(dajare):
            return "それ知ってる"
    tmpword = word
    word = sen2read(word) # 漢字が含まれているとkeyの文字数が合わなくなるため
    for i in range(2, int(len(word)/2)+2): # ダジャレの半分の長さまで繰り返す
        for j in range(len(word)-i+1): # keyを全パターン確認する
            sumWord = ""
            for k in range(i): # keyを作る、最初は２文字、次は３文字、、、
                sumWord += word[j+k]
            print(sumWord) # 最後に表示されているのがkeyとなっている
            # 形態素解析を使うとkeyが正確なものになるが、全探索するこのプログラムだと
            # keyがどのくらいの大きさまで認められるのか調べることができる
            if isDajare(word, sumWord):
                dajareList.append(tmpword) # 変換前のダジャレを追加する
                return "おもしろーい"
    return "それダジャレじゃないでしょ"
        
def dajareLoad():
    with open(r"dajare.txt") as file: # ファイル読み込み
        file.readline().rstrip("\n")
        file.readline().rstrip("\n") # 1,2行目は読み込まない
        for line in file:
            line = line.rstrip("\n")
            print(eng2kana(line)) # ダジャレの出力をしたいなら表示
            dajareList.append(eng2kana(line))

def sen2read(dajare): # 文章を読み(カタカナ)に変換
    word = ""
    for converted_word in kks.convert(dajare):
        word += converted_word['kana']
    return word
    
def dajareSort(): # 50音順にソート
    global dajareList
    tmpList = []
    for dajare in dajareList:
        tmpList.append(sen2read(dajare))
    tmpList = np.sort(tmpList, kind='quick sort') # ダジャレを50音順にソート
    sortedList = []
    for dajare1 in tmpList: # 全ての読みのダジャレについて
        for dajare2 in dajareList: # 全ての元のダジャレについて
            if dajare1 == sen2read(dajare2): # 読みで同じか確認
                sortedList.append(dajare2)
    if not len(sortedList) == len(dajareList):
        print("似たようなダジャレが登録されています")
        print("sortを中止します")
        return
    for i in range(len(sortedList)): # ソートされたリストをコピー
        dajareList[i] = sortedList[i]
        
def dajareAppend():
    global dajareList
    print("読み込み中")
    dajareSort()
    print("終了")
    with open(r"dajare.txt", mode="w") as file: # ファイル書き込み
        file.write("1行に1つダジャレを書く（解析のためにできる限り漢字やカタカナを使う）\n")
        file.write("↓ ※https://gokkoland.com/articles/271 参考\n")
        for dajare in dajareList:
            file.write(dajare)
            file.write("\n")

# ----tkinterの関数↓----------------------
def modeChange():
    global mode
    if mode == 1:
        mode = 2
        msgs.insert(END, botName+"：ダジャレ教えて")
    elif mode == 2:
        mode = 1
        dajareAppend()
        msgs.insert(END, botName+"：何か単語言って")

def bot_response(word):
    if mode == 1:
        return outputRoop(word)
    elif mode == 2:
        return inputRoop(word)

def ask_from_bot():
    query = textF.get()
    answer_from_bot = bot_response(query)
    msgs.insert(END, "you：" + query)
    msgs.insert(END, botName+"：" + str(answer_from_bot))
    textF.delete(0, END)
    msgs.yview(END)

def enter_function(event):
    ask_from_bot()

textF = Entry(root, font=("Courier", 10),width=50)
textF.pack()

btn = Button(root, text="交代",
             font=("Courier", 10),bg='white', command=modeChange)
btn.pack()

root.bind('<Return>', enter_function)

msgs.insert(END, "※単語の区切りが分かるように、適度に漢字やカタカナを用いてください。")
msgs.insert(END, botName+"：何か単語言って")

dajareList = []
dajareLoad()
