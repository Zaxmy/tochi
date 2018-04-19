import sqlite3
import crypt
import vt100
import urllib.request, json 
from hmac import compare_digest as compare_hash
from tochi import *

class Game():
    actions = { 'L' : 'login',
                'C' : 'create',
                'Q' : 'quit'
                }
    DB_VERSION = "1"

    def __init__(self,dbFile):
        self.ADMIN_RUNNING=True
        self.tick = 0
        self.players = {}
        a = Admin()
        a.name="ADMIN"
        a.set_password("Syp9393")
        self.players[a.name] = a
        self.conn = sqlite3.connect(dbFile)
        self.conn.row_factory = sqlite3.Row
        self.db = self.conn.cursor()
        self.db_init()
        self.load()

    def db_init(self):
        self.db.executescript("""
            create table if not exists Config(
                name    varchar(255) primary key,
                value   varchar(255)
            );
            create table if not exists Players( 
                name varchar(255) primary key, 
                password varchar(255)
            );
            create table if not exists Tochis(
                name varchar(255),
                owner varchar(255),
                level integer,
                health integer,
                foodReserve integer,
                happiness integer,
                weight integer,
                gender varchar(255),
                born integer,
                died integer,
                type varchar(255),
                primary key(name,owner)
            );
            """)
        self.conn.commit()
        if self.db_version() != self.DB_VERSION:
            self.db_upgrade()

    def db_upgrade(self):
        pass
    def db_version(self):
        self.db.execute("select value from Config where name like 'version'")
        ver = self.db.fetchone()
        if ver == None:
            self.db.execute("insert into Config values ('version',?)",self.DB_VERSION)
            return(self.db_version())
        return(ver[0])
        

    def auth(self,net):
        MENU = "\n Tochi Server v1.0 \n"+\
               "\u2554"+"\u2550"*22 +"\u2557 \n"+\
               "\u2551 [L]ogin              \u2551\n"+\
               "\u2551 [C]reate account     \u2551\n"+\
               "\u2551 [Q]uit               \u2551\n"+\
               "\u255a"+"\u2550"*22 + "\u255d\n"+\
               "?:"
               
        ans = []
        while not self.expect(ans,['L','C','Q']):
            net.send(MENU)
            ans = net.recv().strip().split()
        method = getattr(self,self.actions[ans[0].upper()],None)
        method(net,ans[1:])
        
    def expect(self,ans,answers):
            if len(ans)>0:
                if ans[0].upper() in answers:
                    return(True)
            return(False)

    def get_credentials(self,net,args):
        user = None
        passwd = None
        if len(args)>0:
            user = args[0].upper()
        if len(args)>1:
            passwd = args[1]
        if user == None:
            net.send("Username: ")
            ans = net.recv().strip()
            user = ans.upper()
        if passwd == None:
            net.send("Password: "+vt100.INVISIBLE)
            ans = net.recv().strip()
            passwd = ans
            net.send(vt100.OFF)
        return(user,passwd)
 
    def login(self,net,args):
       (user,passwd)  = self.get_credentials(net,args)
       if user == "":
            net.send("To much white space, bye...\n")
            return
       if user.upper() in self.players.keys():
            if self.players[user.upper()].login(passwd):
                self.players[user.upper()].go(net,self)
            else:
                net.send("Wrong password, bye...\n")
       else:
            net.send("No such user %s\n" % (user))

    def create(self,net,args):
       (user,passwd)  = self.get_credentials(net,args)
       while user.upper() in self.players.keys():
           net.send("User already exists\n")
           (user,passwd)  = self.get_credentials(net,[])
       if user == "":
            net.send("To much white space, bye...\n")
            return
       p = Player()
       p.set_password(passwd)
       p.name=user
       self.players[p.name.upper()] = p
       self.players[p.name.upper()].go(net,self)
 
    def step(self):
            self.tick += 1
            for p in self.players.values():
                if p.tama != None:
                    p.tama.tick(self.tick)

    def quit(self,net,args):
        pass

    def load(self):
        self.db.execute("SELECT * FROM Players")
        res = self.db.fetchall()
        for (user,passwd) in res:
            user = user.upper()
            if user == 'ADMIN':
                self.players[user] = Admin()
            else:
                self.players[user] = Player()
            print("Loaded user %s data" % user)
            self.players[user].name = user.upper()
            self.players[user].password = passwd
            self.players[user].load(self.db)
        self.db.execute("SELECT value FROM Config WHERE name = 'time'")
        res = self.db.fetchone()
        if res != None:
            self.tick = int(res['value'])
            print("Loaded server time [%d s]" % self.tick)

    def save(self):
        print("Saving game...")
        self.db.execute("SELECT value FROM Config WHERE name = 'time'")
        one = self.db.fetchone()
        if one != None:
            self.db.execute("UPDATE Config SET value=? WHERE name = 'time'",(str(self.tick),))
        else:
            self.db.execute("INSERT INTO Config(name,value) VALUES('time',?)",(str(self.tick),))
        print("Server time [%d s] saved" % self.tick)
        pc = 0
        for p in self.players.values():
            p.save(self.db)
            pc += 1
        print("Saved %d players" % pc)
        self.conn.commit()

