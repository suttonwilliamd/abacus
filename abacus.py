"""Six-column decimal Soroban. Pure state/geometry; pygame starts only in main."""
from dataclasses import dataclass

WIDTH, HEIGHT = 1000, 740
COLUMNS = 6
DIVIDER = 310
RADIUS = 20
PLACES = (100000, 10000, 1000, 100, 10, 1)


def bounded_int(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'Expected integer in {low}..{high}')
    return value


@dataclass(frozen=True)
class Column:
    """The digit is the sole bead state: no mutable geometry or active flags."""
    digit: int = 0

    def __post_init__(self):
        bounded_int(self.digit, 0, 9)

    @property
    def lower_count(self):
        return self.digit % 5

    @property
    def upper_active(self):
        return self.digit >= 5

    def lower_click(self, index):
        bounded_int(index, 0, 3)
        count = index if index < self.lower_count else index + 1
        return Column(5 * self.upper_active + count)

    def toggle_upper(self):
        return Column((self.digit + 5) % 10)

    def adjust_lower(self, delta):
        bounded_int(delta, -1, 1)
        return Column(5 * self.upper_active + max(0, min(4, self.lower_count + delta)))


@dataclass(frozen=True)
class Bead:
    x: int
    y: int
    index: int  # -1 is the upper bead
    active: bool

    def contains(self, pos):
        return (pos[0] - self.x)**2 + (pos[1] - self.y)**2 <= RADIUS**2


def beads(column, index):
    """Two chambers. 46px pitch, 6px inter-bead gap, 50px group gap."""
    bounded_int(index, 0, COLUMNS - 1)
    x = 170 + 132 * index
    result = [Bead(x, 280 if column.upper_active else 204, -1, column.upper_active)]
    for i in range(4):
        active = i < column.lower_count
        y = 342 + 46*i if active else 578 - 46*(3-i)
        result.append(Bead(x, y, i, active))
    return tuple(result)


class Abacus:
    def __init__(self):
        self._columns = (Column(),) * COLUMNS
        self._selected = COLUMNS - 1

    @property
    def columns(self):
        return self._columns

    @property
    def selected(self):
        return self._selected

    @property
    def total(self):
        return sum(col.digit * place for col, place in zip(self.columns, PLACES))

    def select(self, index):
        self._selected = bounded_int(index, 0, COLUMNS - 1)

    def set_digit(self, digit):
        col = Column(digit)
        self._columns = self.columns[:self.selected] + (col,) + self.columns[self.selected + 1:]

    def reset(self):
        self._columns = (Column(),) * COLUMNS

    def click(self, pos):
        # Evaluate a fixed geometry snapshot and stop on the first hit.
        for index, column in enumerate(self.columns):
            for bead in beads(column, index):
                if bead.contains(pos):
                    self.select(index)
                    changed = column.toggle_upper() if bead.index == -1 else column.lower_click(bead.index)
                    self.set_digit(changed.digit)
                    return True
        return False


def handle_event(model, event):
    """Actual desktop and smoke tests share this event-to-state boundary."""
    import pygame
    if event.type == pygame.QUIT:
        return False
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        model.click(event.pos)
    if event.type == pygame.KEYDOWN:
        key = event.key
        if key == pygame.K_ESCAPE:
            return False
        if key in (pygame.K_LEFT, pygame.K_RIGHT):
            model.select(max(0, min(5, model.selected + (-1 if key == pygame.K_LEFT else 1))))
        elif pygame.K_0 <= key <= pygame.K_9:
            model.set_digit(key - pygame.K_0)
        elif key == pygame.K_SPACE:
            model.set_digit(model.columns[model.selected].toggle_upper().digit)
        elif key in (pygame.K_UP, pygame.K_DOWN):
            model.set_digit(model.columns[model.selected].adjust_lower(1 if key == pygame.K_UP else -1).digit)
        elif key == pygame.K_r:
            model.reset()
        keypad = [pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4,
                  pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9]
        if key in keypad:
            model.set_digit(keypad.index(key))
    return True


def render(surface, model):
    import pygame
    bg, ink, muted = '#F6EFDF', '#30261E', '#655344'
    surface.fill(bg)
    def text(message, size, color, center, bold=False):
        font = pygame.font.Font(None, size)
        font.set_bold(bold)
        image = font.render(message, True, color)
        surface.blit(image, image.get_rect(center=center))

    text('SOROBAN / SIX PLACES', 24, muted, (500, 28), True)
    text(f'{model.total:,}', 64, ink, (500, 79), True)
    text('Move beads toward the bar to count them.', 24, muted, (500, 125))
    pygame.draw.rect(surface, '#855431', (70, 156, 860, 482), border_radius=18)
    pygame.draw.rect(surface, '#553620', (70, 156, 860, 482), 4, border_radius=18)
    pygame.draw.rect(surface, '#E3C598', (96, 180, 808, 432), border_radius=7)
    for i, column in enumerate(model.columns):
        x = beads(column, i)[0].x
        if i == model.selected:
            pygame.draw.rect(surface, '#FFF5DB', (x-49, 184, 98, 424), border_radius=10)
            pygame.draw.rect(surface, '#234E5A', (x-49, 184, 98, 424), 3, border_radius=10)
        pygame.draw.line(surface, '#715D46', (x, 190), (x, 604), 5)
    pygame.draw.rect(surface, '#553620', (96, DIVIDER-8, 808, 16))
    for i, column in enumerate(model.columns):
        for bead in beads(column, i):
            color = '#FFF0C9' if bead.active else '#873E2E'
            pygame.draw.circle(surface, '#553620', (bead.x, bead.y+3), RADIUS)
            pygame.draw.circle(surface, color, (bead.x, bead.y), RADIUS)
            pygame.draw.circle(surface, '#412C22', (bead.x, bead.y), RADIUS, 2)
            pygame.draw.line(surface, '#856137' if bead.active else '#C77E59',
                             (bead.x-10, bead.y-7), (bead.x+8, bead.y-7), 2)
        x = beads(column, i)[0].x
        text(f'{column.digit} x {PLACES[i]:,}', 22, '#FFF5DB', (x, 624), True)
    text(f'Selected: {PLACES[model.selected]:,} place  |  digit {model.columns[model.selected].digit}',
         25, ink, (500, 660), True)
    text('Left / Right: select   |   0-9: set digit   |   Space: toggle five', 24, ink, (500, 695))
    text('Up / Down: lower beads   |   R: reset   |   Esc: exit   |   Left-click: move bead', 23, ink, (500, 723))


def main():
    import pygame
    try:
        pygame.display.init()
        pygame.font.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Soroban - Six Places')
        clock = pygame.time.Clock()
        model = Abacus()
        running = True
        while running:
            for event in pygame.event.get():
                if not handle_event(model, event):
                    running = False
                    break
            if running:
                render(screen, model)
                pygame.display.flip()
                clock.tick(60)
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
