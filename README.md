# About

A secure web pot of the boardgame "Diplomacy". Supports multiple games, user accounts, secure chat and automatic turn resolution.

## Running the application
Via the release docker image : `docker up`.
The application requires a database to function. See the Database section for more details.
By default, the application is served on port 5173.

## Environment variables:
* `DATABASE_URL` -> The url for the game data database. Must be set up beforehand. See the Database section for more details.
* `SECRET_KEY` -> The key used to encrypt session jvt tokens.
* `DOMAIN` -> The domain name that the app is to be served from. HTTPS only.

## Setting up the database
1. Create an empty database in a database server odf your choice. The release image supports Postgres and SQLite.
2. Create a user that can access and modify the database created in step 1 (if necessary).
3. Set environment variable `DATABASE_URL` to the full url of the database from steps 1-2.
4. Run the app and from the container console run `flask db upgrade`.
5. Repeat step 4 when upgrading to a new major release.

## Game description
Diplomacy is a turn based game, devised by a Harvard student in the middle of the 20th century. 7 players communicate,
plan, strategize, deploy their army and fleet, control territories and conquer supply centers. When a player exerts
authority over more than half of the 34 supply centers, the game is considered over -- the said player being the
victor.




