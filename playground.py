import json

t: dict = json.loads('{"some": 21, "inte": "inter"}')
f = {"some": 0, "inte": ""}

for k, v in t.items():
    print(k, v)

print(t)
print(f)