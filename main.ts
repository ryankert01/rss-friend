import { parse } from "rss-to-json";

import fs = require('fs');

const friends = require("./_rss_data/friends.json");

interface RSS_POST {
    title: string,
    link:  string,
    date: Date
}

async function ParseRSS() {

    let FriendItems : RSS_POST[] = [];

    for(const e of friends) {
        const rss = await parse(e.feed);

        for(const it of rss.items) {
            FriendItems.push({
                title: it.title,
                link: it.link,
                date: new Date(Number(it.created)),
            });
        }

    }

    fs.writeFile("./assests/unsort.json", JSON.stringify(FriendItems), err => {
        console.log(err);
    })  

    FriendItems.sort(
        (obj1, obj2) => obj2.date.getTime() - obj1.date.getTime()
    );

    const sortedPosts = FriendItems;

    fs.writeFile("./assests/sorted.json", JSON.stringify(sortedPosts), err => {
        console.log(err);
    })  

    const MaximumPost = 30;

    if(sortedPosts.length > MaximumPost)
        sortedPosts.length = MaximumPost;

    

    if(sortedPosts.length > 0) {
        let data = [{
            "title": sortedPosts[0].title,
            "link": sortedPosts[0].link,
            "year": sortedPosts[0].date.getFullYear(),
            "month": sortedPosts[0].date.getMonth()+1,
            "day": sortedPosts[0].date.getDay(),
        }];

        for(var i = 1; i < sortedPosts.length; i++) {
            data.push({
                "title": sortedPosts[i].title,
                "link": sortedPosts[i].link,
                "year": sortedPosts[i].date.getFullYear(),
                "month": sortedPosts[i].date.getMonth()+1,
                "day": sortedPosts[i].date.getDay(),
            });
        }

        fs.writeFile("./assests/rss.json", JSON.stringify(data), err => {
            console.log(err);
        })    
    }


}

ParseRSS();