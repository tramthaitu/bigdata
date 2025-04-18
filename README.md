mkdir BIGDATA_UEH

git clone https://github.com/tuankhoi25/bigdata.git

cd bigdata/

mkdir logs/ plugins/ data/

cd data/

mkdir mongodb/ postgres_data/

cd ..

docker compose up


docker exec -it mongodb bash

mongosh "mongodb://mongodb:mongodb@localhost:27017/crypto_db?authSource=admin"

db.crypto_history.countDocuments()