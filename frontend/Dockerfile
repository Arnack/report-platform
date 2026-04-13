FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json ./
RUN npm install

# Copy source code
COPY src/ ./src/
COPY public/ ./public/

# Start development server
CMD ["npm", "start"]
