# Use a base image with Python
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the Python code, templates, &, session file into the container
COPY Automation.py /app/
COPY templates /app/templates
COPY Default_WA_personal_my /app/Default_WA_personal_my
COPY req.txt /app/req.txt

# Install dependencies
RUN apt-get update && \
    apt-get install -y xvfb && \
    pip install --upgrade pip && \
    pip install -r req.txt && \
    playwright install && \
    playwright install-deps

EXPOSE 5000

# Set the entry point for the container
CMD ["xvfb-run", "python3", "Automation.py"]