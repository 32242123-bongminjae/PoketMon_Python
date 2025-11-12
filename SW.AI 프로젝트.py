#필요한 모듈
import pygame,random,time,math
#파이게임 초기화
pygame.init()
screen = pygame.display.set_mode((800,500))
pygame.display.set_caption("Python PoketMon")
clock = pygame.time.Clock()
#전역변수 선언
FPS = 30 #프레임 제한
running = True
myTurn = True
isbattle = True
isrun = False
camera_x = 0
camera_y = 0
movespeed = 10 # 속도 제어
movespeed_x = 0
movespeed_y = 0
mapname = "태초마을" #지역 이름
mapdata = "태초마을.txt" #지역별 colider
mapbattle = "관동1번도로B.txt" #지역별 몬스터 정보
player_x, player_y = 325, 425
waiting = 0
battlestack = 0
map_width = 0
map_height = 0
Quest = 0 #스토리
blocked_area = []
No = 1 #현재 출전중인 포켓몬 대기실 번호
direction = 2 #걷는 방향 
current_frame = 0 #현재 프레임
frame_load = 0
#색 설정
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Item:
    def __init__(self):
        self.itemlist = {}
        
    def add_item(self, name, quantity):
        if name in self.itemlist:
            self.itemlist[name] += quantity
        else:
            self.itemlist[name] = quantity
            
    def use_item(self, name, target):
        if name in self.itemlist and self.itemlist[name] > 0:
            self.itemlist[name] -= 1
            if name == "Poketball":
                quality = 1
                return self.use_poketball(target,quality)
            elif name == "Superball":
                quality = 1.5
                return self.use_poketball(target,quality)
            elif name == "Highperball":
                quality = 2
                return self.use_poketball(target,quality)
            elif name == "Masterball":
                quality = 1000
                return self.use_poketball(target,quality)
            elif name == "Potion":
                return self.use_potion(target)
            else:
                return f"{name} has no defined effect."
        else:
            return f"{name} is not available or out of stock."
    def use_poketball(self, target, quality):
        global isbattle
        BattleUI()
        Animation(0, 2)
        pygame.display.update()
        
        Grab = (((3 * int(target.getmaxhp())) - (2 * target.hp)) * target.rate * quality) / (3 * int(target.getmaxhp()))
        Wild = 65535 * ((Grab / 255) ** 0.25)
        
        if Grab >= 255: 
            isbattle = False
            return self.add_to_team_or_box(target)
        
        for i in range(3):
            b = random.randint(0, 65535)
            if Wild < b:
                screen.fill(WHITE)
                BattleUI()
                pygame.display.update()
                return f"You can't Grab a {target.name}!"
            text = [("ring"), ("")]
            Log(text, "None")
        isbattle = False
        return self.add_to_team_or_box(target)

    def add_to_team_or_box(self, new_pokemon):
        global poketmon1, poketmon2, poketmon3, poketmon4, poketmon5, poketmon6
        team = [poketmon1, poketmon2, poketmon3, poketmon4, poketmon5, poketmon6]
        text = [(f"You Grabbed a {new_pokemon.name}!"), ("")]
        Log(text, "None")
        chosen_slot = select_target_menu(team)
        if chosen_slot:
            index = team.index(chosen_slot)
            replaced_name = chosen_slot.name
            if replaced_name != "-":
                confirm_text = [
                    (f"{replaced_name} is already in this slot. Replace it with {new_pokemon.name}?"),
                    ("Press Enter to confirm or Esc to cancel."),
                ]
                Log(confirm_text, "None")
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                if index == 0:
                                    poketmon1 = new_pokemon
                                elif index == 1:
                                    poketmon2 = new_pokemon
                                elif index == 2:
                                    poketmon3 = new_pokemon
                                elif index == 3:
                                    poketmon4 = new_pokemon
                                elif index == 4:
                                    poketmon5 = new_pokemon
                                elif index == 5:
                                    poketmon6 = new_pokemon
                                return f"{new_pokemon.name} replaced {replaced_name} in slot {index + 1}!"
                            elif event.key == pygame.K_ESCAPE:
                                return
            if index == 0:
                poketmon1 = new_pokemon
            elif index == 1:
                poketmon2 = new_pokemon
            elif index == 2:
                poketmon3 = new_pokemon
            elif index == 3:
                poketmon4 = new_pokemon
            elif index == 4:
                poketmon5 = new_pokemon
            elif index == 5:
                poketmon6 = new_pokemon
            return f"{new_pokemon.name} has been added to your team in slot {index + 1}!"
        return

    def use_potion(self, target):
        if target.hp < target.getmaxhp():
            target.hp += 20
            if target.hp > target.getmaxhp():
                target.hp = target.getmaxhp()
            return f"You used a potion on {target.name}. HP is now {target.hp}/{target.getmaxhp()}!"
        else:
            return f"{target.name}'s HP is already full!"
    
    def get_items(self):
        return self.itemlist
        
