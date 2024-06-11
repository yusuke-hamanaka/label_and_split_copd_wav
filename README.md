※ recordings内のwavファイルはすべてダミーのファイル

# 手順
1. `speech`内に、`{id}_(TL15|IP13|IP14)_*.wav`の命名規則に該当するwavファイルを格納する
2. `python directory_organizer.py`を実行すると、`recordings/HC001/ic_recorder/*.wav`のようにディレクトリが構成される
3. `python get_label_timestamps.py`を実行し、`recordings`フォルダを選択する
4. `HC001/ic_recorder, HC001/smartphone`内に、仮ラベルファイル`{id}_(TL15|IP13|IP14)_*_tmp.txt`が作られる
5. Audacityで仮ラベルファイルを修正し、`{id}_(TL15|IP13|IP14)_*.txt`という名前で同じディレクトリに保存する
6. `separate_wav_from_timestamps.exe`を実行する
7. `release`内に分割されたwavファイルが保存される
