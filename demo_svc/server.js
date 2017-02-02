'use strict';

const express = require('express');

// Constants
const PORT = process.env.PORT || 8090;

// App
const app = express();

app.get('/', function (req, res) {
  res.send('Random number generator service\n');
});

app.get('/generate', function (req, res) {
  res.send((Math.random() * 100) + '\n');
});

app.listen(PORT);
console.log('Running on http://localhost:' + PORT);
