"""
copyright WMMKSLab Gbanyan

modified by wwolfyTC 2019/1/24
"""

# -- record.py --

import time
import threading
import socket
import struct
import re
import os
import sys
from subprocess import call
from enum import Enum, unique
from traceback import print_exc


from aiy.board import Board
from aiy.voice.audio import AudioFormat, play_wav, record_file, Recorder

Lab = AudioFormat(sample_rate_hz=16000, num_channels=1, bytes_per_sample=2)


def record():
    with Board() as board:
        print("請按下按鈕開始錄音.")
        board.button.wait_for_press()
        done = threading.Event()

        board.button.when_pressed = done.set

        def wait():
            start = time.monotonic()
            while not done.is_set():
                duration = time.monotonic() - start
                print("錄音中: %.02f 秒 [按下按鈕停止錄音]" % duration)
                time.sleep(0.5)

        record_file(Lab, filename="recording.wav", wait=wait, filetype="wav")

'''

def main():
    while True:
        record()
        print("播放音檔...")
        play_wav("recording.wav")
'''

# -- mi2s_asr.py --
import base64
import requests

import threading
import pyaudio
import wave
import sys



'''
if __name__ == '__main__':
    url = 'http://140.116.245.149:5002/proxy'
    file_path = 'audio.wav' 
    file_path = 'recording.wav' # added

    with open(file_path, 'rb') as file:
        raw_audio = file.read()

        audio_data = base64.b64encode(raw_audio)
        data = {
            'lang': 'STT for course',
            'token': '2025@ME@asr',
            'audio': audio_data.decode()
        }
        response = requests.post(url, data=data)

    if response.status_code == 200:
        data = response.json()
        print(f"辨識结果: {data['sentence']}")
    else:
        data = response.json()
        print(data)
        print(f"錯誤信息: {data['error']}")
'''





import re

def parse_poker_input(input_str: str) -> str | None:
    """
    Parses a poker card string from format "[SuitName][RankNameInEnglish]"
    to "[SuitNumber][RankValueOrLetter]".

    Args:
        input_str: The input string, e.g., "HeartFour", "SpadeOneThree", "ClubOne".

    Returns:
        The parsed string in the target format, e.g., "24", "1k", "4a",
        or None if the input format is invalid.

    Suit Mapping:
        1 = Spades ♠️
        2 = Hearts ♥️
        3 = Diamonds ♦️
        4 = Clubs ♣️
    """
    # Define mappings
    suit_name_to_number = {
        "黑桃": "1",
        "愛心": "2",
        "菱形": "3",
        "梅花": "4"
    }

    rank_name_to_repr = {
        "一": "a",       # Ace
        "依": "a",       # Ace 
        "醫": "a",       # Ace
        "二": "2",
        "三": "3",
        "四": "4",
        "五": "5",
        "武": "5",
        "舞": "5",
        "六": "6",
        "七": "7",
        "八": "8",
        "九": "9",
        "十": "10",      # Ten is represented as 10
        "時": "10",
        "十一": "j",    # Jack
        "十二": "q",    # Queen
        "十三": "k"   # King
    }

    # Find the suit part
    suit_part = None
    rank_part = None
    suit_number = None

    for suit_name, number in suit_name_to_number.items():
        if input_str.startswith(suit_name):
            suit_part = suit_name
            suit_number = number
            # The rest of the string is the rank part
            rank_part = input_str[len(suit_name):]
            break # Found the suit, stop searching

    # Check if a valid suit was found
    if suit_part is None or suit_number is None:
        print(f"Error: Invalid suit name in input '{input_str}'")
        return None

    # Find the rank representation
    if rank_part in rank_name_to_repr:
        rank_repr = rank_name_to_repr[rank_part]
        return suit_number + rank_repr
    else:
        print(f"Error: Invalid rank name '{rank_part}' in input '{input_str}'")
        return None


"""
# --- Example Usage ---
test_cases = [
    "HeartFour",
    "SpadeOneThree",
    "ClubOne",
    "DiamondTen",
    "SpadeTwo",
    "HeartOneOne",
    "ClubOneTwo",
    "InvalidCard",
    "HeartFifteen",
    "SpadesNine" # Incorrect capitalization for suit
]

for test in test_cases:
    result = parse_poker_input(test)
    print(f'Input: "{test}" -> Output: {result}')

"""

def audio_to_text():
    url = 'http://140.116.245.149:5002/proxy'
    file_path = 'audio.wav' 
    file_path = 'recording.wav' # added

    with open(file_path, 'rb') as file:
        raw_audio = file.read()

        audio_data = base64.b64encode(raw_audio)
        data = {
            'lang': 'STT for course',
            'token': '2025@ME@asr',
            'audio': audio_data.decode()
        }
        response = requests.post(url, data=data)

    if response.status_code == 200:
        data = response.json()
        print(f"辨識结果: {data['sentence']}")
    else:
        data = response.json()
        print(data)
        print(f"錯誤信息: {data['error']}")

    if "跳過" in data['sentence']:
        print("跳過")
        return "skip"
    else :
        result = parse_poker_input(data['sentence'])
        if result is None:
            print("無效的輸入")
            return "skip"
        else:
            print(f"有效的輸入: {result}")
            return result
    


def get_cards_record_parse() -> str:
    total_result= ""
    while True:
        record()
        print("播放音檔...")
        play_wav("recording.wav")
        result = audio_to_text()

        if os.path.exists("recording.wav"):
            os.remove("recording.wav")

        if result == "skip":
            break
        else:
            total_result += result.strip() + " "

    return total_result.strip()

