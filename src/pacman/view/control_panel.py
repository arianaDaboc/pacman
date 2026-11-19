"""The control panel next to the maze: chooses the ghosts' search algorithm and shows what each ghost is doing."""

import pygame

from pacman import config


class ControlPanel:
    """A column on the right of the maze, with one button per search algorithm and one block per ghost."""

    def __init__(self, finders) -> None:
        """Prepare one button for each path finder, two per row."""
        self.finders = finders
        self.font = pygame.font.Font(config.FONT_PATH, config.PANEL_FONT_SIZE)
        self.left = config.SCREEN_WIDTH - config.PANEL_WIDTH + config.PANEL_MARGIN
        self.width = config.PANEL_WIDTH - 2 * config.PANEL_MARGIN
        self.line = self.font.get_height() + config.PANEL_LINE_GAP  # distance between two lines of text
        self.buttons: list[pygame.Rect] = []
        button_width = (self.width - config.PANEL_MARGIN) // 2
        top = config.PANEL_MARGIN + 2 * self.line
        for index in range(len(finders)):
            column, row = index % 2, index // 2
            x = self.left + column * (button_width + config.PANEL_MARGIN)
            y = top + row * (config.BUTTON_HEIGHT + config.PANEL_MARGIN)
            self.buttons.append(pygame.Rect(x, y, button_width, config.BUTTON_HEIGHT))

    def handle(self, event: pygame.event.Event):
        """Return the path finder whose button was clicked, or None if the click was somewhere else."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for finder, button in zip(self.finders, self.buttons):
                if button.collidepoint(event.pos):
                    return finder
        return None

    def draw(self, surface: pygame.Surface, ghosts, current_finder, overlay_on: bool) -> None:
        """Draw the buttons, the overlay hint and, for each ghost, its state and its last search."""
        self._text(surface, "GHOST SEARCH", self.left, config.PANEL_MARGIN)
        for number, (finder, button) in enumerate(zip(self.finders, self.buttons), start=1):
            selected = finder is current_finder
            if selected:
                pygame.draw.rect(surface, config.BUTTON_SELECTED_COLOUR, button)
            pygame.draw.rect(surface, config.TEXT_COLOUR, button, 1)
            colour = config.BACKGROUND_COLOUR if selected else config.TEXT_COLOUR
            label = self.font.render(f"{number} {finder.name}", True, colour)
            surface.blit(label, label.get_rect(center=button.center))

        y = self.buttons[-1].bottom + self.line
        self._text(surface, f"O: PATHS {'ON' if overlay_on else 'OFF'}", self.left, y)
        y += 2 * self.line
        for ghost in ghosts:
            self._text(surface, ghost.name.upper(), self.left, y, config.GHOST_COLOURS[ghost.name])
            self._text(surface, f" STATE {ghost.state.value.upper()}", self.left, y + self.line)
            self._text(surface, f" PATH  {ghost.path_length}", self.left, y + 2 * self.line)
            self._text(surface, f" NODES {ghost.expanded}", self.left, y + 3 * self.line)
            y += 5 * self.line

    def _text(self, surface: pygame.Surface, text: str, x: int, y: int, colour=config.TEXT_COLOUR) -> None:
        """Draw one line of text with its top-left corner at (x, y)."""
        surface.blit(self.font.render(text, True, colour), (x, y))
