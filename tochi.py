#!/usr/bin/env python3

import random as rand
import urllib.request, json 
import re
import images 
import vt100 as vt
import random


class Bar():
    BAR_WIDTH=15
    def __init__(self,title,value=0.0,step=1.0,texts={}):
        self.title=title
        self.value=value
        self.step=step
        self.texts = texts

    def sprint(self):
        v = int(self.value*self.BAR_WIDTH/100)
        return("%15s |%s|%3d%%" % (self.title,"#"*v+"-"*(self.BAR_WIDTH-v),self.value))

    def inc(self,step=None):
        if step == None:
            step = self.step
        self.value += step
        if self.value > 100:
            self.value = 100.0

    def dec(self,step=None):
        if step == None:
            step = self.step
        self.value -= step
        if self.value < 0:
            self.value = 0.0
    
    def status(self):
        for k in self.texts.keys():
            (min,max) = self.texts[k]
            if min <= self.value and self.value <= max:
                     return(k)
        return("")

    def comp(self,val):
        return(self.value >= val)

    def eq(self,val):
        return(self.value == val)



class Tochi():   
    EVOLVE_RATE = 4      # Chance to evolve on weight gain 1/n
    FOOD_CONSUME_RATE   = (60*30)/20
    FOOD_CONSUME_AMOUNT = 5
    FOOD_FULL_HAPPINES_DEC = 10
    HEALTH_STARVE_RATE = (60*5)/10
    HEALTH_STARVE_AMOUNT = 10
    HEAL_RATE = 60
    HEAL_FOOD_COST = 10
    HEAL_AMOUNT = 10
    HAPPINESS_RATE = (60*45)/20  # Tick rate where happiness is adjusted
    HAPPINESS_AMOUNT = 5         # Amount happiness goes down per tick rate
    PLAY_FOOD_COST = 2           # Energy cost (food) to play
    PLAY_FOOD_LIMIT = 30         # Food reserve needed to be played with
    PLAY_HAPPINESS_BOOST = 10    # Happiness increse on play
    GROW_RATE = (60*15)          # How often creature grow
    GROW_AMOUNT = 1

    THINGS = ['a bicycle','a stick','a ball','a teddybear','Donald Trump',
              'an advaark','an apple','a new 1 TB SSD', 'a Ferrari','the swedish prime minister']
    FOOD = ['an asparagus','an apple','avacados','an alfalfa','almonds','artichokes',
            'some applesauce','an antelope','a tuna','some apple juice','an avocado roll',
            'a bruscetta','bacon','black beans','bagels','baked beans','a bison',
            'some barley','a beer','a bisque','a bluefish','a bread','broccolies','a buritto',
            'a cabbage','a cake','carrots','celeries','a cheese','a chicken','a catfish',
            'some chips','some chocolate','clams','a cookie','a corn','cupcakes',
            'a crab','a curry','cereals with milk','dates','a duck','some dumplings','a donut','eggs',
            'enchiladas','an eggroll','an english muffin','eels','a fajita','a falafel',
            'a fish ','some fondu','a french toast','french fries','a garlic','a ginger','gnocchis',
            'a goose','granolas','some grapes','green beans','guacamole','gumbos',
            'graham crackers','a ham','a hamburger ','a cheeseburger','honey',
            'a hot dog','a haiku roll','an ice cream','an italian bread','jambalaya','some jelly',
            'jams','a beef jerky','jalapeños','a kebab','ketchup','a kiwi','kidney beans',
            'a kingfish','a lobster','a lamb','linguines','a lasagna','meatballs','a moose',
            'milk','a milkshake','noodles','an ostrich','a pizza','pepperonis','a porter',
            'pancakes','quesadillas','spinach','spaghetti','toasts',
            'waffles','some wine','walnuts','yogurt']
    FOOD_INSULT = [ 'looks at you like you are crazy',
                    'wonders if you have all horses in the stable',
                    'thinks your lights are on but no one is at home',
                    'wonders if you were dropped behind a wagon',
                    'wonders when you will get a grip of reality',
                    'ponders of the meaning of life',
                    'regrets befriending you',
                    "thinks you have two parts of brain, 'left' and 'right'. In the left side, there's nothing right. In the right side, there's nothing left.",
                    "won't engage in mental combat with the unarmed",
                    "thinks your birth certificate is probably an apology letter from the condom factory",
                    "thinks you must have been born on a highway because that's where most accidents happen",
                    "says you're so ugly, that when your mom dropped you off at school she got a fine for littering",
                    "thinks that if laughter is the best medicine, your face must be curing the world",
                    "thinks the only way you'll ever get laid is if you crawl up a chicken's ass and wait",
                    "is jealous of all the people that haven't met you",
                    "thinks stupidity is not a crime so you are free to go"]
    GENDERS = ['male','female']
    GENDER_HE_SHE = {'male':'he','female':'she'}
    GENDER_SELF = {'male':'himself','female':'herself'}
    GENDER_REPLACE = {'he':'she','his':'hers','himself':'herself','him':'her'}
    NAME_HE = ['Piston','Motor','Heinrich','Valter','Button','Maslov','Vippe','Aslof','Jacke']
    NAME_SHE = ['Blossom','Peachy','Vicki','Pedal','Trinity','Kate','Pearl','Hazel']
    NAME_LAST = ['Featherry','Soda','Wiggle','Flower','Grinch','Smokey','Teflon','Jacketty']
    CHUCK_URL = "http://api.icndb.com/jokes/random?firstName=%s&lastName="
    DEBUG = True
    def __init__(self,tick,player):
        self.health = Bar("Health",value=100,texts={
            'dead':(0,1),
            'barely alive':(2,10),
            'badly hurt':(11,30),
            'hurt':(31,60),
            'ruffed up':(61,80),
            'alive':(81,100)}
            )
        self.foodReserve= Bar("Food stash",value=100,texts={
            'starving':(0,10),
            'really hungry':(0,30),
            'hungry':(31,50),
            'satisfied':(51,100)
            })
        self.happiness = Bar("Happiness",value=50,texts={
            'empatic':(0,10),
            'depressed':(11,30),
            'sad':(31,45),
            'happy':(46,60),
            'thrilled':(61,80),
            'ecstatic':(81,100)
            })
        self.weight = 20
        self.gender = random.choice(self.GENDERS)
        names = getattr(self,"NAME_"+self.GENDER_HE_SHE[self.gender].upper())
        self.name = random.choice(names)
        self.owner = player
        self.born = tick
        self.died = -1
        self.lvl = 1
        self.type = images.toshis.lvl[self.lvl]['type']
        self.pic = images.toshis.lvl[self.lvl]['pic']

    def sprint(self,tick):
        age = self.age(tick)
        out = self.pic + '\n'
        out += "+-------[%-24s]-------+\n" % (self.name+' the ' +self.type)
        out += "| %-38s |\n" % (self.status().capitalize())
        out += "|                                        |\n"
        out += "| Age: %3d min %02d sec                    |\n" % ( age/60, age%60)
        out += "| Weight: %04d kg              Level: %2d |\n"  % (self.weight,self.lvl)
        if self.dead():
           out += "+---------------------------+------------+\n"
           out += "|    ###     ###     ###    |\n"
           out += "|    #  #     #      #  #   |\n"
           out += "|    ###      #      ###    |\n"
           out += "|    #  # #  ###  #  #      |\n"
           out += "+---------------------------+\n"
        else:
           out += "+----------------------------------------+\n"
           out += "| " + self.health.sprint()        + "  |\n"
           out += "| " + self.happiness.sprint()     + "  |\n"
           out += "| " + self.foodReserve.sprint()   + "  |\n"
           out += "+----------------------------------------+\n"
        return(out)

    def status(self):
        if self.dead():
            return('died at age %d min %s sec'%((self.died-self.born)/60,(self.died-self.born)%60))
        status = self.health.status()+", "+self.foodReserve.status() +\
            " and " + self.happiness.status()
        return(status)

        
    def dead(self):
        if self.died>0:
            return(True)
        return(False)

    def evolve(self):
         self.lvl += 1
         self.type = images.toshis.lvl[self.lvl]['type']
         self.pic = images.toshis.lvl[self.lvl]['pic']

    def save(self,fd):
        pass

    def load(self,fd):
        pass
        

    def play(self):
        if self.dead():
            return("You throw %s %s, but it won't change the fact that %s is dead!" % (
                self.name, rand.choice(self.THINGS), self.GENDER_HE_SHE[self.gender]))
        if self.foodReserve.comp(self.PLAY_FOOD_LIMIT):
            self.happiness.inc(self.PLAY_HAPPINESS_BOOST)
            self.foodReserve.dec(self.PLAY_FOOD_COST)
            return("%s plays with %s and feels a bit better about %s." % (
                self.name,rand.choice(self.THINGS),self.GENDER_SELF[self.gender]))
        return("%s is to hungry to play." % ( self.name))
   
    def feed(self):
        if self.dead():
            return("In a desperate move you give %s %s, but nope %s is still dead." % (
                self.name,rand.choice(self.FOOD),self.GENDER_HE_SHE[self.gender]))
        if self.foodReserve.value == 100:
            self.happiness.dec(self.FOOD_FULL_HAPPINES_DEC)
            return("%s %s.\n" % (self.name,rand.choice(self.FOOD_INSULT)))
        self.foodReserve.inc(20)
        return("You give %s %s, %s eats is all and feel a bit better." % (
                self.name,rand.choice(self.FOOD),self.GENDER_HE_SHE[self.gender]))
        
    def joke(self):
        # { "type": "success", "value": { "id": 140, "joke": "Bubbles  built a better mousetrap, but the world was too frightened to beat a path to his door.", "categories": [] } }
        with urllib.request.urlopen(self.CHUCK_URL % self.name) as url:
            data = json.loads(url.read().decode())
            joke = data["value"]["joke"]
            return(self.fix_gender(joke))

    def fix_gender(self,s):
        if self.gender == 'male':
            return(s)
        pattern = re.compile(r'\b(' + '|'.join(self.GENDER_REPLACE.keys()) + r')\b')
        result = pattern.sub(lambda x: self.GENDER_REPLACE[x.group()], s)
        return(result)

    def age(self,tick):
        if self.dead():
            return(self.died - self.born)
        return(tick - self.born)
    
    def tick(self,tick):
        # Dead do nothing
        if self.dead():
            return
        age = self.age(tick)
        # Consume food
        if age % self.FOOD_CONSUME_RATE == 0:
            self.foodReserve.dec(self.FOOD_CONSUME_AMOUNT)
        # No food, health and happiness goes down
        if self.foodReserve.eq(0) and age % self.HEALTH_STARVE_RATE == 0: 
            self.health.dec(self.HEALTH_STARVE_AMOUNT)
            self.happiness.dec(50)
            if self.health.eq(0):
                self.died=tick
                return
        if age % self.HAPPINESS_RATE == 0:
            self.happiness.dec(self.HAPPINESS_AMOUNT)
        # Hurt, happiness goes down
        if not self.health.eq(100) and age % self.HAPPINESS_RATE == 0:
            self.happiness.dec(self.HAPPINESS_AMOUNT)
            # Also hungry happiness plunges down
            if self.foodReserve.status() in ['hungry','starving','really hungry']: 
                self.happiness.dec(2*self.HAPPINESS_AMOUNT)
        # Heal if exist food 
        if not self.health.eq(100) and age % self.HEAL_RATE == 0:
            if self.foodReserve.comp(self.HEAL_FOOD_COST): 
                self.health.inc(self.HEAL_AMOUNT)
                self.foodReserve.dec(self.HEAL_FOOD_COST)

        # Every stat is good gain weight 
        if self.health.comp(100) and self.foodReserve.comp(50) and\
                age % self.GROW_RATE == 0:
                    self.weight += self.GROW_AMOUNT
                    # Gets harder and harder to evolve
                    if rand.randint(1,self.EVOLVE_RATE + self.lvl >> 1) == 1:
                       self.evolve()
        return


# vim: set sw=3 expandtab ts=3
