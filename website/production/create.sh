set -e

PYTHONANYWHERE_USERNAME="lwl501"

# Variables
GLOBAL_BAK=../frontend/src/global_old.bak
GLOBAL_JSX=../frontend/src/global.jsx

# frontend
cat $GLOBAL_JSX > $GLOBAL_BAK
cat ./_global.jsx > $GLOBAL_JSX

cd ../frontend
./deploy.sh
cd ../production

# production
rm -rf ./website website.zip
mkdir website

cp -r ../backend/* ./website

rm -rf ./website/env || true
rm -rf ./website/__pycache__ || true
rm     ./website/results/*.pkl || true

sed -i "s/\"\" #B700/\"\/home\/${PYTHONANYWHERE_USERNAME}\/website\/\"/g" ./website/config.py 

zip -s 90M -r website.zip website
echo "[*] website.zip created!"

rm -rf website
cat $GLOBAL_BAK > $GLOBAL_JSX
rm $GLOBAL_BAK || true
