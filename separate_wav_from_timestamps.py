import os

import numpy as np
import pandas as pd
from pydub import AudioSegment


def split_wav_from_timestamps(folder_name: str = "recordings") -> None:
    wav_files_full_path = []
    for root, _, files in os.walk(folder_name):
        for file in files:
            if file.lower().endswith(".wav"):
                wav_files_full_path.append(os.path.join(root, file))

    for wav_file in wav_files_full_path:
        timestamps_file = f"{wav_file.split('.')[0]}.txt"

        # オーディオファイルを読み込み、チャンネルを分割した後、サチっていないかつ音量の大きいチャンネルを選択
        audio = AudioSegment.from_wav(wav_file)
        channels = audio.split_to_mono()
        selected_channel = get_louder_and_unsaturated_channel(channels)

        # タイムスタンプに基づいてオーディオを分割
        timestamps_df = pd.read_csv(
            timestamps_file, sep="\t", header=None, names=["start", "end", "sound_type"]
        )
        for _, row in timestamps_df.iterrows():
            start_time = int(row["start"] * 1000)
            end_time = int(row["end"] * 1000)
            segment = selected_channel[start_time:end_time]

            save_folder = "./release"
            machine_type = os.path.dirname(wav_file).split(os.sep)[-1]
            patient_id = os.path.basename(wav_file).split("_")[0]
            output_file_name = (
                f"{save_folder}/{machine_type}/{patient_id}_1_{row['sound_type']}.wav"
            )
            segment.export(output_file_name, format="wav")


def get_louder_and_unsaturated_channel(channels: list[AudioSegment]) -> AudioSegment:
    # RMSレベルに基づいて、より音量の大きいチャンネルを返す
    channels_array = [np.array(channel.get_array_of_samples()) for channel in channels]
    max_possible_value = np.iinfo(channels_array[0].dtype).max
    max_allowed_value = max_possible_value * 0.99
    is_saturated = [
        np.any(np.abs(channel) > max_allowed_value) for channel in channels_array
    ]
    if all(is_saturated):
        raise ValueError("All channels are saturated")
    elif any(is_saturated):
        print(f"Channel {is_saturated.index(True)} is saturated")
        selected_channel_index = is_saturated.index(False)
    else:
        rms_levels = [channel.rms for channel in channels]
        selected_channel_index = np.argmax(rms_levels)
        print(f"rms levels: {rms_levels}, selected channel: {selected_channel_index}")
    return channels[selected_channel_index]


if __name__ == "__main__":
    split_wav_from_timestamps()
