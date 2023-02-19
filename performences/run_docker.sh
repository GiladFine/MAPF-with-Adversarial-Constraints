
COMMAND=$(python performences/performence.py $1 $2 $3)
docker run --rm -it -v/home/dsi/giladfine/:/gilad python:gilad COMMAND
