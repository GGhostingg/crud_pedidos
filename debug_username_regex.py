import re
pattern = r'^[A-Za-z0-9 @.+_-]+$'
tests = ['Luis Mesa', 'Luis', 'Luis_Mesa', 'Luis.Mesa', 'Luis+Mesa', 'Luis-Mesa', 'Luis@Mesa']
for u in tests:
    print(u, bool(re.match(pattern, u)))
