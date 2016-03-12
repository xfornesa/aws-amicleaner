import unittest2 as unittest

from resources.models import AWSTag


class ParsingModelsTest(unittest.TestCase):

    def test_get_awstag_from_none(self):
        aws_tag = AWSTag.object_with_json(None)
        self.assertEqual(aws_tag, None)


if __name__ == '__main__':
    unittest.main()
