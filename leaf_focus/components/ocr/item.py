import csv
import dataclasses
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Any


@dataclass
class Item:
    """One found text item (could be a word or phrase) in an image."""

    text: str
    """The recognised text."""

    top_left_x: float
    top_left_y: float

    top_right_x: float
    top_right_y: float

    bottom_right_x: float
    bottom_right_y: float

    bottom_left_x: float
    bottom_left_y: float

    line_number: Optional[int] = None
    line_order: Optional[int] = None

    @property
    def top_left(self):
        """The top left point."""
        return self.top_left_x, self.top_left_y

    @property
    def top_right(self):
        """The top right point."""
        return self.top_right_x, self.top_right_y

    @property
    def bottom_right(self):
        """The bottom right point."""
        return self.bottom_right_x, self.bottom_right_y

    @property
    def bottom_left(self):
        """The bottom left point."""
        return self.bottom_left_x, self.bottom_left_y

    @property
    def top_length(self):
        # Get the length of the hypotenuse side.
        side1 = abs(self.top_right_x - self.top_left_x)
        side2 = abs(self.top_right_y - self.top_left_y)
        if side2 == 0:
            return side1
        return math.sqrt(pow(side1, 2) + pow(side2, 2))

    @property
    def left_length(self):
        # Get the length of the hypotenuse side.
        side1 = abs(self.top_left_y - self.bottom_left_y)
        side2 = abs(self.top_left_x - self.bottom_left_x)
        if side2 == 0:
            return side1
        return math.sqrt(pow(side1, 2) + pow(side2, 2))

    @property
    def line_bounds(self):
        """Line bounds from top of text to bottom of text."""
        top_bound = min(
            [self.top_left_y, self.top_right_y, self.bottom_left_y, self.bottom_right_y]
        )
        bottom_bound = max(
            [self.top_left_y, self.top_right_y, self.bottom_left_y, self.bottom_right_y]
        )
        return top_bound, bottom_bound

    def is_same_line(self, other: "Item"):
        """
        Check if other found text overlaps this found text.
        Calculated as the midpoint +- 1/3 of the height of the text
        """
        if not other:
            return False
        self_bounds = self.line_bounds
        self_top = self_bounds[0]
        self_bottom = self_bounds[1]
        self_third = (self_bottom - self_top) / 3
        self_top += self_third
        self_bottom -= self_third

        other_bounds = other.line_bounds
        other_top = other_bounds[0]
        other_bottom = other_bounds[1]
        other_third = (other_bottom - other_top) / 3
        other_top += other_third
        other_bottom -= other_third

        return self_top <= other_bottom and other_top <= self_bottom

    @property
    def top_slope(self):
        """The slope of the top of the rectangle."""
        return self._slope(
            self.top_left_x, self.top_right_x, self.top_left_y, self.top_right_y
        )

    @property
    def left_slope(self):
        """The slope of the left of the rectangle."""
        return self._slope(
            self.top_left_x, self.bottom_left_x, self.top_left_y, self.bottom_left_y
        )

    @property
    def bottom_slope(self):
        """The slope of the bottom of the rectangle."""
        return self._slope(
            self.bottom_right_y,
            self.bottom_left_y,
            self.bottom_right_x,
            self.bottom_left_x,
        )

    @property
    def right_slope(self):
        """The slope of the right of the rectangle."""
        return self._slope(
            self.top_right_y, self.bottom_right_y, self.top_right_x, self.bottom_right_x
        )

    def _slope(self, x1, x2, y1, y2):
        return (y2 - y1) / (x2 - x1 + 0.000001)

    @property
    def is_top_horizontal(self):
        """Is the top approximately horizontal?"""
        # -0.1 -> 0.1 is strictly horizontal
        # give a bit of buffer
        return -0.2 <= self.top_slope <= 0.2

    def is_left_vertical(self):
        return False

    @classmethod
    def save(cls, path: Path, items: list["Item"]):
        """Save found text items to a file."""
        logger = logging.getLogger(cls.__name__)
        logger.info(f"Saving {len(items)} OCR items to '{path}'.")

        fields = [
            "text",
            "line_number",
            "line_order",
            "top_left_x",
            "top_left_y",
            "top_right_x",
            "top_right_y",
            "bottom_right_x",
            "bottom_right_y",
            "bottom_left_x",
            "bottom_left_y",
        ]
        with open(path, "wt", newline="", encoding="utf8") as f:
            writer = csv.DictWriter(f, fields)
            writer.writeheader()
            sorted_items = sorted(
                items, key=lambda i: (i.line_number or 0, i.line_order or 0)
            )
            writer.writerows([dataclasses.asdict(i) for i in sorted_items])

        logger.info(f"Saved OCR items to '{path}'.")

    @classmethod
    def load(cls, path: Path):
        """Load found text items from a file."""
        logger = logging.getLogger(cls.__name__)
        logger.info(f"Loading OCR items from '{path}'.")
        count = 0

        with open(path, "rt", encoding="utf8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                line_number = row.get("line_number", "").strip()
                line_number = int(line_number) if line_number != "" else None

                line_order = row.get("line_order", "").strip()
                line_order = int(line_order) if line_order != "" else None

                count += 1

                yield Item(
                    text=row["text"],
                    line_number=line_number,
                    line_order=line_order,
                    top_left_x=float(row["top_left_x"]),
                    top_left_y=float(row["top_left_y"]),
                    top_right_x=float(row["top_right_x"]),
                    top_right_y=float(row["top_right_y"]),
                    bottom_right_x=float(row["bottom_right_x"]),
                    bottom_right_y=float(row["bottom_right_y"]),
                    bottom_left_x=float(row["bottom_left_x"]),
                    bottom_left_y=float(row["bottom_left_y"]),
                )

        logger.info(f"Loaded {count} OCR items from '{path}'.")

    @classmethod
    def from_prediction(cls, prediction: tuple[Any, Any]):
        """
        Convert from (text, box) to item.
        Box is (top left, top right, bottom right, bottom left).
        Its structure is [[startX,startY], [endX,startY], [endX,endY], [startX, endY]].
        """
        text, (
            (top_left_x, top_left_y),
            (top_right_x, top_right_y),
            (bottom_right_x, bottom_right_y),
            (bottom_left_x, bottom_left_y),
        ) = prediction
        return Item(
            text=text,
            top_left_x=top_left_x,
            top_left_y=top_left_y,
            top_right_x=top_right_x,
            top_right_y=top_right_y,
            bottom_right_x=bottom_right_x,
            bottom_right_y=bottom_right_y,
            bottom_left_x=bottom_left_x,
            bottom_left_y=bottom_left_y,
        )

    def to_prediction(self):
        return (
            self.text,
            (
                (self.top_left_x, self.top_left_y),
                (self.top_right_x, self.top_right_y),
                (self.bottom_right_x, self.bottom_right_y),
                (self.bottom_left_x, self.bottom_left_y),
            ),
        )

    def __str__(self):
        line_info = f"({self.line_number or 0}:{self.line_order})"
        pos_info = f"[top left:{self.top_left}, top slope: {self.top_slope}]"
        return f"{self.text} {line_info} {pos_info}"
