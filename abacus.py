"""
Interactive Abacus - Realistic Soroban-style abacus
Based on code from conversation with Gippity
"""

import pygame
import sys

pygame.init()

# ----------------------------
# Settings
# ----------------------------
WIDTH, HEIGHT = 1000, 600
FPS = 60
COLUMNS = 6

WOOD = (139, 94, 60)
WOOD_DARK = (100, 65, 40)
BACKGROUND = (240, 228, 200)
BEAD = (120, 30, 30)
BEAD_HIGHLIGHT = (160, 50, 50)
TEXT_COLOR = (40, 20, 10)
METAL = (60, 60, 60)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Interactive Abacus")
clock = pygame.time.Clock()
font = pygame.font.SysFont("georgia", 48)

# ----------------------------
# Bead Class
# ----------------------------
class Bead:
    def __init__(self, x, y, radius, value, is_upper):
        self.x = x
        self.y = y
        self.start_y = y
        self.radius = radius
        self.value = value
        self.is_upper = is_upper
        self.active = False

    def draw(self, surface):
        color = BEAD_HIGHLIGHT if self.active else BEAD
        pygame.draw.circle(surface, color, (self.x, int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 0, 0), (self.x, int(self.y)), self.radius, 2)

    def is_clicked(self, pos):
        mx, my = pos
        return (mx - self.x) ** 2 + (my - self.y) ** 2 <= self.radius ** 2


# ----------------------------
# Column Class
# ----------------------------
class Column:
    def __init__(self, x):
        self.x = x
        self.bar_y = HEIGHT // 2
        self.spacing = 50
        self.bead_radius = 20
        
        # Upper bead (value 5)
        self.upper = Bead(x, self.bar_y - 120, self.bead_radius, 5, True)
        
        # Lower beads (value 1)
        self.lowers = []
        for i in range(4):
            y = self.bar_y + 40 + i * self.spacing
            self.lowers.append(Bead(x, y, self.bead_radius, 1, False))

    def draw(self, surface):
        # Rod
        pygame.draw.line(surface, METAL, (self.x, 100), (self.x, HEIGHT - 100), 4)
        
        # Divider bar
        pygame.draw.rect(surface, WOOD_DARK, (self.x - 35, self.bar_y - 8, 70, 16))
        
        self.upper.draw(surface)
        for bead in self.lowers:
            bead.draw(surface)

    def handle_click(self, pos):
        # Upper bead
        if self.upper.is_clicked(pos):
            self.upper.active = not self.upper.active
            if self.upper.active:
                self.upper.y = self.bar_y - 30
            else:
                self.upper.y = self.bar_y - 120
        
        # Lower beads
        for i, bead in enumerate(self.lowers):
            if bead.is_clicked(pos):
                if bead.active:
                    # deactivate this and above
                    for j in range(i, 4):
                        self.lowers[j].active = False
                        self.lowers[j].y = self.bar_y + 40 + j * self.spacing
                else:
                    # activate this and below
                    for j in range(0, i + 1):
                        self.lowers[j].active = True
                        self.lowers[j].y = self.bar_y - 10 - (i - j) * self.spacing

    def get_value(self):
        total = 0
        if self.upper.active:
            total += 5
        total += sum(b.active for b in self.lowers)
        return total


# ----------------------------
# Create Columns
# ----------------------------
columns = []
start_x = 150
gap = 120

for i in range(COLUMNS):
    columns.append(Column(start_x + i * gap))


# ----------------------------
# Draw Frame
# ----------------------------
def draw_frame():
    pygame.draw.rect(screen, WOOD, (50, 50, WIDTH - 100, HEIGHT - 100), border_radius=20)
    pygame.draw.rect(screen, WOOD_DARK, (50, 50, WIDTH - 100, HEIGHT - 100), 10, border_radius=20)


# ----------------------------
# Calculate Total Number
# ----------------------------
def calculate_total():
    total = 0
    for i, col in enumerate(reversed(columns)):
        total += col.get_value() * (10 ** i)
    return total


# ----------------------------
# Main Loop
# ----------------------------
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
        col.draw(screen)

    # Display number
    total = calculate_total()
    text_surface = font.render(str(total), True, TEXT_COLOR)
    screen.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
