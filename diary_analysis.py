#CSV読み込み用
import pandas as pd
#正規表現モジュール
import re
#Googleドライブマウント用
from google.colab import drive 
from google.colab import files
#日付関係
from datetime import datetime as dt
from datetime import timedelta
#グラフ関係
from matplotlib import pyplot as plt 
!pip install japanize-matplotlib 
import japanize_matplotlib
#日本語形態分析janome
!pip install janome
from janome.analyzer import Analyzer
from janome.tokenfilter import *
from janome.tokenizer import Tokenizer
from janome.charfilter import *
#WordCloud用
!pip install wordcloud
from wordcloud import WordCloud
!apt-get -y install fonts-ipafont-gothic

import numpy as np

#グラフ保存時のファイル形式
filetype=".svg"
'''
txtデータを読み取って下処理する関数
'''
def importDateAndPreparation():
  drive.mount('/content/drive')
  txt_pass="月に書く日記_2021.01.31 午後 11:07.txt"
  directory="/content/drive/My Drive/others/"
  rawDataTxtInstance = open(directory+txt_pass,'r',encoding="utf-8")
  rawDataTxt=rawDataTxtInstance.read()
  # print(rawDataTxt)
  #テキスト表示まで成功

  #日付取得
  rawDiaryDateList=re.findall(r'\d{4}\.\d{1,2}\.\d{1,2}',rawDataTxt)#正規表現を用いて日記が存在する日付をリスト形式で取得←日記を書いてない日も存在するため、r "正規表現"でrはraw文字のこと(エスケープシーケンスを展開しないそのままの文字列にする。
  print(rawDiaryDateList)
  print("最新は",rawDiaryDateList[-1],"最古は",rawDiaryDateList[0])
  '''

  本当は一つ下の下処理for文で処理したかったが秘伝のソースを変えるのがあまりにも非効率なためここで日付の下処理をする。
  日付内の(2020/01/01)などに含まれる01などはエラー出るので→0をとって1にする処理(datetimeでエラーや生合成整えのための手間を事前に防ぐため)
  →結局不要になった。
  →いや、必要になった。局所的に使うので必要箇所で配列作り直す処理に変更

   '''
  # diaryDateList=[]
  # print("rawDiaryDateList",rawDiaryDateList)
  # print("rawDiaryDateList",len(rawDiaryDateList))
  # for date in rawDiaryDateList:
  #   #日の0除く 02日→2日な感じ
  #   if(str(date[7])=="0"):
  #     date=date[:7]+date[8:]
  #     # print("former",date)
  #     #月の0除く
  #   if(str(date[5])=="0"):
  #     date=date[:5]+date[6:]
  #     # print("latter",date)
  #   diaryDateList.append(date)

  diaryDateList=rawDiaryDateList#やっぱり0がほしい
  '''
  ここまで日付下処理
  '''

  #日記タイトル取得
  diaryTitleList=re.findall(r'\d{4}\.\d{1,2}\.\d{1,2}\s[\u4E00-\u9FFF]{2}\s\d{2}\:\d{2}[\s\S]*?\s-\s',rawDataTxt)
  print("日記タイトル要素数",len(diaryTitleList))

  #日記本文取得
  rawDataTxt+="2000.99.99"#一番最後の日記分の正規表現マッチがどうしてもうまくいかなかったため、ファイルに予め最後の存在を追記しておく、今回は"2000.99.99"を最終行に代入した←他に該当しそうにない文字列かつ正規表現を変えずに使える文字列なので

  diaryContentListRaw=re.findall(r'\s-\s[\s\S]*?\d{4}\.\d{1,2}\.\d{1,2}',rawDataTxt)#*?←最小マッチ [\s\S]で改行含めてにした 

  
  '''
    下処理、同一日統合、結合、改行分割、文字数カウント
  '''
  mozisuuTotal=0
  mozisuuList=[];
  diaryContentListProcessed=[]
  i=0
  n=0
  '''
    下処理
  '''
  for content in diaryContentListRaw:
    
    


    #タイトル下処理
    removeTitleTop=re.sub("\d{4}\.\d{1,2}\.\d{1,2}\s[\u4E00-\u9FFF]{2}\s\d{2}\:\d{2}","",diaryTitleList[i])
    newTitle=removeTitleTop.replace(" - ","")
   
    #本文下処理
    removedTop=content.replace(" - ","")#" - "とそれに付随する改行を取り除く
    removedBottom=re.sub(r"\d{4}\.\d{1,2}\.\d{1,2}","",removedTop)#最後の20**.**.**を取り除く（正規表現使う）
    
    #タイトル＋本文結合
    combinedTitleAndContentRaw=newTitle+removedBottom

    #！！↓↓↓↓↓
    #単語統一処理←コーヒー、珈琲など意味は同じだが文字としては違うものを統一する処理をする→単語の登場頻度などを正しく出力するため、文字起こしの時気になったものをとりあえず（精度がわずかばかり向上する程度だと思われるが）
    combinedTitleAndContent=combinedTitleAndContentRaw.replace("珈琲","コーヒー").replace("わりと","割と").replace("だめ","ダメ").replace("何故","なぜ").replace("ごはん","ご飯").replace("PC","パソコン").replace("pc","パソコン").replace("良い","いい").replace("無い","ない")

    '''
    文字数カウント
    '''
    newContentRemoveKaigyou=combinedTitleAndContent.replace('\n', '')#改行コード取り除き用,
    # print("文字数は",len(newContentRemoveKaigyou),newContentRemoveKaigyou)
    mozisuuList.append(len(newContentRemoveKaigyou))#文字数カウント個別配列
    mozisuuTotal+=len(newContentRemoveKaigyou)#文字数カウント総計

    '''
    同一日の日記が複数あるときに1つに統合
    '''
    if(i!=0):
      if(diaryDateList[i-1]==diaryDateList[i]):
        n+=1
        #統合(すでに改行で配列分けたデータしかないので改行コードつきにデコードする)古い方を上書き削除して新しい方に持っていく
        formerContent=""
        for formerSplited in diaryContentListProcessed[i-1]:
          formerContent+=formerSplited+"\n"
        combinedDuplicatedContent=formerContent+combinedTitleAndContent
        mozisuuList[i]+=mozisuuList[i-1]
        #日付の重複削除すると色々と狂うので重複箇所は代替文字にする、ただし代替文字にするのはformerの方
        diaryContentListProcessed[i-1]="-AtodeTorinozokuYouNoMozi-"
        diaryDateList[i-1]="-AtodeTorinozokuYouNoMozi-"
        mozisuuList[i-1]="-AtodeTorinozokuYouNoMozi-"
        # mozisuuTotal=mozisuuTotal-len(combinedTitleAndContent)#コードのみやすさを考慮してあえてここで整合性とる←何がしたかった？？

      else:
        combinedDuplicatedContent=combinedTitleAndContent
    else:
      combinedDuplicatedContent=combinedTitleAndContent
      






    #改行コードごとにリスト切る処理
    newContent=combinedDuplicatedContent.split()#CSVで改行毎にカラム分ける案の改行毎に切った配列作るコード(reライブラリで正規表現利用)、{1,}としたので複数改行があるか？という情報は残念ながら消えてしまうがやむを得ない、空のカラムができる方が面倒なので

    diaryContentListProcessed.append(newContent)#新しいリストに加工済みデータを入れていく
    i+=1
    # newContent=combinedDuplicatedContent#現状のままま

  #forここまで
  print("重複処理",n,"回")

  #重複かぶりで代替文字にした部分を消す、リスト内包表記で
  diaryContentListProcessed=[s for s in diaryContentListProcessed if s != "-AtodeTorinozokuYouNoMozi-"]
  diaryDateList= [s for s in diaryDateList if s != "-AtodeTorinozokuYouNoMozi-"]
  mozisuuList=[s for s in mozisuuList if s != "-AtodeTorinozokuYouNoMozi-"]



  #文字数平均、合計
  mozisuuAverage=mozisuuTotal/len(mozisuuList)

  print("日記の総文字数は",mozisuuTotal,"字(改行タグ含まない）")#改行タグをcsvカラム式にするなら1行前のカウントで配列展開させることで文字数カウントにあてる
  print("400字詰め原稿用紙",mozisuuTotal/400,"枚分")
  print("日記の平均文字数は",  mozisuuAverage,"字")
  # print(diaryContentListProcessed)
  print("日記の本文を配列に入れることを確認（個人的な内容を含むため配列のprintは控えた）")




  #一応ちゃんと抽出できているか確認(配列の数から)
  # if(len(diaryDateList)==len(diaryContentListProcessed)):
  #   print("整合性OK")
  # else:
  #   print("error")
    
  # rawDataTxtInstance.close()
  # print(diaryDateList)
  # print(diaryContentListProcessed)
  # print(mozisuuList)
  return diaryDateList,diaryContentListProcessed,mozisuuList;


