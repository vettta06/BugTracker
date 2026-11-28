
#!/bin/bash

REQUESTS=200
URL="http://127.0.0.1/health"

for i in $(seq 1 "$REQUESTS"); do
    curl -sS --fail "$URL"
    echo
done | grep -o '"version":"[^"]*"' | sort | uniq -c
