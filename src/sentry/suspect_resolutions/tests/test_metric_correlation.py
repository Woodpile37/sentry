from unittest import mock

from django.utils import timezone

from sentry.models import GroupStatus
from sentry.suspect_resolutions.metric_correlation import is_issue_error_rate_correlated
from sentry.testutils import TestCase


class TestMetricCorrelation(TestCase):
    @mock.patch("sentry.tsdb.get_range")
    def test_correlated_issues(self, mock_get_range):
        group1 = self.create_group(status=GroupStatus.RESOLVED, resolved_at=timezone.now())
        group2 = self.create_group()

        mock_get_range.return_value = {
            group1.id: [
                (1656393120, 4),
                (1656393180, 2),
                (1656393240, 2),
                (1656393300, 1),
                (1656393360, 3),
                (1656393420, 2),
                (1656393480, 0),
                (1656393540, 3),
                (1656393600, 0),
                (1656393660, 0),
                (1656393720, 0),
                (1656393780, 0),
                (1656393840, 0),
                (1656393900, 0),
                (1656393960, 0),
                (1656394020, 0),
                (1656394080, 0),
                (1656394140, 0),
                (1656394200, 0),
                (1656394260, 0),
                (1656394320, 0),
                (1656394380, 0),
                (1656394440, 0),
                (1656394500, 0),
                (1656394560, 0),
                (1656394620, 0),
                (1656394680, 0),
                (1656394740, 0),
                (1656394800, 0),
                (1656394860, 0),
                (1656394920, 0),
                (1656394980, 0),
                (1656395040, 0),
                (1656395100, 0),
                (1656395160, 0),
                (1656395220, 0),
                (1656395280, 0),
                (1656395340, 0),
                (1656395400, 0),
                (1656395460, 0),
                (1656395520, 0),
                (1656395580, 0),
                (1656395640, 0),
                (1656395700, 0),
                (1656395760, 0),
                (1656395820, 0),
                (1656395880, 0),
                (1656395940, 0),
                (1656396000, 0),
                (1656396060, 0),
                (1656396120, 0),
                (1656396180, 0),
                (1656396240, 0),
                (1656396300, 0),
                (1656396360, 0),
                (1656396420, 0),
                (1656396480, 0),
                (1656396540, 0),
                (1656396600, 0),
                (1656396660, 0),
                (1656396720, 0),
            ],
            group2.id: [
                (1656393120, 17),
                (1656393180, 17),
                (1656393240, 15),
                (1656393300, 16),
                (1656393360, 16),
                (1656393420, 14),
                (1656393480, 13),
                (1656393540, 19),
                (1656393600, 13),
                (1656393660, 0),
                (1656393720, 0),
                (1656393780, 0),
                (1656393840, 0),
                (1656393900, 0),
                (1656393960, 0),
                (1656394020, 0),
                (1656394080, 0),
                (1656394140, 0),
                (1656394200, 0),
                (1656394260, 0),
                (1656394320, 0),
                (1656394380, 0),
                (1656394440, 0),
                (1656394500, 0),
                (1656394560, 0),
                (1656394620, 0),
                (1656394680, 0),
                (1656394740, 0),
                (1656394800, 0),
                (1656394860, 0),
                (1656394920, 0),
                (1656394980, 0),
                (1656395040, 0),
                (1656395100, 0),
                (1656395160, 0),
                (1656395220, 0),
                (1656395280, 0),
                (1656395340, 0),
                (1656395400, 0),
                (1656395460, 0),
                (1656395520, 0),
                (1656395580, 0),
                (1656395640, 0),
                (1656395700, 0),
                (1656395760, 0),
                (1656395820, 0),
                (1656395880, 0),
                (1656395940, 0),
                (1656396000, 0),
                (1656396060, 0),
                (1656396120, 0),
                (1656396180, 0),
                (1656396240, 0),
                (1656396300, 0),
                (1656396360, 0),
                (1656396420, 0),
                (1656396480, 0),
                (1656396540, 0),
                (1656396600, 0),
                (1656396660, 0),
                (1656396720, 0),
            ],
        }

        assert is_issue_error_rate_correlated(group1.id, group2.id)

    @mock.patch("sentry.tsdb.get_range")
    def test_uncorrelated_issues(self, mock_get_range):
        group1 = self.create_group(status=GroupStatus.RESOLVED, resolved_at=timezone.now())
        group2 = self.create_group()

        mock_get_range.return_value = {
            group1.id: [
                (1656393120, 4),
                (1656393180, 2),
                (1656393240, 2),
                (1656393300, 1),
                (1656393360, 3),
                (1656393420, 2),
                (1656393480, 0),
                (1656393540, 3),
                (1656393600, 8),
                (1656393660, 0),
                (1656393720, 0),
                (1656393780, 0),
                (1656393840, 0),
                (1656393900, 0),
                (1656393960, 0),
                (1656394020, 4),
                (1656394080, 26),
                (1656394140, 0),
                (1656394200, 0),
                (1656394260, 0),
                (1656394320, 0),
                (1656394380, 0),
                (1656394440, 0),
                (1656394500, 0),
                (1656394560, 0),
                (1656394620, 0),
                (1656394680, 13),
                (1656394740, 0),
                (1656394800, 11),
                (1656394860, 0),
                (1656394920, 0),
                (1656394980, 0),
                (1656395040, 6),
                (1656395100, 0),
                (1656395160, 0),
                (1656395220, 0),
                (1656395280, 0),
                (1656395340, 0),
                (1656395400, 0),
                (1656395460, 0),
                (1656395520, 0),
                (1656395580, 0),
                (1656395640, 13),
                (1656395700, 0),
                (1656395760, 0),
                (1656395820, 22),
                (1656395880, 0),
                (1656395940, 0),
                (1656396000, 0),
                (1656396060, 27),
                (1656396120, 0),
                (1656396180, 0),
                (1656396240, 0),
                (1656396300, 0),
                (1656396360, 0),
                (1656396420, 88),
                (1656396480, 54),
                (1656396540, 32),
                (1656396600, 11),
                (1656396660, 30),
                (1656396720, 0),
            ],
            group2.id: [
                (1656393120, 17),
                (1656393180, 17),
                (1656393240, 1),
                (1656393300, 16),
                (1656393360, 16),
                (1656393420, 14),
                (1656393480, 13),
                (1656393540, 19),
                (1656393600, 13),
                (1656393660, 0),
                (1656393720, 0),
                (1656393780, 0),
                (1656393840, 0),
                (1656393900, 0),
                (1656393960, 0),
                (1656394020, 0),
                (1656394080, 0),
                (1656394140, 0),
                (1656394200, 85),
                (1656394260, 0),
                (1656394320, 0),
                (1656394380, 0),
                (1656394440, 0),
                (1656394500, 0),
                (1656394560, 0),
                (1656394620, 3),
                (1656394680, 0),
                (1656394740, 0),
                (1656394800, 0),
                (1656394860, 0),
                (1656394920, 0),
                (1656394980, 10),
                (1656395040, 0),
                (1656395100, 0),
                (1656395160, 0),
                (1656395220, 0),
                (1656395280, 0),
                (1656395340, 0),
                (1656395400, 0),
                (1656395460, 0),
                (1656395520, 0),
                (1656395580, 0),
                (1656395640, 10),
                (1656395700, 0),
                (1656395760, 0),
                (1656395820, 0),
                (1656395880, 0),
                (1656395940, 38),
                (1656396000, 0),
                (1656396060, 0),
                (1656396120, 0),
                (1656396180, 0),
                (1656396240, 0),
                (1656396300, 0),
                (1656396360, 0),
                (1656396420, 0),
                (1656396480, 0),
                (1656396540, 0),
                (1656396600, 0),
                (1656396660, 0),
                (1656396720, 0),
            ],
        }

        assert not is_issue_error_rate_correlated(group1.id, group2.id)
