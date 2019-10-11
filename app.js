var express = require('express')
var app = express()

app.get('/', function (req, res) {
    console.log("Got the request.")
    res.send('This is version no. ' + process.env.VERSION)
})

app.listen(process.env.PORT, function () {
    console.log('Example app listening on port !' + process.env.PORT)
})

process.on("SIGTERM", () => {
    console.log("Received SIGTERM.");
    app.listen.close(function () {
        winston.info("Closed out remaining connections.");
        process.exit(143);
    });
});