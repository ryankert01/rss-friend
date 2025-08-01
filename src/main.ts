import axios from 'axios';
import { XMLParser } from 'fast-xml-parser';
import fs from 'fs/promises';
import path from 'path';

// 常數定義
const ASSETS_DIR = path.join(__dirname, './assets');
const MAX_POSTS = 30;
const FRIENDS_JSON_PATH = path.join(__dirname, '../_data/friends.json');

// 類型定義
interface Author {
    name: string;
    link: string;
}

interface RSSPost {
    title: string;
    link: string;
    date: Date;
    author: Author;
}

interface Friend {
    title: string;
    link: string;
    feed: string;
}

interface FormattedPost {
    title: string;
    link: string;
    year: number;
    month: number;
    day: number;
    author: Author;
}

// 工具函數：確保目錄存在（如果不存在則創建）
async function ensureDirectoryExists(dirPath: string): Promise<void> {
    try {
        await fs.access(dirPath);
    } catch {
        await fs.mkdir(dirPath, { recursive: true });
    }
}

// 寫入JSON文件
async function writeJsonFile<T>(filePath: string, data: T): Promise<void> {
    return fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');
}

// 解析單個RSS源
async function parseRssFeed(friend: Friend): Promise<RSSPost[]> {
    const { title: friendName, link: friendLink, feed: rssUrl } = friend;

    try {
        // 驗證RSS地址
        if (!rssUrl || !rssUrl.startsWith('http')) {
            console.warn(`無效的RSS地址: ${rssUrl} (來自: ${friendName})`);
            return [];
        }

        // 獲取RSS內容
        const { data: xmlData } = await axios.get(rssUrl, {
            timeout: 10000,
            headers: { 'User-Agent': 'RSS Aggregator Bot' }
        });

        // 解析XML
        const parser = new XMLParser({
            ignoreAttributes: false,
            attributeNamePrefix: ''
        });
        const parsedData = parser.parse(xmlData);

        // 提取文章列表（兼容不同RSS格式）
        const items = parsedData.rss?.channel?.item ||
            parsedData.feed?.entry ||
            [];

        // 處理單篇文章情況
        const articles = Array.isArray(items) ? items : [items];

        // 轉換為統一格式
        return articles.map((article: any) => {
            // 提取日期（兼容不同RSS格式）
            const dateStr = article.published ||
                article.updated ||
                article.pubDate ||
                article.created;

            const date = dateStr ? new Date(dateStr) : new Date();

            // 處理標題可能是對象的情況
            const title = typeof article.title === 'object' ?
                (article.title._text || article.title.__text || '無標題') :
                (article.title || '無標題');

            // 處理鏈接可能是對象的情況
            const link = article.link?.href || article.link || friendLink;

            return {
                title,
                link,
                date,
                author: {
                    name: friendName,
                    link: friendLink
                }
            };
        });

    } catch (error) {
        console.error(`解析RSS失敗 (${friendName} - ${rssUrl}):`, error instanceof Error ? error.message : String(error));
        return [];
    }
}

// 主函數
async function aggregateRssFeeds() {
    try {
        // 確保輸出目錄存在
        await ensureDirectoryExists(ASSETS_DIR);

        // 讀取好友列表
        const friendsData = await fs.readFile(FRIENDS_JSON_PATH, 'utf8');
        const friends: Friend[] = JSON.parse(friendsData);

        if (!Array.isArray(friends) || friends.length === 0) {
            console.warn('未找到有效的好友列表數據');
            return;
        }

        // 並行解析所有RSS源
        const allPosts: RSSPost[] = [];
        const parsePromises = friends.map(friend => parseRssFeed(friend));
        const results = await Promise.all(parsePromises);

        // 合併所有文章
        results.forEach(posts => allPosts.push(...posts));

        // 保存未排序的原始數據
        await writeJsonFile(path.join(ASSETS_DIR, 'unsort.json'), allPosts);

        // 按發布時間排序（最新在前）
        const sortedPosts = [...allPosts]
            .sort((a, b) => b.date.getTime() - a.date.getTime())
            .slice(0, MAX_POSTS);

        // 保存排序後的數據
        await writeJsonFile(path.join(ASSETS_DIR, 'sorted.json'), sortedPosts);

        // 生成格式化數據（拆分日期）
        const formattedPosts: FormattedPost[] = sortedPosts.map(post => ({
            title: post.title,
            link: post.link,
            year: post.date.getFullYear(),
            month: post.date.getMonth() + 1, // 月份從0開始，需要+1
            day: post.date.getDate(),
            author: post.author
        }));

        // 保存格式化數據
        await writeJsonFile(path.join(ASSETS_DIR, 'rss.json'), formattedPosts);

        console.log(`處理完成 - 共聚合 ${allPosts.length} 篇文章，已保存前 ${sortedPosts.length} 篇`);

    } catch (error) {
        console.error('主程序執行失敗:', error instanceof Error ? error.message : String(error));
    }
}

// 執行主函數
aggregateRssFeeds();
