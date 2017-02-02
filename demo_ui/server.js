'use strict';

const express = require('express');
const request = require('request');

// Constants
const PORT = process.env.PORT || 8080;
const SERVICE_URI_HOST = process.env.SERVICE_URI_HOST;
const SERVICE_URI_PORT = process.env.SERVICE_URI_PORT;

// App
const app = express();
app.get('/', function (req, res) {
  request('http://'+SERVICE_URI_HOST+':'+SERVICE_URI_PORT+'/generate', function (error, response, body) {
    if(error){
        res.send('Unable to talk to service \n'+error);
    } else {
        res.send('The random number generated is '+body);
    }
  });
});

app.listen(PORT);
console.log('Running on http://localhost:' + PORT);
