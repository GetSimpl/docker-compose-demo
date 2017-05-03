var express = require('express')
var app = express()

app.get('/', function (req, res) {
    res.send('This is version no. ' + process.env.VERSION)
})

app.listen(process.env.PORT, function () {
    console.log('Example app listening on port !' + process.env.PORT)
})
