import json
from flask import Flask, render_template, request

class Trie:
    def __init__(self):
        self.end = False
        self.letters = {}

# FLASK
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        trie_root = build_trie()
        game_board = create_board()
        letters_array = flat_and_upper(game_board)
        words_found = find_words(game_board, trie_root)
        answers = dict(sorted(words_found.items(), key=lambda item: len(item[0]), reverse=True))
        post = True
        return render_template("index.html", answers=answers,
                               post=post,
                               letters_array=letters_array)
    return render_template("index.html")

# Helper functions
def flat_and_upper(game_array):
    flat_list = []
    for row in game_array:
        flat_list.extend(row)
    
    flat_list = [x.upper() for x in flat_list]
    return flat_list

def create_board():
    game_board = []
    counter = 1
    for _ in range(5):
        temp_array = []
        for _ in range(5):
            letter = (request.form.get(f"{counter}")).lower()
            temp_array.append(letter)
            counter += 1
        game_board.append(temp_array)
    return game_board

def build_trie():
    trie_root = Trie()
    for i in range(2, 15):
        file_name = f"words/{i}-letter-words.json"
        with open(file_name, encoding="utf-8") as file:
            words = json.load(file)
            for word in words:
                curr_node = trie_root
                curr_word = word['word']
                for letter in curr_word:
                    if letter not in curr_node.letters:
                        curr_node.letters[letter] = Trie()
                    curr_node = curr_node.letters[letter]
                curr_node.end = True
    return trie_root

def find_words(array, trie):
    result = {}
    for row in range(5):
        for col in range(5):
            check_position(row, col, trie, set(), [], array, result)
    return result

def check_position(row, col, node, visited, path, game_board, result):
    if row not in range(5) or col not in range(5) or (row, col) in visited or game_board[row][col] not in node.letters:
        return
    
    curr_node = node.letters[game_board[row][col]]
    visited.add((row, col))
    path.append((row, col))

    if curr_node.end:
        word_list = []
        position_in_numbers = []
        for position in path:
            word_row, word_col = position
            word_list.append(game_board[word_row][word_col])
            position_in_numbers.append(word_row * 5 + word_col + 1)

        word_string = "".join(word_list).capitalize()

        if word_string not in result:
            result[word_string] = position_in_numbers

    neighbours = [(row - 1, col + 1), (row, col + 1), (row + 1, col + 1), 
                    (row - 1, col), (row + 1, col), 
                    (row - 1, col - 1), (row, col - 1), (row + 1, col - 1),]
    
    for neighbour in neighbours:
        neighbour_row, neighbour_col = neighbour
        check_position(neighbour_row, neighbour_col, curr_node, visited, path, game_board, result)
    
    visited.remove((row, col))
    path.pop()