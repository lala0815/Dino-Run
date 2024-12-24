import pygame
import random
import ctypes
import sys
import os

# 在 pygame.init() 之前添加以下代碼
if sys.platform.startswith('win'):
    try:
        import win32api
        import win32con
        # 切換到英文輸入法
        win32api.LoadKeyboardLayout('00000409', win32con.KLF_ACTIVATE)
        print("已切換至英文輸入法")
    except ImportError:
        print("提示：請安裝 pywin32 以啟用自動切換輸入法功能")
        print("可使用指令：pip install pywin32")

# 設置默認中文字體
def get_font_path():
    if sys.platform.startswith('win'):
        # Windows 系統字體路徑
        font_paths = [
            "C:\\Windows\\Fonts\\msjh.ttc",  # 微軟正黑體
            "C:\\Windows\\Fonts\\mingliu.ttc",  # 細明體
            "C:\\Windows\\Fonts\\simsun.ttc",  # 新宋體
        ]
    else:
        # Linux/Mac 系統字體路徑
        font_paths = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/System/Library/Fonts/PingFang.ttc",
        ]
    
    # 尋找可用的字體
    for font_path in font_paths:
        if os.path.exists(font_path):
            return font_path
            
    return None  # 如果找不到合適的字體，返回 None

# 初始化 Pygame
pygame.init()
FONT_PATH = get_font_path()

# 設定視窗大小
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Dino Game")

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
SKY_BLUE = (135, 206, 235)
GROUND_COLOR = (83, 144, 83)

# 在遊戲開始前添加這些調試信息
print("Game Controls:")
print("- SPACE/UP/W: Jump")
print("- R: Restart when game over")
print("- H: Toggle AI auto-jump")
print("- ESC: Exit game")


