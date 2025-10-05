from typing import Union

from fastapi import FastAPI, HTTPException, Query
import httpx
import os
from dotenv import load_dotenv

app = FastAPI()

GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
load_dotenv()
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

@app.get("/search_books")
async def search_books(q: Union[str, None] = None):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_BOOKS_API, 
                params={
                    "q": q, 
                    "maxResults": 15, 
                    "key": GOOGLE_API_KEY
                }
            )
            response.raise_for_status()
        data = response.json()

        # Simplify the result structure
        items = data.get("items", [])
        results = []
        for item in items:
            volume = item.get("volumeInfo", {})
            results.append({
                "id": item.get("id"),
                "title": volume.get("title"),
                "authors": volume.get("authors"),
                "publishedDate": volume.get("publishedDate"),
                "description": volume.get("description"),
                "thumbnail": volume.get("imageLinks", {}).get("thumbnail"),
                "previewLink": volume.get("previewLink")
            })

        return {"results": results}

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Google Books API error")
