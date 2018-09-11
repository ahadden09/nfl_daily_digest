import analytics
import email_me
import nfldb.update as nfl

nfl.run()

print 'Top Total Yds - RB\n', analytics.get_weekly_stat(2018, 1, 'RB', 'total_yds'), '\n'	
print 'Top Receptions - RB\n', analytics.get_weekly_stat(2018, 1,'RB','receiving_rec'), '\n'	
print 'Top Offenses', analytics.create_team_agg_total(2018, 1)

analytics.get_season_player(2017, 'name')

email_data = analytics.get_weekly_stat(2018, 1, 'RB', 'receiving_tar')

email_me.send_email(email_data)