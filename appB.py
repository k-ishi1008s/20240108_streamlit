import streamlit as st
import sqlite3
import time
from datetime import datetime
import pandas as pd
from PIL import Image
import io

# タイトル
st.header("pix2pixによって生成したピクトグラムについての評価実験B")

st.markdown("""
            評価実験にご協力いただき、ありがとうございます。
            
            本実験は画像生成モデルpix2pixによって生成されたピクトグラムが何に見えるかアンケートをとり、その結果を分析することで画像生成モデルの評価を行うことを目的としています。

            本実験への参加は任意であり、一度同意した場合でも、いつでも同意を撤回し実験を中断することが可能です。その場合、希望に応じて提供いただいたデータは破棄いたします。
            
            参加者から得たデータや個人情報は実験後、分析を行うために必要な範囲において利用いたします。個人情報が資料等に記載されることはございません。

            質問等あれば下記までご連絡ください。

            和歌山大学システム工学部　石橋孝太郎 
            
            E-mail: s256016@wakayama-u.ac.jp 

            ---
""")
st.markdown("""
            実験は **約30分** で終わります。

            今から、100個のピクトグラムを見てもらい、そのピクトグラムが何に見えるか、テキストボックスへ入力してもらいます。

            手順は以下の通りです。休憩はどこでとってもらってもいいです。

            &ensp;

            1. テキスト入力ボックスへユーザー名をアルファベットで入力してください。ユーザー名はハンドルネームで構いません。
            他の人との被りを防ぐためハンドルネーム＋好きな数字４桁にしていただきたいです。

            &emsp; &ensp;エラーが出ていますが、ユーザー名を入力すると消えます。
""")

# st.image('./demo/form1.png')
# st.image('./demo/form2.png', caption='使用可能かどうか、確認することができます')

st.markdown("""
            2. **「始める」** のボタンをクリックすると、5秒間だけ黒の画像がピクトグラム画像へ変わります。
""")

#st.image('./demo/form3.png')

st.markdown("""
            3. 何を表したピクトグラムなのか考え、下の **テキストボックスへ入力** してください。
            表示のボタンを押してからならいつ入力してもいいですが、回答には制限時間が設けられています
""")

#st.image('./demo/form4.png')


st.markdown("""
            4. 入力が終わったら、 **「回答を保存」** ボタンを押してください。制限時間内に入力できていると「保存完了」と表示されます。 **「閉じる」** を押すと、次の問題へ進みます
""")

# st.image('./demo/form5.png')

# st.image('./demo/form6.png')

st.markdown("""
            6. 2~5を100枚のピクトグラムで行ってもらいます。

            7. 終了のボタンを押すと実験終了です。

            以下がデモ動画です
""")

st.video('./demo/demo.mov')

user_name = None

if st.checkbox("以上の内容に同意していただけたら、チェックを入れてください"):
    st.markdown("""
                ---
    """)
    # ユーザー名入力フォーム
    user_name = st.text_input('ユーザー名をアルファベット+数字４文字で入力してください','name')

# データベース接続
conn = sqlite3.connect('data_B_20240121.db')
c = conn.cursor()

