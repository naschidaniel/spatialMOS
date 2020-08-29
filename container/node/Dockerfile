FROM node:lts

ADD ./package.*json /www/

WORKDIR /www

RUN npm install

CMD ./node_modules/webpack-serve/cli.js --host 0.0.0.0
