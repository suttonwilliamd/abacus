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
ROD_LIGHT = (180, 180, 180)
TEXT_COLOR = (40, 25, 15)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Semi-Realistic Abacus")
clock = pygame.time.Clock()
font = pygame.font.SysFont("georgia", 54)


# -------------------------------------------------
# Utility
# -------------------------------------------------
def lerp(a, b, t):
    return a + (b - a) * t


# -------------------------------------------------
# Bead Class (3D shaded + animated)
# -------------------------------------------------
class Bead:
    def __init__(self, x, y, radius, value):
        self.x = x
        self.y = y
        self.target_y = y
        self.radius = radius
        self.value = value
        self.active = False  # Only used for upper bead

    def update(self):
        # Smooth slide animation
        self.y = lerp(self.y, self.target_y, 0.25)

    def draw(self, surface):
        # Shadow
        shadow_rect = pygame.Rect(
            self.x - self.radius, self.y - self.radius // 2, self.radius * 2, self.radius
        )
        shadow = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
        surface.blit(shadow, shadow_rect.topleft)

        # Radial gradient bead
        for i in range(self.radius, 0, -1):
            shade = 120 + int(40 * (i / self.radius))
            color = (shade, 30, 30)
            pygame.draw.circle(surface, color, (self.x, int(self.y)), i)

        # Highlight
        pygame.draw.circle(surface, (255, 200, 200), (self.x - self.radius // 3, int(self.y - self.radius // 3)), self.radius // 4)
        pygame.draw.circle(surface, (40, 0, 0), (self.x, int(self.y)), self.radius, 2)

    def is_clicked(self, pos):
        mx, my = pos
        return (mx - self.x) ** 2 + (my - self.y) ** 2 <= self.radius ** 2


# -------------------------------------------------
# Column Class (correct stacking logic)
# -------------------------------------------------
class Column:
    def __init__(self, x):
        self.x = x
        
        # Calculate bar position with correct 1:4 ratio (upper:lower)
        inner_top = 110
        inner_bottom = HEIGHT - 110
        total_bead_space = inner_bottom - inner_top
        
        # 1 unit for upper beads, 4 units for lower beads
        unit = total_bead_space / 5
        self.bar_y = int(inner_top + unit)
        
        self.radius = 22
        self.spacing = 48

        # Upper bead (still uses active state)
        self.upper = Bead(x, self.bar_y - int(unit * 0.7), self.radius, 5)
        self.upper_rest = self.bar_y - int(unit * 0.7)
        self.upper_active = self.bar_y - 35

        # Lower beads - use active_count for contiguous stack
        # active_count = beads pushed UP toward the bar (value = 1-4)
        # 0 = all beads pushed DOWN (away from bar) = value 0
        self.active_count = 0
        self.lowers = []
        
        # At program start: all lower beads pushed DOWN (away from bar) = value 0
        # When activated: beads move UP toward the bar
        self.lower_inactive_base = self.bar_y + 150  # Down/away from bar (value 0)
        self.lower_active_base = self.bar_y + 10     # Up/at the bar (value 4 max)

        for i in range(4):
            # Start all beads at bottom (inactive position)
            y = self.lower_inactive_base + i * self.spacing
            self.lowers.append(Bead(x, y, self.radius, 1))

    def update(self):
        self.upper.update()
        for b in self.lowers:
            b.update()

    def draw(self, surface):
        # Rod with vertical gradient
        for i in range(-3, 4):
            t = abs(i) / 3
            color = (
                int(lerp(ROD_LIGHT[0], ROD_DARK[0], t)),
                int(lerp(ROD_LIGHT[1], ROD_DARK[1], t)),
                int(lerp(ROD_LIGHT[2], ROD_DARK[2], t)),
            )
            pygame.draw.line(surface, color, (self.x + i, 110), (self.x + i, HEIGHT - 110), 1)

        # Divider bar
        pygame.draw.rect(surface, WOOD_DARK, (self.x - 40, self.bar_y - 10, 80, 20), border_radius=4)

        self.upper.draw(surface)
        for bead in self.lowers:
            bead.draw(surface)

    def handle_click(self, pos):
        # Upper bead
        if self.upper.is_clicked(pos):
            self.upper.active = not self.upper.active
            self.upper.target_y = self.upper_active if self.upper.active else self.upper_rest

        # Lower beads - click to push beads toward/away from bar
        for i, bead in enumerate(self.lowers):
            if bead.is_clicked(pos):
                # Set active_count to i+1 to push beads 0 through i toward the bar
                self.active_count = i + 1
                self.update_lower_positions()
                break

    def update_lower_positions(self):
        # First active_count beads are at the bar (UP)
        # Remaining beads are at the bottom (DOWN)
        for i in range(self.active_count):
            self.lowers[i].target_y = self.lower_active_base - i * self.spacing

        for i in range(self.active_count, 4):
            self.lowers[i].target_y = self.lower_inactive_base + (i - self.active_count) * self.spacing

    def get_value(self):
        total = 0
        if self.upper.active:
            total += 5
        total += self.active_count
        return total


# -------------------------------------------------
# Frame
# -------------------------------------------------
def draw_frame():
    # Outer frame
    pygame.draw.rect(screen, WOOD_BORDER, (40, 40, WIDTH - 80, HEIGHT - 80), border_radius=25)

    # Inner frame
    pygame.draw.rect(screen, WOOD_LIGHT, (60, 60, WIDTH - 120, HEIGHT - 120), border_radius=20)

    # Subtle wood grain lines
    for i in range(60, HEIGHT - 60, 12):
        alpha = random.randint(10, 25)
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
