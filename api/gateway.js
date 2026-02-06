const express = require('express');
const cors = require('cors');
const axios = require('axios');
const compression = require('compression');
const NodeCache = require('node-cache');

const app = express();
const PORT = 4000;

// --- OPTIMIZATION: Compression & Caching ---
app.use(compression()); // Gzip
app.use(cors());

// Cache for 5 minutes (300 seconds)
const cache = new NodeCache({ stdTTL: 300 });

// Cache Middleware
const verifyCache = (req, res, next) => {
    try {
        const key = req.originalUrl;
        if (cache.has(key)) {
            return res.json(cache.get(key));
        }
        next();
    } catch (err) {
        next();
    }
};

const getServiceUrl = (service, req) => {
    if (process.env.VERCEL_URL) {
        const protocol = req.headers['x-forwarded-proto'] || 'https';
        const host = req.headers.host;
        const baseUrl = `${protocol}://${host}`;

        switch (service) {
            case 'berita-indo': return `${baseUrl}/berita-indo`;
            case 'rss': return `${baseUrl}/rss`;
            case 'cnn': return `${baseUrl}/cnn-api`;
            case 'detik': return `${baseUrl}/detik`;
            default: return baseUrl;
        }
    } else {
        switch (service) {
            case 'berita-indo': return 'http://localhost:3000';
            case 'rss': return 'http://localhost:3002';
            case 'cnn': return 'http://localhost:5001';
            case 'detik': return 'http://localhost:5002';
            default: return 'http://localhost:4000';
        }
    }
};

// --- HELPER: Standardization ---
const standardize = (item, source) => {
    return {
        title: item.title || item.judul || "",
        link: item.link || item.url || "",
        image: item.image?.small || item.image || item.poster || item.thumbnail || item.gambar || "",
        source: source,
        time: item.isoDate || item.pubDate || item.waktu || new Date().toISOString(),
        body: item.description || item.body || ""
    };
};

// --- HELPER: Deduplication & Image Priority ---
const deduplicate = (items) => {
    const uniqueMap = new Map();

    items.forEach(item => {
        const key = item.title.toLowerCase().replace(/[^a-z0-9]/g, '');

        if (!uniqueMap.has(key)) {
            uniqueMap.set(key, item);
        } else {
            const existing = uniqueMap.get(key);
            if (!existing.image && item.image) {
                uniqueMap.set(key, item);
            }
        }
    });

    return Array.from(uniqueMap.values());
};

// --- AGGREGATION ENDPOINTS ---

