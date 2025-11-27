# Setup

## Seting up database
1. `sudo -u postgres psql`
2. `CREATE DATABASE diplomats`
3. `flaks db migrate -m "initial migrate"`
4. `flask db upgrade`

## Runnung app
`flask run`