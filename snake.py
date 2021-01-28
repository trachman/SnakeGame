#!/usr/bin/env
import time
import random
from pynput import keyboard
import tkinter as tk
from tkinter import messagebox

class Block(object):
	def __init__(self, x, y, parent):
		self.parent = parent
		self.x = x
		self.y = y
		self.previousx = x # initialize
		self.previousy = y # initialize

class Snake(object):
	def __init__(self, canv, x, y):
		head = Block(x,y,None) 
		self.canv = canv
		self.blocks = [ head ] 
		self.direction = 'UP' # start upwards
		self.ids = [] # list of all ids so we can clear them
	def move(self, direction):
		for i in range(len(self.blocks)):
			self.blocks[i].previousx = self.blocks[i].x
			self.blocks[i].previousy = self.blocks[i].y
			if i == 0: 
				if direction == 'UP': self.blocks[i].y -= 20
				if direction == 'DOWN': self.blocks[i].y += 20
				if direction == 'LEFT': self.blocks[i].x -= 20
				if direction == 'RIGHT': self.blocks[i].x += 20	
			else:
				self.blocks[i].x = self.blocks[i-1].previousx
				self.blocks[i].y = self.blocks[i-1].previousy 
	def grow(self):
		parent = self.blocks[len(self.blocks)-1]
		self.blocks.append(Block(parent.previousx,parent.previousy,parent))
		
class Candy(object):
	def __init__(self):
		self.x = random.randint(0,24) * 20
		self.y = random.randint(0,24) * 20
		self.found = False
		self.id = None

class Events(object):
	def __init__(self, snake):
		self.keys = (keyboard.Key.up, keyboard.Key.down, 
					keyboard.Key.left, keyboard.Key.right)
		self.running = True
		self.snake = snake
		listener = keyboard.Listener(
					on_press=self.on_press, 
					on_release=self.on_release)
		listener.start() # starts a listening thread
	def on_press(self, key):
		if key == keyboard.Key.up: self.snake.direction = 'UP'
		if key == keyboard.Key.down: self.snake.direction = 'DOWN'
		if key == keyboard.Key.left: self.snake.direction = 'LEFT'
		if key == keyboard.Key.right: self.snake.direction = 'RIGHT'	
	def on_release(self, key):
		if key == keyboard.Key.esc:
			self.running = False
			return False # Stop listener

def game_window(width,height,cell_size):
	master = tk.Tk()
	master.geometry('{}x{}'.format(width+10,height+10))
	master.resizable(False,False)
	master.title('The Game of Snake')
	canv = tk.Canvas(master, width=width, height=height)
	canv.pack()
	return master, canv

def draw_grid(width, height, cell_size, canv):
	num_cells = int(height/cell_size)
	for line in range(1,num_cells):
		xy = line * cell_size
		canv.create_line(0,xy,500,xy)
		canv.create_line(xy,0,xy,500)

def clear_canvas(canv, snake, candy):
	for item in snake.ids: canv.delete(item)
	canv.delete(candy.id)
	snake.ids = []

def draw(snake, candy, canv):
	if candy.found:
		candy = Candy()
		snake.grow()
	snake.move(snake.direction)
	candy.id = canv.create_rectangle(candy.x, candy.y,candy.x+20, candy.y+20,fill='purple')
	for i in range(len(snake.blocks)):
		x, y = snake.blocks[i].x, snake.blocks[i].y
		snake.ids.append(canv.create_rectangle(x,y,x+20,y+20,fill='red'))
	return snake, candy 

def candy_found(snake,candy,score):
	if snake.blocks[0].x == candy.x and snake.blocks[0].y == candy.y:
		candy.found = True
		score += 1
	return score	 

def check_collision(snake):
	xs = [block.x for block in snake.blocks]
	ys = [block.y for block in snake.blocks]
	head = (xs.pop(0),ys.pop(0))
	pairs = list(map(lambda n1,n2 : (n1,n2), xs, ys))
	if head in pairs: return False
	if head[0] > 499 or head[0] < 0 or head[1] > 499 or head[1] < 0: return False
	return True	

def newgame(master,canv,width,height,cell_size,button):
	button.destroy()
	draw_grid(width,height,cell_size,canv)
	snake = Snake(canv,240,240)
	candy = Candy()
	events = Events(snake)
	score = 0
	while events.running:
		clear_canvas(canv,snake, candy)
		snake, candy = draw(snake, candy, canv)
		score = candy_found(snake,candy,score)
		events.running = check_collision(snake)
		master.update_idletasks() # replaces master.mainloop()
		master.update() # replaces master.mainloop()
		time.sleep(0.1) # 0.1 seconds
	canv.delete('all')
	message = 'Your score was {}'.format(score)
	title = 'Game Over'
	messagebox.showinfo(title, message)
	main_menu(master,canv,width,height,cell_size,None)

def main_menu(master,canv,width,height,cell_size,start):
	def startgame():
		newgame(master,canv,width,height,cell_size,start)
	start = tk.Button(master,text='New Game',command=startgame,
				highlightbackground='red',padx=50,pady=50)
	start.place(x=175,y=200)
	master.mainloop()

def main():
	WIDTH, HEIGHT, GRID_CELL_SIZE = 500, 500, 20
	master, canv = game_window(WIDTH,HEIGHT,GRID_CELL_SIZE)
	main_menu(master,canv,WIDTH,HEIGHT,GRID_CELL_SIZE,None)
