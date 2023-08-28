# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
#
# Note this image uses node@10.15.3 and npm@6.4.1.
FROM tiangolo/node-frontend:10 as build-stage

WORKDIR /app

COPY package*.json /app/

RUN npm install

COPY ./ /app/

ARG FRONTEND_ENV=production

ENV VUE_APP_ENV=${FRONTEND_ENV}

# Comment out the next line to disable tests
#RUN npm run test:unit

RUN npm run build


# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1.15

COPY --from=build-stage /app/dist/ /usr/share/nginx/html

COPY --from=build-stage /nginx.conf /etc/nginx/conf.d/default.conf
COPY ./nginx-backend-not-found.conf /etc/nginx/extra-conf.d/backend-not-found.conf
COPY ./nginx-performance.conf /etc/nginx/extra-conf.d/performance.conf
