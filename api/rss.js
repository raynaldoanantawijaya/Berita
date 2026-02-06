try {
    const app = require('../api-berita-indonesia/src/server.js');
    module.exports = app;
} catch (error) {
    const express = require('express');
    const app = express();
    app.all('*', (req, res) => {
        res.status(500).json({
            error: "Startup Error",
            message: error.message,
            stack: error.stack,
            cwd: process.cwd()
        });
    });
    module.exports = app;
}
