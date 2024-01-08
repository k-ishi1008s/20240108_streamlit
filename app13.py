import streamlit as st
import sqlite3
import time
from datetime import datetime
import pandas as pd
from PIL import Image
import io

# タイトル
st.title("pix2pixによって生成したピクトグラムについての実験（アンケート）")

st.markdown("""
            ### 実験概要
            
            実験は **約n分** で終わります。実験期間は **1/9 ~ 1/nn** までです。

            今から、n個のピクトグラムを見てもらい、そのピクトグラムが何に見えるか、テキストボックスへ入力してもらいます。

            手順は以下の通りです。休憩はどこでとってもらってもいいです。

            1. ユーザー名をアルファベットで入力してください。
            他の人と被るとエラーが発生するため、人と被らないもの（和歌山大学生ならs602///の学生番号）にしてください。二文字目からは数字も使用可能です。
            初めは謎のエラー文が出ていますが、ユーザー名を記入すると消えます。
            
            2.  **「数字.pngを表示」** のボタンをクリックすると、5秒間だけ黒の画像がピクトグラム画像へ変わります。

            3. 何を表したピクトグラムなのか考え、下の **テキストボックスへ入力** してください。表示のボタンを押してからならいつ入力してもいいです。

            4.  **制限時間はn秒間** です。残り時間がn秒になるととカウントダウンが始まります。

            5. 入力が終わったら、 **「保存」** ボタンを押してください。制限時間内に入力できていると「保存完了」と表示されます。

            6. 2~5をn枚のピクトグラムで行ってもらいます。

            7. 終了のボタンを押すと実験終了です。

            ---

""")

# ユーザー名入力フォーム
user_name = st.text_input('ユーザー名をアルファベットで入力してください:')

# データベース接続
conn = sqlite3.connect('data_timestamp.db')
c = conn.cursor()

# ユーザーごとのテーブルを作成
c.execute(f'''
    CREATE TABLE IF NOT EXISTS {user_name}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_number INTEGER,
        input_text TEXT,
        time REAL,
        timelimit BOOLEAN  -- 追加: timelimit 列を追加 (True or False)
    )
''')
conn.commit()

# 画像表示のための準備
imgsum = 10
sleeptime = 5  # 表示時間
countdown = 15 # 表示時間 + countdown = 制限時間
image_folder = './2value/'
blackImg = Image.open('black.png')

# st.session_stateに解答時間と制限時間を用意する
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = {f'{i+1}': {'start': None, 'save': None, 'timelimit': countdown} for i in range(imgsum)}

# 画像を表示する関数
def display_image(i):
    img = Image.open(image_folder + f'{i}.png')
    return img

try:
    for imgIndex in range(1, imgsum + 1):
        showImg = st.empty()
        # はじめは黒画像
        showImg.image(blackImg)

        # 追加: カウントダウンの表示
        countdown_text = st.empty()

        if st.button(f'({imgIndex})を表示'):
            # 表示ボタンがクリックされたときにタイムスタンプを更新
            st.session_state.timestamps[f'{imgIndex}']['start'] = time.time()
            # カウントダウンの初期値を設定
            st.session_state.timestamps[f'{imgIndex}']['timelimit'] = countdown
            countdown_text.text(f'残り時間: {st.session_state.timestamps[f"{imgIndex}"]["timelimit"]:.1f} 秒')
            
            # 画像を表示
            img = display_image(imgIndex)
            showImg.image(img)
            time.sleep(sleeptime)
            showImg.image(blackImg)
            
            # カウントダウン
            while st.session_state.timestamps[f'{imgIndex}']['timelimit'] > 0:
                st.session_state.timestamps[f'{imgIndex}']['timelimit'] -= 0.1
                countdown_text.text(f'残り時間: {st.session_state.timestamps[f"{imgIndex}"]["timelimit"]:.1f} 秒')
                time.sleep(0.1)

            showImg.image(blackImg)

        # 入力フォーム
        input_text = st.text_input(f'({imgIndex})は何に見えますか？')

        if st.button(f'({imgIndex})の解答を保存'):
            # タイムスタンプを更新
            st.session_state.timestamps[f'{imgIndex}']['save'] = time.time()

            # 解答にかかった時間を計算
            elapsed_time = st.session_state.timestamps[f'{imgIndex}']['save'] - st.session_state.timestamps[f'{imgIndex}']['start']

            # データベースへ保存
            c.execute(f'INSERT INTO {user_name}(image_number,input_text,time,timelimit) VALUES (?, ?, ?, ?)',
                      (imgIndex, input_text, elapsed_time, elapsed_time <= 10))
            conn.commit()
            if elapsed_time <= 10:
                st.success('保存完了')
            else:
                st.warning('制限時間切れ')
    
    # 終了ボタンがクリックされた時にありがとうを表示
    if st.button('終了'):
        st.success('これで実験は終了です。ありがとうございました。')
    
    # データベースからデータを取得
    data = c.execute(f'SELECT * FROM {user_name}').fetchall()
    
    # データを表示
    st.subheader('只今の入力情報:')
    if data:
        # テーブル形式で表示
        st.table(data)
    else:
        st.warning('データベースにはまだ情報がありません')
    
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
    if st.button('管理者用'):
        current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        excel_filename = f'user_data_{current_time}.xlsx'
        st.download_button(label='ダウンロード', data=excel_data, file_name=excel_filename, key='download_data')

finally:
    # データベースクローズ
    conn.close()