if user_name is not None:
    # ユーザーごとのテーブルを作成
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {user_name}(
            image_number INTEGER,
            input_text TEXT,
            time REAL,
            timelimit BOOLEAN  -- 追加: timelimit 列を追加 (True or False)
        )
    ''')
    conn.commit()

# 画像表示のための準備
imgsum = 200
sleeptime = 5  # 表示時間
countdown = 25  # 表示時間 + countdown = 制限時間
timelimit = sleeptime + countdown
image_folder = './imageB_2value/'
blackImg = Image.open('black.png')

if 'imgIndex' not in st.session_state:
    st.session_state.imgIndex = 101

# st.session_stateに解答時間と制限時間を用意する
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = {f'{i+1}': {'start': None, 'save': None, 'sleeptime':sleeptime, 'countdown': countdown} for i in range(imgsum)}

if 'firstQ' not in st.session_state:
    st.session_state.firstQ = False

if 'otherQ' not in st.session_state:
    st.session_state.otherQ = False 

def display_image(i):
    img = Image.open(image_folder + f'{i}.png')
    return img

def show_question(imgIndex):
    showImg = st.empty()
    
    # はじめは黒画像
    showImg.image(blackImg)

    # 追加: カウントダウンの表示
    countdown_text = st.empty()

    # 入力フォーム
    input_text = st.text_input(f'({imgIndex})は何に見えますか？')

    # 画像を表示
    img = display_image(imgIndex)
    showImg.image(img)

    if st.button(f'({imgIndex})の回答を保存'):
        # タイムスタンプを更新
        st.session_state.timestamps[f'{imgIndex}']['save'] = time.time()
        # 解答にかかった時間を計算
        elapsed_time = st.session_state.timestamps[f'{imgIndex}']['save'] - st.session_state.timestamps[f'{imgIndex}']['start']

        # データベースへ保存
        c.execute(f'INSERT INTO {user_name}(image_number,input_text,time,timelimit) VALUES (?, ?, ?, ?)',
                (imgIndex, input_text, elapsed_time, elapsed_time <= timelimit))
        conn.commit()
        if elapsed_time <= timelimit:
            st.success('保存完了')
        else:
            st.warning('制限時間切れ')
            
        st.session_state.imgIndex += 1
        st.session_state.otherQ = False
        st.button('閉じる')

    # 表示時間のカウントダウン
    while st.session_state.timestamps[f'{imgIndex}']['sleeptime'] > 0:
        st.session_state.timestamps[f'{imgIndex}']['sleeptime'] -= 0.1
        countdown_text.text(f'ピクトグラム表示 残り時間: {st.session_state.timestamps[f"{imgIndex}"]["sleeptime"]:.1f} 秒')
        time.sleep(0.1)

    showImg.image(blackImg)

    # 解答時間のカウントダウン
    while st.session_state.timestamps[f'{imgIndex}']['countdown'] > 0:
        st.session_state.timestamps[f'{imgIndex}']['countdown'] -= 0.1
        countdown_text.text(f'回答 残り時間: {st.session_state.timestamps[f"{imgIndex}"]["countdown"]:.1f} 秒')
        time.sleep(0.1)

try:
    showImg = st.empty()

    if st.session_state.imgIndex == 101 and user_name is not None:
        if st.button("始める"):
            if st.session_state.firstQ == False : st.session_state.firstQ = True
            # 表示ボタンがクリックされたときにタイムスタンプを更新
            st.session_state.timestamps[f'{st.session_state.imgIndex}']['start'] = time.time()
            #st.write(st.session_state.timestamps[f'{st.session_state.imgIndex}']['start'])
        if st.session_state.firstQ:
            show_question(st.session_state.imgIndex)
    
    elif st.session_state.imgIndex == imgsum + 1:
        # 終了ボタンがクリックされた時にありがとうを表示
        if st.button('終了'):
            st.success('これで実験は終了です。ありがとうございました。')

    elif user_name is not None:
        if st.button(f'({st.session_state.imgIndex})を開始') :
            if st.session_state.otherQ == False : st.session_state.otherQ = True
            # 表示ボタンがクリックされたときにタイムスタンプを更新
            st.session_state.timestamps[f'{st.session_state.imgIndex}']['start'] = time.time()
            #st.write(st.session_state.timestamps[f'{st.session_state.imgIndex}']['start'])
        if st.session_state.otherQ:
            show_question(st.session_state.imgIndex)

    if user_name is not None:       
        # データベースからデータを取得
        data = c.execute(f'SELECT * FROM {user_name}').fetchall()
        
        # データを表示
        if data:
            # テーブル形式で表示
            if st.session_state.firstQ == False: st.warning('このユーザー名は既に使用されています')
            #st.table(data)
        elif st.session_state.firstQ == True:
            st.write('')
        else:
            st.success('このユーザー名は使用可能です！')
        
        # Excelファイル生成
        all_data = c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()
        excel_data = io.BytesIO()

        with pd.ExcelWriter(excel_data, engine='openpyxl') as writer:
            pd.DataFrame(columns=[]).to_excel(writer, index=False, sheet_name='EmptySheet', header=True)

            for table_name, in all_data:
                user_df = pd.read_sql_query(f'SELECT * FROM {table_name}', conn)
                user_df.to_excel(writer, index=False, sheet_name=table_name, header=True)

        excel_data.seek(0)  # ファイルの先頭に戻す

    # ダウンロードボタンがクリックされたときにエクセルファイルを出力
    if st.button('管理者用(絶対に押さないでください)'):
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        excel_filename = f'user_data_{current_time}.xlsx'
        st.download_button(label='ダウンロード(絶対に押さないでください)', data=excel_data, file_name=excel_filename, key='download_data')

finally:
    # データベースクローズ
    conn.close()