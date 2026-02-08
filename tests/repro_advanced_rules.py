import re

# 1. Deep Recursion
def recursive_function(n):
    if n <= 0:
        return 0
    return 1 + recursive_function(n - 1)

# 2. Inefficient Lookup
def inefficient_lookup():
    my_list = [1, 2, 3, 4, 5]
    for i in range(100):
        if i in my_list: # Violation: list lookup in loop
            print("Found")

# 3. Regex in Loop
def regex_in_loop():
    data = ["a", "b", "c"]
    for item in data:
        pattern = re.compile(r"[a-z]") # Violation: re.compile in loop
        if pattern.match(item):
            print("Match")
