from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class SmarterPaginator(Paginator):
    def __init__(self, spread=2, current_page=None, *args, **kwargs):
        super(SmarterPaginator, self).__init__(*args, **kwargs)
        self.spread = spread
        try:
            self.current_page = self.page(current_page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            self.current_page = self.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of
            # results.
            self.current_page = self.page(self.num_pages)

    @staticmethod
    def _page_range_with_ellipses(page_range, current, spread, num_pages):
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
        return slices
        # return tuple(page_range.__getslice__(*s) for s in slices)

    def page_range_with_ellipses(self):
        return self._page_range_with_ellipses(
            page_range=self.page_range,
            # Get it into zero-index space:
            current=self.current_page.number - 1,
            spread=self.spread,
            num_pages=self.num_pages,
        )
