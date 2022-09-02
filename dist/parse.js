"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const fast_xml_parser_1 = require("fast-xml-parser");
const axios_1 = __importDefault(require("axios"));
async function ParseRSSHUB(url) {
    var _a, _b;
    if (!/(^http(s?):\/\/[^\s$.?#].[^\s]*)/i.test(url))
        return null;
    const { data } = await (0, axios_1.default)(url);
    const xml = new fast_xml_parser_1.XMLParser({
        attributeNamePrefix: '',
        textNodeName: '$text',
        ignoreAttributes: false,
    });
    const result = xml.parse(data);
    let channel = result.rss && result.rss.channel ? result.rss.channel : result.feed;
    if (Array.isArray(channel))
        channel = channel[0];
    const rss = {
        title: (_a = channel.title) !== null && _a !== void 0 ? _a : '',
        description: (_b = channel.description) !== null && _b !== void 0 ? _b : '',
        link: channel.link && channel.link.href ? channel.link.href : channel.link,
        image: channel.image ? channel.image.url : channel['itunes:image'] ? channel['itunes:image'].href : '',
        category: channel.category || [],
        items: [],
    };
    let items = channel.item || channel.entry || [];
    if (items && !Array.isArray(items))
        items = [items];
    for (let i = 0; i < items.length; i++) {
        const val = items[i];
        const obj = {
            title: val.title && val.title.$text ? val.title.$text : val.title,
            description: val.summary && val.summary.$text ? val.summary.$text : val.description,
            link: val.link && val.link.href ? val.link.href : val.link,
            author: val.author && val.author.name ? val.author.name : val['dc:creator'],
            published: val.created ? Date.parse(val.created) : val.pubDate ? Date.parse(val.pubDate) : Date.now(),
            created: val.updated ? Date.parse(val.updated) : val.pubDate ? Date.parse(val.pubDate) : val.created ? Date.parse(val.created) : Date.now(),
        };
        rss.items.push(obj);
    }
    return rss;
}
;
//# sourceMappingURL=parse.js.map