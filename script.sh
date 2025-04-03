#!/bin/bash

# On simule la requete effectuée par le navigateur(F12) pour récupérer les données
URL="https://api.londonstockexchange.com/api/v1/components/refresh"
DATA='{"path":"ftse-index","parameters":"indexname%3Dftse-100","components":[{"componentId":"block_content%3Aab7ff856-2875-48b9-a01a-33faefc45062","parameters":""},{"componentId":"block_content%3Adabc61a4-85a1-4ca1-816a-164bc7b79dd8","parameters":""},{"componentId":"block_content%3Ade3cfa38-4389-4729-93b7-6a35ac11ff4a","parameters":""},{"componentId":"block_content%3Aad7502b0-91e6-46a8-ac93-56877c3d2c44","parameters":""}]}'

# Récupération de la réponse via curl
INFO=$(curl -s "$URL" \
  -H 'accept: application/JSON, text/plain, */*' \
  -H 'accept-language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/JSON' \
  -H 'origin: https://www.londonstockexchange.com' \
  -H 'priority: u=1, i' \
  -H 'referer: https://www.londonstockexchange.com/' \
  -H 'sec-ch-ua: "Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36' \
  --data-raw "$DATA")

# Extraction des différentes valeurs depuis le bloc "ftseticker"
PRICE=$(echo "$INFO" | grep -oP '"name":"FTSE 100","description":"FTSE 100","value":\K[0-9]+\.[0-9]+' | head -n1 | tr -d '\n')
PERCENT=$(echo "$INFO" | grep -oP '"name":"FTSE 100","description":"FTSE 100".*?"percentualchange":\K-?[0-9]+\.[0-9]+' | head -n1 | tr -d '\n')
NETCHANGE=$(echo "$INFO" | grep -oP '"name":"FTSE 100","description":"FTSE 100".*?"netchange":\K-?[0-9]+\.[0-9]+' | head -n1 | tr -d '\n')
HIGH=$(echo "$INFO" | grep -oP '"name":"FTSE 100","description":"FTSE 100".*?"high":\K[0-9]+\.[0-9]+' | head -n1 | tr -d '\n')
LOW=$(echo "$INFO" | grep -oP '"name":"FTSE 100","description":"FTSE 100".*?"low":\K[0-9]+\.[0-9]+' | head -n1 | tr -d '\n')

# Récupération de la date et l'heure actuelles
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

CSVFILE="./data.csv"
if [ ! -f "$CSVFILE" ]; then
    echo "Timestamp,Price,PercentChange,NetChange,High,Low" > "$CSVFILE"
fi

# Sauvegarde des info
echo "$TIMESTAMP,$PRICE,$PERCENT,$NETCHANGE,$HIGH,$LOW" >> "$CSVFILE"
