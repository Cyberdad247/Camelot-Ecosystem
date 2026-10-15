const path = require('node:path');

module.exports = {
  plugins: [
    require(path.resolve(__dirname, '../pwa/node_modules/tailwindcss')),
    require('autoprefixer'),
  ],
};
