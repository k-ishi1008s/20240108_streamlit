import streamlit as st
import sqlite3
import time
from datetime import datetime
import pandas as pd
from PIL import Image
import io

if st.checkbox("以上の内容に同意していただけたら、チェックを入れてください"):
    st.markdown("""
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
countdown = 25 # 表示時間 + countdown = 制限時間
timelimit = sleeptime + countdown
image_folder = './2value/'
blackImg = Image.open('black.png')

if 'imgIndex' not in st.session_state:
    st.session_state.imgIndex = 1

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

    # # 入力フォーム
    # input_text = st.text_input(f'({imgIndex})は何に見えますか？')
    # # 表示ボタンがクリックされたときにタイムスタンプを更新
    # st.session_state.timestamps[f'{imgIndex}']['start'] = time.time()
    # st.write(st.session_state.timestamps[f'{imgIndex}']['start'])

    # 画像を表示
    img = display_image(imgIndex)
    showImg.image(img)

    # if st.button(f'({imgIndex})の回答を保存'):
    #     # タイムスタンプを更新
    #     st.session_state.timestamps[f'{imgIndex}']['save'] = time.time()
    #     st.write(st.session_state.timestamps[f'{imgIndex}']['save'])
        
    #     # 解答にかかった時間を計算
    #     elapsed_time = st.session_state.timestamps[f'{imgIndex}']['save'] - st.session_state.timestamps[f'{imgIndex}']['start']

    #     # データベースへ保存
    #     c.execute(f'INSERT INTO {user_name}(image_number,input_text,time,timelimit) VALUES (?, ?, ?, ?)',
    #             (imgIndex, input_text, elapsed_time, elapsed_time <= timelimit))
    #     conn.commit()
    #     if elapsed_time <= timelimit:
    #         st.success('保存完了')
    #     else:
    #         st.warning('制限時間切れ')
        
    #     st.session_state.imgIndex += 1
        

    # 表示時間のカウントダウン
    while st.session_state.timestamps[f'{imgIndex}']['sleeptime'] > 0:
        st.session_state.timestamps[f'{imgIndex}']['sleeptime'] -= 0.1
        countdown_text.text(f'ピクトグラム表示 残り時間: {st.session_state.timestamps[f"{imgIndex}"]["sleeptime"]:.1f} 秒')
        time.sleep(0.1)

    showImg.image(blackImg)

    # 解答時間のカウントダウン
    while st.session_state.timestamps[f'{imgIndex}']['countdown'] > 0:
        st.session_state.timestamps[f'{imgIndex}']['countdown'] -= 0.1
        countdown_text.text(f'何に見えるかの回答 残り時間: {st.session_state.timestamps[f"{imgIndex}"]["countdown"]:.1f} 秒')
        time.sleep(0.1)

try:
    showImg = st.empty()

    if st.session_state.imgIndex == 1:
        if st.button("始める"):
            if st.session_state.firstQ == False : st.session_state.firstQ = True
            else: st.session_state.firstQ = False
        if st.session_state.firstQ:
            # 表示ボタンがクリックされたときにタイムスタンプを更新
            st.session_state.timestamps[f'{st.session_state.imgIndex}']['start'] = time.time()
            st.write(st.session_state.timestamps[f'{st.session_state.imgIndex}']['start'])
            
            # 入力フォーム
            input_text = st.text_input(f'({st.session_state.imgIndex})は何に見えますか？')
            
            if st.button(f'({st.session_state.imgIndex})の回答を保存'):
            # タイムスタンプを更新
                st.session_state.timestamps[f'{st.session_state.imgIndex}']['save'] = time.time()
                st.write(st.session_state.timestamps[f'{st.session_state.imgIndex}']['save'])
                
                # 解答にかかった時間を計算
                elapsed_time = st.session_state.timestamps[f'{st.session_state.imgIndex}']['save'] - st.session_state.timestamps[f'{st.session_state.imgIndex}']['start']

                # データベースへ保存
                c.execute(f'INSERT INTO {user_name}(image_number,input_text,time,timelimit) VALUES (?, ?, ?, ?)',
                        (st.session_state.imgIndex, input_text, elapsed_time, elapsed_time <= timelimit))
                conn.commit()
                if elapsed_time <= timelimit:
                    st.success('保存完了')
                else:
                    st.warning('制限時間切れ')
            
            st.session_state.imgIndex += 1
            
            show_question(st.session_state.imgIndex)
    
    elif st.session_state.imgIndex == imgsum:
        # 終了ボタンがクリックされた時にありがとうを表示
        if st.button('終了'):
            st.success('これで実験は終了です。ありがとうございました。')

    else:
        if st.button("次へ"):
            if st.session_state.otherQ == False : st.session_state.otherQ = True
            else: st.session_state.otherQ = False

        if st.session_state.otherQ:
            st.session_state.otherQ = False
            show_question(st.session_state.imgIndex)
    
    
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