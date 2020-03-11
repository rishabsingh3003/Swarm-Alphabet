from simple_pid import PID
from sympy import Point2D, Line, Ray
import math 
import time, threading
import numpy as np
import pandas as pd
import socket

############################################## UDP ########################################################
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)     # For UDP

#clients IP over WIFI
udp_host = "192.168.0.132" 		# Host IP
udp_port = 2801			        # specified port to connects
##########################################################################################################

waypoint_pointer = 0
in_pivot_mode = False
is_simulation = False


# get latest data from DB
def get_db_data():
	if(is_simulation):
		df_bot = pd.read_csv("../Simulation/bot_2_sim.csv")
		row= df_bot.iloc[-1]
		bot_x           =int(float(row[2]))
		bot_y           =int(float(row[3]))
		bot_front_x     =int(float(row[4]))
		bot_front_y     =int(float(row[5]))
		print(bot_front_x,bot_front_y)
		return bot_x,bot_y, bot_front_x,bot_front_y
	
	#its not simulation 
	df_bot = pd.read_csv("../OpenCV/bot_2.csv")
	row= df_bot.iloc[-1]
	bot_x           =int(float(row[2]))
	bot_y           =int(float(row[3]))
	bot_front_x     =int(float(row[4]))
	bot_front_y     =int(float(row[5]))
	# print(bot_front_x,bot_front_y)
	return bot_x,bot_y, bot_front_x,bot_front_y

#get updated goal
def get_goal(id):

	goal_x = [170,405,405,170]
	goal_y = [360,360,90,90]
	loop = True
	return goal_x[id],goal_y[id], len(goal_x), loop

def package_msg(l_direction,l_speed, r_direction, r_speed):
	#adding comma in the end of a string is important so client knows where the stream ends 
	package = str(int(l_direction)) + "," + str(int(l_speed)) + "," + str(int(r_direction)) + "," + str(int(r_speed)) + ","
	return package

#PID controller class
class PID_controller:
	def __init__(self,Thr,Steer):
		self.Thr =Thr
		self.Steer = Steer

	pid_throttle_controller = PID(5, 0, 0, setpoint=0) #4.5,0,0
	pid_throttle_controller.output_limits = (0, 1023)
	pid_steering_controller = PID(12, 0, 0, setpoint=0)  #30,0,0
	pid_steering_controller.output_limits = (-1023,1023)

	#round the values so that they are stable. Small value changes dont reflect well in motor driver.
	#motor driver takes value between 0-1023

	def Output_left_wheel(self):
		clipped_left = float(np.clip((self.Thr - self.Steer),-1023,1023))
		return np.round(clipped_left,-2)
	
	def Output_right_wheel(self):
		clipped_right = float(np.clip((self.Thr + self.Steer),-1023,1023))
		return np.round(clipped_right,-2)

############################################## Declare new Bots in system here ############################################		
BOT_2 = PID_controller(0,0)
#################################################################################################################


#main loop

def repeat():

	global waypoint_pointer 
	global in_pivot_mode
	stopping_flag = False
	msg = package_msg(0,0,0,0)
	#get latest available data
	bot_x,bot_y, bot_front_x,bot_front_y = get_db_data()
	
	#deal with goal changes 
	goal_x, goal_y,wp_count,loop_on = get_goal(waypoint_pointer)
	
	Bot_Loc = Point2D(bot_x,bot_y)
	Goal_Loc = Point2D(goal_x,goal_y)

	#distance between goal and present loc
	eucledian_dist_error = (Bot_Loc.distance(Goal_Loc)).evalf()

	#angle to move so that vehicle heading is correct
	r1 = Ray((bot_x,bot_y),(goal_x,goal_y))
	r2 = Ray((bot_x,bot_y), (bot_front_x,bot_front_y)) 
	angle_error = math.degrees(r1.closing_angle(r2).evalf())
	
	#redundant check, do not remove. 
	if angle_error < -180:
		angle_error = angle_error + 360
	if angle_error > 180:
		angle_error = angle_error - 360


	#####################################UNCOMMENT THESE FOR DEBUGGING######################################
	# print("angle error")
	# print(angle_error)

	# print("distance error")
	# print(eucledian_dist_error)
	
	# print("Steer PID")
	# print(BOT_2.Steer)

	# print("Throt PID")
	# print(BOT_2.Thr)
	# print("LEFT WHEEL")
	# print(out_left_wheel)

	# print("RIGHT WHEEL")
	# print(out_right_wheel)

	# print("Goal")
	# print(get_goal(waypoint_pointer))
	#######################################################################################################

	# pivot if angle_error is too big
	#TO-DO: change hard coded values into parameter's. Maybe a class that can be accessed from command line 
	if abs(angle_error) > 60 or in_pivot_mode:
		in_pivot_mode = True
		if abs(angle_error) >= 35:
			pivot_speed = int(np.interp(abs(angle_error),[35,180],[400,500]))
			print ("pivoting")
			if angle_error > 0:
				#pivot anti-cws
				msg = package_msg(0,pivot_speed,1,pivot_speed)
			else:
				#pivot cws
				msg = package_msg(1,pivot_speed,0,pivot_speed)
		else:
			in_pivot_mode = False
	
	if in_pivot_mode == False:	 		
		
		#what to do when approaching goal, i.e run precision controller
		if(eucledian_dist_error <= 100 and eucledian_dist_error > 40):
			left_direction = 1
			left_speed = 600 + 3*angle_error
			right_direction = 1
			right_speed = 600 - 3*angle_error
			msg = package_msg(1,left_speed,1,right_speed)

		elif (eucledian_dist_error <= 40):
			if stopping_flag == False:
				waypoint_pointer = waypoint_pointer + 1
				if waypoint_pointer == wp_count:
					if loop_on:
						waypoint_pointer = 0
					else:
						msg = package_msg(0,0,0,0)
			else:
				#stop
				msg = package_msg(0,0,0,0)

			
		#convert PID value into motor driver understandable value
		#xyz_direction = 1 for forward

		else:

			#calculate PID values based on error obtained 
			BOT_2.Steer = BOT_2.pid_steering_controller(angle_error)
			BOT_2.Thr = BOT_2.pid_throttle_controller(-eucledian_dist_error)
	
			#get computed values from PID
			out_left_wheel = BOT_2.Output_left_wheel()
			out_right_wheel = BOT_2.Output_right_wheel()

			if(out_left_wheel>=0):
				left_direction = 1
				left_speed = out_left_wheel
			else:
				left_direction = 0
				left_speed = -out_left_wheel
		
			if(out_right_wheel >= 0):
				right_direction = 1
				right_speed = out_right_wheel
			else:
				right_direction = 0
				right_speed = -out_right_wheel

			msg = package_msg(left_direction,left_speed,right_direction,right_speed)

	#pack the message and send
	sock.sendto(msg.encode(),(udp_host,udp_port))
	print(msg)
	#repeat every x seconds
	threading.Timer(0.3, repeat).start()
	
repeat()