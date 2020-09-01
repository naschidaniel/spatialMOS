const path = require("path");
const devMode = process.env.NODE_ENV !== 'production';
const CompressionPlugin = require('compression-webpack-plugin');

module.exports = {
  entry: [
    '/www/site/static/js/index.js'
  ],
  output: {
    filename: '[name].js',
    chunkFilename: "[name].js",
    publicPath: "/static/",
    path: path.resolve(__dirname, 'static')
  },
  resolve: {
    modules: [
        path.resolve(__dirname, "site/static/js"),
        'node_modules'
    ],
    extensions: ['*', '.js', '.json']
  },
  plugins: [new CompressionPlugin()],
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
  },
  devServer: {
    public: "http://localhost",
    proxy: {
      '**': {
        target: 'http://nginx:80',
        changeOrigin: false
      }
    },
    host: "0.0.0.0",
    port: 3000,
    hot: true,
    https: false,
    headers: { "Access-Control-Allow-Origin": ["*"] }
    }
};