'''
日付、内容、文字数の別個の関数を[[日付,文字数,内容],[日付,文字数,内容]]のリストに変換する関数←同一日付の日記統合の場合に必須
'''
def combineDateAndContetn(diaryDateList,mozisuuList,diaryContentListProcessed):
  #
  #[[日付,内容],[日付,内容]]のリストに変換
  #
  combinedDiary=[]

  for i in range(len(diaryDateList)):
      combinedDiary.append([diaryDateList[i],mozisuuList[i],diaryContentListProcessed[i]])
  return combinedDiary

'''
日付の配列を作る関数(現状だと日記を書いていない日付がリストに存在しないので)
'''
def makeAllDataList(startDate,endDate):

  processedStartDate = dt.strptime(startDate, '%Y.%m.%d')  # 開始日
  processedEndDate = dt.strptime(endDate, '%Y.%m.%d')  # 終了日
  daySum = (processedEndDate - processedStartDate).days + 1#日数う
  AllDataList = []
  for i in range(daySum):
    madeDate=processedStartDate + timedelta(days=i)
    AllDataList.append(str(madeDate.year)+"."+str(madeDate.month)+"."+str(madeDate.day))
  return AllDataList

'''
配列の日記をただの文字に戻す関数
'''
def makeNonListContent(diaryContentListProcessed):
  text=""
  for a in diaryContentListProcessed:
    for b in a:
      text+=b
  return text
