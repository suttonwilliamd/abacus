"""
Simple Baby Abacus - Clear and unambiguous
"""

import pygame
import sys

pygame.init()

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
WIDTH, HEIGHT = 1100, 650
FPS = 60
COLUMNS = 6

BACKGROUND = (240, 234, 210)
WOOD_COLOR = (160, 120, 80)
BEAD_COLOR = (200, 60, 60)
BEAD_HIGHLIGHT = (255, 100, 100)
ROD_COLOR = (180, 180, 180)
TEXT_COLOR = (40, 20, 10)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Baby Abacus")
clock = pygame.time.Clock()
font = pygame.font.SysFont("georgia", 48)

# -------------------------------------------------
# Bead
# -------------------------------------------------
class Bead:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.target_y = y
        self.radius = radius
        self.active = False
    
    def update(self):
        # Smooth movement
        self.y += (self.target_y - self.y) * 0.2
    
    def draw(self, surface):
        # Draw bead
        pygame.draw.circle(surface, BEAD_COLOR, (self.x, int(self.y)), self.radius)
        pygame.draw.circle(surface, BEAD_HIGHLIGHT, (self.x - 5, int(self.y) - 5), self.radius // 3)
        pygame.draw.circle(surface, (80, 20, 20), (self.x, int(self.y)), self.radius, 2)
    
    def is_clicked(self, pos):
        mx, my = pos
        return (mx - self.x) ** 2 + (my - self.y) ** 2 <= self.radius ** 2


# -------------------------------------------------
# Column
# -------------------------------------------------
class Column:
    def __init__(self, x):
        self.x = x
        self.radius = 20
        self.spacing = 45
        
        # Bar position - roughly 1/5 from top
        self.bar_y = HEIGHT // 5 * 1
        
        # Upper bead (value 5) - above bar
        self.upper = Bead(x, self.bar_y - 70, self.radius)
        self.upper.active = False
        
        # Lower beads (value 1 each) - below bar
        self.lowers = []
        for i in range(4):
            y = self.bar_y + 50 + i * self.spacing
            b = Bead(x, y, self.radius)
            b.active = False  # False = away from bar (bottom), True = at bar (top of lower section)
            self.lowers.append(b)
    
    def update(self):
        self.upper.update()
        for b in self.lowers:
            b.update()
    
    def draw(self, surface):
        # Draw rod
        pygame.draw.line(surface, ROD_COLOR, (self.x, 80), (self.x, HEIGHT - 80), 6)
        
        # Draw bar
        pygame.draw.rect(surface, WOOD_COLOR, (self.x - 50, self.bar_y - 10, 100, 20), border_radius=5)
        
        # Draw upper bead
        self.upper.draw(surface)
        
        # Draw lower beads
        for b in self.lowers:
            b.draw(surface)
    
    def handle_click(self, pos):
        # Check upper bead
        if self.upper.is_clicked(pos):
            self.upper.active = not self.upper.active
            self.upper.target_y = self.bar_y - 70 if not self.upper.active else self.bar_y + 25
        
        # Check lower beads
        for i, bead in enumerate(self.lowers):
            if bead.is_clicked(pos):
                # Toggle: if clicking an inactive bead, activate it and all below
                # if clicking active, deactivate it and all above
                if not bead.active:
                    # Activate this bead and all below it
                    for j in range(i, 4):
                        self.lowers[j].active = True
                else:
                    # Deactivate this bead and all above it
                    for j in range(i + 1):
                        self.lowers[j].active = False
                break
        
        # Update positions
        self.update_lower_positions()
    
    def update_lower_positions(self):
        # All active beads go to bar, all inactive go to bottom
        for i, bead in enumerate(self.lowers):
            if bead.active:
                bead.target_y = self.bar_y + 50 + i * self.spacing
            else:
                bead.target_y = self.bar_y + 50 + (i + 4) * self.spacing
    
    def get_value(self):
        total = 0
        if self.upper.active:
            total += 5
        total += sum(1 for b in self.lowers if b.active)
        return total


# -------------------------------------------------
# Frame
# -------------------------------------------------
def draw_frame():
    pygame.draw.rect(screen, WOOD_COLOR, (30, 30, WIDTH - 60, HEIGHT - 60), border_radius=20)
    pygame.draw.rect(screen, (120, 90, 60), (30, 30, WIDTH - 60, HEIGHT - 60), 8, border_radius=20)


# -------------------------------------------------
# Setup
# -------------------------------------------------
columns = []
start_x = 180
gap = 140

for i in range(COLUMNS):
    col = Column(start_x + i * gap)
    columns.append(col)
    # Initialize positions
    col.update_lower_positions()


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
