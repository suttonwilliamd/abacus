import itertools
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import pygame
from abacus import Abacus, Column, beads, handle_event, DIVIDER, RADIUS, PLACES


class ModelTests(unittest.TestCase):
    def test_all_digits(self):
        for d in range(10):
            col = Column(d)
            self.assertEqual(col.lower_count, d % 5)
            self.assertEqual(col.upper_active, d >= 5)
            self.assertEqual(col.toggle_upper().digit, d - 5 if d >= 5 else d + 5)

    def test_every_lower_click_transition(self):
        # Independent literal truth table: row=count, column=clicked bead.
        expected = ((1, 2, 3, 4), (0, 2, 3, 4), (0, 1, 3, 4),
                    (0, 1, 2, 4), (0, 1, 2, 3))
        for upper, count, index in itertools.product((0, 5), range(5), range(4)):
            self.assertEqual(Column(upper+count).lower_click(index).digit,
                             upper+expected[count][index])

    def test_adjust_and_reset(self):
        model = Abacus()
        for d in range(10):
            col = Column(d)
            self.assertEqual(col.adjust_lower(1).lower_count, min(4, d % 5 + 1))
            self.assertEqual(col.adjust_lower(-1).lower_count, max(0, d % 5 - 1))
            self.assertEqual(col.adjust_lower(-1).upper_active, col.upper_active)
        model.set_digit(9)
        model.reset()
        self.assertEqual(model.total, 0)
        self.assertEqual([c.digit for c in model.columns], [0]*6)

    def test_place_totals(self):
        for number in (0, 1, 10, 100000, 123456, 999999):
            model = Abacus()
            for i, digit in enumerate(f'{number:06d}'):
                model.select(i)
                model.set_digit(int(digit))
            self.assertEqual(model.total, number)
        self.assertEqual(PLACES, (100000, 10000, 1000, 100, 10, 1))

    def test_invalid_state(self):
        for d in (-1, 10, True, 1.5, '1', None):
            with self.assertRaises(ValueError):
                Column(d)
        model = Abacus()
        for index in (-1, 6, True):
            with self.assertRaises(ValueError):
                model.select(index)
            with self.assertRaises(ValueError):
                beads(Column(), index)
        for index in (-1, 4):
            with self.assertRaises(ValueError):
                Column().lower_click(index)
        with self.assertRaises(ValueError):
            Column().adjust_lower(2)
        with self.assertRaises(AttributeError):
            model.columns = ()
        with self.assertRaises(AttributeError):
            model.columns[0].digit = 10

    def test_geometry_exhaustive_local_states_and_column_pairs(self):
        # Geometry depends only on local digit. Exhaust all 10 states per column
        # and all 100 state combinations for every pair, not a few sample totals.
        for i, d in itertools.product(range(6), range(10)):
            group = beads(Column(d), i)
            self.assertEqual([b.active for b in group[1:]], [j < d % 5 for j in range(4)])
            for bead in group:
                self.assertGreaterEqual(bead.x-RADIUS, 96)
                self.assertLessEqual(bead.x+RADIUS, 904)
                self.assertGreaterEqual(bead.y-RADIUS, 180)
                self.assertLessEqual(bead.y+RADIUS, 612)
                if bead.index == -1:
                    self.assertLess(bead.y+RADIUS, DIVIDER-8)
                else:
                    self.assertGreater(bead.y-RADIUS, DIVIDER+8)
            for a, b in itertools.combinations(group, 2):
                self.assertGreater((a.x-b.x)**2 + (a.y-b.y)**2, (2*RADIUS)**2)
            lower = group[1:]
            self.assertEqual(list(lower), sorted(lower, key=lambda b: b.y))
            if 0 < d % 5 < 4:
                self.assertGreaterEqual(lower[d % 5].y - lower[d % 5-1].y - 2*RADIUS, 50)
        for i, j in itertools.combinations(range(6), 2):
            for a, b in itertools.product(range(10), repeat=2):
                for ba, bb in itertools.product(beads(Column(a), i), beads(Column(b), j)):
                    self.assertGreater((ba.x-bb.x)**2+(ba.y-bb.y)**2, (2*RADIUS)**2)

    def test_import_safety(self):
        result = subprocess.run([sys.executable, '-c',
            "import sys; import abacus; assert 'pygame' not in sys.modules"],
            capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '')