# 在主遊戲循環之前添加開始畫面函數
def draw_start_screen(surface, font_size=36):
    # 繪製背景
    surface.fill(SKY_BLUE)
    
    # 繪製裝飾性雲朵
    clouds = [
        {'x': 100, 'y': 80, 'width': 60},
        {'x': WINDOW_WIDTH-200, 'y': 120, 'width': 70},
        {'x': WINDOW_WIDTH//2, 'y': 60, 'width': 50}
    ]
    for cloud in clouds:
        pygame.draw.ellipse(surface, WHITE, 
                          (cloud['x'], cloud['y'], 
                           cloud['width'], cloud['width']*0.6))
    
    # 繪製地面
    ground_y = WINDOW_HEIGHT - 50
    pygame.draw.rect(surface, GROUND_COLOR, 
                    (0, ground_y, WINDOW_WIDTH, WINDOW_HEIGHT - ground_y))
    
    # 使用較小的字體大小
    if FONT_PATH:
        font = pygame.font.Font(FONT_PATH, 24)        # 從 36 改為 24
        title_font = pygame.font.Font(FONT_PATH, 48)  # 從 72 改為 48
    else:
        font = pygame.font.Font(None, 24)
        title_font = pygame.font.Font(None, 48)
    
    # 顯示遊戲標題
    title = 'Dino Run'
    shadow_color = (100, 100, 100)
    title_shadow = title_font.render(title, True, shadow_color)
    title_text = title_font.render(title, True, BLACK)
    
    title_x = WINDOW_WIDTH//2 - title_text.get_width()//2
    title_y = WINDOW_HEIGHT//4
    
    # 繪製陰影和標題
    surface.blit(title_shadow, (title_x + 3, title_y + 3))  # 陰影偏移
    surface.blit(title_text, (title_x, title_y))
    
    # 繪製示例恐龍
    demo_dino = Dino()
    demo_dino.x = WINDOW_WIDTH//2 - 100
    demo_dino.y = WINDOW_HEIGHT//2
    demo_dino.draw(surface)
    
    # 顯示開始提示（閃爍效果）
    current_time = pygame.time.get_ticks()
    if (current_time // 500) % 2:  # 每500毫秒切換一次
        start_text = font.render('Press any key to start', True, BLACK)
        surface.blit(start_text, 
                    (WINDOW_WIDTH//2 - start_text.get_width()//2, 
                     WINDOW_HEIGHT*2//3))
    
    # 顯示控制說明（使用半透明背景）
    controls = [
        'SPACE/UP/W: Jump',
        'R: Restart when game over',
        'H: Toggle AI auto-jump',
        'ESC: Exit game'
    ]
    
    # 調整控制說明背景的大小
    control_surface = pygame.Surface((300, 80))  # 從 (400, 100) 改為 (300, 80)
    control_surface.fill(WHITE)
    control_surface.set_alpha(180)
    surface.blit(control_surface, 
                (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT*3//4 - 10))
    
    # 繪製控制說明文字，使用較小的行距
    for i, text in enumerate(controls):
        control_text = font.render(text, True, BLACK)
        surface.blit(control_text, 
                    (WINDOW_WIDTH//2 - control_text.get_width()//2, 
                     WINDOW_HEIGHT*3//4 + i*20))  # 行距從 30 改為 20

# 在主遊戲循環前添加開始畫面循環
def show_start_screen():
    waiting = True
    clock = pygame.time.Clock()
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                waiting = False
                return True
        
        draw_start_screen(window, 36)
        pygame.display.flip()
        clock.tick(60)

# 添加背景類
class Background:
    def __init__(self):
        self.ground_y = WINDOW_HEIGHT - 50
        self.cloud_list = []
        self.terrain_elements = []
        self.terrain_type = 'plains'  # 當前地形
        self.next_change = 100  # 下一次改變的距離
        
        # 地形顏色設定
        self.terrain_colors = {
            'plains': (83, 144, 83),     # 草原：淺綠
            'mountain': (139, 137, 137),  # 山地：灰色
            'forest': (34, 100, 34)       # 森林：深綠
        }
        
        # 生成初始背景
        self.generate_clouds()
        self.generate_terrain()
    
    def generate_terrain(self):
        self.terrain_elements = self.generate_terrain_elements(self.terrain_type)
    
    def change_terrain(self):
        # 直接切換到下一個地形
        terrains = ['plains', 'mountain', 'forest']
        current_index = terrains.index(self.terrain_type)
        next_index = (current_index + 1) % len(terrains)
        self.terrain_type = terrains[next_index]
        
        # 立即生成新地形
        self.generate_terrain()
        
        # 設置下次改變的距離
        self.next_change += 100
    
    def update(self, speed, current_distance):
        # 檢查是否需要改變地形
        if current_distance >= self.next_change:
            self.change_terrain()
        
        # 更新元素位置
        for element in self.terrain_elements[:]:
            if element['type'] == 'mountain':
                element['x'] -= speed * 0.2
            elif element['type'] == 'tree':
                element['x'] -= speed * 0.8
            else:  # grass
                element['x'] -= speed
            
            # 如果元素移出畫面，在右側重新生成
            if element['x'] + element['width'] < 0:
                element['x'] = WINDOW_WIDTH
                if element['type'] == 'mountain':
                    element['height'] = random.randint(100, 180)
                    element['width'] = random.randint(120, 200)
                elif element['type'] == 'tree':
                    element['height'] = random.randint(60, 100)
                    element['width'] = element['height'] // 2
                else:  # grass
                    element['height'] = random.randint(5, 15)
                    element['width'] = random.randint(20, 40)
        
        # 更新雲朵
        for cloud in self.cloud_list:
            cloud['x'] -= speed * 0.5
            if cloud['x'] + cloud['width'] < 0:
                cloud['x'] = WINDOW_WIDTH
                cloud['y'] = random.randint(50, 150)
                cloud['width'] = random.randint(40, 70)
    
    def draw(self, surface):
        # 繪製天空
        surface.fill(SKY_BLUE)
        
        # 繪製雲朵
        for cloud in self.cloud_list:
            pygame.draw.ellipse(surface, WHITE, 
                              (cloud['x'], cloud['y'], 
                               cloud['width'], cloud['width']*0.6))
        
        # 繪製地面
        pygame.draw.rect(surface, self.terrain_colors[self.terrain_type], 
                        (0, self.ground_y, WINDOW_WIDTH, WINDOW_HEIGHT - self.ground_y))
        
        # 繪製地形元素
        for element in self.terrain_elements:
            if element['type'] == 'mountain':
                color = (100, 100, 100)
                points = [
                    (element['x'], self.ground_y),
                    (element['x'] + element['width']//2, self.ground_y - element['height']),
                    (element['x'] + element['width'], self.ground_y)
                ]
                pygame.draw.polygon(surface, color, points)
            
            elif element['type'] == 'tree':
                # 樹幹
                trunk_color = (139, 69, 19)
                trunk_width = element['width'] // 3
                trunk_height = element['height'] // 2
                pygame.draw.rect(surface, trunk_color,
                               (element['x'] + element['width']//3,
                                self.ground_y - trunk_height,
                                trunk_width, trunk_height))
                
                # 樹冠
                crown_color = (34, 139, 34)
                points = [
                    (element['x'], self.ground_y - trunk_height),
                    (element['x'] + element['width']//2, self.ground_y - element['height']),
                    (element['x'] + element['width'], self.ground_y - trunk_height)
                ]
                pygame.draw.polygon(surface, crown_color, points)
            
            else:  # grass
                color = (50, 205, 50)
                points = [
                    (element['x'], self.ground_y),
                    (element['x'] + element['width']//2, self.ground_y - element['height']),
                    (element['x'] + element['width'], self.ground_y)
                ]
                pygame.draw.polygon(surface, color, points)
    
    def generate_terrain_elements(self, terrain_type):
        elements = []
        if terrain_type == 'mountain':
            for _ in range(random.randint(3, 5)):
                x = random.randint(0, WINDOW_WIDTH)
                height = random.randint(100, 180)
                width = random.randint(120, 200)
                elements.append({
                    'type': 'mountain',
                    'x': x,
                    'height': height,
                    'width': width
                })
        elif terrain_type == 'forest':
            for _ in range(random.randint(6, 10)):
                x = random.randint(0, WINDOW_WIDTH)
                height = random.randint(60, 100)
                elements.append({
                    'type': 'tree',
                    'x': x,
                    'height': height,
                    'width': height // 2
                })
        else:  # plains
            for _ in range(random.randint(15, 20)):
                x = random.randint(0, WINDOW_WIDTH)
                height = random.randint(5, 15)
                elements.append({
                    'type': 'grass',
                    'x': x,
                    'height': height,
                    'width': random.randint(20, 40)
                })
        return elements
    
    def generate_clouds(self):
        # 生成3-5朵雲
        for _ in range(random.randint(3, 5)):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(50, 150)
            width = random.randint(40, 70)
            self.cloud_list.append({
                'x': x,
                'y': y,
                'width': width
            })

# 在顏色定義後添加圖片載入相關代碼
def load_sprite_sheet(filename, cols, rows):
    # 載入完整的 sprite sheet
    full_image = pygame.image.load(filename)
    full_rect = full_image.get_rect()
    width = full_rect.width / cols
    height = full_rect.height / rows
    frames = []
    
    for row in range(rows):
        for col in range(cols):
            x = col * width
            y = row * height
            # 創一個新的 surface 來存放裁剪的圖片
            frame_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            frame_surface.blit(full_image, (0, 0), (x, y, width, height))
            frames.append(frame_surface)
    
    return frames

# 在文件開頭添加圖片路徑設置
GAME_ROOT = os.path.dirname(__file__)
IMAGE_ROOT = os.path.join(GAME_ROOT, 'images')

# 修改 Dino 類
class Dino:
    def __init__(self):
        self.x = 50
        self.y = WINDOW_HEIGHT - 100
        self.jump_speed = 0
        self.is_jumping = False
        
        # 置恐龍期望的小
        self.width = 40  # 縮小寬度
        self.height = 44  # 縮小高度
        
        try:
            # 載入並縮放圖片
            run_frames_original = [
                pygame.image.load(os.path.join(IMAGE_ROOT, 'dino_run.png')),
                pygame.image.load(os.path.join(IMAGE_ROOT, 'dino_run2.png'))
            ]
            jump_image_original = pygame.image.load(os.path.join(IMAGE_ROOT, 'dino_jump.png'))
            
            # 縮放所有圖片到指定大小
            self.run_frames = [
                pygame.transform.scale(img, (self.width, self.height))
                for img in run_frames_original
            ]
            self.jump_image = pygame.transform.scale(jump_image_original, (self.width, self.height))
            
        except pygame.error as e:
            print(f"Failed to load dinosaur image: {e}")
            # 使用臨時的紫色方塊作為替代
            self.run_frames = [pygame.Surface((self.width, self.height), pygame.SRCALPHA) for _ in range(2)]
            self.jump_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for img in self.run_frames + [self.jump_image]:
                img.fill((255, 0, 255))  # 紫色
        
        self.image = self.run_frames[0]  # 前
        self.distance = 0
        self.speed = 5
        self.max_speed = 12  # 設置最大速度為12
        self.distance_multiplier = 0.01
        # 動畫相關
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.acceleration = 0.2  # 每100米增加的速度

    def jump(self):
        if not self.is_jumping:
            print("Jump executed!")
            self.jump_speed = -15
            self.is_jumping = True
            self.image = self.jump_image  # 立即切換到跳躍圖片

    def update(self):
        if self.is_jumping:
            self.y += self.jump_speed
            self.jump_speed += 0.8
            self.image = self.jump_image  # 使用跳躍圖片

            if self.y >= WINDOW_HEIGHT - 100:
                self.y = WINDOW_HEIGHT - 100
                self.is_jumping = False
                self.jump_speed = 0
                self.image = self.run_frames[0]  # 落地時使用跑步圖片
        else:
            # 更新跑步動畫
            self.animation_frame = (self.animation_frame + self.animation_speed)
            if self.animation_frame >= len(self.run_frames):
                self.animation_frame = 0
            self.image = self.run_frames[int(self.animation_frame)]
        
        # 更新距離
        self.distance += self.speed * self.distance_multiplier
        
        # 更新速度，但限制最大值
        new_speed = 5 + (self.distance // 100) * self.acceleration
        self.speed = min(new_speed, self.max_speed)

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# 修改 Obstacle 類
class Obstacle:
    def __init__(self, terrain_type='plains'):
        self.terrain_type = terrain_type
        
        # 設置固定的尺寸和高度
        if terrain_type == 'plains':
            # 平地：岩石
            self.width = 40
            self.height = 40
            self.y = WINDOW_HEIGHT - 90  # 固定高度
            self.image = self.create_rock()
        elif terrain_type == 'mountain':
            # 山地：仙人掌
            self.width = 30
            self.height = 40  # 改為與岩石相同高度
            self.y = WINDOW_HEIGHT - 90  # 與岩石相同的位置
            try:
                self.image = pygame.image.load(os.path.join(IMAGE_ROOT, 'cactus.png'))
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Failed to load cactus image: {e}")
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                self.image.fill((34, 139, 34))  # 深綠色
        else:  # forest
            # 森林：鳥
            self.width = 40
            self.height = 40  # 改為與其他障礙物相同高度
            self.y = WINDOW_HEIGHT - 90  # 與其他障礙物相同的位置
            try:
                self.image = pygame.image.load(os.path.join(IMAGE_ROOT, 'bird.png'))
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except pygame.error as e:
                print(f"Failed to load bird image: {e}")
                self.image = self.create_bird()
            
        self.x = WINDOW_WIDTH
        
    def create_rock(self):
        # 創建岩石圖形
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 主體（深灰色）
        rock_color = (90, 90, 90)  # 更深的灰色
        
        # 更自然的岩石形狀
        points = [
            (self.width * 0.1, self.height),          # 左下
            (0, self.height * 0.7),                   # 左凹點
            (self.width * 0.2, self.height * 0.5),    # 左中突起
            (self.width * 0.3, self.height * 0.2),    # 左上突起
            (self.width * 0.5, 0),                    # 頂點
            (self.width * 0.7, self.height * 0.3),    # 右上突起
            (self.width * 0.9, self.height * 0.6),    # 右中突起
            (self.width, self.height * 0.8),          # 右凹點
            (self.width * 0.9, self.height)           # 右下
        ]
        pygame.draw.polygon(surface, rock_color, points)
        
        # 添加明暗面和紋理
        highlight_color = (130, 130, 130)  # 淺灰色
        shadow_color = (60, 60, 60)        # 暗灰色
        
        # 明面（左上到右下的斜線）
        for i in range(3):
            start_x = self.width * 0.2 + i * 5
            start_y = self.height * 0.3 + i * 5
            end_x = start_x + self.width * 0.3
            end_y = start_y + self.height * 0.3
            pygame.draw.line(surface, highlight_color, 
                           (start_x, start_y), 
                           (end_x, end_y), 2)
        
        # 暗面（右上到左下的斜線）
        for i in range(2):
            start_x = self.width * 0.6 + i * 5
            start_y = self.height * 0.4 + i * 5
            end_x = start_x - self.width * 0.2
            end_y = start_y + self.height * 0.3
            pygame.draw.line(surface, shadow_color, 
                           (start_x, start_y), 
                           (end_x, end_y), 2)
        
        return surface
        
    def create_bird(self):
        # 創建鳥的圖形
        surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 身體（深藍色）
        body_color = (70, 130, 180)
        body_points = [
            (self.width * 0.3, self.height * 0.5),  # 頭部
            (self.width * 0.7, self.height * 0.3),  # 上翼
            (self.width * 0.9, self.height * 0.5),  # 尾部
            (self.width * 0.7, self.height * 0.7),  # 下翼
        ]
        pygame.draw.polygon(surface, body_color, body_points)
        
        # 頭部（圓形）
        head_pos = (int(self.width * 0.25), int(self.height * 0.5))
        pygame.draw.circle(surface, body_color, head_pos, int(self.height * 0.2))
        
        # 眼睛（白色）
        eye_pos = (int(self.width * 0.2), int(self.height * 0.45))
        pygame.draw.circle(surface, WHITE, eye_pos, 2)
        
        # 喙（黃色）
        beak_color = (255, 215, 0)
        beak_points = [
            (self.width * 0.1, self.height * 0.5),
            (self.width * 0.25, self.height * 0.45),
            (self.width * 0.25, self.height * 0.55)
        ]
        pygame.draw.polygon(surface, beak_color, beak_points)
        
        return surface
    
    def update(self, speed):
        self.x -= speed

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

# 將函數定義移到遊戲主循環外面
def draw_language_reminder(surface, font_size=36):
    if FONT_PATH:
        font = pygame.font.Font(FONT_PATH, font_size)
    else:
        font = pygame.font.Font(None, font_size)
        
# 在 DinoAI 類中添加繪製狀態的方法
class DinoAI:
    def __init__(self, dino):
        self.dino = dino
        self.base_distance = 90  # 減小基礎跳躍距離
        self.jump_cooldown = 0
        self.enabled = False
        self.last_jump_gap = 0   # 記錄上次跳躍時的間距
        
    def should_jump(self, obstacles):
        if not obstacles or self.dino.is_jumping:
            return False
            
        nearest_obstacle = obstacles[0]
        distance = nearest_obstacle.x - (self.dino.x + self.dino.width)
        
        # 計算當前速度下的全跳躍距離
        speed_factor = (self.dino.speed - 5) / 5  # 計算速度加的比例
        jump_distance = self.base_distance + (self.dino.speed - 5) * 6  # 減小速度補償
        
        # 檢查連續障礙物
        if len(obstacles) > 1:
            next_obstacle = obstacles[1]
            gap = next_obstacle.x - nearest_obstacle.x
            self.last_jump_gap = gap  # 記錄當前間距
            
            # 根據度和間距動態調整跳躍時機
            if gap < 180:  # 非常近的障礙物
                jump_distance = min(distance + 30, jump_distance)  # 確保不會跳太早
            elif gap < 250:  # 較近的障礙物
                jump_distance *= 0.9  # 稍微延後跳躍
            
            # 高速時的特殊處理
            if speed_factor > 0.6:  # 速度超過 8
                if gap < 200:
                    jump_distance *= 0.85  # 高速時更晚跳
                elif gap < 300:
                    jump_distance *= 0.95
        
        # 根據當前速度調整冷卻時間
        if 0 < distance < jump_distance and self.jump_cooldown <= 0:
            # 根據間距調整冷卻時間
            if self.last_jump_gap < 200:
                self.jump_cooldown = 3  # 連續障礙物時縮短冷卻
            else:
                self.jump_cooldown = 4
            return True
            
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
            
        return False
    
    def toggle(self):
        self.enabled = not self.enabled
        print(f"AI auto-jump {'enabled' if self.enabled else 'disabled'}")
    
    def update(self, obstacles):
        if self.enabled and self.should_jump(obstacles):  # 只在啟用時執行
            self.dino.jump()
    
    def draw_status(self, surface, font):
        # 創建半透明背景
        status_surface = pygame.Surface((150, 40))
        status_surface.fill(WHITE)
        status_surface.set_alpha(180)
        
        # 設置位置（右上角）
        x = WINDOW_WIDTH - 160
        y = 10
        
        # 繪製背景
        surface.blit(status_surface, (x, y))
        
        # 繪製文字
        status_text = font.render(f"AI: {'ON' if self.enabled else 'OFF'}", True, 
                                (34, 139, 34) if self.enabled else (139, 34, 34))
        surface.blit(status_text, (x + 10, y + 5))

# 在主遊戲循環外添加變量來追踪連續障礙物
class ObstacleManager:
    def __init__(self):
        self.consecutive_count = 0  # 追踪連續障礙物數量
        self.last_obstacle_x = 0    # 記錄上一個障礙物的位置
        self.base_gap = 400         # 基礎間距從300增加到400
    
    def should_spawn(self, obstacles, window_width, speed):
        # 根據速度調整最小間距（每增加1速度，增加15間距）
        min_gap = self.base_gap + (speed - 5) * 15  # 速度補償係數從10增加到15
        
        # 如果沒有障礙物，可以生成
        if not obstacles:
            self.consecutive_count = 0
            return True
        
        # 檢查是否有足夠空間生成新障礙物
        last_obstacle = obstacles[-1]
        if last_obstacle.x >= window_width - min_gap:
            return False
            
        # 檢查與上一個障礙物的間距
        gap = last_obstacle.x - self.last_obstacle_x
        if gap < min_gap * 0.7:  # 連續障礙物判定閾值從0.67增加到0.7
            self.consecutive_count += 1
        else:
            self.consecutive_count = 0
            
        # 如果已經有2個連續障礙物，不再生成
        if self.consecutive_count >= 2:
            return False
            
        # 更新上一個障礙物的位置
        self.last_obstacle_x = last_obstacle.x
        return True
    
    def reset(self):
        self.consecutive_count = 0
        self.last_obstacle_x = 0

# 在主遊戲開始前初始化
obstacle_manager = ObstacleManager()

# 遊戲主要物件
dino = Dino()
dino_ai = DinoAI(dino)  # 創建 AI 控制器
obstacles = []
clock = pygame.time.Clock()
score = 0
game_over = False

# 在遊戲主循環中添加計時器來顯示示（前 5 秒
start_time = pygame.time.get_ticks()
REMINDER_DURATION = 5000  # 5秒

# 修改主遊戲循環的開始部分
if not show_start_screen():
    running = False
else:
    running = True
    # 重置開始時間（這樣輸入提示才會從遊戲實際開始時計時）
    start_time = pygame.time.get_ticks()

# 添加背景
background = Background()

# 遊戲主循環
while running:
    # 事件處理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            unicode_char = event.unicode.lower()
            print(f"Key pressed: {key_name}")
            print(f"Key code: {event.key}")
            print(f"Key unicode: {unicode_char}")
            print(f"Key modifiers: {pygame.key.get_mods()}")
            
            # 轉換按鍵名為小寫並���除空格，以理全形半形差異
            key_name = key_name.lower().strip()
            
            # 跳躍鍵檢測：支持多種輸入式
            jump_chars = {'w', 'ｗ','ㄊ','space'}  # 空格鍵用 ' ' 表示
            
            if event.key == pygame.K_ESCAPE or unicode_char == 'esc':
                running = False
            elif (event.key in [pygame.K_SPACE, pygame.K_UP, pygame.K_w] or 
                  unicode_char in jump_chars or 
                  key_name in ['space', 'up', 'w']):
                print("Jump detected!")
                dino.jump()
            elif ((event.key == pygame.K_r or 
                   unicode_char in {'r', 'ｒ'}) and 
                  game_over):
                dino = Dino()
                dino_ai = DinoAI(dino)  # 重新創建 AI
                dino_ai.enabled = True  # 如果之前開了 AI，保持開啟
                obstacles = []
                score = 0
                game_over = False
                
                # 重置背景和地形
                background = Background()  # 創建新的背景實例
                background.terrain_type = 'plains'  # 重置為初始地形
                background.next_change = 100  # 重置下一次改變的距離
                background.generate_terrain()  # 重新生成地形元素
                obstacle_manager.reset()
            elif event.key == pygame.K_h:  # 用 H 鍵切換 AI
                dino_ai.toggle()
    

    if not game_over:
        # 更新遊戲狀態
        dino.update()
        dino_ai.update(obstacles)
        
        # 生成障礙物，傳入當前速度
        if obstacle_manager.should_spawn(obstacles, WINDOW_WIDTH, dino.speed):
            if random.random() < 0.02:
                obstacles.append(Obstacle(background.terrain_type))

        # 更新障礙物
        for obstacle in obstacles[:]:
            obstacle.update(dino.speed)  # 使用恐龍的速度
            # 碰撞檢測
            if (dino.x < obstacle.x + obstacle.width and
                dino.x + dino.width > obstacle.x and
                dino.y < obstacle.y + obstacle.height and
                dino.y + dino.height > obstacle.y):
                game_over = True

            # 移除超出畫面的障礙物
            if obstacle.x < -obstacle.width:
                obstacles.remove(obstacle)

        # 更新背景
        background.update(dino.speed, dino.distance)  # 添加 dino.distance 參數

    # 繪製畫面
    window.fill(WHITE)
    background.draw(window)
    dino.draw(window)
    for obstacle in obstacles:
        obstacle.draw(window)

    # 顯示分數（使用距離）
    if FONT_PATH:
        font = pygame.font.Font(FONT_PATH, 36)
    else:
        font = pygame.font.Font(None, 36)
    score_text = font.render(f'Distance: {int(dino.distance)}m', True, BLACK)
    window.blit(score_text, (10, 10))

    # 顯示 AI 狀態
    dino_ai.draw_status(window, font)

    if game_over:
        game_over_text = font.render('Game Stop! Press R to restart', True, BLACK)
        window.blit(game_over_text, (WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2))

    # 顯示輸入法提示（僅在開始的5秒內）
    if pygame.time.get_ticks() - start_time < REMINDER_DURATION:
        draw_language_reminder(window, 36)

    pygame.display.flip()
    clock.tick(60)

pygame.quit() 