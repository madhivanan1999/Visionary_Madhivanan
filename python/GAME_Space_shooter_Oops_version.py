import turtle as td
import random
import time

PLAYER_SPEED = 20
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 600
BULLET_SPEED = 20
DELAY = 0.02
ENEMY_SPEED = 2 

#============================= creating_player =============================
class Player(td.Turtle):
    def __init__(self):
        super().__init__() #it will call the parent constructor
        self.shape("triangle")
        self.color("blue")
        self.penup()
        self.speed(0)
        self.goto(0,-250)#position
        self.setheading(90)#facing towards 90 degree

    def left_side(self):
        x = self.xcor() - PLAYER_SPEED
        if x < -280:
            x = -280
        self.setx(x)
    
    def right_side(self):
        x = self.xcor() + PLAYER_SPEED
        if x > 280:
            x = 280
        self.setx(x)

#============================= Creating_Bullet =============================
class Bullet(td.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.color("yellow")
        self.shapesize(stretch_wid= 0.5, stretch_len= 0.5)
        self.penup()
        self.speed(0)
        self.goto(0, -400)
        self.hideturtle()
        self.active= False

    def fire(self, player_x, player_y):
        if not self.active:
            self.goto(player_x, player_y +10)
            self.showturtle()
            self.active= True 

    def move(self):
        if self.active:
            y = self.ycor() + BULLET_SPEED
            self.sety(y)
            if y > 300:
                self.hideturtle()
                self.active= False

#============================= Creating_Enemy =============================
class Enemy(td.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.color("red")
        self.penup()
        self.speed(0)
        self.goto(random.randint(-250, 250), random.randint(100, 250))
    
    def move_down(self):
        y = self.ycor() - ENEMY_SPEED
        self.sety(y)
        if self.ycor() < -300:
            self.goto(random.randint(-250, 250), random.randint(200, 300))#respawn enemy at top

#============================ Creating_scoreboard ==========================
class Scoreboard(td.Turtle):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.color("white")
        self.penup()
        self.hideturtle()
        self.goto(0, 260)
        self.update_score()
        
    def update_score(self):
        self.clear()
        self.write(f"Score: {self.score}", align= 'center', font= ("courier", 20, 'bold'))    

    def increase(self):
        self.score += 10
        self.update_score()

#=============================== screen_Game =============================== 
class Game:
    def __init__(self):
        self.screen = td.Screen()
        self.screen.bgcolor("black")
        self.screen.title("🚀 Space Shooter ")
        self.screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.screen.tracer(0) #automatically updates the screen. ## tracer(0) = turns off automatic screen updates
        self.player = Player()
        self.bullet = Bullet()
        self.enemies = [Enemy() for _ in range(5)]
        self.scoreboard = Scoreboard()
        #syncronize keyboard
        self.screen.listen() #Without this, pressing keys wouldn’t trigger anything.
        self.screen.onkeypress(self.player.left_side, "Left")
        self.screen.onkeypress(self.player.right_side, "Right")
        self.screen.onkeypress(self.fire_bullet, "space" )
    
    def fire_bullet(self):
       self.bullet.fire(self.player.xcor(), self.player.ycor())
       
    def check_collision(self, t1, t2):
       distance = t1.distance(t2)
       return distance < 20
   
    def run(self):
        game_on = True
        while game_on:
            self.screen.update()
            time.sleep(DELAY)
            self.bullet.move()

            for enemy in self.enemies:
                enemy.move_down()
                if self.bullet.active and self.check_collision(self.bullet, enemy):
                    self.bullet.hideturtle()
                    self.bullet.active = False
                    enemy.goto(random.randint(-250,250), random.randint(200,300))
                    self.scoreboard.increase()

                if self.check_collision(enemy, self.player):
                    self.scoreboard.goto(0,0)
                    self.scoreboard.write("GAME OVER", align="center", font=("courier",30,"bold"))
                    game_on= False

        self.screen.mainloop()

if __name__ == "__main__":
    Game().run()

