from datetime import datetime, timezone
from django.conf import settings
import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def rank(feed_instance, user):
    date = feed_instance["gapt"].date

    # if feed_instance["type"] == 1:
    #     date = feed_instance["gapt"].date
    # else:
    #     date = feed_instance["reGaptLog"].date

    date_diff = datetime.now(tz=timezone.utc) - date                # (days, seconds)

    recency = date_diff.days + (date_diff.seconds / 86400)
    recency = sigmoid(recency)

    likes_count = feed_instance["gapt"].getLikesCount()
    likes_count = sigmoid(likes_count)

    reGapts_count = feed_instance["gapt"].getReGaptsCount()
    reGapts_count = sigmoid(reGapts_count)

    type = feed_instance["type"]

    seen = 1 if feed_instance["gapt"].isSeenBy(user) else 0

    rank = (
        - 0.15 * recency
        + 0.55 * likes_count
        + 0.55 * reGapts_count
        + 0.15 * type
        - 0.1  * seen
    )

    # print(f'#{feed_instance["gapt"].id}: {rank}')

    return rank
