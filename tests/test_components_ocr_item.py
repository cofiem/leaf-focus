import math

from leaf_focus.components.data.text_item import TextItem


class TestComponentsOcrItem:
    def test_create(self):
        text = "test text"
        i = TextItem(
            text=text,
            top_left_x=879,
            top_left_y=131,
            top_right_x=1016,
            top_right_y=131,
            bottom_right_x=1016,
            bottom_right_y=153,
            bottom_left_x=879,
            bottom_left_y=153,
        )

        assert i.top_length == 137
        assert i.left_length == 22

        assert i.line_bounds == (131, 153)

        assert i.slope_top_left_right == 0
        assert i.slope_top_right_left == 0
        assert i.slope_left_top_bottom == math.inf
        assert i.slope_left_bottom_top == -math.inf
        assert i.slope_bottom_left_right == 0
        assert i.slope_bottom_right_left == 0
        assert i.slope_right_top_bottom == math.inf
        assert i.slope_right_bottom_top == -math.inf

        assert i.is_horizontal_level
        assert i.is_vertical_level

        prediction = (
            text,
            (
                (i.top_left_x, i.top_left_y),
                (i.top_right_x, i.top_right_y),
                (i.bottom_right_x, i.bottom_right_y),
                (i.bottom_left_x, i.bottom_left_y),
            ),
        )
        assert TextItem.from_prediction(prediction) == i
        assert i.to_prediction == prediction
