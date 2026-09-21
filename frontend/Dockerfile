FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .

# Vite bakes VITE_* env vars into the compiled JS at BUILD time, not at
# container-start time. So this must be a build ARG (set via docker-compose's
# `build.args`), not a runtime `environment:` entry — a runtime env var here
# would silently have no effect, which was the root cause of "Sign in does
# nothing": the browser was calling a relative /api/v1 path against the
# frontend's own static file server (which has no /api route) instead of
# the backend container.
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
