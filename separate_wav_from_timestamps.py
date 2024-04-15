from pydub import AudioSegment
import numpy as np
import pandas as pd


def split_wav_from_timestamps(file_name_wo_ext: str, ):
    wav_file = f"recordings/{file_name_wo_ext}.WAV"
    timestamps_file = f"timestamps/{file_name_wo_ext}.txt"

    channels = load_and_split_channels(wav_file)
    selected_channel = get_louder_and_unsaturated_channel(channels)
    timestamps_df = pd.read_csv(timestamps_file, sep='\t', header=None, names=["start", "end", "sound_type"])

    for _, row in timestamps_df.iterrows():
        start_time = int(row['start'] * 1000)  # milliseconds
        end_time = int(row['end'] * 1000)      # milliseconds
        
        # タイムスタンプに基づいてオーディオを分割
        segment = selected_channel[start_time:end_time]
        
        # 分割されたセグメントをファイルに保存
        output_file_name = f"{row['sound_type']}_{int(row['start'])}_{int(row['end'])}.wav"
        segment.export(output_file_name, format="wav")

def load_and_split_channels(wav_file):
    audio = AudioSegment.from_wav(wav_file)
    # ステレオトラックの場合、チャンネルを分割
    channels = audio.split_to_mono()
    return channels

def get_louder_and_unsaturated_channel(channels):
    # RMSレベルに基づいて、より音量の大きいチャンネルを返す
    channels_array = [np.array(channel.get_array_of_samples()) for channel in channels]
    max_possible_value = np.iinfo(channels_array[0].dtype).max
    max_allowed_value = max_possible_value * 0.99
    is_saturated = [np.any(np.abs(channel) > max_allowed_value) for channel in channels_array]
    if all(is_saturated):
        raise ValueError('All channels are saturated')
    elif any(is_saturated):
        print(f"Channel {is_saturated.index(True)} is saturated")
        selected_channel_index = is_saturated.index(False)
    else:
        rms_levels = [channel.rms for channel in channels]
        selected_channel_index = np.argmax(rms_levels)
        print(f"rms levels: {rms_levels}, selected channel: {selected_channel_index}")
    return channels[selected_channel_index]


split_wav_from_timestamps("240219_05")