'''
自動で日記をつくる関数
'''
def makeAtumaticalNikki(justMozi):
  from sys import argv
  # 形態素分析ライブラリーMeCab と 辞書(mecab-ipadic-NEologd)のインストール 
  !apt-get -q -y install sudo file mecab libmecab-dev mecab-ipadic-utf8 git curl python-mecab > /dev/null
  !git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git > /dev/null 
  !echo yes | mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -n > /dev/null 2>&1
  !pip install mecab-python3 > /dev/null

  # シンボリックリンクによるエラー回避
  !ln -s /etc/mecabrc /usr/local/etc/mecabrc
  import MeCab#日本語形態素解析エンジン MeCab とマルコフ連鎖ライブラリ markovify を使う
  !pip install markovify
  import markovify
  text=justMozi
  # 改行、スペース、問題を起こす文字の置換←これにめちゃくちゃ苦戦した
  table = str.maketrans({
        '\n': '',
        '\r': '',
        '(': '（',
        ')': '）',
        '[': '［',
        ']': '］',
        '"':'”',
        "'":"’",
         "。":".",#。ではなく.で終わらないと文として正しく学習してくれないらしい
    })
  text = text.translate(table)
  tagger=MeCab.Tagger("-Owakati")
  text =tagger.parse(text)
  # text_model = markovify.Text(text,state_size=4)

  text_model = markovify.NewlineText(text)
  # text="今日 の 天気 は 晴れ です 。"
  sentence=None
  n=0
  while(sentence==None):
    #かなりの頻度でうまく生成されないので
    n+=1
    print(n,"回目")
    sentence=text_model.make_short_sentence(400)
    # sentence.replace(" ","")
  print(sentence)
 
'''
janomeで文字の登場頻度をprintする関数
'''
def rankPhrase(text):
  #地球環境保護のため、昔書いた自分のコードを再利用しています。

  syuruiList=["形容詞","助詞","動詞","名詞"]#品詞←,"名詞,固有名詞"などでも行ける。
  zyogaiList=["名詞,代名詞","名詞,非自立","名詞,数"]#除外
  # tokenizer = Tokenizer()
  for syurui in syuruiList:
    cf = [UnicodeNormalizeCharFilter()]#前処理フィルタ←アルファベット、半角カタカナを全角にするなど,Unicode文字列の正規化とドキュメントにあり
    tf = [CompoundNounFilter(),POSKeepFilter([syurui]),POSStopFilter(zyogaiList),TokenCountFilter(att='base_form')] #後処理フィルタ準備 att="base_form"で品詞活用をまとえｍて基本形のみにする
    a = Analyzer(char_filters =cf,token_filters=tf)#解析器生成
    results = a.analyze(text)#解析
    print(syurui,"登場順")
    s =sorted(results, key=lambda x:x[1],reverse=True)#結果並べ替え
    for i,wc in enumerate(s):
      if i >= 50:break
      print((i +1),':',wc)

'''
月ごとの合計文字数と平均を算出
'''

