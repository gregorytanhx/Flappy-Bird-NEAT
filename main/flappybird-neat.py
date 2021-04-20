import pygame, random, time
import os
import neat

pygame.init()

WIDTH = 600
HEIGHT = 800

font = pygame.font.SysFont('Lato', 50)
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Flappy Bird")

class Bird(object):
	upthrust = 13.5
	gravity = 2.5
	angle = 20
	anglerate = 5
	img = pygame.image.load('bird.png')
	img = pygame.transform.scale(img, (img.get_width()//4,img.get_height()//4))
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.vel = 0
		self.w = self.img.get_width()
		self.h = self.img.get_height()
	def movement(self, pressed):
		if pressed:
			self.vel = -self.upthrust
			self.angle=25

		if self.vel > 0:
			self.angle -= self.anglerate
			self.anglerate+=0.2
		else:
			self.anglerate = 3
		self.vel += self.gravity
		self.y += self.vel
		score = self.vel
				
	def hit(self):
		while self.y+self.h<=HEIGHT-100:
			if self.angle>-90:
				self.angle-=10
			self.y += 1
			
	def draw(self):			
		rotated_img = pygame.transform.rotate(self.img, self.angle)
		new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
		screen.blit(rotated_img, new_rect.topleft)
	
	def get_mask(self):
		return pygame.mask.from_surface(self.img)
		
class Pillar(object):
	gap = 200
	w = 100
	img = pygame.image.load('pipe.png')
	img = pygame.transform.scale(img, (100, 500))
	def __init__(self, x):
		self.x = x
		self.height = random.randint(100,450)
		self.top = pygame.transform.flip(self.img, False, True)
		self.bottom = self.img
		self.y1 = self.height - self.img.get_height()
		self.y2 = self.height + self.gap
		self.passed = False

	def draw(self):
		screen.blit(self.top, (self.x,self.y1))
		screen.blit(self.bottom, (self.x, self.y2))
		#pygame.draw.rect(screen, (255,0,0), (self.x, 0,100,pillar.get_height()-self.toph),5)
		#pygame.draw.rect(screen, (255,0,0), (self.x,self.y2,100,self.bottomh),5)
	def move(self,speed):
		self.x-=speed
  
	def collide(self, bird):
		if bird.x+bird.w>=self.x and bird.x<=self.x:
			if bird.y+bird.h>=self.y2 or bird.y<=self.height:
				return True
		return False

class Background:	
	bg = pygame.image.load('bg.png')
	ground = pygame.image.load('ground.png')
	bg = pygame.transform.scale(bg, (600, 700))
	ground = pygame.transform.scale(ground, (WIDTH+10,100))
	ground_height = 100
	
	def __init__(self):
		self.x1 = 0
		self.x2 = WIDTH 
  
	def move(self, speed):
		self.x1 -= speed
		self.x2 -= speed
		if self.x1 <= -WIDTH:
			self.x1=WIDTH
		if self.x2 <= -WIDTH:
			self.x2=WIDTH
	
	def draw_bg(self):
		screen.blit(self.bg, (self.x1, 0))
		screen.blit(self.bg, (self.x2, 0))
			
	def draw_ground(self):
		screen.blit(self.ground, (self.x1,HEIGHT-self.ground_height))
		screen.blit(self.ground, (self.x2,HEIGHT-self.ground_height))
  
	def collide(self, bird):
		return bird.y+bird.h>=HEIGHT-self.ground_height
  
def draw(birds, pillars, score, background):
	background.draw_bg()
	for i in pillars:
		i.draw()
	background.draw_ground()
	for bird in birds:
	    bird.draw()
	#pygame.draw.rect(screen, (255,0,0), (bird.x,bird.y,bird.w,bird.h),5)
	text=font.render("Score: " + str(score), 1, (255, 255, 255))
	screen.blit(text, (WIDTH-10-text.get_width(),10))
	pygame.display.update()

def main(genomes, config):
	interval = 500
	nets = []
	ge = []
	birds = []
	
	for _, g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g, config)
		nets.append(net)
		birds.append(Bird(200, 300))
		g.fitness = 0 
		ge.append(g)
  
	pillars = [Pillar(WIDTH),Pillar(WIDTH+interval)]
	bg = Background()
	scrollspeed = 15
	run = True
	score = 0
	clock=pygame.time.Clock()
	lastscore = 0
	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run=False
				pygame.quit()
				quit()
		lastscore = score

		pillar_ind = 0
		if len(birds) > 0:
			if len(pillars) > 1 and birds[0].x > pillars[0].x + pillars[0].w:
				pillar_ind = 1
		else:
			run = False
			break

		bg.move(scrollspeed)
		for x, bird in enumerate(birds):
			jump = False
			ge[x].fitness += 0.1 
			output = nets[x].activate((bird.y, abs(bird.y - pillars[pillar_ind].height), abs(bird.y-pillars[pillar_ind].y2)))
			if output[0] > 0.5:
				jump = True
			bird.movement(jump)
   
			if bg.collide(bird) or bird.y<0:
				ge[x].fitness -= 1
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)
					

		for p in pillars:
			p.x-=scrollspeed
			if p.x<-100:
				pillars.pop(pillars.index(p))
				pillars.append(Pillar(pillars[-1].x+interval))
			for x, bird in enumerate(birds):
				if p.collide(bird):
					birds.pop(x)
					nets.pop(x)
					ge.pop(x)
				elif bird.x > p.x + p.w and not p.passed:
					score += 1
					ge[x].fitness += 5
					p.passed = True
					
		draw(birds, pillars, score, bg)
		clock.tick(120)
		
	

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main,50)
    
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = 'config.txt'
    run(config_path)