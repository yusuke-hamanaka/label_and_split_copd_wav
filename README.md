# 手順
1. `speech`内に、`{id}_(smartphone_)?.*.wav`の命名規則に該当するwavファイルを格納する
2. `python directory_organizer.py`を実行すると、`recordings/SP001/ic_recorder/*.wav`のようにディレクトリが構成される
3. `python get_label_timestamps.py`を実行し、`recordings`フォルダを選択する
4. `SN001/ic_recorder, SN001/smartphone`内に、仮ラベルファイル`{id}_(smartphone_)?.*_tmp.txt`が作られる
5. Audacityで仮ラベルファイルを修正し、`{id}_(smartphone_)?.*.txt`という名前で同じディレクトリに保存する
6. `python separate_wav_from_timestamps.py`を実行する
7. `release`内に分割されたwavファイルが保存される