def mozisuuPerMonth(newDiaryList):
  years=[]
  outputList=[]
  months=["01","02","03","04","05","06","07","08","09","10","11","12"]
  for year in range(int(newDiaryList[0][0][0:4]),int(newDiaryList[-1][0][0:4])+1):
    years.append(year)
  listall={}#辞書型配列にしたので{}←日記の文字数と月入れるよう
  listallNikkisuu={}#こちらは日記の文字数ではなく、日記の存在数を入れるよう←平均で使うために。
  listallNikkimozi={}#日記の文字を入れる←月ごとの品詞解析で使うために。
  #空の辞書型配列作っておく（+=するため)
  for year in years:
    for x in months:
      date=str(year)+"."+x
      listall[date]=0
      listallNikkisuu[date]=0
      listallNikkimozi[date]=""
  #該当する配列に代入←大幅リファクタリングに成功。
  for diary in newDiaryList:#newDiaryListは文字数がすでに格納されてるのでそれを使った。
    date=str(diary[0][0:4])+"."+diary[0][5:7]
    listall[date]=listall[date]+diary[1]
    listallNikkisuu[date]=listallNikkisuu[date]+1#日記数なのでプラスイチするだけ
    diaryRaw=""
    for diaryMozi in diary[2]:
      diaryRaw+=diaryMozi+" "
    listallNikkimozi[date]+=diaryRaw
  # print(listall)#{'2018.01': 2805, '2018.02': 281, '2018.03': 1577, ..............
  # print(listallNikkisuu)
  mozisuuPerMonthDate=[]
  mozisuuPerMonthKazu=[]
  mozisuuPerMonthKazuAverage=[]
  mozisuuAll=0
  #合計文字数を出す処理と辞書型配列のキーと値を分離する処理
  for key, value in listall.items():
  #  print(key,"の文字数合計は", value,"字")
   mozisuuAll+=value
   mozisuuPerMonthDate.append(key)
   mozisuuPerMonthKazu.append(value)

  #月ごとの平均文字数を出す処理
  i=0
  average=0
  for key, value in listallNikkisuu.items():
    average=mozisuuPerMonthKazu[i]/value if value!=0 else 0#三項演算子ってやつです 割る0だと怒られちゃうのでそれ防止です。
    mozisuuPerMonthKazuAverage.append(average)
    i+=1

  print("合計文字数",mozisuuAll)
  # print(mozisuuPerMonthDate)
  # print(mozisuuPerMonthKazu)
  # print(mozisuuPerMonthKazuAverage)
  return mozisuuPerMonthDate,mozisuuPerMonthKazu,mozisuuPerMonthKazuAverage,listallNikkisuu,listallNikkimozi#mozisuuPerMonthDateが日付、mozisuuPerMonthKazuが文字数,mozisuuPerMonthKazuAverageが平均文字数,listallNikkisuuが辞書型配列の月ごとの文字数

  # #地獄の入れ子for文
  # yearList=[]
  # for diary in newDiaryList:
  #   mozisuuList=[]
  #   for year in years:
  #     monthmozisuu=0
  #     for month in months:
  #       # print(year)
  #       # print(diary[0][0:4])
  #       # print(month)
  #       # print(diary[0][5:7])
  #       # print(diary[1])
  #       # print(year==diary[0][0:4])
  #       if(year==diary[0][0:4] and month==diary[0][5:7]):
  #         monthmozisuu+=diary[1]
  #         print("add")
  #     mozisuuList.append(monthmozisuu)
  #   yearList+=mozisuuList
  # print(yearList)
  
  # print("----------------------------")
  # i=-1
  # for year in years:
  #   i+=1
  #   for month in months:
  #     monthMozisuu=months[i][int(month)-1]
  #     print(year,"年",str(month),"月の総文字数は",monthMozisuu,"字")
  #     date=year,".",month
  #     outputList.appned([date,monthMozisuu])
  # print("----------------------------")

  # return listall

'''
文字数と日付の"棒"グラフを描画する関数
'''
def drawCharAndDateGraphBou(diaryDateList,mozisuuList,AllDataList,graphTitle):
 
  fig =  plt.figure() 
  plt.title(graphTitle) 
  plt.xlabel("日付")
  plt.ylabel("文字数(字)")
  # print(len(diaryDateList),len(mozisuuList))
  # for x in range(len(AllDataList)) :
  #   if(AllDataList[x]!=diaryDateList[x]):
  #     x
  #     diaryDateList.insert(x,AllDataList[x])
  #     mozisuuList.insert(x,0)
  # print(len(diaryDateList),len(mozisuuList),len(AllDataList))
  plt.bar(diaryDateList,mozisuuList)
  plt.xticks(rotation=90)
  plt.show()
  dateTitile=graphTitle+filetype
  # dateTitile=graphTitle+".pdf"
  # dateTitile=graphTitle+".svg"
  fig.savefig(dateTitile)
  files.download(dateTitile)
  plt.close()
'''
文字数と日付の"折れ線"グラフを描画する関数
'''
def drawCharAndDateGraphOresen(diaryDateList,mozisuuList,AllDataList,graphTitle):
 
  fig =  plt.figure() 
  plt.title(graphTitle) 
  plt.xlabel("日付")
  plt.ylabel("文字数(字)")
  plt.plot(diaryDateList,mozisuuList)
  plt.xticks(rotation=90)
  plt.show()
  dateTitile=graphTitle+filetype
  # dateTitile=graphTitle+".pdf"
  # dateTitile=graphTitle+".svg"
  fig.savefig(dateTitile)
  files.download(dateTitile)
  plt.close()