class EventTests(unittest.TestCase):
    def key(self, model, key):
        return handle_event(model, pygame.event.Event(pygame.KEYDOWN, key=key))

    def test_keyboard(self):
        model = Abacus()
        for d in range(10):
            self.key(model, pygame.K_0+d)
            self.assertEqual(model.total, d)
        for key in (pygame.K_KP0, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4,
                    pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9):
            self.key(model, key)
        self.assertEqual(model.total, 9)
        self.key(model, pygame.K_SPACE)
        self.assertEqual(model.total, 4)
        for _ in range(6):
            self.key(model, pygame.K_DOWN)
        self.assertEqual(model.total, 0)
        for _ in range(6):
            self.key(model, pygame.K_UP)
        self.assertEqual(model.total, 4)
        for _ in range(8):
            self.key(model, pygame.K_LEFT)
        self.assertEqual(model.selected, 0)
        self.key(model, pygame.K_1)
        self.assertEqual(model.total, 100004)
        for _ in range(8):
            self.key(model, pygame.K_RIGHT)
        self.assertEqual(model.selected, 5)
        self.key(model, pygame.K_r)
        self.assertEqual(model.total, 0)
        self.assertFalse(self.key(model, pygame.K_ESCAPE))
        self.assertFalse(handle_event(model, pygame.event.Event(pygame.QUIT)))

    def test_desktop_main_lifecycle(self):
        from abacus import main
        for event in (pygame.event.Event(pygame.QUIT),
                      pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)):
            def observe_live():
                self.assertTrue(pygame.display.get_init())
                self.assertTrue(pygame.font.get_init())
                self.assertIsNone(pygame.mixer.get_init())
                return [event]
            with patch.object(pygame, 'init', side_effect=AssertionError('broad init')), \
                    patch.object(pygame.event, 'get', side_effect=observe_live) as events:
                main()
                events.assert_called_once()
            self.assertFalse(pygame.get_init())
            self.assertFalse(pygame.display.get_init())
            self.assertFalse(pygame.font.get_init())
            self.assertIsNone(pygame.mixer.get_init())

    def test_mouse_and_ignored_inputs(self):
        model = Abacus()
        for d in range(10):
            for bead_index in range(5):
                model.select(2)
                model.set_digit(d)
                bead = beads(model.columns[2], 2)[bead_index]
                before = model.total
                for button in (2, 3, 4, 5):
                    handle_event(model, pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(bead.x, bead.y), button=button))
                    self.assertEqual(model.total, before)
                expected = (d-5 if d >= 5 else d+5) if bead_index == 0 else (5*(d>=5) + ((bead_index-1) if bead_index-1 < d % 5 else bead_index))
                handle_event(model, pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(bead.x, bead.y), button=1))
                self.assertEqual(model.columns[2].digit, expected)
                self.assertEqual([c.digit for i,c in enumerate(model.columns) if i != 2], [0]*5)
        before = model.total
        handle_event(model, pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(0,0), button=1))
        self.key(model, pygame.K_a)
        self.assertEqual(model.total, before)


class LifecycleTests(unittest.TestCase):
    def assert_clean(self):
        self.assertFalse(pygame.display.get_init())
        self.assertFalse(pygame.font.get_init())
        self.assertIsNone(pygame.mixer.get_init())

    def test_smoke_live_subsystems(self):
        import render_smoke
        original = render_smoke.rendered_centers
        def observe_live(*args, **kwargs):
            self.assertTrue(pygame.display.get_init())
            self.assertTrue(pygame.font.get_init())
            self.assertIsNone(pygame.mixer.get_init())
            return original(*args, **kwargs)
        with tempfile.TemporaryDirectory() as output, \
                patch.object(sys, 'argv', ['render_smoke.py', '--output', output]), \
                patch.object(pygame, 'init', side_effect=AssertionError('broad init')), \
                patch.object(render_smoke, 'rendered_centers', side_effect=observe_live) as observed:
            render_smoke.main()
            self.assertEqual(observed.call_count, 2)
        self.assert_clean()

    def test_partial_setup_failures_clean_both_entrypoints(self):
        import abacus
        import render_smoke
        for entry in (abacus.main, render_smoke.main):
            for subsystem in (pygame.display, pygame.font):
                with self.subTest(entry=entry.__module__, subsystem=subsystem.__name__):
                    original_init = subsystem.init
                    def fail_after_init():
                        original_init()
                        self.assertTrue(subsystem.get_init())
                        raise RuntimeError('partial setup failure')
                    with tempfile.TemporaryDirectory() as output, \
                            patch.object(sys, 'argv', ['smoke', '--output', output]), \
                            patch.object(pygame, 'init', side_effect=AssertionError('broad init')), \
                            patch.object(subsystem, 'init', side_effect=fail_after_init):
                        with self.assertRaisesRegex(RuntimeError, 'partial setup failure'):
                            entry()
                    self.assert_clean()


if __name__ == '__main__':
    unittest.main()
