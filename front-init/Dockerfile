# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir pymongo requests

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run main.py when the container launches
CMD ["python", "main.py"]