'''
一文あたりの文字数の平均を導出する関数
'''
def countPerParagraph(diaryContentListProcessed):
  count=0
  mozisuu=0
  for contentPerDate in diaryContentListProcessed:
    for contentPerParagraph in contentPerDate:#行ごとに分けられた配列を1こずつ取り出す。
      contentPerParagraphListre=re.findall(r'.+。|.+\!+|.+！+|.+…+',contentPerParagraph)#一文の終わりを配列に分ける→。か!(1つ以上)か！(1つ以上)か…(1つ以上)のときが該当するのでsplitではなく正規表現で。
      for minimumContent in contentPerParagraphListre:
        # print(minimumContent)#きちんと分割できていることを確認済み
        count+=1
        mozisuu+=len(minimumContent)
  countPerParagraphMozisuu=mozisuu/count
  return countPerParagraphMozisuu


'''
wordCloud
'''
def drawWordCloud(justMozi):
  
  !apt-get -q -y install sudo file mecab libmecab-dev mecab-ipadic-utf8 git curl python-mecab > /dev/null
  !git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git > /dev/null 
  !echo yes | mecab-ipadic-neologd/bin/install-mecab-ipadic-neologd -n > /dev/null 2>&1
  !pip install mecab-python3 > /dev/null
  !ln -s /etc/mecabrc /usr/local/etc/mecabrc
  import MeCab
  #出典
  #https://water2litter.net/rum/post/python_wordcloud_jp/
  #http://cedro3.com/ai/word-cloud/
  # MeCabの準備

  #太宰治 女生徒をサンプルとして入れてみたコーナー
  # txt_pass="joseito.txt"
  # directory="/content/drive/My Drive/AdDS2020/"
  # rawDataTxtInstance = open(directory+txt_pass,'r',encoding="utf-8")
  # justMozi=rawDataTxtInstance.read()
  
  tagger = MeCab.Tagger()
  tagger.parse('')
  node = tagger.parseToNode(justMozi)

  # 名詞を取り出す
  word_list = []
  while node:
      word_type = node.feature.split(',')[0]
      if word_type == '名詞':
          word_list.append(node.surface)
      node = node.next

  # リストを文字列に変換
  word_chain = ' '.join(word_list)

  # ワードクラウド作成
  fpath = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
  W = WordCloud(width=900, height=600, background_color='white', colormap='bone',font_path=fpath,max_words=500).generate(word_chain)
  fig=plt.figure(figsize=(15,12))
  plt.imshow(W)
  plt.axis('off')
  plt.show()
  fig.savefig("wordCloud.png")
  files.download("wordCloud.png")
  plt.close()

'''
日記を書いた割合の帯グラフ
'''
def percenteageOfNikki(listallNikkisuu,AllDataList):
  import calendar#月ごとに日数を取得する用←うるう年の処理のため。
  import datetime
  # startDate=datetime.date(AllDataList[0][0])
  # endDate=datetime.date(AllDataList[-1][0])
  months=["01","02","03","04","05","06","07","08","09","10","11","12"]
  monthsDays=[]
  yearAndMonth=[]
  yearAndMonthNikkiTotal=[]
  yearAndMonthDayTotal=[]
  yearAndMonthDayWariai=[]
  for key, value in listallNikkisuu.items():
    yearAndMonth.append(key)
    yearAndMonthNikkiTotal.append(value)
    # print(int(key[0:4]), int(key[5:7]))
    monthKazu=calendar.monthrange(int(key[0:4]), int(key[5:7]))[1]#月の日数を取得←配列で予め用意でも良かったのだが、うるう年などあるため。また4年に1度のうるう年が2100年にはうるう年とならないため、冗長性のため毎度出すことにした
    monthWarial=value/monthKazu if value!=0 else 0#月ごとの割合算出
    yearAndMonthDayTotal.append(monthKazu)
    yearAndMonthDayWariai.append(monthWarial)
  # print(yearAndMonthDayWariai)
  #ここからグラフ　matplotlibでは帯グラフ作れないのでhttps://qiita.com/yu4u/items/89bf0127ed340c026290を参考にした←参考にできなかった

  yearAndMonthDayHikuiti=[]
  for x in yearAndMonthDayWariai:
    yearAndMonthDayHikuiti.append(1)


  #2回積み重ねることで帯グラフにする barhで横向き
  fig =  plt.figure() 
  x_position = yearAndMonth
  wariai=yearAndMonthDayWariai#なぜかnp.arrayじゃないとエラー出る
  wariai2=yearAndMonthDayHikuiti
  plt.barh(x_position,wariai2, label='擱筆', color="gray")
  plt.barh(x_position,wariai, label='執筆', color="blue")
  # plt.set_xticklabels(yearAndMonth)
  #ax.bar(x_position, y_DEG1, label='FDR < 0.01')
  graphTitle="日記の月ごとの執筆率"
  plt.title(graphTitle) 
  plt.xlabel("割合")
  plt.ylabel("月と年")

  plt.xticks(rotation=90)
  plt.legend()
  plt.show()

  plt.show()
  dateTitile=graphTitle+filetype
  # dateTitile=graphTitle+".pdf"
  # dateTitile=graphTitle+".svg"
  fig.savefig(dateTitile)
  files.download(dateTitile)
  plt.close()

