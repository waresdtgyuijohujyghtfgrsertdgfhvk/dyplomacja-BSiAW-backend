# Setup

## Seting up database
1. `sudo -u postgres psql`
2. `CREATE DATABASE diplomats`
3. `flaks db migrate -m "initial migrate"`
4. `flask db upgrade`

## Runnung app
`flask run`
Diplomacy is a turn based game, devised by a Harvard student in the middle of the 20th century. 7 players communicate,
plan, strategize, deploy their army and fleet, control territories and conquer supply centers. When a player exerts
authority over more than half of the 34 supply centers, the game is considered over -- the said player being the
victor.

