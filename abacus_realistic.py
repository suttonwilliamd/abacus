"""
Semi-Realistic Interactive Abacus - Soroban style
Based on improved code from Gippity
"""

import pygame
import sys
import math
import random

pygame.init()

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
WIDTH, HEIGHT = 1100, 650
FPS = 60
COLUMNS = 6

BACKGROUND = (230, 215, 185)
WOOD_LIGHT = (160, 110, 70)
WOOD_DARK = (110, 70, 40)
WOOD_BORDER = (90, 55, 30)
ROD_DARK = (90, 90, 90)
ROD_LIGHT = (200, 200, 200)
TEXT_COLOR = (40, 25, 15)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Semi-Realistic Soroban")
clock = pygame.time.Clock()
font = pygame.font.SysFont("georgia", 54)


# -------------------------------------------------
# Utility
# -------------------------------------------------
def lerp(a, b, t):
    return a + (b - a) * t


# -------------------------------------------------
# Bead (3D shaded + animated)
# -------------------------------------------------
class Bead:
    def __init__(self, x, y, radius, value):
        self.x = x
        self.y = y
        self.target_y = y
        self.radius = radius
        self.value = value

    def update(self):
        self.y = lerp(self.y, self.target_y, 0.25)

    def draw(self, surface):
        # Shadow
        shadow = pygame.Surface((self.radius * 2, self.radius), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
        surface.blit(shadow, (self.x - self.radius, self.y - self.radius // 2))

        # Radial gradient
        for r in range(self.radius, 0, -1):
            shade = 120 + int(40 * (r / self.radius))
            color = (shade, 30, 30)
            pygame.draw.circle(surface, color, (self.x, int(self.y)), r)

        # Highlight
        pygame.draw.circle(surface, (255, 210, 210), (self.x - self.radius // 3, int(self.y - self.radius // 3)), self.radius // 4)
        pygame.draw.circle(surface, (40, 0, 0), (self.x, int(self.y)), self.radius, 2)

    def is_clicked(self, pos):
        mx, my = pos
        return (mx - self.x) ** 2 + (my - self.y) ** 2 <= self.radius ** 2


# -------------------------------------------------
# Column (Correct Soroban Geometry)
# -------------------------------------------------
class Column:
    def __init__(self, x):
        self.x = x
        self.radius = 22
        self.spacing = 50

        # Define usable vertical area
        inner_top = 110
        inner_bottom = HEIGHT - 110
        total_height = inner_bottom - inner_top

        # Soroban 1:4 ratio (upper:lower)
        upper_units = 1
        lower_units = 4
        unit = total_height / (upper_units + lower_units)

        self.bar_y = int(inner_top + unit * upper_units)

        # Upper bead (value = 5)
        # When active = touching bar = value 5
        # When not active = away from bar = value 0
        self.upper_rest = self.bar_y - unit * 0.8
        self.upper_active = self.bar_y - self.radius - 35
        self.upper = Bead(x, self.upper_rest, self.radius, 5)
        self.upper_active_state = False

        # Lower beads (value = 1 each, max 4)
        # active_count = how many beads are pushed UP toward the bar
        # 0 = all beads down (away from bar) = value 0
        # 4 = all beads up (at bar) = value 4
        self.active_count = 0
        
        # Position when at bar (active)
        self.lower_active_base = self.bar_y + self.radius + 35
        # Position when away from bar (inactive)
        self.lower_rest_base = inner_bottom - (3 * self.spacing)

        self.lowers = []
        for i in range(4):
            # Start all beads at the bottom (inactive/away from bar)
            y = self.lower_rest_base + i * self.spacing
            self.lowers.append(Bead(x, y, self.radius, 1))

    def update(self):
        self.upper.update()
        for bead in self.lowers:
            bead.update()

    def draw(self, surface):
        # Rod with gradient
        for i in range(-3, 4):
            t = abs(i) / 3
            color = (
                int(lerp(ROD_LIGHT[0], ROD_DARK[0], t)),
                int(lerp(ROD_LIGHT[1], ROD_DARK[1], t)),
                int(lerp(ROD_LIGHT[2], ROD_DARK[2], t)),
            )
            pygame.draw.line(surface, color, (self.x + i, 100), (self.x + i, HEIGHT - 100), 1)

        # Divider bar
        pygame.draw.rect(surface, WOOD_DARK, (self.x - 42, self.bar_y - 12, 84, 24), border_radius=6)

        self.upper.draw(surface)
        for bead in self.lowers:
            bead.draw(surface)

    def handle_click(self, pos):
        # Upper bead - toggle between touching/away from bar
        if self.upper.is_clicked(pos):
            self.upper_active_state = not self.upper_active_state
            self.upper.target_y = self.upper_active if self.upper_active_state else self.upper_rest

        # Lower beads
        # Click on bead i -> push beads 0 through i toward the bar
        for i, bead in enumerate(self.lowers):
            if bead.is_clicked(pos):
                self.active_count = i + 1
                self.update_lower_positions()
                break

    def update_lower_positions(self):
        # Active beads (0 to active_count-1): AT the bar (up), stacked vertically
        for i in range(self.active_count):
            self.lowers[i].target_y = self.lower_active_base - i * self.spacing

        # Inactive beads (active_count to 3): AWAY from bar (down), stacked vertically
        for i in range(self.active_count, 4):
            self.lowers[i].target_y = self.lower_rest_base + (i - self.active_count) * self.spacing

    def get_value(self):
        total = 0
        if self.upper_active_state:
            total += 5
        total += self.active_count
        return total


# -------------------------------------------------
# Frame
# -------------------------------------------------
def draw_frame():
    pygame.draw.rect(screen, WOOD_BORDER, (40, 40, WIDTH - 80, HEIGHT - 80), border_radius=25)
    pygame.draw.rect(screen, WOOD_LIGHT, (60, 60, WIDTH - 120, HEIGHT - 120), border_radius=20)

    # Subtle wood grain
    for i in range(60, HEIGHT - 60, 14):
        alpha = random.randint(10, 20)
        grain = pygame.Surface((WIDTH - 120, 2), pygame.SRCALPHA)
        pygame.draw.line(grain, (90, 60, 30, alpha), (0, 0), (WIDTH - 120, 0))
        screen.blit(grain, (60, i))


# -------------------------------------------------
# Setup columns
# -------------------------------------------------
columns = []
start_x = 200
gap = 130

for i in range(COLUMNS):
    columns.append(Column(start_x + i * gap))


def calculate_total():
    total = 0
    for i, col in enumerate(reversed(columns)):
        total += col.get_value() * (10 ** i)
    return total


# -------------------------------------------------
# Main Loop
# -------------------------------------------------
running = True

while running:
    clock.tick(FPS)
    screen.fill(BACKGROUND)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for col in columns:
                col.handle_click(event.pos)

    draw_frame()

    for col in columns:
        col.update()
        col.draw(screen)

    total = calculate_total()
    text_surface = font.render(str(total), True, TEXT_COLOR)
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 5))

    pygame.display.flip()

pygame.quit()
sys.exit()
