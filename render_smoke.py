"""Finite real pygame render/event smoke. Only synthetic digits enter artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pygame
from abacus import Abacus, WIDTH, HEIGHT, RADIUS, render, handle_event


def rendered_centers(screen, model, column_x=830):
    # Observe actual draw calls, forwarding every call to pygame. No geometry
    # formula/Bead data is consulted by the overlapping-hit regression oracle.
    centers = []
    original = pygame.draw.circle
    def capture(surface, color, center, radius, width=0):
        if radius == RADIUS and width == 2 and center[0] == column_x:
            centers.append(center)
        return original(surface, color, center, radius, width)
    with patch.object(pygame.draw, 'circle', capture):
        render(screen, model)
    assert len(centers) == 5, centers
    return centers


def queued(model, event):
    pygame.event.post(event)
    running = True
    for received in pygame.event.get():
        if not handle_event(model, received):
            running = False
            break
    return running


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('artifacts'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        pygame.display.init()
        pygame.font.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        model = Abacus()
        centers = rendered_centers(screen, model)
        queued(model, pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=centers[4], button=1))
        assert model.total == 4
        centers = rendered_centers(screen, model)
        queued(model, pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=centers[2], button=1))
        assert model.total == 1, model.total
        assert not model.columns[-1].upper_active
        # Run controls through SDL's real event queue as the desktop does.
        for key, total in [(pygame.K_9, 9), (pygame.K_SPACE, 4), (pygame.K_DOWN, 3),
                           (pygame.K_UP, 4), (pygame.K_LEFT, 4), (pygame.K_1, 14),
                           (pygame.K_RIGHT, 14), (pygame.K_r, 0)]:
            assert queued(model, pygame.event.Event(pygame.KEYDOWN, key=key))
            assert model.total == total, (key, model.total)
        images = []
        for label, digits in [('zero','000000'), ('four','000004'), ('nine','000009'), ('mixed','123456')]:
            model.reset()
            for i, digit in enumerate(digits):
                model.select(i)
                queued(model, pygame.event.Event(pygame.KEYDOWN, key=pygame.K_0+int(digit)))
            assert model.total == int(digits)
            render(screen, model)
            pygame.display.flip()
            path = args.output / f'candidate-{label}.png'
            pygame.image.save(screen, path)
            images.append({'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                           'total': model.total, 'size': [WIDTH, HEIGHT]})
        assert not queued(model, pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        assert not queued(model, pygame.event.Event(pygame.QUIT))
        result = {'platform': sys.platform, 'python': sys.version.split()[0],
                  'pygame': pygame.version.ver, 'sdl': list(pygame.get_sdl_version()),
                  'video_driver': pygame.display.get_driver(),
                  'overlap_regression': [4, 1], 'event_smoke': 'passed', 'images': images}
        (args.output / 'render-results.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result, indent=2))
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
