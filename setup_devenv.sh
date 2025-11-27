# setup python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
pip3 install psycopg2-binary

#update the database
flask db merge
flask db upgrade

# run flask server
flask run

# setup vite (ts -> js, module bundler)
flask vite init
flask vite install

# use vite for continuous typescript trasplation while coding. Doesn't work beacause of flask settings
# flask vite start

# use vite for finishing and getting ready to host the app
flask vite build

# for further reference: 
# https://pypi.org/project/flask-vite/
