FROM node:lts

ADD ./package.*json /www/

WORKDIR /www

RUN npm install

CMD node_modules/.bin/webpack-dev-server --host 0.0.0.0
