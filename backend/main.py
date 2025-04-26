from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from backend.crawler import process_walmart_links
import shutil
import csv
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    with open("frontend/index.html", "r") as f:
        return f.read()


@app.post("/process/")
async def process(inputType: str = Form(...), url: str = Form(None), file: UploadFile = File(None)):
    urls = []

    if inputType == "single" and url:
        urls.append(url.strip())
    elif inputType == "csv" and file:
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        with open(file_location, "r") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if row:
                    urls.append(row[0].strip())
        os.remove(file_location)

    results = process_walmart_links(urls)
    
    html_content = "<h2>Results:</h2>"
    for res in results:
        html_content += f"<h3>Walmart URL: {res['walmart_url']}</h3>"
        html_content += f"<p><b>Title:</b> {res['title']}</p>"
        html_content += f"<p><b>Brand:</b> {res['brand']}</p>"
        html_content += f"<p><b>Model:</b> {res['model']}</p>"
        html_content += f"<p><b>Price:</b> {res['price']}</p>"
        html_content += f"<p><b>Image URL:</b> <a href='{res['image_url']}' target='_blank'>View Image</a></p>"
        html_content += f"<p><b>Amazon URL:</b> {res['amazon_url']}</p>"
        html_content += "<hr>"
    
    return HTMLResponse(content=html_content)
