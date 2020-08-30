const path = require("path");
const devMode = process.env.NODE_ENV !== 'production';

module.exports = {
  entry: {
    main: '/www/site/static/js/index.js'
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      }
    ]
  }
};
