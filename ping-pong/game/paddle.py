import pygame
import random
import time


class Paddle:
    def __init__(self, x, y, width, height, is_ai=False, reaction_time=0.1, error_margin=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = 7

        # AI specific parameters
        self.is_ai = is_ai
        # reaction_time in seconds (float) - how often AI updates its target (simulates reaction delay)
        # We will use a small random jitter around this to avoid perfect timing.
        self.reaction_time = reaction_time
        # error_margin in pixels - how far off the AI aims from the exact ball center (simulates inaccuracy)
        self.error_margin = error_margin
        self._next_reaction = time.time()
        self._target_y = None

    def move(self, dy, screen_height):
        self.y += dy
        self.y = max(0, min(self.y, screen_height - self.height))

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def auto_track(self, ball, screen_height):
        # If not AI-controlled, do nothing
        if not self.is_ai:
            return

        now = time.time()
        if now >= self._next_reaction or self._target_y is None:
            # Decide on a new target (ball center plus some error)
            ball_center_y = ball.y + ball.height / 2
            # add a random offset within [-error_margin, error_margin]
            offset = random.uniform(-self.error_margin, self.error_margin)
            self._target_y = ball_center_y + offset - self.height / 2
            # schedule next reaction with a small jitter
            jitter = random.uniform(-0.02, 0.02)
            self._next_reaction = now + max(0.0, self.reaction_time + jitter)

        # Move toward target smoothly
        if self._target_y is None:
            return

        if self.y + self.height / 2 < self._target_y + 1:
            self.move(self.speed, screen_height)
        elif self.y + self.height / 2 > self._target_y - 1:
            self.move(-self.speed, screen_height)
