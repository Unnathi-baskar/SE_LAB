import pygame
from .paddle import Paddle
from .ball import Ball

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Default settings
DEFAULT_WINNING_SCORE = 5


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        # Create AI paddle with a small reaction delay and some inaccuracy so it's beatable
        # reaction_time (seconds) and error_margin (pixels) can be tuned
        ai_reaction = 0.18
        ai_error = 22
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height,
                         is_ai=True, reaction_time=ai_reaction, error_margin=ai_error)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 60)

        self.winning_score = DEFAULT_WINNING_SCORE
        self.game_over = False
        self.winner_text = ""
        self.screen = None

        # --- Load sounds ---
        # Attempt to load sounds; if anything fails, disable sounds gracefully.
        self.snd_paddle = None
        self.snd_wall = None
        self.snd_score = None
        try:
            if pygame.mixer.get_init() is None:
                # Try to initialize mixer; if it fails, we'll continue without sound
                try:
                    pygame.mixer.init()
                except Exception:
                    pass

            self.snd_paddle = pygame.mixer.Sound("sounds/paddle_hit.wav")
            self.snd_wall = pygame.mixer.Sound("sounds/wall_bounce.wav")
            self.snd_score = pygame.mixer.Sound("sounds/score.wav")
        except Exception:
            # If sound loading fails, set to None and continue
            self.snd_paddle = None
            self.snd_wall = None
            self.snd_score = None

        # Assign sounds to ball
        self.ball.sound_paddle = self.snd_paddle
        self.ball.sound_wall = self.snd_wall
        self.ball.sound_score = self.snd_score

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    def update(self):
        if self.game_over:
            return

        # Ball movement
        self.ball.move()
        self.ball.check_collision(self.player, self.ai)

        # Score check
        if self.ball.x <= 0:
            self.ai_score += 1
            self.ball.reset()
            if self.snd_score:
                try:
                    self.snd_score.play()
                except Exception:
                    pass
        elif self.ball.x >= self.width:
            self.player_score += 1
            self.ball.reset()
            if self.snd_score:
                try:
                    self.snd_score.play()
                except Exception:
                    pass

        # AI paddle
        self.ai.auto_track(self.ball, self.height)

        # Game over check
        if self.player_score >= self.winning_score:
            self._trigger_game_over("Player Wins!")
        elif self.ai_score >= self.winning_score:
            self._trigger_game_over("AI Wins!")

    def render(self, screen):
        self.screen = screen
        screen.fill(BLACK)

        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())
        pygame.draw.aaline(screen, WHITE, (self.width // 2, 0), (self.width // 2, self.height))

        # Draw scores
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width // 4, 20))
        screen.blit(ai_text, (self.width * 3 // 4, 20))

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            text = self.big_font.render(self.winner_text, True, WHITE)
            text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 50))
            screen.blit(text, text_rect)

            # Replay options
            menu_lines = [
                "Press 3 for Best of 3",
                "Press 5 for Best of 5",
                "Press 7 for Best of 7",
                "Press ESC to Exit"
            ]
            for i, line in enumerate(menu_lines):
                line_surf = self.font.render(line, True, WHITE)
                line_rect = line_surf.get_rect(center=(self.width // 2, self.height // 2 + 30 + i * 40))
                screen.blit(line_surf, line_rect)

            pygame.display.flip()
            self._handle_replay_input()

    def _trigger_game_over(self, winner_text):
        if not self.game_over:
            self.game_over = True
            self.winner_text = winner_text

    def _handle_replay_input(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_3:
                        self.winning_score = 3
                        waiting = False
                    elif event.key == pygame.K_5:
                        self.winning_score = 5
                        waiting = False
                    elif event.key == pygame.K_7:
                        self.winning_score = 7
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
        self.reset_game()

    def reset_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.ball.reset()
        self.player.set_position(10, self.height // 2 - self.paddle_height // 2)
        self.ai.set_position(self.width - 20, self.height // 2 - self.paddle_height // 2)
        self.game_over = False
        self.winner_text = ""
