import pygame
from pygame.locals import *
from sys import exit
import time, threading
import pandas as pd
from sympy import Point2D

pygame.init()
screen = pygame.display.set_mode((640, 480), 0, 32)

#colout template
SHADOW = (160, 192, 160)
WHITE = (255, 255, 255)
LIGHTGREEN = (0, 255, 0 )
GREEN = (0, 200, 0 )
BLUE = (0, 0, 128)
LIGHTBLUE= (0, 0, 255)
RED= (200, 0, 0 )
LIGHTRED= (255, 100, 100)
PURPLE = (102, 0, 102)
LIGHTPURPLE= (153, 0, 153)
BLACK= (0,0,0)

total_bots = 3

#get data from the specified bot ID
def get_data(id):
	try:
		df_bot = pd.read_csv("../OpenCV/bot_"+str(id)+".csv")
		row= df_bot.iloc[-1]
		bot_x=int(float(row[2]))
		bot_y=int(float(row[3]))
		return bot_x,bot_y
	except:
		return 0,0

#smoothen out the data
def check_smooth_data(new_point,old_point):
	present_loc = Point2D(new_point)
	old_loc = Point2D(old_point)
	eucledian_dist = (present_loc.distance(old_loc)).evalf()
	if eucledian_dist > 30:
		return False
	return True


bot0_coordinate = [] 
bot1_coordinate = []
bot2_coordinate = []
bot3_coordinate = []


while True:
	
	#mark bot goals permanently
	goal_x = [170,405,405,170]
	goal_y = [360,360,90,90]
	goal_x_1 = [288,288]
	goal_y_1 = [90,360]
	bot0= get_data(0)
	bot1= get_data(1)
	bot2= get_data(2)
	bot3= get_data(3)
	try:
		if check_smooth_data(bot0, bot0_coordinate[-1]):
			bot0_coordinate.append(bot0)
	except:
		bot0_coordinate.append(bot0)

	try:
		if check_smooth_data(bot1, bot1_coordinate[-1]):	
			bot1_coordinate.append(bot1)
	except:
		bot1_coordinate.append(bot1)

	try:
		if check_smooth_data(bot2, bot2_coordinate[-1]):
			bot2_coordinate.append(bot2)
	except:
		bot2_coordinate.append(bot2)
	
	try:
		if check_smooth_data(bot3, bot3_coordinate[-1]):
			bot3_coordinate.append(bot3)
	except:
		bot3_coordinate.append(bot3)

	screen.fill(BLACK)
	for i in range(len(goal_x)):
		pygame.draw.circle(screen, WHITE, (goal_x[i],goal_y[i]),18)
	for i in range(len(goal_x_1)):
		pygame.draw.circle(screen, SHADOW, (goal_x_1[i],goal_y_1[i]),18)
	
	
	if len(bot0_coordinate)>1 :
		pygame.draw.lines(screen, (LIGHTGREEN), False, bot0_coordinate, 10)
		pygame.draw.circle(screen, LIGHTGREEN, (bot0_coordinate[-1]),18)
	if len(bot1_coordinate)>1:
		pygame.draw.lines(screen, (RED), False, bot1_coordinate, 20)
		pygame.draw.circle(screen, RED, (bot1_coordinate[-1]),24)
	if len(bot2_coordinate)>1:
		pygame.draw.lines(screen, (PURPLE), False, bot2_coordinate, 10)
		pygame.draw.circle(screen, PURPLE, (bot2_coordinate[-1]),18)
	if len(bot3_coordinate)>1:
		pygame.draw.lines(screen, (BLUE), False, bot3_coordinate, 20)
		pygame.draw.circle(screen, BLUE, (bot3_coordinate[-1]),24)

	
	for event in pygame.event.get():
		if event.type == QUIT:
			exit()
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_c:
				#clear screen if "c" is pressed
				bot0_coordinate.clear()
				bot1_coordinate.clear()
				bot2_coordinate.clear()
				bot3_coordinate.clear()

	pygame.display.update()
	