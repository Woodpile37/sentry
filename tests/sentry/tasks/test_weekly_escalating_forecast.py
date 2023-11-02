from datetime import datetime, timezone
from typing import List
from unittest.mock import MagicMock, patch

from sentry.issues.escalating_group_forecast import ONE_EVENT_FORECAST, EscalatingGroupForecast
from sentry.issues.grouptype import (
    ErrorGroupType,
    PerformanceDurationRegressionGroupType,
    PerformanceSlowDBQueryGroupType,
)
from sentry.models.group import Group, GroupStatus
from sentry.tasks.weekly_escalating_forecast import run_escalating_forecast
from sentry.testutils.cases import APITestCase, SnubaTestCase
from sentry.testutils.helpers.features import with_feature
from sentry.types.group import GroupSubStatus
from tests.sentry.issues.test_utils import get_mock_groups_past_counts_response


class TestWeeklyEscalatingForecast(APITestCase, SnubaTestCase):
    def create_archived_until_escalating_groups(
        self, num_groups: int, group_type: int
    ) -> List[Group]:
        group_list = []
        project_1 = self.project
        for i in range(num_groups):
            group = self.create_group(project=project_1, type=group_type)
            group.status = GroupStatus.IGNORED
            group.substatus = GroupSubStatus.UNTIL_ESCALATING
            group.save()
            group_list.append(group)
        return group_list

    @patch("sentry.issues.forecasts.generate_and_save_missing_forecasts.delay")
    @patch("sentry.issues.escalating.query_groups_past_counts")
    def empty_escalating_forecast(
        self,
        mock_query_groups_past_counts: MagicMock,
        mock_generate_and_save_missing_forecasts: MagicMock,
        group_type: int = ErrorGroupType.type_id,
    ) -> None:
        """
        Test that when fetch is called and the issue has no forecast, the forecast for one
        event/hr is returned, and the forecast is regenerated.
        """
        with self.tasks():
            group_list = self.create_archived_until_escalating_groups(
                num_groups=1, group_type=group_type
            )

            mock_query_groups_past_counts.return_value = {}

            run_escalating_forecast()
            group = group_list[0]
            fetched_forecast = EscalatingGroupForecast.fetch(group.project.id, group.id)
            assert fetched_forecast and fetched_forecast.forecast == ONE_EVENT_FORECAST
        assert mock_generate_and_save_missing_forecasts.call_count == 1

    def test_empty_escalating_forecasts(self):
        self.empty_escalating_forecast()
        self.empty_escalating_forecast(group_type=PerformanceSlowDBQueryGroupType.type_id)
        self.empty_escalating_forecast(group_type=PerformanceDurationRegressionGroupType.type_id)

    @with_feature("organizations:issue-platform-api-crons-sd")
    def test_empty_escalating_forecasts_ff_on(self):
        self.empty_escalating_forecast()
        self.empty_escalating_forecast(group_type=PerformanceSlowDBQueryGroupType.type_id)
        self.empty_escalating_forecast(group_type=PerformanceDurationRegressionGroupType.type_id)

    @patch("sentry.analytics.record")
    @patch("sentry.issues.forecasts.query_groups_past_counts")
    def single_group_escalating_forecast(
        self,
        mock_query_groups_past_counts: MagicMock,
        record_mock: MagicMock,
        group_type: int = ErrorGroupType.type_id,
    ) -> None:
        with self.tasks():
            group_list = self.create_archived_until_escalating_groups(
                num_groups=1, group_type=group_type
            )

            mock_query_groups_past_counts.return_value = get_mock_groups_past_counts_response(
                num_days=7, num_hours=1, groups=group_list
            )

            run_escalating_forecast()
            approximate_date_added = datetime.now(timezone.utc)
            fetched_forecast = EscalatingGroupForecast.fetch(
                group_list[0].project.id, group_list[0].id
            )
            assert fetched_forecast is not None
            assert fetched_forecast.project_id == group_list[0].project.id
            assert fetched_forecast.group_id == group_list[0].id
            assert fetched_forecast.forecast == [100] * 14
            assert fetched_forecast.date_added.replace(
                second=0, microsecond=0
            ) == approximate_date_added.replace(second=0, microsecond=0)
            assert fetched_forecast.date_added < approximate_date_added
            record_mock.assert_called_with("issue_forecasts.saved", num_groups=1)

    def test_single_group_escalating_forecasts(self):
        self.single_group_escalating_forecast()
        self.single_group_escalating_forecast(group_type=PerformanceSlowDBQueryGroupType.type_id)
        self.single_group_escalating_forecast(
            group_type=PerformanceDurationRegressionGroupType.type_id
        )

    @with_feature("organizations:issue-platform-api-crons-sd")
    def test_single_group_escalating_forecasts_ff_on(self):
        self.single_group_escalating_forecast()
        self.single_group_escalating_forecast(group_type=PerformanceSlowDBQueryGroupType.type_id)
        # Not ready yet
        # self.single_group_escalating_forecast(
        #     group_type=PerformanceDurationRegressionGroupType.type_id
        # )

    @patch("sentry.analytics.record")
    @patch("sentry.issues.forecasts.query_groups_past_counts")
    def multiple_groups_escalating_forecast(
        self,
        mock_query_groups_past_counts: MagicMock,
        record_mock: MagicMock,
        group_type: int = ErrorGroupType.type_id,
    ) -> None:
        with self.tasks():
            group_list = self.create_archived_until_escalating_groups(
                num_groups=3, group_type=group_type
            )

            mock_query_groups_past_counts.return_value = get_mock_groups_past_counts_response(
                num_days=7, num_hours=23, groups=group_list
            )

            run_escalating_forecast()
            approximate_date_added = datetime.now(timezone.utc)
            for i in range(len(group_list)):
                fetched_forecast = EscalatingGroupForecast.fetch(
                    group_list[i].project.id, group_list[i].id
                )
                assert fetched_forecast is not None
                assert fetched_forecast.project_id == group_list[i].project.id
                assert fetched_forecast.group_id == group_list[i].id
                assert fetched_forecast.forecast == [100] * 14
                assert fetched_forecast.date_added.replace(
                    second=0, microsecond=0
                ) == approximate_date_added.replace(second=0, microsecond=0)
                assert fetched_forecast.date_added < approximate_date_added
                record_mock.assert_called_with("issue_forecasts.saved", num_groups=3)

    def test_multiple_groups_escalating_forecasts(self):
        self.multiple_groups_escalating_forecast()
        self.multiple_groups_escalating_forecast(group_type=PerformanceSlowDBQueryGroupType.type_id)
        self.multiple_groups_escalating_forecast(
            group_type=PerformanceDurationRegressionGroupType.type_id
        )

    @with_feature("organizations:issue-platform-api-crons-sd")
    def test_multiple_groups_escalating_forecasts_ff_on(self):
        self.multiple_groups_escalating_forecast()
        self.multiple_groups_escalating_forecast(group_type=PerformanceSlowDBQueryGroupType.type_id)
        # Not ready yet
        # self.multiple_groups_escalating_forecast(
        #     group_type=PerformanceDurationRegressionGroupType.type_id
        # )

    @patch("sentry.analytics.record")
    @patch("sentry.issues.forecasts.query_groups_past_counts")
    def update_group_escalating_forecast(
        self,
        mock_query_groups_past_counts: MagicMock,
        record_mock: MagicMock,
        group_type: int = ErrorGroupType.type_id,
    ) -> None:
        with self.tasks():
            group_list = self.create_archived_until_escalating_groups(
                num_groups=1, group_type=group_type
            )

            mock_query_groups_past_counts.return_value = get_mock_groups_past_counts_response(
                num_days=7, num_hours=2, groups=group_list
            )

            run_escalating_forecast()
            first_fetched_forecast = EscalatingGroupForecast.fetch(
                group_list[0].project.id, group_list[0].id
            )

            # Assert update when this is run twice
            run_escalating_forecast()
            second_fetched_forecast = EscalatingGroupForecast.fetch(
                group_list[0].project.id, group_list[0].id
            )
            assert first_fetched_forecast is not None
            assert second_fetched_forecast is not None
            assert first_fetched_forecast.date_added < second_fetched_forecast.date_added
            record_mock.assert_called_with("issue_forecasts.saved", num_groups=1)

    def test_update_group_escalating_forecasts(self):
        self.update_group_escalating_forecast()
        self.update_group_escalating_forecast(group_type=PerformanceSlowDBQueryGroupType.type_id)
        self.update_group_escalating_forecast(
            group_type=PerformanceDurationRegressionGroupType.type_id
        )

    @with_feature("organizations:issue-platform-api-crons-sd")
    def testupdate_group_escalating_forecasts_ff_on(self):
        self.update_group_escalating_forecast()
        self.update_group_escalating_forecast(group_type=PerformanceSlowDBQueryGroupType.type_id)
        # Not ready yet
        # self.update_group_escalating_forecast(
        #     group_type=PerformanceDurationRegressionGroupType.type_id
        # )
