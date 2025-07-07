# გამოსაყენებელი Python ვერსია
FROM python:3.10-slim

# სამუშაო დირექტორია
WORKDIR /app

# კოპირება
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Google credentials თუ გინდა პირდაპირ ჩააგდო (სხვა შემთხვევაში secrets-ში დაამატე)
COPY . .

# პორტი Render-ისთვის (FastAPI-ს გამო)
ENV PORT=8000

# სერვისის გაშვება
CMD ["python", "main.py"]
