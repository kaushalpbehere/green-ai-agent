def calculate_sum(n):
    # Inefficient loop (should be detected)
    total = 0
    for i in range(n):
        total += i
    return total

def infinite_loop():
    # Infinite loop (critical violation)
    while True:
        print("Looping...")