'''
文字数の分布ヒストグラム作成
'''
def makeHistgram(mozisuuList):
  graphTitle="文字数の分布"
  fig =  plt.figure() 
  plt.title(graphTitle) 
  plt.xlabel("文字数(字)")
  plt.ylabel("日記数(個)")
  plt.hist(mozisuuList,bins=30)#ヒストグラム
  # plt.xticks(rotation=90)
  plt.show()
  dateTitile=graphTitle+filetype

  fig.savefig(dateTitile)
  files.download(dateTitile)
  plt.close()
'''
天気と文字数の関係
'''
def relationWeatherAndMozisuu(diaryDateList,mozisuuList):
  df = pd.read_csv('/content/drive/My Drive/AdDS2020/weatherProcessed.csv',encoding="shift-jis")
  # print(df)
  weatherDateDF=df["年月日"]
  weatherRyouDF=df["降水量の合計(mm)"]
  weatherDate=weatherDateDF.values.tolist()#PandasDateframe型→numpy配列→普通の配列　に変換https://note.nkmk.me/python-pandas-list/
  weatherRyou=weatherRyouDF.values.tolist()
  #csv内の日付と降水量で辞書型配列を作成
  precipitations={}
  i=0
  for date in weatherDate:
    precipitations[date]=weatherRyou[i]
    i+=1
  # print(precipitations)
  #日記側の配列の日付の文字を変更 01→1に
  diaryDateListProcessed=[]
  for date in diaryDateList:
    date=date.replace(".","/")#..から//にする

    #日の0除く 02日→2日な感じ
    if(str(date[8])=="0"):
      # print("former",date)
      date=date[:8]+date[9:]

      #月の0除く
    if(str(date[5])=="0"):
      date=date[:5]+date[6:]
    diaryDateListProcessed.append(date)
  #該当する日付の降水量のみ抽出した配列を作成
  precipitationsUse=[]
  # print("date",diaryDateListProcessed)
  for date in diaryDateListProcessed:
    precipitation=precipitations[date]
    precipitationsUse.append(precipitation)
  print(precipitationsUse)
  print("降水量",precipitationsUse)
  print("文字数",mozisuuList)
  #ここよりグラフ
  graphTitle="降水量と文字数の関係"
  fig =  plt.figure() 
  plt.title(graphTitle) 
  plt.xlabel("文字数(字)")
  plt.ylabel("降水量(mm/日)")
  plt.scatter(mozisuuList, precipitationsUse)#散布図
  # plt.xticks(rotation=90)
  plt.show()
  dateTitile=graphTitle+filetype

  fig.savefig(dateTitile)
  files.download(dateTitile)
  plt.close()
  soukan = np.corrcoef(mozisuuList, precipitationsUse)
  print("相関係数は",soukan[0,1])

'''
日記の文字数2000字以上と50字以下取得
'''
def getNikkiMoziContent(newDiaryList):
  print("----------------------")
  print("2000字以上の日記は")
  for nikki in newDiaryList:
    if(nikki[1]>=2000):
      print(nikki[1],"字,",nikki[0],"の日記で内容は",nikki[2])
  print("----------------------")
  print("50字以下の日記は")
  for nikki in newDiaryList:
    if(nikki[1]<=50):
      print(nikki[1],"字,",nikki[0],"の日記で内容は",nikki[2])
  print("----------------------")

