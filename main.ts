import { parse } from "rss-to-json";

import fs = require('fs');

const friends = require("./friends.json");

interface Author {
    name: string,
    link: string
}

interface RSS_POST {
    title: string,
    link:  string,
    date: Date,
    author: Author
}

async function ParseRSS() {

    let FriendItems : RSS_POST[] = [];

    for(const e of friends) {
        const rss = await parse(e.feed);
        const auth : Author = { name : e.title, link : e.link }

        for(const it of rss.items) {
            FriendItems.push({
                title: it.title,
                link: it.link,
                date: new Date(Number(it.created)),
                author: auth
            });
        }

    }

    // unsort.json
    if(FriendItems.length > 0) {
        fs.writeFile("./assests/unsort.json", JSON.stringify(FriendItems), err => {
            if(err) {
                console.log(err);                
            }
        })         
    }
 

    // sort-by-date
    FriendItems.sort(
        (obj1, obj2) => obj2.date.getTime() - obj1.date.getTime()
    );

    const sortedPosts = FriendItems;

    const MaximumPost = 30;

    if(sortedPosts.length > MaximumPost)
        sortedPosts.length = MaximumPost;

    // sorted.json
    if(sortedPosts.length > 0) {
        fs.writeFile("./assests/sorted.json", JSON.stringify(sortedPosts), err => {
            if(err) {
                console.log(err);                
            }
        })         
    }

    

    if(sortedPosts.length > 0) {
        let data = [{
            "title": sortedPosts[0].title,
            "link": sortedPosts[0].link,
            "year": sortedPosts[0].date.getFullYear(),
            "month": sortedPosts[0].date.getMonth()+1,
            "day": sortedPosts[0].date.getDay(),
            "author" : {
                name: sortedPosts[0].author.name,
                link: sortedPosts[0].author.link
            }
        }];

        for(var i = 1; i < sortedPosts.length; i++) {
            data.push({
                "title": sortedPosts[i].title,
                "link": sortedPosts[i].link,
                "year": sortedPosts[i].date.getFullYear(),
                "month": sortedPosts[i].date.getMonth()+1,
                "day": sortedPosts[i].date.getDay(),
                "author" : {
                    name: sortedPosts[i].author.name,
                    link: sortedPosts[i].author.link
                }
            });
        }
        
        // rss.json
        fs.writeFile("./assests/rss.json", JSON.stringify(data), err => {
            if(err) {
                console.log(err);                
            }
        });
    }

}

try {
    ParseRSS();
} catch (err) {
    console.log(err);
}

console.log("sucessfully generate!")