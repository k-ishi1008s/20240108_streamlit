import sqlite3

# データベース接続
conn = sqlite3.connect('data_timestamp.db')
c = conn.cursor()

# テーブル名を取得
table_names = [table[0] for table in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

# テーブル名一覧を表示
print("テーブル名一覧:")
for table_name in table_names:
    print(table_name)

# データベースクローズ
conn.close()
