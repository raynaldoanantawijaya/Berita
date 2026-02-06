const express = require('express');
const cors = require('cors');
const Parser = require('rss-parser');

const app = express();
const parser = new Parser();
const PORT = process.env.PORT || 3002;

app.use(cors());

// --- Vercel Middleware: Strip Prefix ---
app.use((req, res, next) => {
    if (req.url.startsWith('/rss')) {
        req.url = req.url.replace('/rss', '');
        if (req.url === '') req.url = '/';
    }
    next();
});
// ---------------------------------------

// URL Mappings (extracted from feedid)
const rssEndpoints = {
    cnn: {
        terbaru: 'https://www.cnnindonesia.com/rss',
        nasional: 'https://www.cnnindonesia.com/nasional/rss',
        internasional: 'https://www.cnnindonesia.com/internasional/rss',
        ekonomi: 'https://www.cnnindonesia.com/ekonomi/rss',
        olahraga: 'https://www.cnnindonesia.com/olahraga/rss',
        teknologi: 'https://www.cnnindonesia.com/teknologi/rss',
        hiburan: 'https://www.cnnindonesia.com/hiburan/rss',
        gayaHidup: 'https://www.cnnindonesia.com/gaya-hidup/rss'
    },
    antara: {
        terbaru: 'https://www.antaranews.com/rss/terkini.xml',
        politik: 'https://www.antaranews.com/rss/politik.xml',
        hukum: 'https://www.antaranews.com/rss/hukum.xml',
        ekonomi: 'https://www.antaranews.com/rss/ekonomi.xml',
        metro: 'https://www.antaranews.com/rss/metro.xml',
        bola: 'https://www.antaranews.com/rss/sepakbola.xml',
        olahraga: 'https://www.antaranews.com/rss/olahraga.xml',
        humaniora: 'https://www.antaranews.com/rss/humaniora.xml',
        lifestyle: 'https://www.antaranews.com/rss/lifestyle.xml',
        hiburan: 'https://www.antaranews.com/rss/hiburan.xml',
        dunia: 'https://www.antaranews.com/rss/dunia.xml',
        tekno: 'https://www.antaranews.com/rss/tekno.xml',
        otomotif: 'https://www.antaranews.com/rss/otomotif.xml'
    },
    cnbc: {
        terbaru: 'https://www.cnbcindonesia.com/rss',
        investment: 'https://www.cnbcindonesia.com/investment/rss',
        news: 'https://www.cnbcindonesia.com/news/rss',
        market: 'https://www.cnbcindonesia.com/market/rss',
        entrepreneur: 'https://www.cnbcindonesia.com/entrepreneur/rss',
        syariah: 'https://www.cnbcindonesia.com/syariah/rss',
        tech: 'https://www.cnbcindonesia.com/tech/rss',
        lifestyle: 'https://www.cnbcindonesia.com/lifestyle/rss',
        opini: 'https://www.cnbcindonesia.com/opini/rss',
        profil: 'https://www.cnbcindonesia.com/profil/rss'
    }
};

// Generic Route Handler
app.get('/:provider/:category', async (req, res) => {
    const { provider, category } = req.params;

    if (!rssEndpoints[provider] || !rssEndpoints[provider][category]) {
        return res.status(404).send({
            success: false,
            message: 'Endpoint or category not found',
            available_providers: Object.keys(rssEndpoints)
        });
    }

    try {
        const feedUrl = rssEndpoints[provider][category];
        const feed = await parser.parseURL(feedUrl);

        const items = feed.items.map(item => ({
            title: item.title,
            link: item.link,
            pubDate: item.pubDate,
            description: item.contentSnippet || item.content,
            thumbnail: item.enclosure ? item.enclosure.url : ''
        }));

        res.send({
            success: true,
            data: items,
            length: items.length
        });

    } catch (error) {
        console.error(error);
        res.status(500).send({
            success: false,
            message: 'Internal Server Error (RSS Fetch Failed)',
            error: error.message
        });
    }
});

app.get('/', (req, res) => {
    res.send({
        message: 'API Berita Indonesia (Fixed Version)',
        endpoints: rssEndpoints
    });
});

module.exports = app;
