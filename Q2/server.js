const express = require('express');
const cors = require('cors');
const app = express();
const port = 5000;

// Enable CORS to allow frontend to communicate with backend
app.use(cors());

// Mock stock price data for symbols AAPL, GOOGL, MSFT
const generateStockPrices = (symbol, minutes) => {
  const prices = [];
  const now = Date.now();
  const basePrice = symbol === 'AAPL' ? 150 : symbol === 'GOOGL' ? 2700 : 300; // Base prices
  for (let i = minutes; i >= 0; i--) {
    const timestamp = now - i * 60 * 1000;
    const price = basePrice + Math.random() * 10 - 5; // Random variation
    prices.push({ timestamp, price });
  }
  const average = prices.reduce((sum, p) => sum + p.price, 0) / prices.length;
  return { prices, average };
};

// Mock correlation data
const generateCorrelationData = (minutes) => {
  const stocks = [
    { symbol: 'AAPL', avgPrice: 150 + Math.random() * 5, stdDev: Math.random() * 2 },
    { symbol: 'GOOGL', avgPrice: 2700 + Math.random() * 50, stdDev: Math.random() * 10 },
    { symbol: 'MSFT', avgPrice: 300 + Math.random() * 10, stdDev: Math.random() * 5 },
  ];
  const correlations = [
    [1, 0.8, 0.3],
    [0.8, 1, -0.2],
    [0.3, -0.2, 1],
  ];
  return { stocks, correlations };
};

// API endpoint for stock prices
app.get('/api/stocks/:symbol/prices', (req, res) => {
  const { symbol } = req.params;
  const { m } = req.query; // Minutes
  if (!symbol || !['AAPL', 'GOOGL', 'MSFT'].includes(symbol)) {
    return res.status(400).json({ error: 'Invalid stock symbol. Use AAPL, GOOGL, or MSFT.' });
  }
  const minutes = parseInt(m) || 30;
  if (minutes < 1 || minutes > 60) {
    return res.status(400).json({ error: 'Minutes must be between 1 and 60.' });
  }
  const data = generateStockPrices(symbol, minutes);
  res.json(data);
});

// API endpoint for correlation data
app.get('/api/correlation', (req, res) => {
  const { m } = req.query; // Minutes
  const minutes = parseInt(m) || 30;
  if (minutes < 1 || minutes > 60) {
    return res.status(400).json({ error: 'Minutes must be between 1 and 60.' });
  }
  const data = generateCorrelationData(minutes);
  res.json(data);
});

// Start the server
app.listen(port, () => {
  console.log(`Mock backend running at http://localhost:${port}`);
});