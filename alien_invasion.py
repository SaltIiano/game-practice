import pygame
import sys
from time import sleep
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from utils import hide_mouse_cursor
from boss import Boss

class AlienInvasion:
    def __init__(self):
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption('Alien Invasion')

        self.stats = GameStats(self)
        self.score_board = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        self.create_fleet_of_aliens()
        self.play_button = Button(self, 'Play')

        self.wave_counter = 0

    def run_game(self):
        print("Game started") 
        while True:
            self.respond_to_events()

            if self.stats.game_active:
                self.ship.update()
                self.update_bullet_positions()
                self._update_aliens()

            self._update_screen()

    def respond_to_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self.check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.start_game_if_player_clicks_play(mouse_pos)

    def start_game_if_player_clicks_play(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.reset_game_settings()
            self.remove_aliens_and_bullets()
            self.create_new_fleet()
            hide_mouse_cursor()

    def reset_game_settings(self):
        self.settings.initialize_dynamic_settings()
        self.reset_game_statistics()

    def remove_aliens_and_bullets(self):
        self.aliens.empty()
        self.bullets.empty()

    def create_new_fleet(self):
        self.create_fleet_of_aliens()
        self.ship.align_center()

    def reset_game_statistics(self):
        self.stats.reset_stats()
        self.stats.game_active = True
        self.score_board.prep_score()
        self.score_board.prep_level()
        self.score_board.prep_ships()

    def check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            print("Exiting game") 
            sleep(5) 
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.fire_bullet()

    def check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def fire_bullet(self):
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def update_bullet_positions(self):
        self.bullets.update()
        self.remove_bullets_that_have_disappeared()
        self.manage_bullet_alien_collision()

    def remove_bullets_that_have_disappeared(self):
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

    def manage_bullet_alien_collision(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.score_board.prep_score()
            self.score_board.check_high_score()

        collisions = pygame.sprite.groupcollide(self.bullets, self.bosses, True, False)
        if collisions:
            for boss in self.bosses:
                boss.health -= 1
                if boss.health <= 0:
                    self.bosses.remove(boss)
                    self.stats.score += self.settings.boss_points
                    self.score_board.prep_score()
                    self.score_board.check_high_score()

        if not self.aliens:
            self.increase_level()

    def increase_level(self):
        self.bullets.empty()
        self.create_fleet_of_aliens()
        self.settings.increase_speed()

        self.stats.level += 1
        self.score_board.prep_level()

        self.wave_counter += 1

        if self.wave_counter % 3 == 0:
            self.create_boss()

    def create_boss(self):
        self.bosses.empty()

        boss = Boss(self)
        self.bosses.add(boss)

    def create_fleet_of_aliens(self):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self.place_alien_in_row(alien_number, row_number)

    def place_alien_in_row(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()

        self.bosses.update()

        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.score_board.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self.create_fleet_of_aliens()
            self.ship.align_center()

            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.draw()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        
        if self.bosses:
            self.bosses.draw(self.screen)

        self.score_board.show_score()

        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()

if __name__ == "__main__":
    ai = AlienInvasion()
    ai.run_game()