'''
日記の感情数値化
'''
def calculateKanzyou(diaryDateList,diaryContentListProcessed):
  txt_pass="pn_ja.dic"
  directory="/content/drive/My Drive/AdDS2020/"
  rawDataTxtInstance = open(directory+txt_pass,'r',encoding="shift_jis")#Shift_jisなら読める
  justMozi=rawDataTxtInstance.readlines()#readlinesで1行ごとに読み取る
  kanzyouDictionary={}
  KanzyouAtaiList=[]
  # print(justMozi)
  #辞書型配列の辞書へ
  for line in justMozi:
    # "優れる:すぐれる:形容詞:1.0".........."を
    #{'優れる': 1.0, '良い': 0.999995,...}の辞書型配列へ
    columns = line.split(':')
    kanzyouDictionary[columns[0]] = float(columns[3])
  print(kanzyouDictionary)
  #janomeで単語に分けたもので辞書から値を引っ張ってくる
  t = Tokenizer()

  semantic_value = 0
  semantic_count = 0
  for diary in diaryContentListProcessed:
    sentences=""
    for sentence in diary:
      sentences+=sentence
    tokens = t.tokenize(sentences)
    words = []
    for token in tokens:
        # 品詞を取り出し
        partOfSpeech = token.part_of_speech.split(',')[0]

        #感情分析(感情極性実数値より)
        if( partOfSpeech in ['動詞','名詞', '形容詞', '副詞']):
            if(token.surface in kanzyouDictionary):
                data = token.surface + ":" + str(kanzyouDictionary[token.surface])
                # print(data)
                semantic_value = kanzyouDictionary[token.surface] + semantic_value
                semantic_count = semantic_count + 1
        words.append(token.surface)

    # data ="分析した単語数:" +  str(semantic_count) +  " 感情極性実数値合計:" + str(semantic_value) + " 感情極性実数値平均値:" + str(semantic_value / semantic_count)
    print(data)
    average=semantic_value / semantic_count
    KanzyouAtaiList.append(average)#平均を格納

  #グラフにする
  print(KanzyouAtaiList)
  graphTitle="気持ちの推移"
  fig =  plt.figure() 
  plt.title(graphTitle) 
  plt.xlabel("日付")
  plt.ylabel("気持ち(+1[positive]～-1[negative])")
  # print(len(diaryDateList),len(mozisuuList))
  # for x in range(len(AllDataList)) :
  #   if(AllDataList[x]!=diaryDateList[x]):
  #     x
  #     diaryDateList.insert(x,AllDataList[x])
  #     mozisuuList.insert(x,0)
  # print(len(diaryDateList),len(mozisuuList),len(AllDataList))
  plt.plot(diaryDateList,KanzyouAtaiList)
  plt.xticks(rotation=90)
  plt.show()
  dateTitile=graphTitle+filetype

  fig.savefig(dateTitile)
  files.download(dateTitile)
  plt.close()


'''
月ごとの品詞解析
'''
def checkHinsiPerMonth(listallNikkimozi):
  # print(listallNikkimozi)
  syuruiList=["形容詞","助詞","動詞","名詞"]#品詞←,"名詞,固有名詞"などでも行ける。
  for hinsi in syuruiList:
    for key, value in listallNikkimozi.items():
      # print(key,value)
      zyogaiList=["名詞,代名詞","名詞,非自立","名詞,数"]#除外
      cf = [UnicodeNormalizeCharFilter()]#前処理フィルタ←アルファベット、半角カタカナを全角にするなど,Unicode文字列の正規化とドキュメントにあり
      tf = [CompoundNounFilter(),POSKeepFilter(hinsi),POSStopFilter(zyogaiList),TokenCountFilter(att='base_form')] #後処理フィルタ準備 att="base_form"で品詞活用をまとえｍて基本形のみにする
      a = Analyzer(char_filters =cf,token_filters=tf)#解析器生成
      results = a.analyze(value)#解析
      s =sorted(results, key=lambda x:x[1],reverse=True)#結果並べ替え
      tmpList=[]
      for i,wc in enumerate(s):
        if i >= 10:break
        tmpList.append(wc)
      print(key,"の",hinsi,"トップ10は",tmpList)
      i+=1

  
