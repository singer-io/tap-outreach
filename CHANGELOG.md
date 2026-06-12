# Changelog

# 1.3.0
  * Exclude 403-inaccessible streams from catalog during discovery [#45](https://github.com/singer-io/tap-outreach/pull/45)
  * Added `OutreachForbiddenError` exception class raised on HTTP 403 responses
  * Added unit tests for discovery access-check behaviour
  * bump requests to version 2.34.2 and singer-python to version 6.8.0

# 1.2.2
  * Bump requests to 2.33.0 for security updates [#37](https://github.com/singer-io/tap-outreach/pull/37)


## 1.2.1
  * Bump dependency versions for twistlock compliance [#40](https://github.com/singer-io/tap-outreach/pull/40)

## 1.2.0
  * Fix for error "CRITICAL Only `data` or `links` expected in relationships" [#39](https://github.com/singer-io/tap-outreach/pull/39)
  * Bump requests from 2.31.0 to 2.32.3
  * singer-python and backoff updates to 6.1.1 and 2.1.1, respectively

## 1.1.3
  * Fix refresh logic for long running pagination requests [#35](https://github.com/singer-io/tap-outreach/pull/35)

## 1.1.2
  * Add handling for new x-rate-limit-remaining structure [#33](https://github.com/singer-io/tap-outreach/pull/33)

## 1.1.1
  * Dependabot update [#26](https://github.com/singer-io/tap-outreach/pull/26)
## 1.1.0
  * Fix for attribute & generated relationship name [#32](https://github.com/singer-io/tap-outreach/pull/32)

## 1.0.0
  * Add schema changes and integration test suite [#28](https://github.com/singer-io/tap-outreach/pull/28)

## 0.9.0
  * add property - `request_timeout` to set the time limit for the API requests [#30](https://github.com/singer-io/tap-outreach/pull/30)

## 0.8.0
  * Relationship precedence over attributes for `Prospects` stream [#25](https://github.com/singer-io/tap-outreach/pull/25)

## 0.7.0
  * Add the `name` field to the `Events` stream [#13](https://github.com/singer-io/tap-outreach/pull/13)

## 0.6.0
  * Adds sequence, sequence_template, sequence_state, sequence_step tables [#11](https://github.com/singer-io/tap-outreach/pull/11)

## 0.5.0
  * Add `page_size` a config option [#7](https://github.com/singer-io/tap-outreach/pull/7)

## 0.4.0
  * Change from `offset` to `cursor` [pagination](https://api.outreach.io/api/v2/docs#pagination) in `sync.py`. Add [rate limit](https://api.outreach.io/api/v2/docs#rate-limiting) decorator to `client.py`.

## 0.3.0
  * changed readme

## 0.2.0
  * Additional Endpoints

## 0.1.0
  * First iteration
