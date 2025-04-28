from itertools import combinations
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import random
import PokerInput
import ultrasonic_oled

# ----------- 基礎牌物件與解析 ----------- #
class Card:
    def __init__(self, suit, rank):  # suit: 1~4, rank: 2~14
        self.suit = suit
        self.rank = rank

    def __eq__(self, other): return self.suit == other.suit and self.rank == other.rank
    def __hash__(self): return hash((self.suit, self.rank))
    def __repr__(self):
        suit_map = {1: '1', 2: '2', 3: '3', 4: '4'}
        rank_map = {11: 'j', 12: 'q', 13: 'k', 14: 'a'}
        return f"{suit_map[self.suit]}{rank_map.get(self.rank, str(self.rank))}"

def parse_card(text):
    suit_map = {'1': 1, '2': 2, '3': 3, '4': 4}
    rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                '8': 8, '9': 9, 't': 10, 'j': 11, 'q': 12, 'k': 13, 'a': 14}
    text = text.lower()
    suit = suit_map[text[0]]
    rank = rank_map[text[1]]
    return Card(suit, rank)

def build_deck(): return [Card(s, r) for s in range(1, 5) for r in range(2, 15)]

# ----------- 牌型評估 ----------- #
def evaluate_hand(cards):
    ranks = [c.rank for c in cards]
    suits = [c.suit for c in cards]
    suit_groups = {}
    for card in cards:
        suit_groups.setdefault(card.suit, []).append(card.rank)

    flush_suit, flush_ranks = None, []
    for s, rs in suit_groups.items():
        if len(rs) >= 5:
            flush_suit = s
            flush_ranks = sorted(rs, reverse=True)
            break

    if flush_suit:
        unique_flush = sorted(set(flush_ranks), reverse=True)
        if 14 in unique_flush: unique_flush.append(1)
        for i in range(len(unique_flush) - 4):
            if unique_flush[i] - unique_flush[i+4] == 4:
                return (9,) if unique_flush[i] == 14 else (8, unique_flush[i])

    unique_ranks = sorted(set(ranks), reverse=True)
    if 14 in unique_ranks: unique_ranks.append(1)
    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i] - unique_ranks[i+4] == 4:
            return (4, unique_ranks[i])

    count = Counter(ranks)
    most = count.most_common()
    if most[0][1] == 4:
        kicker = max(r for r in ranks if r != most[0][0])
        return (7, most[0][0], kicker)
    if most[0][1] == 3 and most[1][1] >= 2:
        return (6, most[0][0], most[1][0])
    if flush_suit:
        return (5, *flush_ranks[:5])
    if most[0][1] == 3:
        kick = sorted((r for r in ranks if r != most[0][0]), reverse=True)
        return (3, most[0][0], *kick[:2])
    if most[0][1] == 2 and most[1][1] == 2:
        high, low = sorted([most[0][0], most[1][0]], reverse=True)
        kicker = max(r for r in ranks if r != high and r != low)
        return (2, high, low, kicker)
    if most[0][1] == 2:
        kick = sorted((r for r in ranks if r != most[0][0]), reverse=True)
        return (1, most[0][0], *kick[:3])
    return (0, *sorted(ranks, reverse=True)[:5])

# ----------- 多執行緒模擬 ----------- #
def simulate_worker(hero_cards, board_cards, deck_snapshot, simulations):
    win = tie = total = 0
    for _ in range(simulations):
        if len(deck_snapshot) < 2:
            continue
        opp = random.sample(deck_snapshot, 2)
        remain = [c for c in deck_snapshot if c not in opp]

        if len(board_cards) < 5:
            try:
                extra_board = random.sample(remain, 5 - len(board_cards))
            except:
                continue
            full_board = board_cards + extra_board
        else:
            full_board = board_cards

        my_score = evaluate_hand(hero_cards + full_board)
        opp_score = evaluate_hand(opp + full_board)
        if my_score > opp_score:
            win += 1
        elif my_score == opp_score:
            tie += 1
        total += 1
    return win, tie, total

def simulate_with_partial_board(hero_cards, board_cards, simulations=100000, threads=4):
    used = set(hero_cards + board_cards)
    full_deck = [c for c in current_deck if c not in used]

    sims_per_thread = simulations // threads
    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(simulate_worker, hero_cards, board_cards, full_deck, sims_per_thread)
            for _ in range(threads)
        ]
        for f in futures:
            results.append(f.result())

    total_win = sum(r[0] for r in results)
    total_tie = sum(r[1] for r in results)
    total = sum(r[2] for r in results)

    return total_win / total if total else 0, total_tie / total if total else 0

# ----------- 牌堆管理 ----------- #
current_deck = set()

def reset_deck():
    global current_deck
    current_deck = set(build_deck())

def remove_used_cards(cards):
    global current_deck
    for c in cards:
        current_deck.discard(c)

# ----------- 主流程 ----------- #
if __name__ == "__main__":
    reset_deck()

    while True:
        cmd = input("請輸入指令（zero 重洗 / 其他跳過）：").strip().lower()
        if cmd == "zero":
            reset_deck()
            print(">> 整副牌已重置")
        else:
            print(">> 使用剩餘牌繼續")

        #hero_input = input("請輸入你的兩張手牌（例如 2k 3a）：").strip().split()
        hero_input = PokerInput.get_cards_record_parse().strip().split()
        #board_input = input("請輸入公共牌（0～5 張，例如 1q 3t 4a）：").strip().split()
        board_input = PokerInput.get_cards_record_parse().strip().split()

        try:
            hero_cards = [parse_card(c) for c in hero_input]
            board_cards = [parse_card(c) for c in board_input]
            if len(hero_cards) != 2 or len(board_cards) > 5:
                raise ValueError()
        except:
            print("!! 輸入格式錯誤，請用正確格式（例如 2a, 3k）")
            continue

        print(f">> 模擬中（手牌 + {len(board_cards)} 張公共牌，模擬 1000000 次 × 4 threads）...")
        win, tie = simulate_with_partial_board(hero_cards, board_cards, simulations=1000000, threads=4)
        print(f">> 勝率：{win:.4%}，平手率：{tie:.4%}")
        ultrasonic_oled.main()
        ultrasonic_oled.display_text(f"{win:.1%}, {tie:.1%}")

        remove_used_cards(hero_cards + board_cards)