'''
株価と文字数推移の関係
地球環境保護のため、コードは降水量との関係を大幅借用した。
'''
def relationStockAndMozisuu(diaryDateList,mozisuuList,AllDataList):
  # !pip install mplfinance#株価用のグラフ描写ライブラリ
  # import mplfinance as mpf
  df = pd.read_csv('/content/drive/My Drive/AdDS2020/nikkei_stock_average_daily_jp.csv',encoding="shift-jis")
  # print(df)
  # print(df)
  weatherDateDF=df["データ日付"]

  weatherRyouDF=df["終値"]
  weatherDate=weatherDateDF.values.tolist()#PandasDateframe型→numpy配列→普通の配列　に変換https://note.nkmk.me/python-pandas-list/
  weatherRyou=weatherRyouDF.values.tolist()
  #csv内の日付と降水量で辞書型配列を作成
  precipitations={}
  i=0
  for date in weatherDate:
    precipitations[date]=weatherRyou[i]
    i+=1
  print(precipitations)
  #日記側の配列の日付の文字を変更は不要
  diaryDateListProcessed=[]
  for date in diaryDateList:
    date=date.replace(".","/")#..から//にする
    diaryDateListProcessed.append(date)
  #該当する日付の降水量のみ抽出した配列を作成
  precipitationsUse=[]
  # print("date",diaryDateListProcessed)
  precipitationBefore=0
  for date in diaryDateListProcessed:
    #日経平均株価は土日休むのでその日は前日の値を入れる←0にするとグラフおかしくなり、空白にすると描画が崩れるのでやむを得ず。
    if date not in precipitations.keys():
      # print("no",date)
      precipitation=precipitationBefore
    else:
      precipitation=precipitations[date]
    precipitationBefore=precipitation
    precipitationsUse.append(precipitation)
  print(precipitationsUse)
  #ここよりグラフ

  print("日経平均株価",precipitationsUse)
  print("文字数",mozisuuList)
  graphTitle="日経平均株価(終値)と文字数の関係"
  # 棒グラフを出力
  fig, ax1 = plt.subplots()
  ax1.bar(diaryDateList, mozisuuList, align="center",label="文字数",  linewidth=0)
  # ax1.plot(diaryDateList, mozisuuList, label="文字数" )#align="center",linewidth=0
  ax1.set_ylabel('文字数(字)')
  
  # 折れ線グラフを出力
  ax2 = ax1.twinx()
  ax2.plot(diaryDateList, precipitationsUse,linewidth=1, label="日経平均株価(終値)",color="red")
  ax2.set_ylabel('日経平均株価(終値)(円)')
  # ax2.set_yscale('log')#対数にしたらもっとわからなくなった
  plt.xticks(rotation=90)
  plt.title(graphTitle) 
  plt.xlabel("日付")
  plt.legend()
  plt.show()
  dateTitile=graphTitle+filetype
  # dateTitile=graphTitle+".pdf"
  # dateTitile=graphTitle+".svg"
  fig.savefig(dateTitile)
  files.download(dateTitile)
  plt.close()
  soukan = np.corrcoef(mozisuuList, precipitationsUse)
  print("相関係数は",soukan[0,1])

'''
本文
'''
'''
下処理系↓
'''

diaryDateList,diaryContentListProcessed,mozisuuList=importDateAndPreparation()#日記を読み込む

allmozi=0
for x in diaryContentListProcessed:
  for y in x:
    allmozi+=len(y)
print("【再計算】文字数合計",allmozi)
'''
diaryDateList                日付のリスト
diaryContentListProcessed   本文（配列） 
mozisuuList                 文字数リスト
'''
newDiaryList=combineDateAndContetn(diaryDateList,mozisuuList,diaryContentListProcessed)#統合されたリストを作る
justMozi=makeNonListContent(diaryContentListProcessed)#配列じゃなくてそのままの文字にする

print("同日日記結合後の要素数",len(newDiaryList))
AllDataList=makeAllDataList(newDiaryList[0][0],newDiaryList[-1][0])#日付のリスト作る
# print(AllDataList)
mozisuuPerMonthDate,mozisuuPerMonthKazu,mozisuuPerMonthKazuAverage,listallNikkisuu,listallNikkimozi=mozisuuPerMonth(newDiaryList)#月ごとに総文字数と平均文字数を出す。listallNikkisuuは副産物で生まれた月ごとの日記の数

#↑essentialなもの


countPerParagraphMozisuu=countPerParagraph(diaryContentListProcessed)#一文あたりの文字数平均を出す関数
print("一文あたりの文字数の平均は",countPerParagraphMozisuu)
'''
テキストマイニング系↓
'''
# rankPhrase(justMozi)#品詞ごとの順位を出す関数
# makeAtumaticalNikki(justMozi)#日記生成←相当時間かかります。
# drawWordCloud(justMozi)#wordCloudを生成する
'''
グラフ系↓
'''

drawCharAndDateGraphBou(diaryDateList,mozisuuList,AllDataList,"日付と日記文字数の変化")#グラフ描写

drawCharAndDateGraphBou(mozisuuPerMonthDate,mozisuuPerMonthKazu,AllDataList,"月ごとの合計日記文字数の変化")#グラフ描写
drawCharAndDateGraphOresen(mozisuuPerMonthDate,mozisuuPerMonthKazuAverage,AllDataList,"月ごとの1日記あたりの平均文字数の変化")#グラフ描写

percenteageOfNikki(listallNikkisuu,AllDataList)#グラフ描写(執筆率の割合帯グラフ)
makeHistgram(mozisuuList)#グラフ描写(文字数分布のヒストグラム)
relationWeatherAndMozisuu(diaryDateList,mozisuuList)#グラフ描写(降水量と文字数の散布図)

# getNikkiMoziContent(newDiaryList)#日記の極端に多いところ少ないところを表示

# 2/6以降追加分
checkHinsiPerMonth(listallNikkimozi)#月ごとの単語の変化

calculateKanzyou(diaryDateList,diaryContentListProcessed)#感情解析とグラフ化
relationStockAndMozisuu(diaryDateList,mozisuuList,AllDataList)#株価との関係
