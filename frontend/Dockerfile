FROM node:24.0.2-bookworm

# Set the working directory
RUN mkdir /app

COPY package.json /app/package.json
COPY package-lock.json /app/package-lock.json

# Install dependencies
RUN cd /app && npm install

# Copy the rest of the application code
COPY . /app

WORKDIR /app

# Build the application
RUN npm run build

# Set environment variables
ENV NODE_ENV production
ENV PORT 3000

# Start the application
CMD ["npm", "start"]

# Expose the port the app runs on
EXPOSE 3000