// 1. Unified Search (With Fallback & Cache)
app.get('/api/search', verifyCache, async (req, res) => {
    const query = req.query.q;
    if (!query) return res.status(400).json({ error: "Query 'q' required" });

    let results = [];

    // Fallback/Fault Tolerance is built-in via Promise.allSettled
    try {
        const [detikReq, cnnReq] = await Promise.allSettled([
            axios.get(`${getServiceUrl('detik', req)}/search?q=${query}`),
            axios.get(`${getServiceUrl('cnn', req)}/search/?q=${query}`)
        ]);

        if (detikReq.status === 'fulfilled' && detikReq.value.data.data) {
            detikReq.value.data.data.forEach(item => results.push(standardize(item, 'Detik News')));
        } else {
            console.warn("Detik Search Failed/Empty, continuing...");
        }

        if (cnnReq.status === 'fulfilled') {
            const cnnData = cnnReq.value.data.data || cnnReq.value.data;
            if (Array.isArray(cnnData)) {
                cnnData.forEach(item => results.push(standardize(item, 'CNN Indonesia')));
            }
        } else {
            // FALLBACK: If CNN API fails, maybe try generic RSS? 
            // For search, real fallback is hard without a search RSS. 
            // We just ensure 'results' isn't empty if Detik worked.
            console.warn("CNN Search Failed, continuing...");
        }

        const uniqueResults = deduplicate(results);

        const responseData = {
            status: 200,
            total: uniqueResults.length,
            cached: false,
            data: uniqueResults
        };

        // Set Cache
        cache.set(req.originalUrl, { ...responseData, cached: true });

        res.json(responseData);

    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// 2. Unified Categories (With Fallback & Cache)
const CATEGORY_MAP = {
    'terbaru': [
        { service: 'rss', path: '/cnn/terbaru', source: 'CNN RSS' },
        { service: 'rss', path: '/cnbc/terbaru', source: 'CNBC RSS' },
        { service: 'rss', path: '/antara/terbaru', source: 'Antara RSS' }
    ],
    'nasional': [
        { service: 'cnn', path: '/nasional', source: 'CNN Official' },
        { service: 'rss', path: '/cnn/nasional', source: 'CNN RSS' },
        { service: 'rss', path: '/antara/politik', source: 'Antara Politik' }
    ],
    'teknologi': [
        { service: 'cnn', path: '/teknologi', source: 'CNN Official' },
        { service: 'rss', path: '/cnn/teknologi', source: 'CNN RSS' },
        { service: 'rss', path: '/cnbc/tech', source: 'CNBC Tech' },
        { service: 'rss', path: '/antara/tekno', source: 'Antara Tekno' }
    ],
    'ekonomi': [
        { service: 'cnn', path: '/ekonomi', source: 'CNN Official' },
        { service: 'rss', path: '/cnbc/market', source: 'CNBC Market' },
        { service: 'rss', path: '/antara/ekonomi', source: 'Antara Ekonomi' }
    ],
    'bolasport': [
        { service: 'cnn', path: '/olahraga', source: 'CNN Official' },
        { service: 'rss', path: '/antara/bola', source: 'Antara Bola' }
    ]
};

app.get('/api/category/:name', verifyCache, async (req, res) => {
    const catName = req.params.name.toLowerCase();
    const sources = CATEGORY_MAP[catName];

    if (!sources) {
        return res.status(404).json({ error: "Category not found" });
    }

    let results = [];

    // Smart Fallback Logic:
    // We request ALL sources. If 'CNN Official' fails, the 'CNN RSS' (which is also in the list)
    // naturally acts as the fallback because it's a separate request in the batch.

    const requests = sources.map(src => {
        const baseUrl = getServiceUrl(src.service, req);
        return axios.get(`${baseUrl}${src.path}`)
            .then(resp => ({ status: 'fulfilled', source: src.source, data: resp.data }))
            .catch(err => ({
                status: 'rejected',
                source: src.source,
                error: err.message,
                url: `${baseUrl}${src.path}`,
                error_obj: err
            }));
    });

    const responses = await Promise.all(requests);

    responses.forEach(r => {
        if (r.status === 'fulfilled') {
            const rawData = r.data.data || r.data.values || r.data;
            if (Array.isArray(rawData)) {
                rawData.forEach(item => {
                    results.push(standardize(item, r.source));
                });
            }
        } else {
            console.warn(`Source ${r.source} failed (Auto-Fallback active).`);
        }
    });

    const uniqueResults = deduplicate(results);

    const responseData = {
        status: 200,
        category: catName,
        total: uniqueResults.length,
        cached: false,
        data: uniqueResults
    };

    // DEBUG: If empty, show why
    if (uniqueResults.length === 0) {
        responseData.debug_errors = responses.filter(r => r.status === 'rejected').map(r => ({
            source: r.source,
            error: r.error,
            url: r.url,
            // Try to extract response body if available (e.g. from axios error)
            response_data: r.error_obj?.response?.data || "No response data"
        }));
        // DO NOT CACHE ERRORS/EMPTY
    } else {
        cache.set(req.originalUrl, { ...responseData, cached: true });
    }

    res.json(responseData);
});

// --- PROXY ROUTES (No Cache for direct proxy to allow debug, or add if needed) ---
const proxyRequest = async (serviceUrl, req, res) => {
    try {
        const url = `${serviceUrl}${req.path}`;
        const response = await axios.get(url, { params: req.query });
        res.status(response.status).send(response.data);
    } catch (error) {
        if (error.response) res.status(error.response.status).send(error.response.data);
        else res.status(500).send({ error: 'Service Unavailable' });
    }
};

app.use('/berita-indo', (req, res) => proxyRequest(getServiceUrl('berita-indo', req), req, res));
app.use('/rss', (req, res) => proxyRequest(getServiceUrl('rss', req), req, res));
app.use('/cnn-api', (req, res) => proxyRequest(getServiceUrl('cnn', req), req, res));
app.use('/cnn-detail', (req, res) => {
    // Append the slug (req.url) to '/detail'
    // req.url comes in as '/teknologi/...' (stripped of /cnn-detail)
    req.url = `/detail${req.url}`;
    proxyRequest(getServiceUrl('cnn', req), req, res);
});
app.use('/detik', (req, res) => proxyRequest(getServiceUrl('detik', req), req, res));
app.use('/detik-detail', (req, res) => {
    req.url = `/detail${req.url}`;
    proxyRequest(getServiceUrl('detik', req), req, res);
});

app.get('/', (req, res) => {
    res.send({
        message: 'Unified News Gateway v3.0 (Turbo: Cache + Compression + Stealth + Fallback)',
        smart_endpoints: {
            search: '/api/search?q=...',
            category: '/api/category/:name'
        }
    });
});

module.exports = app;
