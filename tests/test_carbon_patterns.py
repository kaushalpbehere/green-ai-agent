"""
Test file to validate carbon calculation against real code patterns.
This demonstrates the carbon impact of different violations.
"""

# PATTERN 1: Nested loops (CRITICAL - O(n³))
# Energy impact: 100x+ normal loops
def inefficient_search(data, target):
    """Example of highly inefficient nested loop."""
    for i in range(len(data)):          # n iterations
        for j in range(len(data)):       # n iterations  
            for k in range(len(data)):   # n iterations
                if data[i][j][k] == target:  # Total: n³ = 1,000,000 iterations!
                    return (i, j, k)
    return None

# PATTERN 2: Redundant computation in loop (CRITICAL)
# Energy impact: 10-100x waste
def inefficient_string_parsing(data):
    """Expensive operation repeated in loop."""
    import re
    pattern = re.compile(r'\w+')  # Should be outside!
    results = []
    for line in data:
        pattern = re.compile(r'\w+')  # WASTEFUL: Recompile 1000x
        results.append(pattern.findall(line))
    return results

# PATTERN 3: Memory inefficiency (HIGH)
# Energy impact: 2-3x more energy
def load_entire_file(filename):
    """Loads entire file into memory at once."""
    with open(filename, 'r') as f:
        data = f.readlines()  # All lines at once: 2-3x energy
        # Process all...
    return data

# PATTERN 4: I/O in loop (CRITICAL)  
# Energy impact: 1000x+ per I/O
def inefficient_db_query(user_ids):
    """N+1 query problem: multiple DB hits."""
    results = []
    for user_id in user_ids:  # 1000 iterations
        user = query_database(f"SELECT * FROM users WHERE id={user_id}")  # 1000 queries!
        results.append(user)
    return results

# PATTERN 5: Unused variables (MEDIUM)
# Energy impact: Small per variable
def function_with_waste(data):
    """Variables that don't contribute."""
    unused_var = expensive_computation()  # Computed but never used!
    temp = []
    for item in data:
        temp.append(item * 2)
    
    unused_var2 = sum([x**2 for x in data])  # Never used
    
    return temp

# PATTERN 6: Resource leak (HIGH)
# Energy impact: Persistent resource consumption
def file_not_closed(filename):
    """File handle not properly closed."""
    f = open(filename)  # Never closed - resource leak!
    data = f.read()
    # If exception occurs, file stays open
    return data

# PATTERN 7: Algorithm complexity (HIGH)
# Energy impact: O(n²) vs O(n) = huge for large data
def inefficient_lookup(haystack, needles):
    """Using inefficient search in loop."""
    results = []
    for needle in needles:
        # list.index() is O(n) - total O(n*m)
        # Should use set: O(1) - total O(n+m)
        idx = haystack.index(needle)  
        results.append(idx)
    return results

# PATTERN 8: String concatenation in loop (MEDIUM)
# Energy impact: O(n²) memory allocations
def build_string_badly(words):
    """Concatenating strings creates new objects each time."""
    result = ""
    for word in words:
        result += word  # Creates new string object 1000x
    return result

# PATTERN 9: High cyclomatic complexity (MEDIUM)
# Energy impact: More branches = more CPU
def high_complexity_function(a, b, c, d, e, f):
    """Too many decision points."""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            return "all positive"
                        else:
                            return "f is negative"
                    else:
                        return "e is negative"
                else:
                    return "d is negative"
            else:
                return "c is negative"
        else:
            return "b is negative"
    else:
        return "a is negative"

# PATTERN 10: Blocking I/O (HIGH for I/O heavy)
# Energy impact: CPU wasted waiting for I/O
def blocking_http_request(urls):
    """Synchronous I/O blocks execution."""
    import requests
    results = []
    for url in urls:
        # Blocks until request completes
        response = requests.get(url)  # One at a time: inefficient
        results.append(response.text)
    return results

# PATTERN 11: Inefficient data structure (HIGH)
# Energy impact: O(n) lookups vs O(1)
def inefficient_membership_test(data, queries):
    """Using list for membership testing."""
    # list.count() and list.index() are O(n)
    results = []
    for query in queries:
        if query in data:  # O(n) lookup, should be O(1)
            results.append(data.index(query))  # O(n) lookup
    return results

# PATTERN 12: Dead code (LOW)
# Energy impact: Compiled and loaded into memory
def function_with_dead_code():
    """Unreachable code still consumes memory."""
    result = calculate_important_thing()
    return result
    
    # This code is never executed but still loaded
    unused_function()
    another_unused_call()

# GREEN PATTERNS (for reference)
# ================================

def efficient_search_green(data, target):
    """Use set lookup instead of nested loops."""
    data_set = set(data)  # O(n) conversion
    return target in data_set  # O(1) lookup

def efficient_string_parsing_green(data):
    """Compile pattern once, outside loop."""
    import re
    pattern = re.compile(r'\w+')  # Compiled once
    results = []
    for line in data:
        results.append(pattern.findall(line))  # Reused pattern
    return results

def efficient_file_reading_green(filename):
    """Stream processing instead of loading all."""
    results = []
    with open(filename, 'r') as f:
        for line in f:  # Generator: O(line_length) memory
            results.append(process(line))
    return results

def efficient_db_query_green(user_ids):
    """Batch query instead of N+1."""
    # Single query: 1 call instead of 1000
    users = query_database(f"SELECT * FROM users WHERE id IN ({','.join(user_ids)})")
    return users

def efficient_string_building_green(words):
    """Use join() for efficient concatenation."""
    # O(n) instead of O(n²)
    return ''.join(words)

def efficient_async_io_green(urls):
    """Parallel async I/O instead of sequential."""
    import asyncio
    import aiohttp
    async def fetch_all():
        async with aiohttp.ClientSession() as session:
            tasks = [session.get(url) for url in urls]
            return await asyncio.gather(*tasks)
    
    return asyncio.run(fetch_all())