class Pokemon:
    def __init__(self, number, name, level, exp, type1, type2, maxhp, hp, attack, defense, special_attack, special_defense, speed, catch_rate,lowlevel,maxlevel,rate,individual,sk1,sk2,sk3,sk4,movelevel,needexp,baseexp):
        self.number = number
        self.name = name
        self.level = level
        self.exp = 0
        self.type1 = type1
        self.type2 = type2
        self.maxhp = maxhp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.special_attack = special_attack
        self.special_defense = special_defense
        self.speed = speed
        self.catch_rate = catch_rate
        self.lowlevel = lowlevel
        self.maxlevel = maxlevel
        self.rate = rate
        self.individual = individual
        self.sk1 = sk1
        self.sk2 = sk2
        self.sk3 = sk3
        self.sk4 = sk4
        self.movelevel = movelevel
        self.needexp = needexp
        self.skill_data = {}
        self.baseexp = baseexp
    def __str__(self):
        return (f"Number: {self.number}, Name: {self.name}, Level: {self.level}, Exp: {self.exp}, Types: {self.type1}/{self.type2}, "
                f"HP: {self.getmaxhp()}/{self.hp}, Attack: {self.getattack()}, Defense: {self.getdefense()}, "
                f"Special Attack: {self.getspecialattack()}, Special Defense: {self.getspecialdefence()}, "
                f"Speed: {self.getspeed()}, Catch Rate: {self.catch_rate}, Lowlevel: {self.lowlevel}, "
                f"Maxlevel: {self.maxlevel}, Rate: {self.rate}, Individual: {self.individual},Sk1 : {self.sk1},Sk2 : {self.sk2},Sk3 : {self.sk3},Sk4 : {self.sk4},Needexp : {self.needexp}")
    def setvalue(self):
        self.individual = random.randint(0, 31)
        self.level = random.randint(self.lowlevel,self.maxlevel)
        self.hp = ((((self.maxhp * 2) + self.individual + 100) * (int(self.level) / 100) + 10) // 1) //1
        self.needexp = (((6/5) * self.level* self.level* self.level) - (15 * self.level * self.level) + (100 * self.level) - 140) // 1
    def setneedexp(self):
        self.needexp = (((6/5) * self.level* self.level* self.level) - (15 * self.level * self.level) + (100 * self.level) - 140) // 1
    def getmaxhp(self):
        return (((self.maxhp * 2) + self.individual + 100) * (int(self.level) / 100) + 10)//1
    def getattack(self):
        return (((self.attack * 2) + self.individual) * (int(self.level) / 100) + 5) // 1
    def getdefense(self):
        return (((self.defense * 2) + self.individual) * (int(self.level) / 100) + 5) // 1
    def getspecialattack(self):
        return (((self.special_attack * 2) + self.individual) * (int(self.level) / 100) + 5) // 1
    def getspecialdefence(self):
        return (((self.special_defense * 2) + self.individual) * (int(self.level) / 100) + 5) // 1
    def getspeed(self):
        return (((self.speed * 2) + self.individual) * (int(self.level) / 100) + 5) // 1
    
    def levelup(self):
        global poketmon7,poketmon0
        text = [("you gain"f"{poketmon7.baseexp * poketmon7.level} exp!"),("")]
        Log(text,"None")
        latehp = self.getmaxhp()
        while self.exp >= self.needexp:
            self.exp -= self.needexp
            self.level += 1
            self.setneedexp()
            self.hp += self.getmaxhp() - latehp
            
        if self.level > self.movelevel:
            text = [(f"{poketmon0.name} has been level {poketmon0.level}"),("")]
            Log(text,"None")
            self.Listup(0)
        
    def Listup(self,who):
        global moves_by_level
        if self.number not in moves_by_level:
            return

        available_moves = moves_by_level[self.number]

        new_moves = [move for lvl, move in available_moves.items() if self.movelevel < lvl <= self.level]
        if who == 0:
            for move in new_moves:
                self.LearnMove(move,0)
        elif who == 1:
            if len(new_moves) < 4:
                random_moves = random.sample(new_moves, len(new_moves))
            else:
                random_moves = random.sample(new_moves, 4)
            for move in random_moves:
                self.LearnMove(move,1)
            
        self.movelevel = self.level

    def LearnMove(self, new_move,who):
        current_moves = [self.sk1, self.sk2, self.sk3, self.sk4]
        print(self.sk4)
        if self.sk4 == "-":
            if self.sk1 == "-":
                self.sk1 = new_move
                self.save_skill_data(1)
            elif self.sk2 == "-":
                self.sk2 = new_move
                self.save_skill_data(2)
            elif self.sk3 == "-":
                self.sk3 = new_move
                self.save_skill_data(3)
            elif self.sk4 == "-":
                self.sk4 = new_move
                self.save_skill_data(4)
            if who == 0:
                text = [(f"{new_move} has been added!"),("")]
                f = Log(text,"None")
        else:
            text = [(f"Your Pokémon can learn {new_move}. Would you like to learn it?")]
            f = Log(text,"None")
            n = answer(f,"None")
            if n == 460:
                return
            text = [(f"Your Pokémon already knows 4 skills."),(f"Which move would you like to forget to learn {new_move}?"),("")]
            f = Log(text,"None")
            POS = 80
            running = True
            draw_text(screen, "What did you forget?", 20,WHITE, 10, 360)
            draw_text(screen, self.sk1, 20,WHITE, 125, 380)
            draw_text(screen, self.sk2, 20,WHITE, 275, 380)
            draw_text(screen, self.sk3, 20,WHITE, 425, 380)
            draw_text(screen, self.sk4, 20,WHITE, 575, 380)
            draw_text(screen, ">", 20,WHITE, POS, 380)
            pygame.display.update()
            while running:
                Log("","None")
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_d:
                            POS += 150
                        if event.key == pygame.K_a:
                            POS -= 150
                        if event.key == pygame.K_RETURN:
                            running = False
                        if POS > 530:
                                POS = 80
                        if POS < 80:
                                POS =530
                draw_text(screen, "What did you forget?", 20,WHITE, 10, 310)
                draw_text(screen, self.sk1, 20,WHITE, 100, 375)
                draw_text(screen, self.sk2, 20,WHITE, 250, 375)
                draw_text(screen, self.sk3, 20,WHITE, 400, 375)
                draw_text(screen, self.sk4, 20,WHITE, 550, 375)
                draw_text(screen, ">", 20,WHITE, POS, 375)
                pygame.display.update()
                clock.tick(60)
            if POS == 50:
                    self.sk1 = new_move
                    self.save_skill_data(1)
            elif POS == 200:
                    self.sk2 = new_move
                    self.save_skill_data(2)
            elif POS == 350:
                    self.sk3 = new_move
                    self.save_skill_data(3)
            elif POS == 500:
                    self.sk4 = new_move
                    self.save_skill_data(4)
            text = [(f"{new_move} has been added!"),("")]
            f = Log(text,"None")
            
    def save_skill_data(self, skill_slot):
            global skills_data

            skill_name = None
            if skill_slot == 1:
                skill_name = self.sk1
            elif skill_slot == 2:
                skill_name = self.sk2
            elif skill_slot == 3:
                skill_name = self.sk3
            elif skill_slot == 4:
                skill_name = self.sk4

            if not skill_name or skill_name == "-":
                print("No skill assigned to this slot.")
                return

            if skill_name in skills_data:
                self.skill_data[skill_name] = skills_data[skill_name]
                print(f"Skill {skill_name} data saved: {self.skill_data[skill_name]}")
            else:
                print(f"Skill {skill_name} not found in skills_data.")
                
    def get_skill_data(self, skill_slot, key_index):
        if skill_slot == 1:
            skill_name = self.sk1
        elif skill_slot == 2:
            skill_name = self.sk2
        elif skill_slot == 3:
            skill_name = self.sk3
        elif skill_slot == 4:
            skill_name = self.sk4
        else:
            print("Invalid skill slot number.")
            return None

        if skill_name in self.skill_data:
            skill_keys = list(self.skill_data[skill_name].keys())
            if key_index < len(skill_keys):
                key = skill_keys[key_index]
                return self.skill_data[skill_name][key]
            else:
                print("Invalid key index.")
                return None
        else:
            print(f"Skill {skill_name} not found in skill_data.")
            return None

skills_data = {
    "Tackle": {"power": 40, "category": "Physical", "type": "Normal", "pp": 35, "Hitrate": 100, "Priority": 0},
    "Growl": {"power": "-", "category": "Status", "type": "Normal", "pp": 40, "Hitrate": 100, "Priority": 0},
    "Leech Seed": {"power": "-", "category": "Status", "type": "Grass", "pp": 10, "Hitrate": 90, "Priority": 0},
    "Vine Whip": {"power": 35, "category": "Physical", "type": "Grass", "pp": 10, "Hitrate": 100, "Priority": 0},
    "Poison Powder": {"power": "-", "category": "Status", "type": "Poison", "pp": 35, "Hitrate": 75, "Priority": 0},
    "Razor Leaf": {"power": 55, "category": "Physical", "type": "Grass", "pp": 25, "Hitrate": 95, "Priority": 0},
    "Growth": {"power": "-", "category": "Status", "type": "Normal", "pp": 40, "Hitrate": "-", "Priority": 0},
    "Sleep Powder": {"power": "-", "category": "Status", "type": "Grass", "pp": 15, "Hitrate": 75, "Priority": 0},
    "SolarBeam": {"power": 120, "category": "Special", "type": "Grass", "pp": 10, "Hitrate": 100, "Priority": 0},
    "Ember": {"power": 40, "category": "Special", "type": "Fire", "pp": 25, "Hitrate": 100, "Priority": 0},
    "Leer": {"power": "-", "category": "Status", "type": "Normal", "pp": 30, "Hitrate": 100, "Priority": 0},
    "Rage": {"power": "-", "category": "Physical", "type": "Normal", "pp": 20, "Hitrate": 100, "Priority": 0},
    "Slash": {"power": 70, "category": "Physical", "type": "Normal", "pp": 20, "Hitrate": 100, "Priority": 0},
    "Flamethrower": {"power": 95, "category": "Special", "type": "Fire", "pp": 15, "Hitrate": 100, "Priority": 0},
    "Fire Spin": {"power": 35, "category": "Special", "type": "Fire", "pp": 15, "Hitrate": 70, "Priority": 0},
    "Bubble": {"power": 20, "category": "Special", "type": "Water", "pp": 30, "Hitrate": 100, "Priority": 0},
    "Water Gun": {"power": 40, "category": "Special", "type": "Water", "pp": 25, "Hitrate": 100, "Priority": 0},
    "Bite": {"power": 60, "category": "Physical", "type": "Normal", "pp": 25, "Hitrate": 100, "Priority": 0},
    "Withdraw": {"power": "-", "category": "Status", "type": "Water", "pp": 40, "Hitrate": "-", "Priority": 0},
    "Hydro Pump": {"power": 120, "category": "Special", "type": "Water", "pp": 5, "Hitrate": 80, "Priority": 0},
    "Quick Attack": {"power": 40, "category": "Physical", "type": "Normal", "pp": 30, "Hitrate": 100, "Priority": 1},
    "Whirlwind": {"power": "-", "category": "Status", "type": "Normal", "pp": 20, "Hitrate": 100, "Priority": 0},
    "Wing Attack": {"power": 60, "category": "Physical", "type": "Flying", "pp": 35, "Hitrate": 100, "Priority": 0},
    "Agility": {"power": "-", "category": "Status", "type": "Psychic", "pp": 30, "Hitrate": "-", "Priority": 0},
    "Hyper Fang": {"power": 80, "category": "Physical", "type": "Normal", "pp": 15, "Hitrate": 90, "Priority": 0},
    "Focus Energy": {"power": "-", "category": "Status", "type": "Normal", "pp": 30, "Hitrate": "-", "Priority": 0},
    "Super Fang": {"power": "-", "category": "Physical", "type": "Normal", "pp": 10, "Hitrate": 90, "Priority": 0},
    "Scratch": {"power": 40, "category": "Physical", "type": "Normal", "pp": 35, "Hitrate": 100, "Priority": 0},
    "Tail Whip": {"power": "-", "category": "Status", "type": "Normal", "pp": 30, "Hitrate": 100, "Priority": 0}
}

moves_by_level = {
    1: {1: "Tackle", 3: "Growl", 7: "Leech Seed", 13: "Vine Whip", 20: "Poison Powder", 27: "Razor Leaf", 34: "Growth", 41: "Sleep Powder", 48: "SolarBeam"},
    2: {1: "Tackle", 3: "Growl", 7: "Leech Seed", 13: "Vine Whip", 20: "Poison Powder", 27: "Razor Leaf", 34: "Growth", 41: "Sleep Powder", 48: "SolarBeam"},
    3: {1: "Tackle", 3: "Growl", 7: "Leech Seed", 13: "Vine Whip", 20: "Poison Powder", 27: "Razor Leaf", 34: "Growth", 41: "Sleep Powder", 48: "SolarBeam"}, 
    4: {1: "Scratch", 2: "Growl", 7: "Ember", 15: "Leer", 22: "Rage", 30: "Slash", 38: "Flamethrower", 48: "Fire Spin"},
    5: {1: "Scratch", 2: "Growl", 7: "Ember", 15: "Leer", 22: "Rage", 30: "Slash", 38: "Flamethrower", 48: "Fire Spin"},
    6: {1: "Scratch", 2: "Growl", 7: "Ember", 15: "Leer", 22: "Rage", 30: "Slash", 38: "Flamethrower", 48: "Fire Spin"},
    7: {1: "Tackle", 2: "Tail Whip", 7: "Bubble", 15: "Water Gun", 22: "Bite", 28: "Withdraw", 35: "Rage", 42: "Hydro Pump"},
    8: {1: "Tackle", 2: "Tail Whip", 7: "Bubble", 15: "Water Gun", 22: "Bite", 28: "Withdraw", 35: "Rage", 42: "Hydro Pump"},
    9: {1: "Tackle", 2: "Tail Whip", 7: "Bubble", 15: "Water Gun", 22: "Bite", 28: "Withdraw", 35: "Rage", 42: "Hydro Pump"},
    16: {1: "Tackle", 5: "Sand Attack", 12: "Quick Attack", 21: "Whirlwind", 31: "Wing Attack", 40: "Agility"},
    17: {1: "Tackle", 5: "Sand Attack", 12: "Quick Attack", 21: "Whirlwind", 31: "Wing Attack", 40: "Agility"},
    18: {1: "Tackle", 5: "Sand Attack", 12: "Quick Attack", 21: "Whirlwind", 31: "Wing Attack", 40: "Agility"},
    19: {1: "Tackle", 2: "Tail Whip", 7: "Quick Attack", 14: "Hyper Fang", 23: "Focus Energy", 34: "Super Fang"},
    20: {1: "Tackle", 2: "Tail Whip", 7: "Quick Attack", 14: "Hyper Fang", 23: "Focus Energy", 34: "Super Fang"},
}
    
def Player(moving, direction, screen):
    global player_x, player_y, camera_x, camera_y
    global current_frame,frame_load

    flip = 0
    frame_load += 1
    if direction == 4:
        direction = 1
        flip = 1

    if moving == "idle":
        filename = "Hana Caraka - Base Character [sample]/idle.png"
        total_frames = 3
    elif moving == "walk":
        filename = "Hana Caraka - Base Character [sample]/walk.png"
        total_frames = 7

    if frame_load > 2:
        frame_load = 0
        current_frame += 1
        if current_frame > total_frames:
            current_frame = 0

    sprite_sheet = pygame.image.load(filename).convert_alpha()
    frame_width = 80
    frame_height = 80
    frame_x = current_frame * frame_width
    frame_y = (direction - 1) * frame_height

    frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
    frame_surface.blit(sprite_sheet, (0, 0), (frame_x, frame_y, frame_width, frame_height))

    scale_factor = 2
    scaled_width = frame_width * scale_factor
    scaled_height = frame_height * scale_factor
    scaled_frame_surface = pygame.transform.scale(frame_surface, (scaled_width, scaled_height))

    if flip == 1:
        scaled_frame_surface = pygame.transform.flip(scaled_frame_surface, True, False)

    player_rect = pygame.Rect(player_x - camera_x - scaled_width // 2, player_y - camera_y - scaled_height // 2, scaled_width, scaled_height)
    screen.blit(scaled_frame_surface, player_rect.topleft)

def load_pokemon_from_file( line_number,filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()
    line = lines[line_number].strip().split()
    number = int(line[0])
    name = line[1]
    level = line[2]
    exp = line[3]
    type1 = line[4]
    type2 = line[5] 
    maxhp = int(line[6])
    hp = int(line[7])
    attack = int(line[8])
    defense = int(line[9])
    special_attack = int(line[10])
    special_defense = int(line[11])
    speed = int(line[12])
    catch_rate = int(line[13])
    lowlevel = int(line[14])
    maxlevel = int(line[15])
    rate = int(line[16])
    individual = int(line[17])
    sk1 = line[18]
    sk2 = line[19]
    sk3 = line[20]
    sk4 = line[21]
    movelevel = int(line[22])
    needexp = int(line[23])
    baseexp = int(line[24])
    return Pokemon(number, name,level,exp,type1, type2, maxhp, hp, attack, defense, special_attack, special_defense, speed, catch_rate,lowlevel,maxlevel,rate,individual,sk1,sk2,sk3,sk4,movelevel,needexp,baseexp)

poketmon0 = load_pokemon_from_file(0,"poketmon_data.txt")
poketmon1 = load_pokemon_from_file(0,"poketmon_data.txt")
poketmon2 = load_pokemon_from_file(0,"poketmon_data.txt")
poketmon3 = load_pokemon_from_file(0,"poketmon_data.txt")
poketmon4 = load_pokemon_from_file(0,"poketmon_data.txt")
poketmon5 = load_pokemon_from_file(0,"poketmon_data.txt")
poketmon6 = load_pokemon_from_file(0,"poketmon_data.txt")
poketmon7 = load_pokemon_from_file(0,"poketmon_data.txt")
inventory = Item()
def main():
    global running
    StartGame()
    while running:
        UpdateGame()
        clock.tick(FPS)
    QuitGame()

def MapLoad(mapname, camera_x, camera_y, player_x, player_y):
    global scaled_map_image, map_width, map_height
    if mapname == "태초마을":
        map_image = pygame.image.load("태초마을.png").convert()
        map_width = 1280
        map_height = 1185
    if mapname == "관동1번도로":
        map_image = pygame.image.load("관동1번도로.png").convert()
        map_width = 2310
        map_height = 4400
    if mapname == "상록시티":
        map_image = pygame.image.load("상록시티.png").convert()
        map_width = 2400
        map_height = 1650

    scaled_map_image = pygame.transform.scale(map_image, (map_width, map_height))
    screen.blit(scaled_map_image, (-camera_x, -camera_y))

def UpdateGame():
    global running, camera_x, camera_y, player_x, player_y, mapname, Quest, mapdata, mapbattle
    global waiting, battlestack, direction, current_frame,movespeed_x,movespeed_y

    ismoving = False
    frame = 0
    screen.fill((0, 0, 0))
    
    MapLoad(mapname, camera_x, camera_y, player_x, player_y)
    camera_x = max(0, min(player_x - screen.get_width() // 2, map_width - screen.get_width()))
    camera_y = max(0, min(player_y - screen.get_height() // 2, map_height - screen.get_height()))
    player_x = max(0, min(player_x, map_width))
    player_y = max(0, min(player_y, map_height))
    
    if not ismoving:
        Player("idle", direction, screen)
        pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                Interaction()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        if not is_blocked(player_x, player_y - movespeed, mapdata):
            ismoving = True
            direction = 3
            movespeed_y = -10
    if keys[pygame.K_s]:
        if not is_blocked(player_x, player_y + movespeed, mapdata):
            ismoving = True
            direction = 2
            movespeed_y = 10
    if keys[pygame.K_a]:
        if not is_blocked(player_x - movespeed, player_y, mapdata):
            ismoving = True
            direction = 4
            movespeed_x = -10
    if keys[pygame.K_d]:
        if not is_blocked(player_x + movespeed, player_y, mapdata):
            ismoving = True
            direction = 1
            movespeed_x = 10
    if ismoving:
        Player("walk", direction, screen)
        if movespeed_y != 0 and movespeed_x !=0:
            movespeed_y = movespeed_y // 1.2
            movespeed_x = movespeed_x // 1.2
        player_y += movespeed_y
        player_x += movespeed_x
        movespeed_x = 0
        movespeed_y = 0
        frame = (frame + 1)
    
    if ismoving and (poketmon1.hp > 0 or poketmon2.hp > 0 or poketmon3.hp > 0 or poketmon4.hp > 0 or poketmon5.hp > 0 or poketmon6.hp > 0):
        if is_battled(player_x, player_y - movespeed, mapbattle):
            waiting += 1
            if waiting > 15: #원래 waiting = 15
                waiting = 0
                battlestack += 1
                print(battlestack)
                ran = random.randint(1, 100)
                if battlestack > ran:
                    fade_transition(screen)
                    battle()
                    battlestack = 0
    pygame.display.flip()

def battle():
    global No,poketmon0,poketmon1,poketmon2,poketmon3,poketmon4,poketmon5,poketmon6,poketmon7,isbattle,myTurn,inventory,isrun
    poketmon = [poketmon0,poketmon1,poketmon2,poketmon3,poketmon4,poketmon5,poketmon6,poketmon7]
    isbattle = True
    myTurn = True
    isrun = False
    poketmon0  = poketmon[No]
    POSX = 575
    POSY = 375
    screen.fill(WHITE)
    enemySpawn()
    Log("","None")
    BattleUI()
    time.sleep(0.3)
    print(poketmon0)
    while isbattle:
        screen.fill(WHITE)
        Log("","None")
        Animation(poketmon7.number,0)
        Animation(poketmon0.number,1)
        poketmon[No]  = poketmon[0]
        if myTurn == True:
            running = True
            draw_text(screen, "What did you doing?", 20,WHITE, 10, 360)
            draw_text(screen, "Fight", 20,WHITE, 600, 375)
            draw_text(screen, "Item", 20,WHITE, 700, 375)
            draw_text(screen, "Change", 20,WHITE, 600, 425)
            draw_text(screen, "Run", 20,WHITE, 700, 425)
            draw_text(screen, ">", 20,WHITE, POSX, POSY)
            pygame.display.update()
            while running:
                BattleUI()
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            poketmon0.hp = 1
                        if event.key == pygame.K_b:
                            inventory.add_item("Masterball", 3)
                        if event.key == pygame.K_d:
                            POSX += 100
                        if event.key == pygame.K_a:
                            POSX -= 100
                        if event.key == pygame.K_RETURN:
                            running = False
                        if POSX > 675:
                            if POSY == 375:
                                POSX = 575
                                POSY = 425
                            elif POSY == 425:
                                POSX = 575
                                POSY = 375
                        if POSX < 575:
                            if POSY == 375:
                                POSX =675
                                POSY = 425
                            elif POSY == 425:
                                POSX = 675
                                POSY = 375
                        Log("","None")
                        draw_text(screen, "What did you doing?", 20,WHITE, 10, 360)
                        draw_text(screen, "Fight", 20,WHITE, 600, 375)
                        draw_text(screen, "Item", 20,WHITE, 700, 375)
                        draw_text(screen, "Change", 20,WHITE, 600, 425)
                        draw_text(screen, "Run", 20,WHITE, 700, 425)
                        draw_text(screen, ">", 20,WHITE, POSX, POSY)
                clock.tick(60)
            if POSX == 575:
                if POSY == 375:
                    Fight()
                elif POSY == 425:
                    Change()
                    BattleUI()
                    myTurn = False
            elif POSX == 675:
                if POSY == 375:
                    ItemMenu(inventory)
                    myTurn = False
                elif POSY == 425:
                    Run()
                    myTurn = False
        elif myTurn == False:
            enemyTurn(-1)
            myTurn = True
        if (poketmon7.hp <= 0):
            isbattle = False
        elif (poketmon0.hp <= 0):
            if (poketmon1.hp > 0 or poketmon2.hp > 0 or poketmon3.hp > 0 or poketmon4.hp > 0 or poketmon5.hp > 0 or poketmon6.hp > 0):
                Change()
                isbattle = True
            else:
                isbattle = False
        clock.tick(60)
    reward()

def Run():
    global poketmon0, poketmon7, No,isbattle,isrun
    escape_probability = (poketmon0.speed / poketmon7.speed) * 0.5
    random_chance = random.random() 
    if random_chance < escape_probability:
        text = [(f"{poketmon.name} successfully escaped!"),("")]
        Log(text, "None")
        isbattle = False
        isrun = True
        return "Escape successful!"
    else:
        text = [(f"{poketmon0.name} failed to escape!"),("")]
        Log(text, "None")
        return "Escape failed."



def Change():
    global No, poketmon0, poketmon1, poketmon2, poketmon3, poketmon4, poketmon5, poketmon6
    team = [poketmon1, poketmon2, poketmon3, poketmon4, poketmon5, poketmon6]
    current_pokemon = poketmon0
    text = [("Choose a Pokémon to switch with."), ("")]
    Log(text, "None")
    arunning = True
    nextrunning = False
    selected_index = 0
    num_slots = len(team)
    while arunning:
        screen.fill(BLACK)
        draw_text(screen, "Select a Slot", 40, WHITE, 10, 10)
        y_offset = 100
        for i, target in enumerate(team):
            prefix = ">" if i == selected_index else " "
            color = WHITE
            if target.name != "-":
                draw_text(screen, f"{prefix} {target.name} {int(target.hp)} / {int(target.getmaxhp())}", 30, color, 50, y_offset)
            else:
                draw_text(screen, f"{prefix} Empty Slot", 30, color, 50, y_offset)
            y_offset += 40

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    arunning = False
                    text = ["Switch canceled."]
                    Log(text, "None")
                    break 
                elif event.key == pygame.K_s:  
                    selected_index = (selected_index + 1) % num_slots
                elif event.key == pygame.K_w:  
                    selected_index = (selected_index - 1) % num_slots
                elif event.key == pygame.K_RETURN:
                    selected_pokemon = team[selected_index]

                    if selected_pokemon == current_pokemon:
                        text = [("You cannot switch with the current Pokémon."), ("")]
                        Log(text, "None")
                        continue  
                    elif selected_pokemon.name == "-":
                        text = [("This slot is empty. Please select a valid Pokémon."), ("")]
                        Log(text, "None")
                        continue 
                    elif selected_pokemon.hp <= 0:
                        text = [("This Pokémon is fainted. Please select another Pokémon."), ("")]
                        Log(text, "None")
                        continue  
                    else:
                        confirmation_text = [
                            (f"Switch {current_pokemon.name} with {selected_pokemon.name}?"),
                            ("Press ENTER to confirm or ESC to cancel."),
                            ("")
                        ]
                        Log(confirmation_text, "None")
                        nextrunning = True
                        arunning = False  
    while nextrunning:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    team[No - 1] = current_pokemon  
                    poketmon0 = selected_pokemon 
                    No = team.index(selected_pokemon) + 1  
                    nextrunning = False  
                    text = [f"Switched to {selected_pokemon.name}!"]
                    Log(text, "None")
                    break  
                elif event.key == pygame.K_ESCAPE:
                    nextrunning = False 
                    text = ["Switch canceled."]
                    Log(text, "None")
                    break  



def ItemMenu(inventory):
    running = True
    current_page = 0
    items_per_page = 8
    selected_index = 0
    while running:
        screen.fill(BLACK)
        items = list(inventory.get_items().items())
        total_pages = (len(items) - 1) // items_per_page + 1
        start_index = current_page * items_per_page
        end_index = start_index + items_per_page
        page_items = items[start_index:end_index]
        draw_text(screen, "Item Menu", 40, WHITE, 300, 30)
        y_offset = 100
        for i, (item_name, quantity) in enumerate(page_items):
            prefix = ">" if i == selected_index else " "
            draw_text(screen, f"{prefix} {item_name} x{quantity}", 30, WHITE, 100, y_offset)
            y_offset += 40
        draw_text(screen, f"Page {current_page + 1}/{total_pages}", 30, WHITE, 350, 400)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    current_page = (current_page + 1) % total_pages
                    selected_index = 0  
                elif event.key == pygame.K_a: 
                    current_page = (current_page - 1) % total_pages
                    selected_index = 0  
                elif event.key == pygame.K_w:  
                    selected_index = (selected_index - 1) % len(page_items)
                elif event.key == pygame.K_s:  
                    selected_index = (selected_index + 1) % len(page_items)
                elif event.key == pygame.K_RETURN:
                    if 0 <= selected_index < len(page_items):
                        selected_item = page_items[selected_index][0]
                        if selected_item == "Poketball" or selected_item == "Superball" or selected_item == "Highperball" or selected_item == "Masterball":
                            target = poketmon7
                        else:
                            target = select_target_menu(
                                [poketmon1, poketmon2, poketmon3, poketmon4, poketmon5, poketmon6]
                            )
                        if target:
                            screen.fill(WHITE)
                            BattleUI()
                            result = inventory.use_item(selected_item, target)
                            text = [result,("")]
                            Log(text,"None")
                        running = False
                        


def select_target_menu(target_list):
    running = True
    selected_index = 0
    while running:
        screen.fill(BLACK)
        draw_text(screen, "Select a Slot", 40, WHITE, 10, 10)

        y_offset = 100
        for i, target in enumerate(target_list):
            prefix = ">" if i == selected_index else " "
            color = WHITE
            if target.name != "-":
                draw_text(screen, f"{prefix} {target.name} {int(target.hp)} / {int(target.getmaxhp())}", 30, color, 50, y_offset)
            else:
                draw_text(screen, f"{prefix} Empty Slot", 30, color, 50, y_offset)
            y_offset += 40

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_s:
                    selected_index = (selected_index + 1) % len(target_list)
                elif event.key == pygame.K_w:
                    selected_index = (selected_index - 1) % len(target_list)
                elif event.key == pygame.K_RETURN:
                    return target_list[selected_index]


def reward():
    global poketmon0,poketmon7
    if poketmon0.hp > 0 and isrun == False:
        poketmon0.exp += poketmon7.baseexp * poketmon7.level
        poketmon0.levelup()

def enemyTurn(pi):
    global poketmon0,poketmon7
    ran = random.randint(1,4)
    if (poketmon7.hp <= 0):
                return
    while poketmon7.get_skill_data(ran,0) == None:
        ran = random.randint(1,4)
    if pi == -1:
        Damage(poketmon7,poketmon0,poketmon0.get_skill_data(ran,0),poketmon0.get_skill_data(ran,1),poketmon0.get_skill_data(ran,2),poketmon0.get_skill_data(ran,4))
        return()
    if poketmon7.get_skill_data(ran,5) > poketmon0.get_skill_data(pi,5):
        Damage(poketmon7,poketmon0,poketmon0.get_skill_data(ran,0),poketmon0.get_skill_data(ran,1),poketmon0.get_skill_data(ran,2),poketmon0.get_skill_data(ran,4))
        if (poketmon0.hp <= 0):
                return
        Damage(poketmon0,poketmon7,poketmon0.get_skill_data(pi,0),poketmon0.get_skill_data(pi,1),poketmon0.get_skill_data(pi,2),poketmon0.get_skill_data(pi,4))
    elif poketmon7.get_skill_data(ran,5) < poketmon0.get_skill_data(pi,5):
        Damage(poketmon0,poketmon7,poketmon0.get_skill_data(pi,0),poketmon0.get_skill_data(pi,1),poketmon0.get_skill_data(pi,2),poketmon0.get_skill_data(pi,4))
        if (poketmon0.hp <= 0):
                return
        Damage(poketmon7,poketmon0,poketmon0.get_skill_data(ran,0),poketmon0.get_skill_data(ran,1),poketmon0.get_skill_data(ran,2),poketmon0.get_skill_data(ran,4))
    elif poketmon7.get_skill_data(ran,5) == poketmon0.get_skill_data(pi,5):
        if poketmon0.speed >= poketmon7.speed:
            Damage(poketmon0,poketmon7,poketmon0.get_skill_data(pi,0),poketmon0.get_skill_data(pi,1),poketmon0.get_skill_data(pi,2),poketmon0.get_skill_data(pi,4))
            if (poketmon7.hp <= 0):
                return
            Damage(poketmon7,poketmon0,poketmon0.get_skill_data(ran,0),poketmon0.get_skill_data(ran,1),poketmon0.get_skill_data(ran,2),poketmon0.get_skill_data(ran,4))
        elif poketmon0.speed < poketmon7.speed:
            Damage(poketmon7,poketmon0,poketmon0.get_skill_data(ran,0),poketmon0.get_skill_data(ran,1),poketmon0.get_skill_data(ran,2),poketmon0.get_skill_data(ran,4))
            if (poketmon0.hp <= 0):
                return
            Damage(poketmon0,poketmon7,poketmon0.get_skill_data(pi,0),poketmon0.get_skill_data(pi,1),poketmon0.get_skill_data(pi,2),poketmon0.get_skill_data(pi,4))
    
def Fight():
    global No,poketmon0,poketmon7,myTurn,isbattle
    POSx = 75
    POSy = 370
    i = 1
    running = True
    while running:
        Log("","None")
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_d:
                    POSx += 300
                    i += 1
                    print(poketmon0.get_skill_data(i,0))
                if event.key == pygame.K_a:
                    POSx -= 300
                    i -= 1
                    print(poketmon0.get_skill_data(i,0))
                if event.key == pygame.K_RETURN:
                    running = False
                if POSx > 375:
                    if POSy == 370:
                        POSx = 75
                        POSy = 410
                        i = 3
                    elif POSy == 410:
                        POSx = 75
                        POSy = 370
                        i = 1
                if POSx < 75:
                    if POSy == 370:
                        POSx = 375
                        POSy = 410
                        i = 4
                    elif POSy == 410:
                        POSx = 375
                        POSy = 370
                        i = 2
        draw_text(screen, poketmon0.sk1, 20,WHITE, 100, 370)
        draw_text(screen, poketmon0.sk2, 20,WHITE, 400, 370)
        draw_text(screen, poketmon0.sk3, 20,WHITE, 100, 410)
        draw_text(screen, poketmon0.sk4, 20,WHITE, 400, 410)
        draw_text(screen, ">", 20,WHITE, POSx, POSy)
        if poketmon0.get_skill_data(i,0) != None:
            draw_text(screen, f"[{poketmon0.get_skill_data(i,1)}]" , 20,WHITE, 580, 355)
            draw_text(screen, f"[{poketmon0.get_skill_data(i,2)}]" , 20,WHITE, 680, 355)
            draw_text(screen, "power:"+f"[{poketmon0.get_skill_data(i,0)}]" , 15,WHITE, 580, 385)
            draw_text(screen, "pp:"+f"[{poketmon0.get_skill_data(i,3)}]" , 15,WHITE, 580, 415)
            draw_text(screen, "hitrate:"+f"[{poketmon0.get_skill_data(i,4)}]" , 15,WHITE, 580, 445)
        pygame.display.update()
        clock.tick(60)
    if poketmon0.get_skill_data(i,0) == None:
        text = [("You can't use this skill any more."),("")]
        Log(text,"None")
        myTurn = True
        return
    if poketmon0.get_skill_data(i,3) <= 0:
        text = [("You can't use this skill any more."),("")]
        Log(text,"None")
        myTurn = True
        return
    if i == 1:
        poketmon0.skill_data[poketmon0.sk1]["pp"] -= 1
    if i == 2:
        poketmon0.skill_data[poketmon0.sk2]["pp"] -= 1
    if i == 3:
        poketmon0.skill_data[poketmon0.sk3]["pp"] -= 1
    if i == 4:
        poketmon0.skill_data[poketmon0.sk4]["pp"] -= 1
    enemyTurn(i)
    
def Damage(attacker,defender,power,category,type,hitrate):
    if category == "Status":
        print("상태변화기술")
        return
    crirate = (attacker.speed / 512) * 100
    cri = 1
    ran = random.randint(0,101)
    text = []
    if crirate > ran:
        cri = 2
        text.append("critical!")
    ran = int((random.randint(217,255) * 100) / 255)
    typevalue1, typevalue2 = TypeValue(type, defender.type1, defender.type2)
    typevalue0 = 1
    if typevalue1 != 1 or typevalue2 != 1:
        text.append("effect was good!")
    if attacker.type1 == type:
        typevalue0 = 1.5
    elif attacker.type2 == type:
        typevalue0 = 1.5
    if category == "Special":
        damage = int((power * attacker.getspecialattack() * (attacker.level *cri* 2 / 5  + 2) / defender.getspecialdefence() / 50 + 2) * typevalue0 * typevalue1 * typevalue2 * (ran/255))
    elif category == "Physical":
        damage = int((power * attacker.getattack() * (attacker.level *cri* 2 / 5 + 2) / defender.getdefense() / 50 + 2) * typevalue0 * typevalue1 * typevalue2 * (ran / 255))
    defender.hp -= damage
    text.append(f"{attacker.name} gave "f"{defender.name} "f"{damage}damage!")
    text.append("")
    screen.fill(WHITE)
    BattleUI()
    Log(text,"None")
        
def TypeValue(attacker_type, defender_type1, defender_type2="-"):
    value1 = type_effectiveness[attacker_type].get(defender_type1, 1)
    value2 = type_effectiveness[attacker_type].get(defender_type2, 1) if defender_type2 != "-" else 1
    return value1, value2

type_effectiveness = {
    "Normal": {"Normal": 1, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 1, "Flying": 1, "Bug": 1, "Ghost": 0, "Poison": 1, "Fighting": 2, "Dark": 1, "Steel": 1, "Dragon": 1, "Fairy": 1},
    "Fire": {"Normal": 1, "Fire": 0.5, "Water": 0.5, "Grass": 2, "Electric": 1, "Flying": 1, "Bug": 2, "Ghost": 1, "Poison": 1, "Fighting": 1, "Dark": 1, "Steel": 2, "Dragon": 1, "Fairy": 1},
    "Water": {"Normal": 1, "Fire": 2, "Water": 0.5, "Grass": 0.5, "Electric": 1, "Flying": 1, "Bug": 1, "Ghost": 1, "Poison": 1, "Fighting": 1, "Dark": 1, "Steel": 1, "Dragon": 1, "Fairy": 1},
    "Grass": {"Normal": 1, "Fire": 0.5, "Water": 2, "Grass": 0.5, "Electric": 1, "Flying": 0.5, "Bug": 0.5, "Ghost": 1, "Poison": 0.5, "Fighting": 1, "Dark": 1, "Steel": 1, "Dragon": 1, "Fairy": 1},
    "Electric": {"Normal": 1, "Fire": 1, "Water": 2, "Grass": 1, "Electric": 0.5, "Flying": 2, "Bug": 1, "Ghost": 1, "Poison": 1, "Fighting": 1, "Dark": 1, "Steel": 1, "Dragon": 0.5, "Fairy": 1},
    "Flying": {"Normal": 1, "Fire": 1, "Water": 1, "Grass": 2, "Electric": 0.5, "Flying": 1, "Bug": 2, "Ghost": 1, "Poison": 1, "Fighting": 2, "Dark": 1, "Steel": 1, "Dragon": 1, "Fairy": 1},
    "Bug": {"Normal": 1, "Fire": 0.5, "Water": 1, "Grass": 2, "Electric": 1, "Flying": 0.5, "Bug": 1, "Ghost": 1, "Poison": 1, "Fighting": 1, "Dark": 2, "Steel": 0.5, "Dragon": 1, "Fairy": 0.5},
    "Ghost": {"Normal": 0, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 1, "Flying": 1, "Bug": 1, "Ghost": 2, "Poison": 1, "Fighting": 2, "Dark": 1, "Steel": 1, "Dragon": 1, "Fairy": 1},
    "Poison": {"Normal": 1, "Fire": 1, "Water": 1, "Grass": 2, "Electric": 1, "Flying": 1, "Bug": 1, "Ghost": 1, "Poison": 0.5, "Fighting": 1, "Dark": 1, "Steel": 0, "Dragon": 1, "Fairy": 2},
    "Fighting": {"Normal": 2, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 1, "Flying": 1, "Bug": 1, "Ghost": 0, "Poison": 1, "Fighting": 1, "Dark": 2, "Steel": 2, "Dragon": 1, "Fairy": 0.5},
    "Dark": {"Normal": 1, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 1, "Flying": 1, "Bug": 1, "Ghost": 2, "Poison": 1, "Fighting": 2, "Dark": 1, "Steel": 1, "Dragon": 1, "Fairy": 0.5},
    "Steel": {"Normal": 1, "Fire": 0.5, "Water": 0.5, "Grass": 1, "Electric": 1, "Flying": 1, "Bug": 2, "Ghost": 1, "Poison": 1, "Fighting": 2, "Dark": 1, "Steel": 1, "Dragon": 2, "Fairy": 2},
    "Dragon": {"Normal": 1, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 1, "Flying": 1, "Bug": 1, "Ghost": 1, "Poison": 1, "Fighting": 1, "Dark": 1, "Steel": 1, "Dragon": 2, "Fairy": 0},
    "Fairy": {"Normal": 1, "Fire": 1, "Water": 1, "Grass": 1, "Electric": 1, "Flying": 1, "Bug": 1, "Ghost": 1, "Poison": 1, "Fighting": 2, "Dark": 2, "Steel": 0.5, "Dragon": 2, "Fairy": 1}
}

def BattleUI():
    global No,poketmon0,poketmon7
    Animation(poketmon7.number,0)
    Animation(poketmon0.number,1)
    pygame.draw.rect(screen, RED, (115, 85, 150, 10))
    if poketmon7.hp > 0:
        fill_width = int(150 * (poketmon7.hp / poketmon7.getmaxhp()))
        pygame.draw.rect(screen, GREEN, (115, 85, fill_width, 10))
    pygame.draw.rect(screen, BLACK, (115, 85, 150, 10), 2)
    draw_text(screen, "Hp:", 20,BLACK, 80, 75)
    draw_text(screen, str(int(poketmon7.hp)) + "/" + str(int(poketmon7.getmaxhp())), 20,BLACK, 120, 100)
    draw_text(screen, poketmon7.name+":Lv"+str(poketmon7.level) ,20,BLACK, 80, 45)
    pygame.draw.rect(screen, RED, (560, 260, 150, 10))
    if poketmon0.hp > 0:
        fill_width = int(150 * (poketmon0.hp / poketmon0.getmaxhp()))
        pygame.draw.rect(screen, GREEN, (560, 260, fill_width, 10))
    pygame.draw.rect(screen, BLACK, (560, 260, 150, 10), 2)
    draw_text(screen, "Hp:", 20,BLACK, 520, 250)
    draw_text(screen, str(int(poketmon0.hp) ) + "/" + str(int(poketmon0.getmaxhp()) ), 20,BLACK, 570, 270)
    draw_text(screen, poketmon0.name+":Lv"+str(poketmon0.level) ,20,BLACK, 520, 220)
    pygame.display.flip()

def enemySpawn():
    global poketmon7,mapname
    ran = random.randint(1,100)
    if mapname == "관동1번도로":
        if ran <= 55:
            poketmon7 = load_pokemon_from_file(0,"관동1번도로enemy.txt")
        elif ran > 55:
            poketmon7 = load_pokemon_from_file(1,"관동1번도로enemy.txt")
    poketmon7.setvalue()
    poketmon7.Listup(1)
    print(poketmon7)

def Animation(number,flip):
    battle_UI = pygame.image.load("화살표.png").convert_alpha()
    if number == 0:
        poketmon_image = pygame.image.load("poketball.png").convert_alpha()
    elif number == 1 :
        poketmon_image = pygame.image.load("1.png").convert_alpha()
    elif number == 4:
        poketmon_image = pygame.image.load("4.png").convert_alpha()
    elif number == 7:
        poketmon_image = pygame.image.load("7.png").convert_alpha()
    elif number == 16:
        poketmon_image = pygame.image.load("16.png").convert_alpha()
    elif number == 19:
        poketmon_image = pygame.image.load("19.png").convert_alpha()
    battle_UI = pygame.transform.scale(battle_UI, (350, 150))
    if(flip == 1):
        poketmon_image = pygame.transform.scale(poketmon_image, (200, 200))
        poketmon_image = pygame.transform.flip(poketmon_image, True, False)
        screen.blit(battle_UI, (50,5))
        screen.blit(poketmon_image, (100,150))
    elif(flip == 0):
        poketmon_image = pygame.transform.scale(poketmon_image, (125, 125))
        battle_UI = pygame.transform.flip(battle_UI, True, False)
        screen.blit(battle_UI, (400,175))
        screen.blit(poketmon_image, (550,15))
    elif(flip == 2):
        poketmon_image = pygame.transform.scale(poketmon_image, (200, 200))
        battle_UI = pygame.transform.flip(battle_UI, True, False)
        screen.blit(battle_UI, (400,175))
        screen.blit(poketmon_image, (500,15))
    
def fade_transition(screen, duration=1000, color=(0, 0, 0)):
    width, height = screen.get_size()
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill(color)

    clock = pygame.time.Clock()
    fade_steps = 255 
    fade_speed = fade_steps / (duration / 2 / 1000 * 60)

    alpha = 0
    while alpha < 255:
        fade_surface.set_alpha(int(alpha))
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        alpha += fade_speed
        clock.tick(60)


    alpha = 255
    while alpha > 0:
        fade_surface.set_alpha(int(alpha))
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        alpha -= fade_speed
        clock.tick(60)

def is_battled(x, y,filename):
    try:
        with open(filename, 'r') as file:
            for line in file:
                coords = list(map(int, line.strip().split(',')))
                if len(coords) == 4:
                    x1, y1, x2, y2 = coords
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        return True
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
    return False

def is_blocked(x, y, filename):
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()  
                if not line:  
                    continue
                try:
                    coords = list(map(int, line.split(',')))
                    if len(coords) == 4:
                        x1, y1, x2, y2 = coords
                        if x1 <= x <= x2 and y1 <= y <= y2:
                            return True
                except ValueError:
                    print(f"Invalid data in line: {line}")
    except FileNotFoundError:
        print(f"File not found: {filename}")
    return False


def Story(quest):
    global Quest
    running = True
    if (quest == 0):
        text = [("My name is Python"),("Although I currently live in a small rural town..."),("I will be the best trainer in the world!"),
                ("By the way, I think Dr. Oh called me today."),("Dr. Oh's house was the one on the bottom right, right? I should go there first"),("")]
        f = Log(text,"레드.png")
        Quest = 1
    if (quest == 1 ):
            text = [("Hello Python?"),("Would you like to choose your starting Pokémon?"),("Then I will give you 3 Poketballs and 3 Potion."),("Use this Poké Ball to catch a Pokemon and then go to the gym in Viridian City.")]
            f = Log(text,"오박사.png")
            n = answer(f,"오박사.png")
            if n == 430:
                Quest = 2
                StartPoketMon()
                inventory.add_item("Poketball", 3)
                inventory.add_item("Potion", 3)
            elif n == 460:
                text = [("Really? Then go look around a bit more."),("")]
                Log(text,"오박사.png")
    if (quest == 2):
            if (poketmon2.name != "-" or poketmon3.name != "-" or poketmon4.name != "-" or poketmon5.name != "-" or poketmon6.name != "-" ):
                text = [("Hello Python?"),("Oh you get another poketmon? Good job"),("Unfortunately, however, that's all it's been implemented"),("Good bye!"),("")]
                f = Log(text,"마박사.png")
                QuitGame()
            else:
                text = [("Hello Python?"),("You haven't caught Pokémon yet, have you?"),("I'll give you 5 hyperballs here and heal your poketmon. Go back and catch any Pokemon"),("")]
                f = Log(text,"마박사.png")
                inventory.add_item("Highperball", 5)
                poketmon0.hp = poketmon0.getmaxhp()
                return
def answer(text,image):
    running = True
    POS = 430
    draw_text(screen, "Yes", 18,WHITE, 20, 430)
    draw_text(screen, "No", 18,WHITE, 20, 460)
    draw_text(screen, ">", 18,WHITE, 10, POS)
    pygame.display.flip()
    while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        POS += 30
                    if event.key == pygame.K_a:
                        POS -= 30
                    if event.key == pygame.K_RETURN:
                        running = False
                        return POS
                    if POS > 460:
                        POS = 430
                    if POS < 430:
                        POS = 460
                    Log("",None)
                    if (image != "None"):
                        character_image = pygame.image.load(image).convert_alpha()
                        character_image = pygame.transform.scale(character_image, (300, 600))
                        screen.blit(character_image, (500,100))
                    draw_text(screen, text, 20,WHITE, 10, 360)
                    draw_text(screen, "Yes", 18,WHITE, 20, 430)
                    draw_text(screen, "No", 18,WHITE, 20, 460)
                    draw_text(screen, ">", 18,WHITE, 10, POS)
                    pygame.display.flip()
                    
def Log(text,image):
    Log_image = pygame.image.load("대화창.png").convert()
    screen.blit(Log_image, (0,350))
    for n in range(0,len(text)):
        running = True
        Log_image = pygame.image.load("대화창.png").convert()
        screen.blit(Log_image, (0,350))
        if (image != "None"):
            character_image = pygame.image.load(image).convert_alpha()
            character_image = pygame.transform.scale(character_image, (300, 600))
            screen.blit(character_image, (500,100))
        draw_text(screen, text[n], 20,WHITE, 10, 360)
        pygame.display.flip()
        if (n == len(text) - 1):
            running = False
            return text[n]
        while running:
            clock.tick(FPS)
            for event in pygame.event.get():
                 if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        running = False

def StartPoketMon():
    global poketmon1,No
    POS = 150
    running = True
    screen.fill(BLACK)
    text = [("No.1   Bulbasaur   Lv.5               [Type:Grass/Venom] ")]
    f = Log(text,"None")
    poketmon_image = pygame.image.load("1.png").convert_alpha()
    poketmon_image = pygame.transform.scale(poketmon_image, (150, 150))
    screen.blit(poketmon_image, (100,100))
    poketmon_image = pygame.image.load("4.png").convert_alpha()
    poketmon_image = pygame.transform.scale(poketmon_image, (150, 150))
    screen.blit(poketmon_image, (300,100))
    poketmon_image = pygame.image.load("7.png").convert_alpha()
    poketmon_image = pygame.transform.scale(poketmon_image, (150, 150))
    screen.blit(poketmon_image, (500,100))
    while running:
        draw_text(screen, "v", 20,WHITE, POS, 80)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    POS += 200
                if event.key == pygame.K_a:
                    POS -= 200
                if event.key == pygame.K_RETURN:
                    running = False
                if POS > 550:
                    POS = 150
                if POS <150:
                    POS = 550
                screen.fill(BLACK)
                if POS == 150:
                    text = [("No.1   Bulbasaur   Lv.5               [Type:Grass/Venom] ")]
                    f = Log(text,"None")
                elif POS == 350:
                    text = [("No.4   Charmander  Lv.5               [Type:Fire/-] ")]
                    f = Log(text,"None")
                elif POS == 550:
                    text = [("No.7   Squirtle    Lv.5            [Type:Water/-]    ")]
                    f = Log(text,"None")
                poketmon_image = pygame.image.load("C:/Users/bongm/OneDrive/바탕 화면/SW/1.png").convert_alpha()
                poketmon_image = pygame.transform.scale(poketmon_image, (150, 150))
                screen.blit(poketmon_image, (100,100))
                poketmon_image = pygame.image.load("C:/Users/bongm/OneDrive/바탕 화면/SW/4.png").convert_alpha()
                poketmon_image = pygame.transform.scale(poketmon_image, (150, 150))
                screen.blit(poketmon_image, (300,100))
                poketmon_image = pygame.image.load("C:/Users/bongm/OneDrive/바탕 화면/SW/7.png").convert_alpha()
                poketmon_image = pygame.transform.scale(poketmon_image, (150, 150))
                screen.blit(poketmon_image, (500,100))
        pygame.display.flip()
        clock.tick(FPS)
    if POS == 150:
        poketmon1 = load_pokemon_from_file(1,"poketmon_data.txt")
    elif POS == 350:
        poketmon1 = load_pokemon_from_file(2,"poketmon_data.txt")
    elif POS == 550:
        poketmon1 = load_pokemon_from_file(3,"poketmon_data.txt")
    poketmon1.setvalue()
    poketmon1.Listup(0)
    print(poketmon1)

def Interaction():
    global player_x,player_y,mapname,Quest,mapdata,a,mapbattle
    if mapname == "태초마을":
        if (Quest == 0):
            Story(0)
            return
        if  (574<= player_x <= 700) and 0 <= player_y <= 40:
            print(poketmon1.name)
            if poketmon1.name == "-":
                text = [("First you get starting PoketMon!"),("")]
                Log(text,"None")
                return
            mapname = "관동1번도로"
            mapdata = "관동1번도로.txt"
            mapbattle = "관동1번도로B.txt"
            player_x = 1150
            player_y = 4381
            print("맵 이동:"+ mapname)
            fade_transition(screen)
        elif (880<= player_x <= 920) and 770 <= player_y <= 795:
            print("스타트 퀘스트 작동")
            player_y = 800
            Story(Quest)
    elif mapname == "관동1번도로":
        if  (1020<= player_x <= 1285) and 4350 <= player_y <= 4380:
            mapname = "태초마을"
            mapdata = "태초마을.txt"
            mapbattle = "None"
            player_x = 640
            player_y = 41
            print("맵 이동:"+ mapname)
            fade_transition(screen)
        elif (811<= player_x <= 1024) and 436 <= player_y <= 509:
            mapname = "상록시티"
            mapdata = "상록시티.txt"
            mapbattle = "None"
            player_x = 1526
            player_y = 1376
            print("맵 이동:"+ mapname)
            fade_transition(screen)
    elif mapname == "상록시티":
        if  (1473<= player_x <= 1591) and 1440 <= player_y <= 1508:
            mapname = "관동1번도로"
            mapdata = "관동1번도로.txt"
            mapbattle = "관동1번도로B.txt"
            player_x = 920
            player_y = 510
            print("맵 이동:"+ mapname)
        elif (1364<= player_x <= 1422) and 1092 <= player_y <= 1118:
            print("엔드 퀘스트 작동")
            player_y = 1120
            Story(Quest)
    print(player_x,player_y)
def StartGame():
    POS = 0
    x = 360
    y = 350
    running = True
    draw_text(screen, "PokeMon", 50,RED, 300, 50)
    draw_text(screen, "Start", 20,WHITE, 375, 350)
    draw_text(screen, "Load", 20,WHITE, 375, 375)
    draw_text(screen, "Exit", 20,WHITE, 375, 400)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    POS += 1
                    y += 25
                if event.key == pygame.K_a:
                    POS -= 1
                    y -= 25
                if event.key == pygame.K_RETURN:
                    running = False
                screen.fill(BLACK)
                draw_text(screen, "PokeMon", 50,RED, 300, 50)
                draw_text(screen, "Start", 20,WHITE, 375, 350)
                draw_text(screen, "Load", 20,WHITE, 375, 375)
                draw_text(screen, "Exit", 20,WHITE, 375, 400)
        if POS > 2:
            POS = 0
            y=350
        if POS <0:
            POS = 2
            y=410
        draw_text(screen, ">        ", 20,WHITE, x, y)
        pygame.display.flip()
        clock.tick(FPS)
    if POS == 0:
        screen.fill(BLACK)
        pygame.display.flip()
        return
    if POS == 1:
        screen.fill(BLACK)
        pygame.display.flip()
        return
    if POS == 2:
        QuitGame()        

def draw_text(screen, text, font_size, color, x, y):
    font = pygame.font.Font("Pokemon Solid.ttf", font_size)
    words = text.split(' ') 
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if font.size(test_line)[0] <= 500:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:  
        lines.append(current_line)
    for line in lines:
        rendered_text = font.render(line, True, color)
        text_rect = rendered_text.get_rect()
        text_rect.topleft = (x, y)
        screen.blit(rendered_text, text_rect)
        y += font.size(line)[1] 

def QuitGame():
    pygame.quit()
    
main()
