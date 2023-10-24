# tap-outreach

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md#singer-specification).

This tap:

- Pulls raw data from Outreach API
- Outputs the schema for each resource
- Incrementally pulls data based on the input state


## Streams

[accounts](https://api.outreach.io/api/v2/docs#account)

[call_dispositions](https://api.outreach.io/api/v2/docs#callDisposition)

[call_purposes](https://api.outreach.io/api/v2/docs#callPurpose)

[calls](https://api.outreach.io/api/v2/docs#call)

[content_categories](https://api.outreach.io/api/v2/docs#contentCategory)

[duties](https://api.outreach.io/api/v2/docs#duty)

[events](https://api.outreach.io/api/v2/docs#event)

[mailboxes](https://api.outreach.io/api/v2/docs#mailbox)

[mailings](https://api.outreach.io/api/v2/docs#mailing)

[opportunities](https://api.outreach.io/api/v2/docs#opportunity)

[personas](https://api.outreach.io/api/v2/docs#persona)

[prospects](https://api.outreach.io/api/v2/docs#prospect)

[stages](https://api.outreach.io/api/v2/docs#stage)

[tasks](https://api.outreach.io/api/v2/docs#task)

[teams](https://api.outreach.io/api/v2/docs#team)

[users](https://api.outreach.io/api/v2/docs#user)




## Quick Start

1. Install

    Clone this repository, and then install using setup.py. We recommend using a virtualenv:

    ```bash
    > virtualenv -p python3 venv
    > source venv/bin/activate
    > python setup.py install
    OR
    > cd .../tap-outreach
    > pip install .
    ```

2. Here is what the config should look like

    ```json
    {
        "start_date": "2019-01-01T00:00:00Z",
        "client_id": <CLIENT_ID>,
        "client_secret": <CLIENT_SECRET>,
        "redirect_uri": <REDIRECT_URI>,
        "refresh_token": <REFRESH_TOKEN>,
        "quota_limit": <QUOTA_LIMIT>,
        "page_size": <PAGE_SIZE>,
        "request_timeout": 300
    }
    ```
    The following are required values: `start_date`, `client_id`, `client_secret`, `redirect_uri`, `refresh_token`
    The following are optional values: `quota_limit`, `page_size`

    Optionally, also create a `state.json` file. `currently_syncing` is an optional attribute used for identifying the last object to be synced in case the job is interrupted mid-stream. The next run would begin where the last job left off.

    ```json
      {
        "bookmarks": {
          "stream_1": "2020-01-04T00:00:00.000000Z",
          "stream_2": 1576266090,
          ...
        }
      }
    ```

3. Run the Tap in Discovery Mode
    This creates a catalog.json for selecting objects/fields to integrate:
    ```bash
    tap-outreach --config config.json --discover > catalog.json
    ```
   See the Singer docs on discovery mode
   [here](https://github.com/singer-io/getting-started/blob/master/docs/DISCOVERY_MODE.md#discovery-mode).

4. Run the Tap in Sync Mode (with catalog) and [write out to state file](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#running-a-singer-tap-with-a-singer-target)

    For Sync mode:
    ```bash
    > tap-outreach --config config.json --catalog catalog.json > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    To load to json files to verify outputs:
    ```bash
    > tap-outreach --config config.json --catalog catalog.json | target-json > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    To pseudo-load to [Stitch Import API](https://github.com/singer-io/target-stitch) with dry run:
    ```bash
    > tap-outreach --config config.json --catalog catalog.json | target-stitch --config target_config.json --dry-run > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```

5. Test the Tap
    
    While developing the Outreach tap, the following utilities were run in accordance with Singer.io best practices:
    Pylint to improve [code quality](https://github.com/singer-io/getting-started/blob/master/docs/BEST_PRACTICES.md#code-quality):
    ```bash
    > pylint tap_outreach -d broad-except,chained-comparison,empty-docstring,fixme,invalid-name,line-too-long,missing-class-docstring,missing-function-docstring,missing-module-docstring,no-else-raise,no-else-return,too-few-public-methods,too-many-arguments,too-many-branches,too-many-lines,too-many-locals,ungrouped-imports,wrong-spelling-in-comment,wrong-spelling-in-docstring
    ```
    The pylint disables that Stitch uses are:
    ```
    broad-except,chained-comparison,empty-docstring,fixme,invalid-name,line-too-long,missing-class-docstring,missing-function-docstring,missing-module-docstring,no-else-raise,no-else-return,too-few-public-methods,too-many-arguments,too-many-branches,too-many-lines,too-many-locals,ungrouped-imports,wrong-spelling-in-comment,wrong-spelling-in-docstring
    ```


    To [check the tap](https://github.com/singer-io/singer-tools#singer-check-tap), install singer-check-tap and verify working:
    ```bash
    > tap-outreach --config config.json --catalog catalog.json | singer-check-tap > state.json
    > tail -1 state.json > state.json.tmp && mv state.json.tmp state.json
    ```
    Check tap resulted in the following:
    ```bash
    The output is valid.
    It contained 8240 messages for 16 streams.

        16 schema messages
    8108 record messages
        116 state messages

    Details by stream:
    +-----------------------------+---------+---------+
    | stream                      | records | schemas |
    +-----------------------------+---------+---------+
    | **ENDPOINT_A**              | 23      | 1       |
    +-----------------------------+---------+---------+
    ```
---

Copyright &copy; 2020 Stitch
