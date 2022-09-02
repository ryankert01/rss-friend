import fs = require('fs');
import { XMLParser } from "fast-xml-parser";
import axios from "axios";

const friends = require("../_data/friends.json");

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
        const auth : Author = { name : e.title, link : e.link };
        const rss = await parse(e.feed, auth);

        for(const it of rss) {
            FriendItems.push({
                title: it.title,
                link: it.link,
                date: it.date,
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


ParseRSS().catch(err => {
    console.error(err);
});


async function parse(url: string, author : Author) : Promise<RSS_POST[]> {
    if (!/(^http(s?):\/\/[^\s$.?#].[^\s]*)/i.test(url)) return [];

    const { data } = await axios(url);

    const xml = new XMLParser({
        attributeNamePrefix: '',
        textNodeName: '$text',
        ignoreAttributes: false,
    });

    const result = xml.parse(data);

    let channel = result.rss && result.rss.channel ? result.rss.channel : result.feed;
    if (Array.isArray(channel)) channel = channel[0];

    let items = channel.item || channel.entry || [];
    if (items && !Array.isArray(items)) items = [items];

    let rss : RSS_POST[] = [];

    for (let i = 0; i < items.length; i++) {
        const val = items[i];

        const d = val.published ? Date.parse(val.published) : val.updated ? Date.parse(val.updated) : val.pubDate ? Date.parse(val.pubDate) : val.created ? Date.parse(val.created) : val.published? Date.parse(val.published) : Date.now();

        const obj : RSS_POST= {
            title: val.title && val.title.$text ? val.title.$text : val.title,
            link: val.link && val.link.href ? val.link.href : val.link,
            author: author,
            date: d === 10000 ? val.published ? new Date(val.published) : new Date() : new Date(d),
        };

        rss.push(obj);
    }

    return rss;
};