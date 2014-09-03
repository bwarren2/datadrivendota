from django.test import TestCase


class SmarterPaginatorTestCase(TestCase):
    """
    This test is dodgy and doesn't test the real class, just a similar
    implementation. Fix it at some point.
    """

    def page_range_with_ellipses(self, page_range, current):
        spread = 2
        num_pages = len(page_range)

        top_range = (
            0,
            min(num_pages, 0 + spread) + 1
        )
        middle_range = (
            max(0, current - spread),
            min(num_pages, current + spread) + 1
        )
        bottom_range = (
            max(0, num_pages - (spread + 1)),
            num_pages
        )

        if middle_range[0] - top_range[1] < 1:
            # join them.
            middle_range = (top_range[0], middle_range[1])
            top_range = None

        if bottom_range[0] - middle_range[1] < 1:
            # join them.
            bottom_range = (middle_range[0], bottom_range[1])
            middle_range = None

        slices = [
            x for x in
            [top_range, middle_range, bottom_range]
            if x is not None
        ]

        return tuple(page_range.__getslice__(*s) for s in slices)

    def validate(self, rng, current, expected):
        error = "Saw {}, expected {}".format(
            self.page_range_with_ellipses(rng, current),
            expected
        )
        self.assertEqual(
            self.page_range_with_ellipses(rng, current),
            expected,
            msg=error
        )

    def test_permutations(self):
        self.validate(
            [0],
            0,
            ([0],)
        )

        self.validate(
            [0, 1],
            0,
            ([0, 1],)
        )

        self.validate(
            [0, 1, 2, 3, 4],
            0,
            ([0, 1, 2, 3, 4],)
        )

        self.validate(
            [0, 1, 2, 3, 4],
            1,
            ([0, 1, 2, 3, 4],)
        )

        self.validate(
            [0, 1, 2, 3, 4],
            2,
            ([0, 1, 2, 3, 4],)
        )

        self.validate(
            [0, 1, 2, 3, 4],
            3,
            ([0, 1, 2, 3, 4],)
        )

        self.validate(
            [0, 1, 2, 3, 4],
            4,
            ([0, 1, 2, 3, 4],)
        )

        self.validate(
            [0, 1, 2, 3, 4, 5, 6, 7],
            1,
            ([0, 1, 2, 3], [5, 6, 7])
        )

        self.validate(
            [0, 1, 2, 3, 4, 5, 6, 7],
            2,
            ([0, 1, 2, 3, 4, 5, 6, 7],)
        )

        self.validate(
            [0, 1, 2, 3, 4, 5, 6, 7],
            5,
            ([0, 1, 2, 3, 4, 5, 6, 7],)
        )

        self.validate(
            [0, 1, 2, 3, 4, 5, 6, 7],
            6,
            ([0, 1, 2], [4, 5, 6, 7])
        )

        self.validate(
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            5,
            ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],)
        )

        self.validate(
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            6,
            ([0, 1, 2], [4, 5, 6, 7, 8], [10, 11, 12])
        )
