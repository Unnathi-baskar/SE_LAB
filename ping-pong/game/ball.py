import pygame
import random

class Ball:
    def __init__(self, x, y, width, height, screen_width, screen_height):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        # track previous position to build a swept rect for collision
        self.prev_x = x
        self.prev_y = y
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.velocity_x = random.choice([-5, 5])
        self.velocity_y = random.choice([-3, 3])
        # clamp max speed to reduce tunneling
        self.max_speed = 12

        # sound attributes (assigned by GameEngine)
        self.sound_paddle = None
        self.sound_wall = None
        self.sound_score = None

    def move(self):
        # store previous position for swept collision checks
        self.prev_x = self.x
        self.prev_y = self.y

        # clamp velocities to avoid excessive tunneling
        if abs(self.velocity_x) > self.max_speed:
            self.velocity_x = self.max_speed if self.velocity_x > 0 else -self.max_speed
        if abs(self.velocity_y) > self.max_speed:
            self.velocity_y = self.max_speed if self.velocity_y > 0 else -self.max_speed

        self.x += self.velocity_x
        self.y += self.velocity_y

        # Bounce off top/bottom walls
        if self.y <= 0 or self.y + self.height >= self.screen_height:
            self.velocity_y *= -1
            if self.sound_wall:
                self.sound_wall.play()

    def check_collision(self, player, ai):
        ball_rect = self.rect()

        # Build a swept rect that covers the path from previous position to current.
        swept_x = min(self.prev_x, self.x)
        swept_y = min(self.prev_y, self.y)
        swept_w = self.width + abs(self.x - self.prev_x)
        swept_h = self.height + abs(self.y - self.prev_y)
        swept_rect = pygame.Rect(swept_x, swept_y, swept_w, swept_h)

        if swept_rect.colliderect(player.rect()):
            # place ball next to the player's paddle and reflect
            self.x = player.rect().right
            self.velocity_x = abs(self.velocity_x)
            if self.sound_paddle:
                try:
                    self.sound_paddle.play()
                except Exception:
                    pass

        elif swept_rect.colliderect(ai.rect()):
            # place ball next to the AI paddle and reflect
            self.x = ai.rect().left - self.width
            self.velocity_x = -abs(self.velocity_x)
            if self.sound_paddle:
                try:
                    self.sound_paddle.play()
                except Exception:
                    pass

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.prev_x = self.x
        self.prev_y = self.y
        self.velocity_x *= -1
        self.velocity_y = random.choice([-3, 3])

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
