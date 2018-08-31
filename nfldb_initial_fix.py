# This script is to be used when initially setting up nfldb
# The nfldb module is no longer supported by its creator so some updates to the db will need to be performed before it will properly update


# JAC to JAX fix
# StL to LAR fix
# SD to LAC fix
# Update schedule to include full 2017 season

#import modules
import nfldb
import psycopg2
import nflgame.update_sched

#create connection and cursor object
db = nfldb.connect()
cur = db.cursor()

#Update Team IDs

#Create dictionary for each team needing update
JAX = {'team_id':'JAX', 'city': 'Jacksonville', 'name':'Jaguars'}
LAC = {'team_id':'LAC', 'city': 'Los Angeles', 'name':'Chargers'}
LAR = {'team_id':'LAR', 'city': 'Los Angeles', 'name':'Rams'}

#Create iterable list of teams
team_ids = [JAX,LAC,LAR]

for team in team_ids:
	result = []
	while result == []:
		#check db for team info to make sure it hasn't already been added
		search_sql = "select team_id from team where team_id = %s"
		query = cur.execute(search_sql, [team['team_id']])
		result = cur.fetchall()
		print cur.query
		if result == [] :
			#add team info to db
			print "No Result"
			insert_sql = "insert into team values(%s, %s, %s)"
			cur.execute(insert_sql,[team['team_id'], team['city'], team['name']])
			db.commit()
			print cur.query
		else:
			print result