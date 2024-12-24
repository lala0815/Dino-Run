import pygame
import math

class DinoAI:
    def __init__(self, dino):
        self.dino = dino
        self.safe_distance = 120  # 安全距離，當障礙物進入這個範圍就跳躍
        self.jump_cooldown = 0    # 跳躍冷卻時間
        
    def should_jump(self, obstacles):
        if not obstacles or self.dino.is_jumping:
            return False
            
        # 獲取最近的障礙物
        nearest_obstacle = obstacles[0]
        
        # 計算與最近障礙物的距離
        distance = nearest_obstacle.x - (self.dino.x + self.dino.width)
        
        # 如果障礙物進入安全距離範圍，且恐龍不在跳躍狀態，則跳躍
        if 0 < distance < self.safe_distance and self.jump_cooldown <= 0:
            self.jump_cooldown = 10  # 設置跳躍冷卻時間
            return True
            
        # 更新跳躍冷卻時間
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
            
        return False

    def update(self, obstacles):
        if self.should_jump(obstacles):
            self.dino.jump() 