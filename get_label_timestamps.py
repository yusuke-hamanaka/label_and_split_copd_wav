import os
import tkinter as tk
import wave
from decimal import ROUND_HALF_UP, Decimal
from tkinter import filedialog, ttk
from typing import Any

import numpy as np
import pandas as pd
import os
import wave
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP


def wav2array(wav_file: str) -> tuple:
    with wave.open(wav_file, "rb") as wav:
        nchannels, sampwidth, framerate, nframes, comptype, compname = wav.getparams()
        frames = wav.readframes(nframes)
    frames = np.frombuffer(frames, dtype=np.int16)
    if nchannels == 2:
        left_channel_frames = frames[::2]
        right_channel_frames = frames[1::2]
    else:
        left_channel_frames = frames
        right_channel_frames = None
    return left_channel_frames, right_channel_frames, framerate


class SoundLabeling:
    def __init__(self, wav_file: str) -> None:
        self.wav_file = wav_file
        self.base_dir = os.path.dirname(os.path.dirname(wav_file))
        self.peep_frequencies = [970, 980, 990, 1000, 1010, 1020, 1030]
        self.sound_types = ["text", "a", "i", "u", "e", "o", "cough"]
        self.freq2sound = {
            970: self.sound_types[0],
            980: self.sound_types[1],
            990: self.sound_types[2],
            1000: self.sound_types[3],
            1010: self.sound_types[4],
            1020: self.sound_types[5],
            1030: self.sound_types[6],
        }
        self.df = pd.DataFrame(columns=["start", "end", "sound_type"])
        self.timestamps: dict = {freq: [] for freq in self.peep_frequencies}

    def get_peep_timestamps(self) -> None:
        frames, _, framerate = wav2array(wav_file=self.wav_file)
        block_size = int(framerate * 0.25)
        num_blocks = len(frames) // block_size
        peep_freq_index = 0
        is_peep = 0

        for i in range(num_blocks):
            block = frames[i * block_size : (i + 1) * block_size]
            fft_result = np.fft.fft(block)
            freqs = np.fft.fftfreq(block.size, d=1 / framerate)
            max_fft_idx = np.abs(fft_result).argmax()
            raw_freq_max = abs(freqs[max_fft_idx])
            freq_max = (
                Decimal(str(raw_freq_max / 10)).quantize(
                    Decimal("0"), rounding=ROUND_HALF_UP
                )
                * 10
            )

            if abs(freq_max - self.peep_frequencies[peep_freq_index]) <= 1:
                is_peep += 1

            if is_peep == 2:
                self.timestamps[self.peep_frequencies[peep_freq_index]].append(i * block_size / framerate)
                is_peep = 0
                peep_freq_index = (peep_freq_index + 1) % len(self.peep_frequencies)

        self.timestamps[self.peep_frequencies[0]].append(len(frames) / framerate)

    def timestamp_to_df(self) -> None:
        print(self.timestamps)
        for i in range(3):  # 3回の録音分処理を繰り返す
            for freq in self.peep_frequencies:
                start_freq = freq
                end_freq = self.peep_frequencies[(self.peep_frequencies.index(freq) + 1) % len(self.peep_frequencies)]
                sound_type = self.freq2sound[freq]
                if self.timestamps[start_freq] and self.timestamps[end_freq]:
                    start_time = self.timestamps[start_freq][0]
                    end_time = self.timestamps[end_freq][0] - 0.25
                    self.df = pd.concat(
                        [
                            self.df,
                            pd.DataFrame(
                                [
                                    [start_time, end_time, f"{sound_type}_{i + 1:02d}"]
                                ],
                                columns=["start", "end", "sound_type"],
                            ),
                        ],
                        ignore_index=True,
                    )
                    self.timestamps[start_freq].pop(0)

        txt_file_path = f"{self.wav_file.split('.')[0]}_tmp.txt"
        self.df.to_csv(txt_file_path, sep="\t", index=False, header=False)

class ProgressBarWindow(tk.Toplevel):
    def __init__(self, master: Any, total_files: Any):
        super().__init__(master)
        self.title("処理中")

        self.label = tk.Label(self, text="ファイル処理中...")
        self.label.pack(padx=10, pady=10)

        self.progress = ttk.Progressbar(
            self,
            orient="horizontal",
            length=300,
            mode="determinate",
            maximum=total_files,
        )
        self.progress.pack(padx=10, pady=10)

        self.button = tk.Button(self, text="キャンセル", command=self.destroy)
        self.button.pack(pady=10)

    def update_progress(self, value: Any) -> None:
        self.progress["value"] = value
        self.update()


class SoundLabelingApp:
    def __init__(self, master: Any) -> None:
        self.master = master
        master.title("Sound Labeling App")

        self.label = tk.Label(
            master, text="WAVファイルのあるフォルダを選択してください"
        )
        self.label.pack(padx=10, pady=10)

        self.select_folder_button = tk.Button(
            master, text="フォルダ選択", command=self.select_and_process_folder
        )
        self.select_folder_button.pack(pady=10)

    def select_and_process_folder(self) -> None:
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.make_label_file(folder_selected)

    def make_label_file(self, folder_path: str) -> None:
        wav_files_full_path = []

        # os.walkを使用してディレクトリを再帰的に探索
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".wav"):
                    # フルパスをwav_filesに追加
                    wav_files_full_path.append(os.path.join(root, file))
        total_files = len(wav_files_full_path)
        print(wav_files_full_path)

        # プログレスバーを含む新しいウィンドウを開く
        progress_window = ProgressBarWindow(self.master, total_files)

        for i, wav_file_path in enumerate(wav_files_full_path, start=1):
            print(f"Processing {wav_file_path}...")
            sl = SoundLabeling(wav_file_path)
            sl.get_peep_timestamps()
            sl.timestamp_to_df()
            print(f"Completed {wav_file_path}")

            # プログレスバーを更新
            progress_window.update_progress(i)

        # 処理が完了したら、プログレスバーウィンドウを閉じる
        progress_window.destroy()


def main() -> None:
    root = tk.Tk()
    app = SoundLabelingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
