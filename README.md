# rss-friend: Collects RSS data from my friends' blog

## Usage

Collect RSS data from my friends' blog and convert it to sort-by-date JSON data set, like this:

```json
[
  {
    "title": "Youtube Thumbnail Scraping",
    "link": "https://blog.ryankert.cc/2022/04/20/youtube-thumbnail-scraping/",
    "date": "2022-07-23T13:14:39.835Z"
  },
  {
    "title": "Download Google font and use it in offline html",
    "link": "https://blog.ryankert.cc/2022/04/18/google-font-offline/",
    "date": "2022-07-23T13:14:39.835Z"
  },
]
```

## How to use it

1. Fork this repository

2. install your friends' rss pages into this file (./_rss_data/friends.json), in this format:

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

3. Until it generate file sussessfully, it will generate a new branch automatically. Then, you setup your github page to display the branch `gh-page`.

It will be display at `https://<github-username>.github.io/rss-friend/<file>`.

There are three file generated

```
rss.json       // sorted json year, month, day
sorted.json    // sorted json universal date ex:2022-08-22T17:47:35.000Z
unsort.json    // unsort raw data
```

APIs:

https://www.ryankert.cc/rss-friend/rss.json

https://www.ryankert.cc/rss-friend/sorted.json

https://www.ryankert.cc/rss-friend/unsort.json


## Development:

### To install dependencies

```zsh
npm i
```

### To generate JSON file

```zsh
npm run dev
```
