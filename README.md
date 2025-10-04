# RSS Blog Friend: Collects recent posts from your friends' blogs

## Usage

Collect RSS post data from my friends' blogs and convert it to out-of-the-box, sort-by-nearest-date JSON data set, like this:

```json
[
  {
    "title": "Download Google font and use it in offline html",
    "link": "https://blog.ryankert.cc/2022/04/18/google-font-offline/",
    "date": "2022-08-24T17:40:53.489Z",
    "author": { "name": "Ryan's Blog", "link": "https://blog.ryankert.cc/" }
  },
  {
    "title": "將其他 blog 的文章連結到 Jeykyll blog",
    "link": "https://titaliu1224.github.io//posts/link_to_other_blog/",
    "date": "2022-08-22T17:47:35.000Z",
    "author": {
      "name": "tita's Blog",
      "link": "https://titsliu1224.github.io/"
    }
  },
]
```
*having a maximum display posts of 30

## Auto Update

at (UTC) 10:00 and 22:00

at (UTC+8) 6:00 and 18:00

## How to use it

1. Fork this repository

2. install your friends' rss pages into this file (`./_data/friends.json`), in this format:

```json
[
    {
        "title": "Ryan's Blog",
        "link": "https://blog.ryankert.cc/",
        "feed": "https://blog.ryankert.cc/atom.xml"
    },
    ...
]
```

3. Until it generate file sussessfully, it will generate a new branch automatically. Then, you setup your github page to display the branch `gh-pages`.

It will be display at `https://<github-username>.github.io/rss-friend/<file>`.

There are three file generated

```
rss.json       // sorted json year, month, day
sorted.json    // sorted json universal date ex:2022-08-22T17:47:35.000Z
unsort.json    // unsort raw data
```

> **Warning**
> You have to manually enable github action, which forked repositories disabled by default.

APIs:

https://ryankert01.github.io/rss-friend/rss.json

https://ryankert01.github.io/rss-friend/sorted.json

https://ryankert01.github.io/rss-friend/unsort.json


## Development: (dev)

### To install dependencies

```zsh
pip install -r requirements.txt
```

### To generate JSON file

run the script to generate JSON file
```zsh
python src/main.py
```
