from resources.models import AWSTag


def test_get_awstag_from_none():
    aws_tag = AWSTag.object_with_json(None)
    assert aws_tag is None
