FROM nginx:1.27-alpine

# Drop the packaged default site/content so only ours is served.
RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

COPY frontend/ /usr/share/nginx/html/
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Fail the build on a malformed config instead of at container start.
RUN nginx -t

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s --retries=5 --start-period=10s \
    CMD wget --quiet --tries=1 --spider http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
