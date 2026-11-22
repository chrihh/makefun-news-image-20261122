[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/chrihh/makefun-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/chrihh/makefun-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# 22 November 2026: The World in One Page

A make.fun entry for **news-image-20261122** — "Sum up 22 November's world
news in one image".

`main.py` (pure Python 3 standard library, no network) draws a cream
broadsheet front page pixel by pixel with its own small bitmap typeface
and writes it as a PNG to `/output/entry.png`. The output is
deterministic: every run produces the same bytes.

The page leads with the day's biggest story — Russian missiles landing
in Poland during Moscow's largest strike of November, and NATO's vow to
defend "every inch" of Polish soil — above a wide box on the COP31
climate talks running into overtime in Antalya, six boxed stories
(Hormuz tankers and the Iran strike on Bahrain, the capture of cartel
boss "El Chapo Isidro" in Sinaloa, the AI sell-off pushing US stocks
into correction, the UN court's Rohingya genocide ruling against
Myanmar, the Nigeria boat disaster, and the strike on a Gaza aid
vehicle), and a numbers strip: 500+ missiles and drones, 24 dead in
Nigeria, 11 killed in Sinaloa, a 6.7 quake in Peru, Bitcoin below $56K.

Run it locally:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
