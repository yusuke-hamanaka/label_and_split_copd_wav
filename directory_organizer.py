import os
import re
import shutil


def organize_files(folder_path: str) -> None:
    """
    speechディレクトリ内にあるファイルを以下の要件に従って、recordingsディレクトリに移動する
    - ファイル名は、または"{id}_(TL15|IP13|IP14)_*.wav"
    - idはHCまたはPCから始まり、三桁の数字が続く（例：SP001）
    - idと同じ名前のディレクトリをrecordingsに作成する。
    - recordings内のid名のディレクトリの中に、ic_recorder、smartphoneディレクトリを作成する
    - ic_recorderディレクトリには{id}_*.wavを移動する
    - smartphoneディレクトリには{id}_smartphone_*.wavを移動する
    """
    # パターンの定義
    pattern = re.compile(r"^(HC|PC)\d{3}_(TL15|IP13|IP14)_.*\.wav$")

    # recordingsディレクトリのパス
    recordings_path = os.path.join(folder_path, "recordings")

    # ディレクトリが存在しない場合は作成
    if not os.path.exists(recordings_path):
        os.makedirs(recordings_path)

    # speechディレクトリのパス
    speech_path = os.path.join(folder_path, "speech")
    # speechディレクトリ内の全ファイルを確認
    for file_name in os.listdir(speech_path):
        if pattern.match(file_name):
            print(file_name)
            parts = file_name.split("_")
            id_part = parts[0]
            dir_name = id_part

            # recordings内のターゲットディレクトリ
            target_dir = os.path.join(recordings_path, dir_name)
            ic_recorder_dir = os.path.join(target_dir, "ic_recorder")
            smartphone_dir = os.path.join(target_dir, "smartphone")

            # ターゲットディレクトリが存在しない場合は作成
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            if not os.path.exists(ic_recorder_dir):
                os.makedirs(ic_recorder_dir)
            if not os.path.exists(smartphone_dir):
                os.makedirs(smartphone_dir)

            # ファイルの移動
            source_file = os.path.join(speech_path, file_name)
            if "TL15" in file_name:
                destination_file = os.path.join(ic_recorder_dir, file_name)
            elif ("IP13" in file_name) or ("IP14" in file_name):
                destination_file = os.path.join(smartphone_dir, file_name)
            else:
                raise ValueError(f"Unexpected file name: {file_name}")

            shutil.copyfile(source_file, destination_file)


def main() -> None:
    # このスクリプトが存在するディレクトリのパス
    folder_path = os.path.dirname(os.path.abspath(__file__))
    organize_files(folder_path)


if __name__ == "__main__":
    main()
