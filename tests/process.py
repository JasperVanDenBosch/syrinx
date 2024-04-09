from unittest import TestCase


class ProcessorTests(TestCase):

    def test_wrap(self):
        from syrinx.postprocess import processor
        in_html = """
        <div><a></a></div>
        """
        expect_html = """
        <div><tag x="yz"><a></a></tag></div>
        """
        out_html = processor(in_html, "//a[contains(@href,'bla')]", 'tag', dict(x='xy'))
        self.assertEqual(out_html, expect_html)
