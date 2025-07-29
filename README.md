# Nighthawks Stats API
Flask and SQLAlchemy-based API backend serving calculated EPA/OPR for all FIRST Tech Challenge teams.
Updates automatically every day at 12:00 AM. 


`Powered by Flask, Postgres and Python 3.12`

## Usage
In order to clone and use the repository locally, you need to:
1) Clone the project as you would any other Git repo
2) Create a `.env` file in the main directory of this project.
3) Inside your `.env` file add your FIRST API username and password in the following format:
```
DATABASE_POSTGRES_URL=[postgres_url]
API_USER=[username]
API_TOKEN=[password]
```
*The postgres URL can be found on Vercel by going to Storage -> Connect -> Quickstart -> .env.local -> DATABASE_URL*

4) From a command line interface in the project directory run `pip install -r requirements.txt` to install the required python dependencies.
5) Run `run.py` to start a local Flask server

## How do I adapt this for new seasons?
In order for statistics to work for new seasons, score data needs to be adopted into the three main categories (Auto, Teleop and Endgame) that FIRST uses.

You can change this by:
1) Clone the repository using the steps above under **Usage**
2) Follow the steps in the [stats-calculator repository](https://github.com/team24124/stats-calculator/blob/main/README.md#updating-for-new-seasons) for updating to new seasons in this project.
2) Follow the steps below on *how to calculate data for all teams at once* in order to **RESET** 
the previous season's database. **DISCLAIMER: THIS OVERRIDES ALL EXISTING DATA**


## How do I calculate all teams at once?
**DISCLAIMER: THIS OVERRIDES ALL EXISTING DATA**

You can recalculate statistics and update your database all at once by:
1) Cloning the repository (See relevant steps above)
2) Running `run.py` to start a local Flask server
3) Navigating to `http://127.0.0.1:5000/api/teams/calculate` to calculate teams.
4) Navigating to `http://127.0.0.1:5000/api/events/calculate` to calculate events.

*Disclaimer a Postgres database is required to be setup in your .env file*
