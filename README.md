# 手順
1. `python get_label_timestamps.py`
2. `recordings`を選択
3. `SN001`内にwavファイルと同じ名前の修正済みラベルtxtファイルを置く
4. `python separate_wav_from_timestamps.py`
5. `SN001`内に分割されたwavファイルが保存される

# 音声ファイル格納先ディレクトリ構成
```
└── recordings
    ├── SN001
    │   └── SN001_1_01.wav
    └── SP001
        └── SP001_1_01.wav
```
