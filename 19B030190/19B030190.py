#-------------------------IMPORTING MODULES----------------------------#
#!!!! modules 'tkinter' and 'Pillow' must be installed by pika
from tkinter import *
from PIL import Image, ImageTk    
import pygame
from enum import Enum   
import random
import time, datetime
import pika, json, uuid
from threading import Thread

from operator import itemgetter

AFK=[]
goods=[]
bads=[]
AFK2=[]
goods2=[]
bads2=[]
do=['UP','DOWN','RIGHT','LEFT']
#-------------------------SINGLE MODE----------------------------#
def GameOne():
    window.destroy()
    pygame.init()
    screen = pygame.display.set_mode((1200, 600))
    background_image=pygame.image.load('real.jpg')
    gamer = pygame.image.load('ok.png')
    foodImage = pygame.image.load('cook.png')
    wallImage = pygame.image.load('wall.png')
    bullet = pygame.image.load('at.png')
    enema = pygame.image.load('enema.png')
    utu = pygame.mixer.Sound('s1.wav')
    atu = pygame.mixer.Sound('s2.wav')

    class Direction(Enum):
        UP = 1
        DOWN = 2
        LEFT = 3
        RIGHT = 4
        NOPE=5

    class Tank:

        def __init__(self,item,name ,u, x, y, speed,d_right=pygame.K_RIGHT, d_left=pygame.K_LEFT, d_up=pygame.K_UP, d_down=pygame.K_DOWN):
            self.good = False
            self.item = item
            self.u = u
            self.x = x
            self.y = y
            self.speed = speed
            self.width = 40
            self.direction = Direction.NOPE
            self.lives = 3 
            self.name = name
            self.KEY  = {d_right: Direction.RIGHT, d_left: Direction.LEFT,
                        d_up: Direction.UP, d_down: Direction.DOWN}

        def draw(self):
            tank_c = (self.x + int(self.width / 2), self.y + int(self.width / 2))
            if self.direction == Direction.NOPE:
                self.speed=0
                screen.blit(self.item,(self.x,self.y))
            if self.direction == Direction.RIGHT:
                if self.good==False:
                    self.speed=3
                screen.blit(self.item,(self.x,self.y))
            
            if self.direction == Direction.LEFT:
                if self.good==False:
                    self.speed=3
                screen.blit( pygame.transform.rotate(self.item, 180),(self.x,self.y)  )  

            if self.direction == Direction.UP:
                if self.good==False:
                    self.speed=3
                screen.blit(pygame.transform.rotate(self.item, 90),(self.x,self.y))

            if self.direction == Direction.DOWN:
                if self.good==False:
                    self.speed=3
                screen.blit(pygame.transform.rotate(self.item, 270),(self.x,self.y))

        def change_direction(self, direction):
            self.direction = direction

        def move(self):
                if self.direction == Direction.LEFT:
                    if self.x + self.width < 0:
                        self.x = 1200 
                        self.lives-=1
                    else:
                        self.x-=self.speed
                if self.direction == Direction.RIGHT:
                    if self.x> 1200:
                        self.x = 0
                        self.lives-=1
                    else:
                        self.x += self.speed
                if self.direction == Direction.UP:
                    if self.y< self.width:
                        self.y=600
                        self.lives-=1
                        
                    else:
                        self.y -= self.speed
                if self.direction == Direction.DOWN:
                    if self.y > 600:
                        self.y = self.width
                        self.lives-=1
                    else:
                        self.y += self.speed
                self.draw()

        def chances(self):
            font = pygame.font.Font("game_over.ttf", 80)
            scoreshadow = font.render(self.name + ":   L I V E S: " + str(self.lives), True, (0,0,0))
            screen.blit(scoreshadow, (500, self.u+2))
            
            score = font.render(self.name + ":   L I V E S: " + str(self.lives), True, (255,255,255))
            screen.blit(score, (498, self.u))
            
        def dead(self):
                font = pygame.font.Font("game_over.ttf", 120)
                textshadow=font.render('G A M E O V E R! '+self.name+' LOST...' , True, (0,0,0))
                screen.blit(textshadow, (390,300))
                text = font.render('G A M E O V E R! '  +self.name+' LOST...', True, (255,255,255))
                screen.blit(text, (388,298))
    class Wall:

        def __init__(self,x,y):
            self.x = x
            self.y = y     
            self.width = 35
            self.height = 10

        def draw(self):
            screen.blit( wallImage,(self.x,self.y))
        
        def hits(self,Tank):
            if (Tank.y+Tank.width >= self.y and Tank.y <= self.y+self.height) and (Tank.x+Tank.width >= self.x and Tank.x <= self.x+self.width):
                Tank.lives-=1 
                self.x=2000
                self.y=2000   
        
    class Bullet:

        def __init__(self,x,y,color,drop):
            self.x = x
            self.y = y
            self.color = color
            self.radius = 5
            self.dx, self.dy =0,0
            self.drop = False
            self.speed=10
        
        def draw(self):
            pygame.draw.circle(screen, self.color,(self.x,self.y),self.radius)

        def start(self,x,y):
            if self.drop==True:
                self.x+=self.dx
                self.y+=self.dy
                self.draw()
                
        def shoot(self,Tank):
            atu.play()
            if Tank.direction==Direction.RIGHT:
                self.x,self.y=Tank.x + int(Tank.width / 2), Tank.y + int(Tank.width / 2)
                self.dx,self.dy=self.speed, 0
            if Tank.direction==Direction.LEFT:
                self.x,self.y=Tank.x + int(Tank.width / 2), Tank.y + int(Tank.width / 2)
                self.dx,self.dy= -self.speed, 0
            if Tank.direction==Direction.UP:
                self.x,self.y=Tank.x + int(Tank.width / 2), Tank.y + int(Tank.width / 2)
                self.dx,self.dy= 0, -self.speed
            if Tank.direction==Direction.DOWN:
                self.x,self.y=Tank.x + int(Tank.width / 2), Tank.y + int(Tank.width / 2)
                self.dx,self.dy= 0, self.speed

        def out(self): #for bullets that are already out of walls
            if self.x >=1200 or self.x <=0 or self.y>=600 or self.y <=0:
                return True

        def colissio(self,Tank):  #checking if tank bullet colission
            
            if Tank.direction==Direction.RIGHT and self.drop==True:
                if (self.x > Tank.x and self.x < Tank.x+60) and (self.y>Tank.y and self.y<Tank.y+40):
                    return True
            if Tank.direction==Direction.LEFT and self.drop==True:
                if (self.x>Tank.x-20 and self.x<Tank.x+40)and (self.y>Tank.y and self.y<Tank.y+40):
                    return True
            if Tank.direction==Direction.UP and self.drop==True:
                if (self.y>Tank.y-20 and self.y<Tank.y+40) and (self.x>Tank.y and self.x<Tank.x+40):
                    return True
            if Tank.direction==Direction.DOWN and self.drop==True:
                if (self.y>Tank.y and self.y<Tank.y+60) and (self.x>Tank.x and self.x<Tank.x+40):
                    return True         
            return False

        def colission(self,Wall):  #checking if tank bullet colission

            if self.x>=Wall.x and self.x<=Wall.x+50 and self.y>=Wall.y and self.y<=Wall.y+10:
                return True
                
    class Food:

        def __init__(self,pos):

            self.pos=(50,300)
            self.height=25
            self.width=25

        def draw(self,position):

            self.pos=position
            screen.blit(foodImage,self.pos)
    

    mainloop = True

    tank1 = Tank(gamer,'BLUE',8,300, 300, 3 )
    tank2=Tank(enema,"RED",40,300,100,3,pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s)
    bullet1 = Bullet(tank1.x + int(tank1.width / 2), tank1.y + int(tank1.width / 2),(0, 162, 232),False)
    bullet2=Bullet(tank2.x + int(tank2.width / 2), tank2.y + int(tank2.width / 2),(255,0,0),False)
    tanks=[tank1,tank2]
    walls=[]
    bullets=[bullet1,bullet2]

    for i in (range (5)):
        n=random.randint(3,7)
        X,Y=random.randint(30,1150),random.randint(20,550)
        for number in (range (n) ):
            walls.append(Wall(X,Y))
            X+=35

    food=Food((random.randint(50,1000), random.randint(50, 500)))

    clock = pygame.time.Clock()  
    FPS = 30 
    total = 0
    newtime=random.randint(8,11)
    affecttime = 0
    position = random.randint(50,1000), random.randint(50, 500)
    new_disappear_time=random.randint(7,10)
    disappear_affect = 0

    while mainloop:

        milliseconds = clock.tick(FPS)
        seconds = milliseconds / 1000.0
        total += seconds
        screen.blit(background_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False
                if event.key==pygame.K_RETURN:
                    if bullet1.drop==False:
                        bullet1.drop=True
                        bullet1.shoot(tank1) 
                if event.key==pygame.K_SPACE:
                    if bullet2.drop == False:
                        bullet2.drop = True
                        bullet2.shoot (tank2)  
                for tank in tanks:
                    if event.key in tank.KEY.keys():
                        tank.change_direction(tank.KEY[event.key])

        for tank in tanks:
            tank.move()
            tank.chances()

            if tank.lives == 0:
                tank1.speed, tank2.speed  = 0,0   
                tank.dead()

                for wall in walls:
                    wall.x = 2000
                    wall.y = 2000
                
        if total >= newtime:
            newtime = total + random.randint(8,15) 

        if total >= new_disappear_time:
            new_disappear_time = total + random.randint(8,15) 
            position = random.randint(50, 1000), random.randint(50, 500)

        for tank in tanks:

            if tank.y >= food.pos[1]-tank.width and tank.y <= food.pos[1]+tank.width+food.height and tank.x >= food.pos[0]-tank.width and tank.x <= food.pos[0]+food.width:
            
                affecttime = total + 5
                disappear_affect = total + random.randint(5,15)
                new_disappear_time = total + random.randint(5,15)
                tank.good = True
                
        if total < disappear_affect:

            position = (0,1000)

        if total < affecttime:

            if tank1.good == True:
                tank1.speed = 6
                bullet1.speed = 20
                
            if tank2.good == True:
                tank2.speed = 6
                bullet2.speed = 20

        if total >= affecttime:
            if tank1.good==True:
                tank1.speed = 3
                bullet1.speed = 10
                tank1.good = False

            if tank2.good == True:
                tank2.speed = 3
                bullet2.speed = 10
                tank2.good=False
            
        
        if bullet1.colissio(tank2) == True:

            utu.play()
            tank2.lives -= 1
            bullet1.drop = False
            bullet1.x, bullet1.y = tank1.x + int(tank1.width / 2), tank1.y + int(tank1.width / 2)

        if bullet2.colissio(tank1) == True:

            utu.play()
            tank1.lives -= 1
            bullet2.drop = False
            bullet2.x, bullet2.y = tank2.x + int(tank2.width / 2), tank2.y + int(tank2.width / 2)

        for bullet in bullets:

            if bullet.out() == True:
                bullet.drop = False

        for wall in walls:

            wall.draw()
            wall.hits(tank1)
            wall.hits(tank2)

            if bullet1.colission(wall):  

                utu.play() 
                wall.x,wall.y=2000,2000
                bullet1.drop = False
                bullet1.x, bullet1.y = tank1.x + int(tank1.width / 2), tank1.y + int(tank1.width / 2)

            if bullet2.colission(wall):

                utu.play()
                wall.x,wall.y = 2000,2000
                bullet2.drop = False
                bullet2.x, bullet2.y = tank2.x + int(tank2.width / 2), tank2.y + int(tank2.width / 2)
        
        bullet1.start(tank1.x + int(tank1.width / 2), tank1.y + int(tank1.width / 2))
        bullet2.start(tank2.x + int(tank2.width / 2), tank2.y + int(tank2.width / 2))

        food.draw(position)
        
        pygame.display.flip()

    pygame.quit()
def GameTwo():
    window.destroy()
   
    #---------------------------SERVER INFO---------------------#
    IP ='34.254.177.17'
    PORT = 5672
    VIRTUAL_HOST = 'dar-tanks'
    USERNAME = 'dar-tanks'
    PASSWORD = '5orPLExUYnyVYZg48caMpX'
    #---------------------------SPRITES---------------------#

    vert = pygame.image.load('myBullet.bmp')
    background = pygame.image.load('good.png')
    enemyImage = pygame.image.load('enemy_tank.png')
    tankImage = pygame.image.load('my_tank.png')
    oppovert = pygame.image.load('oppovert.bmp')
    overi=pygame.image.load('gameover.jpg')

    pygame.init()
    screen = pygame.display.set_mode((1250, 600))
    #---------------------------RPC CLIENT---------------------#
    class TankRpcClient:
        def __init__(self):
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host = IP,
                    port = PORT,
                    virtual_host= VIRTUAL_HOST,
                    credentials= pika.PlainCredentials(
                        username= USERNAME,
                        password= PASSWORD
                    )
                )
            )
            self.channel = self.connection.channel()
            queue = self.channel.queue_declare(queue='',
            auto_delete = True,
            exclusive = True 
            )
            self.callback_queue = queue.method.queue
            self.channel.queue_bind(
                exchange = 'X:routing.topic',
                queue = self.callback_queue
            )

            self.channel.basic_consume( queue = self.callback_queue, on_message_callback = self.on_response, auto_ack = True )

            self.response = None
            self.corr_id = None
            self.token = None
            self.tank_id = None
            self.room_id = None

        def on_response(self, ch, method, props, body):
            if self.corr_id == props.correlation_id:
                self.response = json.loads(body)
                print(self.response)

        def call( self, key, message = {} ):
            self.response = None
            self.corr_id = str( uuid.uuid4())
            self.channel.basic_publish(
                exchange = 'X:routing.topic',
                routing_key = key,
                properties = pika.BasicProperties(
                    reply_to = self.callback_queue,
                    correlation_id = self.corr_id,
                ),
                body = json.dumps(message)
            )
            while self.response is None:
                self.connection.process_data_events()
        def check_sever_status(self):
            self.call('tank.request.healthcheck')
            return self.response['status'] == '200'

        def obtain_token( self , room_id ):
            message = {
                'roomId': room_id
            }
            self.call( 'tank.request.register', message)
            if 'token' in self.response:
                self.token = self.response['token']
                self.tank_id = self.response['tankId']
                self.room_id = self.response['roomId']
                return True
            return False

        def turn_tank(self, token, direction):
            message = {
                'token': token,
                'direction': direction
            }
            self.call('tank.request.turn', message)
        def fire(self,token):
            message = {
                'token':token
            }
            self.call('tank.request.fire', message)
    class TankConsumerClient(Thread):
        def __init__(self, room_id):
            super().__init__()
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host = IP,
                    port = PORT,
                    virtual_host=VIRTUAL_HOST,
                    credentials=pika.PlainCredentials(
                        username=USERNAME,
                        password=PASSWORD
                    )
                )
            )
            self.channel = self.connection.channel()
            queue = self.channel.queue_declare(queue = '',
            auto_delete = True,
            exclusive = True 
            )
            event_listener = queue.method.queue
            self.channel.queue_bind(exchange = 'X:routing.topic', 
            queue = event_listener,
            routing_key= 'event.state.' + room_id)

            self.channel.basic_consume(
                queue = event_listener,
                on_message_callback = self.on_response,
                auto_ack = True
            )
            self.response = None

        def on_response(self, ch, method, props, body):
            self.response = json.loads(body)
            print(self.response)

        def run(self):
            self.channel.start_consuming()
        
    #---------------------------VISUALIZING GAME---------------------#
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'

    MOVE_KEYS = {
        pygame.K_w: UP,
        pygame.K_a: LEFT,
        pygame.K_s: DOWN,
        pygame.K_d: RIGHT
    }

    def draw_tank(x, y, direction,**kwargs):
        if direction == "RIGHT":
            screen.blit(tankImage,(x,y))
            
        if direction == "LEFT":
            screen.blit(pygame.transform.rotate(tankImage, 180),(x,y))

        if direction == "UP":
            screen.blit(pygame.transform.rotate(tankImage, 90),(x,y))

        if direction == "DOWN":
            screen.blit(pygame.transform.rotate(tankImage, 270),(x,y))
    def draw_enemy(x, y,direction,**kwargs):
        if direction == "RIGHT":
            screen.blit(pygame.transform.rotate(enemyImage, 180),(x,y))

        if direction == "LEFT":
            screen.blit(enemyImage,(x,y))

        if direction == "UP":
            screen.blit(pygame.transform.rotate(enemyImage, 270),(x,y))

        if direction == "DOWN":
            screen.blit(pygame.transform.rotate(enemyImage,90 ),(x,y))

    def draw_my_bullet(x, y,direction,**kwargs):
        if direction == 'UP' or direction == "DOWN":
            screen.blit(vert,(x,y))
        else:
            screen.blit(pygame.transform.rotate(vert,90 ),(x,y))

    def draw_his_bullet(x, y,direction,**kwargs):
        if direction=='UP' or direction == "DOWN":
            screen.blit(oppovert,(x,y))
        else:
            screen.blit(pygame.transform.rotate(oppovert,90 ),(x,y))

    #---------------------------GAME LOOP---------------------#


    def game_start(client,event_client):
        mainloop = True
        font = pygame.font.Font('game_over.ttf', 50)
        while mainloop:
            screen.blit(background,(0,0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mainloop = False
                    #TankRpcClient.connection.close()
                    event_client.connection.close()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        mainloop = False
                    if event.key == pygame.K_SPACE:
                        client.fire(client.token)
                    if event.key in MOVE_KEYS:
                        client.turn_tank(client.token, MOVE_KEYS[event.key])         
            try:
                
                remaining_time = event_client.response['remainingTime']
                textshadow = font.render(('Remaining Time: '+str(remaining_time)), True, (0, 0, 0)) 
                screen.blit(textshadow, (12,7))
                text = font.render(('Remaining Time: '+str(remaining_time)), True, (255, 255, 255)) 
                screen.blit(text, (10,5))
            

            
                
            #---------------------------GETTING LISTS---------------------#

                tankalar = event_client.response['gameField']['tanks'] 
                tanks = sorted( tankalar, key = itemgetter('score'), reverse=True) 
                bullets = event_client.response['gameField']['bullets']
                kickeds = event_client.response['kicked']
                winners = event_client.response['winners']
                losers = event_client.response['losers']

                global AFK
                global goods
                global bads
                
            #----------------------SAVING LISTS GLOBAL --------------------------#

                for i in winners:
                    goods.append(i)

                for j in kickeds:
                    AFK.append(j)

                for k in losers:
                    bads.append(k)
            #---------------------------GAME OVER CONDITIONS---------------------#

                for afk in AFK:

                    if afk['tankId'] == client.tank_id:
                        screen.blit(overi,(0,0))
                        wordsshadow = font.render('YOU WERE KICKED FOR BEING AFK...', True, (0, 0,0 )) 
                        screen.blit( wordsshadow, (202,252))
                        words = font.render('YOU WERE KICKED FOR BEING AFK...', True, (255, 255, 255)) 
                        screen.blit( words, (200,250))
                        
            
                for good in goods:
                    
                    if good['tankId'] == client.tank_id:
                        screen.blit(overi,(0,0))
                        ordshadow = font.render('YOU ARE WINNER!!...'+'YOUR SCORE:'+str(good['score']), True, (0, 0, 0)) 
                        screen.blit( ordshadow, (202,252))
                        orda = font.render('YOU ARE WINNER!!...'+'YOUR SCORE:'+str(good['score']), True, (255, 255, 255)) 
                        screen.blit( orda, (200,250))
                        
                    
                for bad in bads: 
            
                    if bad['tankId'] == client.tank_id:
                        screen.blit(overi,(0,0))
                        wordshadow = font.render('YOU ARE LOOSER!!...'+'YOUR SCORE:'+str(bad['score']), True, (0, 0, 0)) 
                        screen.blit( wordshadow, (202,252))
                        word = font.render('YOU ARE LOOSER!!...'+'YOUR SCORE:'+str(bad['score']), True, (255, 255, 255)) 
                        screen.blit( word, (200,250))   

            #---------------------------DRAWING TANKS AND  INFORMATION PANEL---------------------#
                
                for tank in  tanks:
                    
                    tank_health = tank['health']
                    tank_score = tank['score']
                    tank_id = tank['id']
                    info_x = 835
                    info_y = 18*tanks.index(tank)+30
            
                
                    if tank['id'] == client.tank_id:
                        draw_tank(**tank)
                        mlshadow = font.render(('YOUR ID:  '+str(tank['id'])+'  YOUR LIVES:  '+ str(tank_health)+ '  SCORE:  '+ str(tank_score)), True, (0,0,0)) 
                        screen.blit( mlshadow, (810,3))
                        ml = font.render(('YOUR ID:  '+str(tank['id'])+'  YOUR LIVES:  '+ str(tank_health)+ '  SCORE:  '+ str(tank_score)), True, (255, 255, 255)) 
                        screen.blit( ml, (808,1))
                        
            
                    else:
                        draw_enemy(**tank)
                        infoshadow = font.render(('NAME : '+ str(tank_id)+ '  LIVES:  '+ str(tank_health)+ '  SCORE:  '+ str(tank_score)), True, (0, 0, 0)) 
                        screen.blit( infoshadow, (info_x+2,info_y+2))
                        info = font.render(('NAME : '+ str(tank_id)+ '  LIVES:  '+ str(tank_health)+ '  SCORE:  '+ str(tank_score)), True, (255, 255, 255)) 
                        screen.blit( info, (info_x,info_y))
                        
                for bullet in bullets:

                    if bullet['owner'] == client.tank_id:
                        draw_my_bullet(**bullet)

                    else:
                        draw_his_bullet(**bullet)
            
            except:
                pass 
        
            pygame.display.flip()
            
    #---------------------------CONNECTING TO SERVER------------------------#

    client = TankRpcClient()
    client.check_sever_status()
    client.obtain_token('room-12')
    event_client = TankConsumerClient('room-12')
    event_client.start()
    game_start(client,event_client)


def GameThree():
    window.destroy()
    
    #---------------------------SERVER INFO---------------------#
    IP ='34.254.177.17'
    PORT = 5672
    VIRTUAL_HOST = 'dar-tanks'
    USERNAME = 'dar-tanks'
    PASSWORD = '5orPLExUYnyVYZg48caMpX'
    #---------------------------SPRITES---------------------#

    vert = pygame.image.load('myBullet.bmp')

    enemyImage = pygame.image.load('enemy_tank.png')
    tankImage = pygame.image.load('my_tank.png')
    oppovert = pygame.image.load('oppovert.bmp')
    overi=pygame.image.load('gameover.jpg')

    pygame.init()
    screen = pygame.display.set_mode((1250, 600))
    #---------------------------RPC CLIENT---------------------#
    class TankRpcClient:
        def __init__(self):
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host = IP,
                    port = PORT,
                    virtual_host= VIRTUAL_HOST,
                    credentials= pika.PlainCredentials(
                        username= USERNAME,
                        password= PASSWORD
                    )
                )
            )
            self.channel = self.connection.channel()
            queue = self.channel.queue_declare(queue='',
            auto_delete = True,
            exclusive = True 
            )
            self.callback_queue = queue.method.queue
            self.channel.queue_bind(
                exchange = 'X:routing.topic',
                queue = self.callback_queue
            )

            self.channel.basic_consume( queue = self.callback_queue, on_message_callback = self.on_response, auto_ack = True )

            self.response = None
            self.corr_id = None
            self.token = None
            self.tank_id = None
            self.room_id = None

        def on_response(self, ch, method, props, body):
            if self.corr_id == props.correlation_id:
                self.response = json.loads(body)
                print(self.response)

        def call( self, key, message = {} ):
            self.response = None
            self.corr_id = str( uuid.uuid4())
            self.channel.basic_publish(
                exchange = 'X:routing.topic',
                routing_key = key,
                properties = pika.BasicProperties(
                    reply_to = self.callback_queue,
                    correlation_id = self.corr_id,
                ),
                body = json.dumps(message)
            )
            while self.response is None:
                self.connection.process_data_events()
        def check_sever_status(self):
            self.call('tank.request.healthcheck')
            return self.response['status'] == '200'

        def obtain_token( self , room_id ):
            message = {
                'roomId': room_id
            }
            self.call( 'tank.request.register', message)
            if 'token' in self.response:
                self.token = self.response['token']
                self.tank_id = self.response['tankId']
                self.room_id = self.response['roomId']
                return True
            return False

        def turn_tank(self, token, direction):
            message = {
                'token': token,
                'direction': direction
            }
            self.call('tank.request.turn', message)
        def fire(self,token):
            message = {
                'token':token
            }
            self.call('tank.request.fire', message)


    #---------------------------CONSUMER CLIENT---------------------#
    class TankConsumerClient(Thread):
        def __init__(self, room_id):
            super().__init__()
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host = IP,
                    port = PORT,
                    virtual_host=VIRTUAL_HOST,
                    credentials=pika.PlainCredentials(
                        username=USERNAME,
                        password=PASSWORD
                    )
                )
            )
            self.channel = self.connection.channel()
            queue = self.channel.queue_declare(queue = '',
            auto_delete = True,
            exclusive = True 
            )
            event_listener = queue.method.queue
            self.channel.queue_bind(exchange = 'X:routing.topic', 
            queue = event_listener,
            routing_key= 'event.state.' + room_id)

            self.channel.basic_consume(
                queue = event_listener,
                on_message_callback = self.on_response,
                auto_ack = True
            )
            self.response = None

        def on_response(self, ch, method, props, body):
            self.response = json.loads(body)
            print(self.response)

        def run(self):
            self.channel.start_consuming()
        
    #---------------------------VISUALIZING GAME---------------------#

    def draw_tank(x, y, direction,**kwargs):
        if direction == "RIGHT":
            screen.blit(tankImage,(x,y))
            
        if direction == "LEFT":
            screen.blit(pygame.transform.rotate(tankImage, 180),(x,y))

        if direction == "UP":
            screen.blit(pygame.transform.rotate(tankImage, 90),(x,y))

        if direction == "DOWN":
            screen.blit(pygame.transform.rotate(tankImage, 270),(x,y))
    def draw_enemy(x, y,direction,**kwargs):
        if direction == "RIGHT":
            screen.blit(pygame.transform.rotate(enemyImage, 180),(x,y))

        if direction == "LEFT":
            screen.blit(enemyImage,(x,y))

        if direction == "UP":
            screen.blit(pygame.transform.rotate(enemyImage, 270),(x,y))

        if direction == "DOWN":
            screen.blit(pygame.transform.rotate(enemyImage,90 ),(x,y))

    def draw_my_bullet(x, y,direction,**kwargs):
        if direction == 'UP' or direction == "DOWN":
            screen.blit(vert,(x,y))
        else:
            screen.blit(pygame.transform.rotate(vert,90 ),(x,y))

    def draw_his_bullet(x, y,direction,**kwargs):
        if direction=='UP' or direction == "DOWN":
            screen.blit(oppovert,(x,y))
        else:
            screen.blit(pygame.transform.rotate(oppovert,90 ),(x,y))

    #---------------------------GAME LOOP---------------------#
    
    

    def game_start(client,event_client):
        mainloop = True
        font = pygame.font.Font('game_over.ttf', 50)
        while mainloop:
            screen.fill((0,0,0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mainloop = False
                    #TankRpcClient.connection.close()
                    event_client.connection.close()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        mainloop = False
                        
            try:
                
                remaining_time = event_client.response['remainingTime']
                text = font.render(('Remaining Time: '+str(remaining_time)), True, (255, 255, 255)) 
                screen.blit(text, (10,5))
            

            
                
            #---------------------------GETTING LISTS---------------------#

            
                tanks = sorted( event_client.response['gameField']['tanks'] , key = itemgetter('score'), reverse=True) 
                bullets = event_client.response['gameField']['bullets']
                kickeds = event_client.response['kicked']
                winners = event_client.response['winners']
                losers = event_client.response['losers']

                global AFK2
                global goods2
                global bads2
                global do
                
            #----------------------SAVING LISTS GLOBAL --------------------------#

                for i in winners:
                    goods.append(i)

                for j in kickeds:
                    AFK.append(j)

                for k in losers:
                    bads.append(k)
            #---------------------------GAME OVER CONDITIONS---------------------#

                for afk in AFK:

                    if afk['tankId'] == client.tank_id:
                        
                        screen.blit( wordsshadow, (202,252))
                        words = font.render('YOU WERE KICKED FOR BEING AFK...', True, (255, 255, 255)) 
                        screen.blit( words, (200,250))
            
                for good in goods:
                    
                    if good['tankId'] == client.tank_id:
                        screen.blit(overi,(0,0))
                        
                        orda = font.render('YOU ARE WINNER!!...'+'YOUR SCORE:'+str(good['score']), True, (255, 255, 255)) 
                        screen.blit( orda, (200,250))
                        
                    
                for bad in bads: 
            
                    if bad['tankId'] == client.tank_id:
                        screen.blit(overi,(0,0))
                        
                        word = font.render('YOU ARE LOOSER!!...'+'YOUR SCORE:'+str(bad['score']), True, (255, 255, 255)) 
                        screen.blit( word, (200,250))   

            #---------------------------DRAWING TANKS AND  INFORMATION PANEL---------------------#
                
                for tank in  tanks:
                    
                    tank_health = tank['health']
                    tank_score = tank['score']
                    tank_id = tank['id']
                    info_x = 835
                    info_y = 18*tanks.index(tank)+30
            
                
                    if tank['id'] == client.tank_id:
                        my_x=tank['x']
                        my_y=tank['y']
                        draw_tank(**tank)
                        
                        ml = font.render(('YOUR ID:  '+str(tank['id'])+'  YOUR LIVES:  '+ str(tank_health)+ '  SCORE:  '+ str(tank_score)), True, (255, 255, 255)) 
                        screen.blit( ml, (808,1))
                        
            
                    else:
                        
                        
                        draw_enemy(**tank)
                        
                        info = font.render(('NAME : '+ str(tank_id)+ '  LIVES:  '+ str(tank_health)+ '  SCORE:  '+ str(tank_score)), True, (255, 255, 255)) 
                        screen.blit( info, (info_x,info_y))
                        
                        
                
                if (tank['x']+45>my_x-30 and tank['x']<my_x+75):
                    if (tank['y']<130 and my_y>400):
                        if tank['direction']=='UP':
                            client.turn_tank(client.token, 'DOWN') 
                            client.fire(client.token)
                        else:
                            client.turn_tank(client.token, 'UP') 
                            client.fire(client.token)
                    elif (my_y<130 and tank['y']>450):
                        if tank['direction']=='DOWN':
                            client.turn_tank(client.token, 'UP') 
                            client.fire(client.token)
                        else:
                            client.turn_tank(client.token, 'DOWN') 
                            client.fire(client.token)
                    else:
                        if my_y>tank['y']:
                            client.turn_tank(client.token, 'UP') 
                            client.fire(client.token)
                        else:
                            client.turn_tank(client.token, 'DOWN') 
                            client.fire(client.token)
            
                elif tank['y']+50>my_y and tank['y']<my_y+30:
                    if tank['x']>500 and my_x<100:
                        if tank['direction']=='RIGHT':
                            client.turn_tank(client.token, 'LEFT')
                            client.fire(client.token) 
                        else:
                            client.turn_tank(client.token, 'RIGHT') 
                            client.fire(client.token)
                    elif my_x>500 and tank['x']<100:
                        if tank['direction']=='LEFT':
                            client.turn_tank(client.token, 'RIGHT') 
                            client.fire(client.token)
                        else:
                            client.turn_tank(client.token, 'LEFT')
                            client.fire(client.token)
                    else:
                        if tank['x']>my_x:
                            client.turn_tank(client.token, 'RIGHT')
                            client.fire(client.token) 
                        else:
                            client.turn_tank(client.token, 'LEFT')
                            client.fire(client.token)
                else:
                    client.turn_tank(client.token, 'UP')

            
                        
                for bullet in bullets:
                    if bullet['owner'] == client.tank_id:
                        draw_my_bullet(**bullet)
                    else:
                        draw_his_bullet(**bullet)
                        
                        if bullet['x']<my_x-150 and bullet['x']>my_x+150+30 and bullet['y']<tank_y-150 and bullet['y']>tank_y+150+30:
                            if bullet['direction']=='RIGHT' or "LEFT":
                                client.turn_tank(client.token, 'UP') 
                                client.fire(client.token)
                            else:
                                client.turn_tank(client.token, 'LEFT') 
                                client.fire(client.token)
            
            except:
                pass 
        
            pygame.display.flip()
            
    #---------------------------CONNECTING TO SERVER------------------------#

    client = TankRpcClient()
    client.check_sever_status()
    client.obtain_token('room-12')
    event_client = TankConsumerClient('room-12')
    event_client.start()
    game_start(client,event_client)



    

def Leave():
  
    window.destroy()

window = Tk()
window.geometry('1200x600')
window.title("                                                                                                                                                                             D A R T A N K S  ")
load = Image.open("background).jpg")
render = ImageTk.PhotoImage(load)
img = Label(window, image=render)
img.image = render
img.place(x=0, y=0)

One = Button(window, text="     S I N G L E   M O D E     ",  command=GameOne,bg='black',fg='white',width=25,height=5,font='Elephant')
One.pack()
One.place(bordermode=INSIDE, x=400,y=200,height=50, width=400)

Two = Button(window, text="      M U L T I P L A Y E R    ", command=GameTwo,bg='black',fg='white', width=25, height=5,font='Elephant')
Two.pack()
Two.place(bordermode=INSIDE, x=400,y=300,height=50, width=400)

Three = Button(window, text="      A R T E F I C I A L   I N T E L L E C T    ", command=GameThree,bg='black',fg='white', width=25, height=5,font='Elephant')
Three.pack()
Three.place(bordermode=INSIDE, x=400,y=400,height=50, width=400)

Four = Button(window,  text="          Q U I T             ",  command=Leave,bg='black',fg='white',width=25,height=5,font='Elephant')
Four.pack()
Four.place(bordermode=INSIDE, x=400,y=520,height=50, width=400)

window.mainloop()