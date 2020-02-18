const Parser = require('icecast-parser');

const URL = process.argv.slice(2)[0];

console.log("Trying to get data for url: " + URL);

const radioStation = new Parser({
    url: URL,
    keepListen: false
});

radioStation.on('metadata', function(metadata) {
    console.log(metadata.StreamTitle);
});
