set -e

PYTHONANYWHERE_USERNAME="lwl501"

# Variables
GLOBAL_BAK=../frontend/src/global_old.bak
GLOABL_JSX=../frontend/src/global.jsx

# fronend
cat $GLOABL_JSX > $GLOBAL_BAK
cat ./_global.jsx > $GLOABL_JSX

cd ../frontend
./deploy.sh
cd ../production_custom

# production
rm -rf ./website website.zip
mkdir website

cp -r ../backend/* ./website

rm -rf ./website/env || true
rm -rf ./website/__pycache__ || true
rm -rf ./website/audio || true
rm     ./website/results/*.pkl || true

sed -i "s/\"\" #B700/\"\/home\/${PYTHONANYWHERE_USERNAME}\/website\/\"/g" ./website/config.py 

zip -s 90M -r website.zip website
echo "[*] website.zip created!"

rm -rf website
cat $GLOBAL_BAK > $GLOABL_JSX
rm $GLOBAL_BAK || true