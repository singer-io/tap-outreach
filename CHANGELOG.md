# Changelog

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