class Player():
    MENU = "| [C]reate tochi\n"+\
           "| [U]pdate status\n"+\
           "| [F]eed\n"+\
           "| [P]lay\n"+\
           "| [J]oke\n"+\
           "| [O]ptions ...\n"+\
           "| [D]isconnect\n"+\
           "+------------------------\n"+\
           "Choice:"
    MENU_OPTIONS = "| [C]hange password\n"+\
                   "| [G]ive me flag\n"+\
                   "| [B]ack\n"+\
                   "+------------------------\n"+\
                   "Choice:"
    actions = { 'C' : 'create',
                'U' : 'do_nothing',
                'F' : 'feed',
                'P' : 'play',
                'J' : 'joke',
                'O' : 'options',
                'D' : 'do_nothing'
                }
    option_actions = { 'C' : 'new_password',
                       'G' : 'insult',
                       'B' : 'do_nothing'
                     }

    DISCONNECT = ['D']
    GOBACK = ['B','D']

    def __init__(self):
        self.password=''
        self.name=''
        self.tama=None

    def login(self,password):
        if compare_hash(crypt.crypt(password,self.password),self.password):
            return(True)
        return(False)

    def set_password(self,password):
        self.password= crypt.crypt(password)

    def go(self,net,game):
        print("%s logged in" % self.name)
        net.send(vt100.CLS+vt100.CURSORHOME)
        if self.tama != None:
            net.send(self.tama.sprint(game.tick))
        net.send(self.MENU)
        ans = net.recv().strip().upper()
        if ans in self.actions.keys():
            net.send(vt100.CLS+vt100.CURSORHOME)
            method = getattr(self,"action_" + self.actions[ans],None)
            method(net,game)
        while not ans in self.DISCONNECT:
            if self.tama != None:
                net.send(self.tama.sprint(game.tick))
            net.send(self.MENU)
            ans = net.recv().strip().upper()
            if ans in self.actions.keys():
                net.send(vt100.CLS+vt100.CURSORHOME)
                method = getattr(self,"action_" + self.actions[ans],None)
                method(net,game)
        
        print("%s logged off" % self.name)

    def action_options(self,net,game):
        net.send(self.MENU_OPTIONS)
        ans = net.recv().strip().upper()
        if ans in self.option_actions.keys():
            method = getattr(self,"action_" + self.option_actions[ans],None)
            method(net,game)
        while not ans in self.GOBACK:
            if self.tama != None:
                net.send(self.tama.sprint(game.tick))
            net.send(self.MENU_OPTIONS)
            ans = net.recv().strip().upper()
            if ans in self.option_actions.keys():
                method = getattr(self,"action_" + self.option_actions[ans],None)
                method(net,game)
    
    def action_new_password(self,net,game):
        net.send("Current password: "+vt100.INVISIBLE)
        ans = net.recv().strip()
        net.send(vt100.OFF)
        if self.login(ans):
            net.send("New password: "+vt100.INVISIBLE)
            ans = net.recv().strip()
            net.send(vt100.OFF+ "Password updated\n")
            self.set_password(ans)

    def action_create(self,net,game):
        if self.tama == None:
            self.tama = Tochi(game.tick,self.name)
        
    def action_feed(self,net,game):
        if self.tama != None:
            net.send(self.tama.feed()+"\n")

    def action_play(self,net,game):
        if self.tama != None:
            net.send(self.tama.play()+"\n")

    def action_joke(self,net,game):
        if self.tama != None:
            net.send(self.tama.joke()+"\n")

    def action_insult(self,net,game):
        with urllib.request.urlopen("http://quandyfactory.com/insult/json") as url:
            data = json.loads(url.read().decode())
            net.send("\n"+data["insult"]+"\n")
            net.send("The one with the heaviest, coolest and alive tochi\n"+\
                      "at the end of the competition gets a flag.\n")

    def action_do_nothing(self,net,game):
        pass

    def load(self,db):
        db.execute("SELECT * FROM Tochis WHERE owner = ?",(self.name,))
        data = db.fetchone()
        if data != None:
            self.tama = Tochi(data['born'],data['owner'])
            self.tama.happiness.value = data['happiness']
            self.tama.lvl = data['level']
            self.tama.foodReserve.value = data['foodReserve']
            self.tama.died = data['died']
            self.tama.weight = data['weight']
            self.tama.health.value = data['health']
            self.tama.gender = data['gender']
            self.tama.name = data['name']
            self.tama.type = images.tamas.lvl[data['level']]['type']
            self.tama.pic = images.tamas.lvl[data['level']]['pic']

    def save(self,db):
        db.execute("SELECT name FROM Players WHERE name = ?",(self.name,))
        entry = db.fetchone()
        if entry == None:
            db.execute("INSERT into Players(name,password) values (?,?)",(self.name,self.password,))
        else:
            db.execute("UPDATE Players set password = ? WHERE name = ?",(self.password,self.name,))
        if self.tama != None:
            db.execute("SELECT * FROM Tochis WHERE name = ?",(self.tama.name,))
            entry = db.fetchone()
            if entry == None:
                db.execute("""
                INSERT INTO Tochis(name,owner,level,health,foodReserve,
                                        happiness,weight,gender,born,died)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                        (self.tama.name,self.name,self.tama.lvl,self.tama.health.value,self.tama.foodReserve.value,
                        self.tama.happiness.value,self.tama.weight,self.tama.gender,self.tama.born,self.tama.died,
                        )
                )
            else:
                db.execute("""
                    UPDATE Tochis SET level=?, health=?,foodReserve=?,
                        happiness=?,weight=?,died=?
                    WHERE name = ? """, 
                        (self.tama.lvl,self.tama.health.value,self.tama.foodReserve.value,
                        self.tama.happiness.value,self.tama.weight,self.tama.died,self.tama.name,)
                    )
class Admin(Player):
    MENU = "[U]pdate status\n"+\
           "[S]hutdown server\n"+\
           "[L]ist users\n"+\
           "[T]ochis\n"+\
           "[O]ptions ...\n"+\
           "[E]volve tochi\n"+\
           "[D]isconnect\n\n"+\
           "Choice:"
    actions = { 'U' : 'update',
                'S' : 'shutdown',
                'L' : 'list_users',
                'T' : 'list_tochis',
                'E' : 'evolve',
                'O' : 'options',
                'D' : 'disconnect'
                }
    DISCONNECT = ['D','S']

    def action_shutdown(self,net,game):
        game.ADMIN_RUNNING = False
        net.send("Shutting down server\n\n")
        print("Admin called shutdown")

    def action_list_users(self,net,game):
        net.send("Usernames\n----------------\n")
        for l in game.players.keys():
            net.send(l+"\n")
        net.send("\n")

    def action_list_tochis(self,net,game):
        net.send("Tochis\n----------------\n")
        for l in game.players.values():
            net.send(l.name+"\t")
            if l.tama:
                t = l.tama
                net.send("N:%20s W:%03d L:%03d T: %-10s H:%03d E:%03d F:%03d" % (t.name,t.weight,
                            t.lvl,t.type,t.health.value,t.happiness.value,t.foodReserve.value))
            net.send("\n")
    def action_evolve(self,net,game):
        pass
    def action_update(self,net,game):
        pass




