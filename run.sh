# pull latest image
docker pull docker.io/searxng/searxng:latest

# remove old container 
docker rm -f searxng

# run
docker run --name searxng -d \
    -p 8888:8080 \
    -v "./config/:/etc/searxng/" \
    -v "./data/:/var/cache/searxng/" \
    docker.io/searxng/searxng:latest

# open search page
open http://localhost:8888
