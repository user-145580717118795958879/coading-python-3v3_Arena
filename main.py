import pygame
import random
import time

# 初始化Pygame
pygame.init()
pygame.mixer.init()  # 初始化混音器

# 屏幕设置
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Turn-Based Battle Game")

# 加载图片并调整大小
background_img = pygame.image.load('images/background.png')
background_img = pygame.transform.scale(background_img, (screen_width, screen_height))

warrior_img = pygame.image.load('images/warrior.png')
warrior_img = pygame.transform.scale(warrior_img, (125, 125))  # 调整比例后的大小

tanker_img = pygame.image.load('images/tanker.png')
tanker_img = pygame.transform.scale(tanker_img, (125, 125))  # 调整比例后的大小

# 设置字体
font = pygame.font.Font(None, 24)  # 调整字体大小

# 加载背景音乐
pygame.mixer.music.load('music/background.wav')  # 替换为你的音乐文件路径
pygame.mixer.music.play(-1)  # 无限循环播放音乐

class Unit:
    def __init__(self, name, unit_type, img, x, y):
        self.name = name
        self.unit_type = unit_type
        self.img = img
        self.x = x
        self.y = y
        self.hp = 100
        self.exp = 0
        self.rank = 1
        if unit_type == 'Warrior':
            self.atk = random.randint(5, 20)
            self.defense = random.randint(1, 10)
        elif unit_type == 'Tanker':
            self.atk = random.randint(1, 10)
            self.defense = random.randint(5, 15)

    def attack(self, target):
        damage = self.atk - target.defense + random.randint(-5, 10)
        damage = max(damage, 0)
        target.hp -= damage
        self.exp += damage
        target.exp += target.defense
        if damage > 10:
            target.exp += int(0.2 * target.exp)
        elif damage <= 0:
            target.exp += int(0.5 * target.exp)
        if self.exp >= 100:
            self.rank_up()
        if target.exp >= 100:
            target.rank_up()
        return damage

    def rank_up(self):
        self.rank += 1
        self.exp -= 100

    def is_defeated(self):
        return self.hp <= 0

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        hp_text = font.render(f"HP: {self.hp}", True, (255, 0, 0))  # 红色字体显示血量
        screen.blit(hp_text, (self.x + self.img.get_width() - hp_text.get_width(), self.y + self.img.get_height() - hp_text.get_height()))

class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = (0, 128, 0)
        self.text_surf = font.render(text, True, (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()

class Game:
    def __init__(self):
        self.player_team = []
        self.ai_team = []
        self.event_log = []
        self.buttons = []
        self.selected_attacker = None

    def setup_teams(self):
        for i in range(3):
            name = f"Player{i+1}"
            unit_type = random.choice(['Warrior', 'Tanker'])
            img = warrior_img if unit_type == 'Warrior' else tanker_img
            self.player_team.append(Unit(name, unit_type, img, 50, 50 + i * 175))
        for i in range(3):
            name = f"AI{i+1}"
            unit_type = random.choice(['Warrior', 'Tanker'])
            img = warrior_img if unit_type == 'Warrior' else tanker_img
            img = pygame.transform.flip(img, True, False)  # 镜像敌方图片
            self.ai_team.append(Unit(name, unit_type, img, 400, 50 + i * 175))

        for i in range(len(self.player_team)):
            self.buttons.append(Button(50, 50 + i * 175, 100, 30, f"Attack {i}", lambda i=i: self.select_attacker(i)))

    def select_attacker(self, index):
        self.selected_attacker = index
        print(f"Selected attacker: {self.player_team[index].name}")
        self.buttons = []
        for i in range(len(self.ai_team)):
            self.buttons.append(Button(400, 50 + i * 175, 100, 30, f"Target {i}", lambda i=i: self.player_attack(i)))

    def player_attack(self, target_index):
        attacker = self.player_team[self.selected_attacker]
        target = self.ai_team[target_index]
        damage = attacker.attack(target)
        print(f"{attacker.name} attacked {target.name} for {damage} damage.")
        self.event_log.append(f"{time.ctime()}: {attacker.name} attacked {target.name} for {damage} damage.")
        if target.is_defeated():
            print(f"{target.name} has been defeated!")
            self.ai_team.pop(target_index)
            self.event_log.append(f"{time.ctime()}: {target.name} has been defeated!")
        self.selected_attacker = None
        self.buttons = []
        self.ai_turn()

    def ai_turn(self):
        print("AI's turn:")
        attacker = random.choice(self.ai_team)
        target = random.choice(self.player_team)
        damage = attacker.attack(target)
        print(f"{attacker.name} attacked {target.name} for {damage} damage.")
        self.event_log.append(f"{time.ctime()}: {attacker.name} attacked {target.name} for {damage} damage.")
        if target.is_defeated():
            print(f"{target.name} has been defeated!")
            self.player_team.remove(target)
            self.event_log.append(f"{time.ctime()}: {target.name} has been defeated!")
        self.buttons = []
        for i in range(len(self.player_team)):
            self.buttons.append(Button(50, 50 + i * 175, 100, 30, f"Attack {i}", lambda i=i: self.select_attacker(i)))

    def draw_units(self):
        for unit in self.player_team:
            unit.draw(screen)
        for unit in self.ai_team:
            unit.draw(screen)
        
        # Draw HP values in the bottom right corner
        y_offset = screen_height - 40
        for i, unit in enumerate(self.player_team + self.ai_team):
            hp_text = font.render(f"{unit.name} HP: {unit.hp}", True, (255, 255, 255))
            screen.blit(hp_text, (screen_width - 200, y_offset - i * 20))

    def draw_buttons(self):
        for button in self.buttons:
            button.draw(screen)

    def play_game(self):
        self.setup_teams()
        running = True

        while running:
            screen.blit(background_img, (0, 0))
            self.draw_units()
            self.draw_buttons()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        button.check_click(event.pos)

            if not self.player_team:
                print("AI wins!")
                self.event_log.append(f"{time.ctime()}: AI wins!")
                running = False
            elif not self.ai_team:
                print("Player wins!")
                self.event_log.append(f"{time.ctime()}: Player wins!")
                running = False

            pygame.display.flip()
            pygame.time.wait(100)

        with open('game_log.txt', 'w') as f:
            for event in self.event_log:
                f.write(event + '\n')

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.play_game()
