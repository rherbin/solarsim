from math import cos,sin,pi,sqrt,atan2
import pygame as pg
import sys
import copy

winsize = 1000
scale=10 #at scale 1: 1px = 15 000 000km
speed = 1000 #with 6000 updates per second, the real speed is 6000*speed
updaterate = 1

display = pg.display.set_mode((winsize,winsize))
clock = pg.time.Clock()

AU = 150e9
G = 6.67e-11

def calcForce(p1,p2):
    #compute values to add to p1 velocity when attracted to p2
    dist = sqrt((p2.pos[0] - p1.pos[0])**2 + (p2.pos[1] - p1.pos[1])**2) #cartesian distance
    force = (G*p1.mass*p2.mass)/(dist**2) #Newton's law
    angle = atan2(p2.pos[1] - p1.pos[1], p2.pos[0] - p1.pos[0]) #tan = opposit/adjacent
    velx = cos(angle)*force #sin to get x vel
    vely = sin(angle)*force #cos to get y vel
    return [velx,vely]

def mult(pos,angle):
    #get new position from a certain angle using sin and cos
    x,y=pos[0],pos[1]
    nx = cos(angle)*x-sin(angle)*y
    ny = sin(angle)*x+cos(angle)*y
    return [nx,ny]

def addVect(v1,v2):
    return [v1[x]+v2[x] for x in range(len(v1))]

def getDisplayPos(pos):
    #convert real world position in meters to pixels, scales with window size
    return [pos[0]*scale/15e9 + winsize/2, pos[1]*scale/15e9 + winsize/2]

class CircularPlanet:
    #planets with perfectly circular trajectory, no heavy physics computing
    def __init__(self,distance,rev_length,color,size):
        self.pos=[0,-distance]
        self.color=color
        self.angle=pi/20/rev_length
        self.size=size
        self.Moons = []
    
    def main(self,speed=1):
        pg.draw.circle(display,self.color,[(self.pos[0])*scale+winsize/2,(self.pos[1])*scale+winsize/2],self.size)
        self.pos=mult(self.pos,self.angle*speed)
        for Moon in self.Moons:
            Moon.main(speed)

    def addMoon(self,distance,rev_length,color,size):
        self.Moons.append(CircularMoon(distance,rev_length,color,size,self))

class CircularMoon(CircularPlanet):
    def __init__(self,distance,rev_length,color,size,mother):
        CircularPlanet.__init__(self,distance,rev_length,color,size)
        self.mother=mother
    
    def main(self,speed=1):
        pg.draw.circle(display,self.color,[(self.mother.pos[0]+self.pos[0])*scale+winsize/2, (self.mother.pos[1]+self.pos[1])*scale+winsize/2], self.size)
        self.pos=mult(self.pos,self.angle*speed)

class Planet:
    #trajectory calculated using newton's law, real mass and real distances
    def __init__(self,pos,size,mass,color):
        self.pos = pos #in AU = 150 000 000 km = 10*scale px
        self.size = size #rayon in km
        self.mass = mass #kg
        self.color = color
        self.vel = [0,0]
        self.orbit = [copy.copy(self.pos)]*2
        print(self.orbit)
    
    def updatePos(self,planets,speed):
        fx = 0
        fy = 0
        for x in planets:
            #compute force exerced by every other planet on self
            if x == self:
                continue
            dvel = calcForce(self,x)
            #adding the resulting x and y force to the sum of forces
            fx += dvel[0]
            fy += dvel[1]
        #transpose force to acceleration and add to velocity
        self.vel[0] += fx/self.mass * speed
        self.vel[1] += fy/self.mass * speed
        #add acceleration to current pos to get new pos
        self.pos[0] += self.vel[0] * speed
        self.pos[1] += self.vel[1] * speed
    
    def main(self,planets,speed=1):
        pg.draw.line(display, "white", getDisplayPos(self.pos),getDisplayPos(center.pos)) #line between planet and center
        pg.draw.circle(display,self.color,getDisplayPos(self.pos),self.size*scale/15e9) #planet itself
        self.updatePos(planets,speed)
        pos = [getDisplayPos(x) for x in self.orbit] #compute position of past positions
        pg.draw.lines(display,self.color,False,pos) #draw trajectory
    
    def addOrbit(self):
        self.orbit = self.orbit + [copy.copy(self.pos)]


CircularPlanets = []
planets = []

def solar(withmoon=True):
    #using real world numbers
    global planets
    sun = Planet([0,0],696340000,1.988e30,"yellow")
    global center
    center = sun
    mercury = Planet([0.4*AU,0],2439000,3.285e23,"gray")
    mercury.vel[1] = -47000
    venus = Planet([0,0.7*AU],6051000,4.867e24,"gray")
    venus.vel[0] = 35000
    earth = Planet([-1*AU,0],6371000,5.972e24,"blue")
    earth.vel[1] = 29783
    if withmoon:
        moon = Planet([-384400000-AU,0],1737000,7.347e22,"lightgray")
        moon.vel[1] = 1022 + 29783
        planets.append(moon)
    mars = Planet([0,-1.5*AU],3389000,6.39e23,"red")
    mars.vel[0] = -24000
    jupiter = Planet([5.2*AU,0],69991000,1.898e27,"orange")
    jupiter.vel[1] = -13070

    asteroid = Planet([-AU,.5*AU],37000,9.39e18,"white")
    asteroid.vel = [3000,11500]

    planets += [sun,earth,mercury,venus,mars,jupiter,asteroid]

def earthmoon():
    #using real world numbers
    global planets
    earth = Planet([0,0],6371000,5.972e24,"blue")
    global center
    center = earth
    moon = Planet([-384400000,0],1737000,7.347e22,"lightgray")
    moon.vel[1] = 1022
    global scale,speed,updaterate
    scale = 10000
    speed = 500
    updaterate = 10

    planets += [earth,moon]

def solarsystemCirlcular():
    #no unit for planet size, .1 AU for planet distance
    mercury=CircularPlanet(4,2.4,"darkgray",2)
    venus=CircularPlanet(7,6.2,"gray",2)
    earth=CircularPlanet(10,10,"blue",2)
    earth.addMoon(.5,10/13,"white",1)
    mars=CircularPlanet(15,18.8,"red",2)

    jupiter=CircularPlanet(52,120,"orange",3)
    saturn=CircularPlanet(96,290,"brown",3)
    uranus=CircularPlanet(192,840,"lightblue",3)
    neptune=CircularPlanet(300,1650,"blue",3)
    global CircularPlanets
    CircularPlanets += [mercury,venus,earth,mars,jupiter,saturn,uranus,neptune]

solar()

frames = 0

while True:
    display.fill((0,0,0))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEWHEEL:
            if event.y == 1:
                scale*=1.1
            elif event.y==-1:
                scale*=(1/1.1)

    keys = pg.key.get_pressed()

    if keys[pg.K_RIGHT]:
        speed*=1.01
    if keys[pg.K_LEFT]:
        speed*=(1/1.01)

    for planet in CircularPlanets:
        planet.main(speed)
    for planet in planets:
        planet.main(planets,speed)
    if frames%(100//(speed/1000)//updaterate)==0:
        for planet in planets:
            planet.addOrbit()

    frames += 1
    clock.tick(6000)
    pg.display.update()