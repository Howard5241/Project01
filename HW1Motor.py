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
from typing import List

def split_card_string(card_string: str) -> List[str]:
       
        if not card_string:
            return []

        # Define patterns for suits and ranks using regular expressions
        # Using non-capturing groups (?:...) inside for clarity, but capturing the whole card.
        suit_pattern = "(愛心|菱形|黑桃|梅花)"
        rank_pattern = "(十一|十二|十三|二|三|四|五|六|七|八|九|十|一)"

        # Create the regex pattern for a single card (Suit followed by Rank).
        # The outer parenthesis captures the entire "SuitRank" string.
        # We use re.compile for slightly better performance if used repeatedly.
        card_pattern_regex = re.compile(f"({suit_pattern}{rank_pattern})")

        # Use findall to get all non-overlapping matches.
        # When the pattern has capturing groups, findall returns a list of tuples,
        # where each tuple contains the strings matched by the groups.
        # Example: for input "HeartFour", findall returns [('HeartFour', 'Heart', 'Four')]
        matches = card_pattern_regex.findall(card_string)

        # We are interested in the full match for each card, which is the first element
        # in each tuple returned by findall (corresponding to the outermost capturing group).
        result = [match[0] for match in matches]

        # --- Validation ---
        # Check if the concatenated matches perfectly reconstruct the original string.
        # This ensures the input string *only* contained valid, contiguous cards
        # and adheres strictly to the [Suit][Rank]* format.
        if "".join(result) != card_string:
            raise ValueError(
                f"Input string '{card_string}' is not a valid sequence of SuitRank cards."
                " Check for typos, invalid suits/ranks, or extra characters."
            )
        # --- End Validation ---

        return result

        
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
    total_result= ""
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
        cards_result = split_card_string(data['sentence'])
        for card in cards_result:
            result = parse_poker_input(card)
            if result is None:
                print("無效的輸入")
                return "skip"
            else:
                print(f"有效的輸入: {result}")
                total_result += result + " "
    return total_result.strip()
    


def get_cards_record_parse() -> str:
    
    record()
    print("播放音檔...")
    play_wav("recording.wav")
    result = audio_to_text()
    

    if os.path.exists("recording.wav"):
        os.remove("recording.wav")


    return result

# -- dcmotor4.py --
import sys
import time
import RPi.GPIO as GPIO
 
GPIO.setmode(GPIO.BCM)
 
STEPS_PER_REVOLUTION = 32 * 64
SEQUENCE = [[1, 0, 0, 0], 
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 1]]
SEQUENCE2 = SEQUENCE[::-1]

STEPPER_PINS = [17,18,27,22]
for pin in STEPPER_PINS:
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, GPIO.LOW)
 
SEQUENCE_COUNT = len(SEQUENCE)
PINS_COUNT = len(STEPPER_PINS)
 
sequence_index = 0
direction = 1
steps = 0
 
wait_time = 10/float(1000)
 

def move_motor(direction:int):

    if direction == 1:
        sequence_used = SEQUENCE
    else:
        sequence_used = SEQUENCE2

    try:
        print('按下 Ctrl-C 可停止程式')
        while True:
            for pin in range(0, PINS_COUNT):
                GPIO.output(STEPPER_PINS[pin], sequence_used[sequence_index][pin])
    
            steps += direction
            if steps >= STEPS_PER_REVOLUTION:
                direction = -1
            elif steps < 0:
                direction = 1
    
            sequence_index += direction
            sequence_index %= SEQUENCE_COUNT
    
            print('index={}, direction={}'.format(sequence_index, direction))
            time.sleep(wait_time)
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        GPIO.cleanup()




record()
print("播放音檔...")
play_wav("recording.wav")
result = audio_to_text()
if "順" in result:
    print("順時針")
    move_motor(1)
elif "逆" in result:
    print("逆時針")
    move_motor(-1)