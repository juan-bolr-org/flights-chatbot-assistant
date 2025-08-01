FROM node:24.0.2-bookworm

# Set the working directory
RUN mkdir /app

ARG API_URL=https://flights-assistant-api-aqcmh5h0e0acgnbg.westus-01.azurewebsites.net

COPY package.json /app/package.json
# Install dependencies
RUN cd /app && npm install

# Copy the rest of the application code
COPY . /app

WORKDIR /app

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Build the application
RUN npm run build

# Expose the port the app runs on
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
