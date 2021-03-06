#This module defines analytics to be used in NFLdb FF Digest

#Import neccessary modules
import nfldb
import psycopg2
import pandas as pd
import numpy as np


#create connection and cursor object
db = nfldb.connect()
cur = db.cursor()

#set display columns to 10
pd.set_option('display.max_columns', 10)

#	RBS? Or maybe have call require position?
#	(Week, Season)
#Top Fantasy Points
#Top Fantasy Points Change
#Top Rushing Yds
#Top Receiving Yds
#Top Carries +
#Top Carries Change
#Top Targets +
#Top Targets Change
#Top Receptions +
#Top Receptions Change
#Top Yards Per Carry +
#Top Yards Per Target +
#Top Yards Per Reception + 
#Top Yards After Catch +
#Top Number First Downs +
#Top Number Third Down Targets (not yet)
#Top Number Third Down Touches (not yet)
#Top Red Zone Carries (not yet)
#Top Red Zone Targets (not yet)
#Top Goal Line Carries (not yet)
#Top Goal Line Targets (not yet)

#Top % of Snaps
#Top % of 1st Down Snaps
#Top % of 2nd Down Snaps
#Top % of 3rd Down Snaps
#Top % of 4th Down Snaps
#Top Yards After First Contact



#Get Raw Data From Source
#Create Aggregate Table by player_id and gsis_id (game_id)
#	e.g. player_id, gsis_id, week, year, fantasy_pts, attempts, etc...


primary_stats_all = ['rushing_att','rushing_yds','rushing_tds','receiving_rec','receiving_yds','receiving_tds']
primary_stats_rush = ['rushing_att','rushing_yds','rushing_tds']
primary_stats_rec = ['receiving_rec','receiving_yds','receiving_tds']
all_stats = {'total_yds':{'RB':primary_stats_all,'WR':primary_stats_all}, 'total_tds':{'RB':primary_stats_all,'WR':primary_stats_rec},'first_down':{'RB':primary_stats_all,'WR':primary_stats_rec},'rushing_att':{'RB':primary_stats_rush,'WR':primary_stats_rush},'rushing_yds':{'RB':primary_stats_rush,'WR':primary_stats_rush},'yards_per_carry':{'RB':primary_stats_rush,'WR':primary_stats_rush},'receiving_tar':{'RB':primary_stats_all,'WR':primary_stats_rec},'receiving_rec':{'RB':primary_stats_all,'WR':primary_stats_rec},'receiving_yds':{'RB':primary_stats_all,'WR':primary_stats_rec},'yards_per_tar':{'RB':primary_stats_all,'WR':primary_stats_rec},'yards_per_rec':{'RB':primary_stats_all,'WR':primary_stats_rec},'avg_depth_of_tar':{'RB':primary_stats_all,'WR':primary_stats_rec},'receiving_yac_yds':{'RB':primary_stats_all,'WR':primary_stats_rec}}



def create_player_agg_total(year, position, week = 0, season_type = 'Regular'):
	
	year = (year)
	position = (position)
	season_type = (season_type)
	player_sql = '''select 
			pp.gsis_id,
			g.week,
			g.season_year as year,
			g.season_type,
			pp.player_id,
			pr.full_name,
			pr.position,
			pp.team,
			pp.play_id,
			p.time,
			p.pos_team,
			p.yardline,
			p.down,
			p.yards_to_go,
			p.description,
			p.first_down,
			p.passing_first_down,
			p.penalty,
			p.rushing_first_down,
			p.third_down_att,
			p.third_down_conv,
			p.third_down_failed,
			ag.passing_cmp_air_yds,
			ag.passing_incmp_air_yds,
			pp.receiving_rec,
			pp.receiving_tar,
			pp.receiving_tds,
			pp.receiving_twopta,
			pp.receiving_twoptm,
			pp.receiving_twoptmissed,
			pp.receiving_yac_yds,
			pp.receiving_yds,
			pp.rushing_att,
			pp.rushing_loss,
			pp.rushing_loss_yds,
			pp.rushing_tds,
			pp.rushing_twopta,
			pp.rushing_twoptm,
			pp.rushing_twoptmissed,
			pp.rushing_yds
		from play_player pp
			inner join play p
				on pp.gsis_id = p.gsis_id
				and pp.play_id = p.play_id
			inner join game g
				on g.gsis_id = pp.gsis_id
			inner join player pr
				on pr.player_id = pp.player_id
			inner join agg_play ag
				on ag.play_id = p.play_id
				and ag.gsis_id = p.gsis_id
				and ag.drive_id = p.drive_id
		where pp.team = p.pos_team
			and g.season_type in (%(type)s)
			and g.season_year in (%(year)s)
			and pr.position in (%(pos)s)
		'''
		
	player_df = pd.read_sql(player_sql, db, params = {'type':season_type, 'year':year, 'pos':position})

#Need to add (third_down_tar, third_down_carry, third_down_touch, red_zone_carry, red_zone_tar, red_zone_rec, goal_line_carry, goal_line_target, goal_line_rec)
	#player_df['depth_of_rec'] = player_df['receiving_yds'] - player_df['receiving_yac_yds']
	player_df['total_yds'] = player_df['receiving_yds'] + player_df['rushing_yds']
	player_df['depth_of_tar'] = player_df['passing_cmp_air_yds'] + player_df['passing_incmp_air_yds']
	player_df['total_tds'] = player_df['rushing_tds'] + player_df['receiving_tds']
	
	if week > 0:
		player_df = player_df[player_df.week == week]

	agg_df = player_df.groupby(['full_name', 'team','year','week']).aggregate(np.sum)
	
	agg_df['yards_per_carry'] = agg_df['rushing_yds']/agg_df['rushing_att']
	agg_df['yards_per_tar'] = agg_df['receiving_yds']/agg_df['receiving_tar']
	agg_df['avg_depth_of_tar'] = agg_df['depth_of_tar']/agg_df['receiving_tar']
	agg_df['yards_per_rec'] = agg_df['receiving_yds']/agg_df['receiving_rec']
	agg_df['avg_depth_of_rec'] = agg_df['depth_of_tar']/agg_df['receiving_rec']
	
	
	return agg_df
	
	
