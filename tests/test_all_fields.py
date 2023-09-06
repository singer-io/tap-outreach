from tap_tester.base_suite_tests.all_fields_test import AllFieldsTest
from base import OutreachBase


class OutreachAllFieldsTest(AllFieldsTest, OutreachBase):
    """Test that with no fields selected for a stream automatic fields are still replicated"""

    @staticmethod
    def name():
        return "tt_outreach_all_fields_test"

    def streams_to_test(self):
        streams_to_exclude = {'mailings', 'events'}
        return self.expected_stream_names().difference(streams_to_exclude)

    # Overriding test_all_fields_for_streams_are_replicated() method from AllFieldsTest
    def test_all_fields_for_streams_are_replicated(self):
        # Skipping fields as per the stream for which there is no data available
        MISSING_FIELDS = {
            'sequence_templates': {'negaitveReplyCount'},
            'tasks': {'taskThemeId'},
            'mailings': {
                'followUpTaskScheduledAt',
                'references',
                'openCount',
                'errorReason',
                'trackOpens',
                'subject',
                'templateId',
                'bodyText',
                'repliedAt',
                'notifyThreadCondition',
                'markedAsSpamAt',
                'notifyThreadScheduledAt',
                'overrideSafetySettings',
                'taskId',
                'openedAt',
                'bouncedAt',
                'id',
                'notifyThreadStatus',
                'followUpTaskType',
                'scheduledAt',
                'retryAt',
                'stateChangedAt',
                'retryInterval',
                'sequenceStateId',
                'opportunityId',
                'state',
                'createdAt',
                'messageId',
                'clickedAt',
                'userId',
                'errorBacktrace',
                'trackLinks',
                'retryCount',
                'deliveredAt',
                'followUpSequenceId',
                'clickCount',
                'prospectId',
                'unsubscribedAt',
                'mailingType',
                'sequenceStepId',
                'updatedAt',
                'sequenceId',
                'bodyHtml',
                'mailboxAddress',
                'mailboxId',
            }
        }
        for stream in self.streams_to_test():
            with self.subTest(stream=stream):
                # gather expectations
                expected_all_keys = self.selected_fields.get(stream, set()) - MISSING_FIELDS.get(stream, set())

                # gather results
                fields_replicated = self.actual_fields.get(stream, set())

                # verify that all fields are sent to the target
                # test the combination of all records
                self.assertSetEqual(fields_replicated, expected_all_keys,
                                    logging=f"verify all fields are replicated for stream {stream}")
