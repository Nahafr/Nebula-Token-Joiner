"""gradient.py: A file for handling gradient prints"""

from __future__ import annotations

import sys
from typing import Tuple, List, Any, Optional

from .color import NebulaColor
from .color import Color


class GradientPrinter:
    """A utility class for handling gradient color operations and printing."""

    @staticmethod
    def gradient(
        start: Tuple[int, int, int], end: Tuple[int, int, int], steps: int
    ) -> List[Tuple[int, int, int]]:
        """
        Generate a gradient of RGB colors between two colors.

        Args:
            start (Tuple[int, int, int]): RGB tuple of the start color.
            end (Tuple[int, int, int]): RGB tuple of the end color.
            steps (int): Number of colors in the gradient.

        Returns:
            List[Tuple[int, int, int]]: List of RGB tuples forming the gradient.

        Raises:
            ValueError: If steps is less than 1.
        """
        if steps < 1:
            raise ValueError("Steps must be greater than 0.")

        rs = [start[0]]
        gs = [start[1]]
        bs = [start[2]]

        for step in range(1, steps):
            rs.append(round(start[0] + (end[0] - start[0]) * step / steps))
            gs.append(round(start[1] + (end[1] - start[1]) * step / steps))
            bs.append(round(start[2] + (end[2] - start[2]) * step / steps))

        return list(zip(rs, gs, bs))

    @staticmethod
    def validate_hex_color(color: str) -> Tuple[int, int, int]:
        """
        Validate and convert a hex color code to an RGB tuple.

        Args:
            color (str): Hex color code, e.g., "#RRGGBB".

        Returns:
            Tuple[int, int, int]: RGB tuple.

        Raises:
            ValueError: If the hex code is invalid.
        """
        try:
            return Color.hex_to_rgb(color)
        except Exception as e:
            raise ValueError(f"Invalid color format '{color}': {e}") from e

    @staticmethod
    def gradient_print(
        *values: Any,
        input_text: str,
        end_text: Optional[str] = "",
        start_color: str,
        end_color: str,
        sep: str = " ",
        end: str = "\n",
        correct: Optional[bool] = None,
        prefix: Optional[str] = None,
    ) -> None:
        """
        Print text with a gradient in your terminal.

        Args:
            *values (Any): Values to print.
            start_color (str): Starting hex color (#RRGGBB).
            end_color (str): Ending hex color (#RRGGBB).
            sep (str, optional): Separator between values. Default is a space.
            end (str, optional): String appended after the last value. Default is a newline.
            end_text (str, optional): Text appended after the gradient.
            correct (bool, optional): Determines prefix format (True for "+", False for "-", None for "N").
            prefix (str, optional): Custom prefix for the output. Overrides `correct`.

        Raises:
            ValueError: If colors are invalid or steps are zero.
        """
        text = input_text

        start_color_rgb = GradientPrinter.validate_hex_color(start_color)
        end_color_rgb = GradientPrinter.validate_hex_color(end_color)

        steps = max(len(text) + len(end_text), 1)

        grad = GradientPrinter.gradient(start_color_rgb, end_color_rgb, steps)

        if prefix is None:
            prefix_mapping = {
                False: f"{NebulaColor.Nebula}[{NebulaColor.LIGHTBLACK}ERROR{NebulaColor.Nebula}]{NebulaColor.RESET} ",
                None: f"{NebulaColor.Nebula}[{NebulaColor.LIGHTBLACK}Nebula{NebulaColor.Nebula}]{NebulaColor.RESET} ",
                True: f"{NebulaColor.Nebula}[{NebulaColor.LIGHTBLACK}SUCCSES{NebulaColor.Nebula}]{NebulaColor.RESET} ",
            }
            prefix = prefix_mapping.get(correct, "")

        try:
            if prefix:
                sys.stdout.write(prefix)
            for i, char in enumerate(text):
                color = grad[i]
                sys.stdout.write(f"{Color.rgb_to_ansi(*color)}{char}")
            sys.stdout.write(end_text)
            sys.stdout.write(end)
        finally:
            sys.stdout.write(NebulaColor.RESET)
            sys.stdout.flush()