def get_weekly_stat(year, week, position, stat, season = 'Regular'):
	
	#I'm thinking I might want to do stats by Call Stat instead of by position
	
	positional_stats = {'RB':[stat,primary_stats_rush], 'WR':[stat, primary_stats_rec]} #stats you always want to see for a given position
	
	#columns = [y for y in positional_stats[position]]
	columns = [x for x in all_stats[stat][position] if x != stat]
	
	columns.insert(0, stat)
	
	stat_df = create_player_agg_total(year, position, week, season).sort_values(by=stat, ascending = False)

	stat_df = stat_df[columns]
	
	return stat_df[:30]	

	
def create_team_agg_total(year, week = 0, season_type = 'Regular'):
	
	play_sql = ''' select
			g.week,
			g.season_year as year,
			p.pos_team,
			case when p.pos_team = g.home_team then g.away_team else g.home_team end as opp_team,
			1 as play_count,
			p.first_down,
			p.passing_first_down,
			p.rushing_first_down,
			p.fourth_down_att,
			p.fourth_down_conv,
			p.third_down_att,
			p.third_down_conv,
			ap.*
		from play p 
			inner join agg_play ap
				on p.gsis_id = ap.gsis_id
				and p.drive_id = ap.drive_id
				and p.play_id = ap.play_id
			inner join game g
				on g.gsis_id = p.gsis_id
		where p.pos_team != 'UNK'
			and g.season_type in (%(type)s)
			and g.season_year in (%(year)s)
		'''
	
	play_df = pd.read_sql(play_sql, db, params = {'type':season_type, 'year':year})
	
	#Add new stat columns
	play_df['total_offense_yds'] = play_df['receiving_yds'] + play_df['rushing_yds']
	play_df['total_offense_tds'] = play_df['receiving_tds'] + play_df['rushing_tds']

	#Limit to week specified, otherwise return season stats
	if week > 0:
		play_df = play_df[play_df.week == week]
	
	#Group up, sum columns, sort by total_offense_yds
	agg_play = play_df.groupby(['pos_team','year','week']).aggregate(np.sum).sort_values(by='total_offense_yds', ascending = False)	
	
	#Add new agg stat columns
	agg_play['rush_pct'] = agg_play['rushing_att'] / agg_play['play_count']
	agg_play['pass_pct'] = agg_play['passing_att'] / agg_play['play_count']
	
	#Define return columns
	#should I make several options for this?
	agg_play = agg_play[['total_offense_yds','total_offense_tds','play_count','first_down','rush_pct','rushing_yds','rushing_tds','pass_pct','passing_yds','passing_tds']]
	
	
	return agg_play.head(n=32)
	
def get_season_player(year, name, season = 'Regular'):	
	print 'get_season_player - gotsta make this!'

	
def create_all_analytics(year, week, position, season = 'Regular'):
	analytics_df = []
	for stat_type in all_stats:
		analytics_df.append(get_weekly_stat(year, week, position, stat_type))
	return analytics_df
	
	#Carries
	#Targets
	#Receptions	
	#Rushing Yds
	#Receiving Yds
	#Total Yds
	#Yards per Carry
	#Yards per Target
	#Yards per Reception
	#Yards After Catch
	#Number First Downs		
	

	
# print 'Top Total Yds - RB\n', analytics.get_weekly_stat(2018, 3, 'RB', 'total_yds', 'Preseason'), '\n'	
# print 'Top Receptions - RB\n', analytics.get_weekly_stat(2018, 3,'RB','receiving_rec','Preseason'), '\n'	
# print 'Top Carries - RB\n', analytics.get_weekly_stat(2018, 3, 'RB', 'rushing_att','Preseason'), '\n'
# print 'Top Targets - RB\n', analytics.get_weekly_stat(2018, 3, 'RB', 'receiving_tar','Preseason'), '\n'
# print 'Top Rushing Yds - RB\n', analytics.get_weekly_stat(2018, 3,'RB','rushing_yds','Preseason'), '\n'
# print 'Top Yds Per Carry - RB\n', analytics.get_weekly_stat(2018, 3, 'RB', 'yards_per_carry', 'Preseason'), '\n'
# print 'Top Yds Per Target - RB\n', analytics.get_weekly_stat(2018, 3, 'RB', 'yards_per_tar', 'Preseason'), '\n'
# print 'Top Yds Per Reception - RB\n', analytics.get_weekly_stat(2018, 3, 'RB', 'yards_per_rec', 'Preseason'), '\n'
# print 'Top Depth of Target - RB\n', analytics.get_weekly_stat(2018, 3, 'RB', 'avg_depth_of_tar', 'Preseason'), '\n'
# print 'Top Depth of Reception - RB\n', analytics.get_weekly_stat(2018, 3, 'RB', 'avg_depth_of_rec', 'Preseason'), '\n'
# print 'Top First Downs - RB\n', analytics.get_weekly_stat(2018, 3, 'RB', 'first_down', 'Preseason'), '\n'


# print analytics.create_team_agg_total(2018, 3, 'Preseason')

# analytics.get_season_player(2017, 'name')











