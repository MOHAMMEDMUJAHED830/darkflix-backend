from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import requests
import json
import os
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept-Language": "en-US,en;q=0.9",
}

OMDB_API_KEY = "3a46bbec"

# ------------------- MOVIES -------------------

@app.route("/api/movie-search")
def movie_search():
    query = request.args.get("q")
    if not query:
        return jsonify({"status": "error", "message": "Missing query"}), 400

    # Try soap2day first
    try:
        res = scrape_soap2day(query)
        if res.get_json().get("movies"):
            return res
    except Exception:
        pass

    # Fallback to yomovies
    try:
        return scrape_yomovies(query)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def scrape_soap2day(query):
    search_url = f"https://ww2.soap2dayhdz.com/search/{query.replace(' ', '%20')}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        movies = []

        # Correct structure for soap2dayhdz.com
        for item in soup.select("div.film-poster"):
            a_tag = item.select_one("a")
            img_tag = item.select_one("img")

            if a_tag and img_tag:
                href = a_tag.get("href")
                title = img_tag.get("alt") or "No title"
                poster = img_tag.get("data-src") or img_tag.get("src")

                full_url = f"https://ww2.soap2dayhdz.com{href}"
                movies.append({
                    "title": title.strip(),
                    "poster": poster.strip(),
                    "source_url": full_url,
                    "label": "Hollywood"
                })

        return jsonify({"status": "done", "movies": movies})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


def scrape_yomovies(query):
    url = f"https://yomovies.design/?s={query.replace(' ', '+')}"
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    movies = []

    for item in soup.select("div.ml-item"):
        a_tag = item.select_one("a")
        img = item.select_one("img")
        if a_tag and img:
            href = a_tag.get("href")
            title = a_tag.get("title") or img.get("alt", "No Title")
            poster = img.get("data-original") or img.get("src")

            if href and poster:
                full_url = href if href.startswith("http") else "https://yomovies.design" + href
                movies.append({
                    "title": title.strip(),
                    "poster": poster,
                    "source_url": full_url,
                    "label": "Bollywood"
                })

    return jsonify({"status": "done", "movies": movies})

@app.route("/api/yomovies-featured")
def yomovies_featured():
    url = "https://yomovies.design/"
    try:
        res = requests.get(url, headers=headers, timeout=20)
        soup = BeautifulSoup(res.text, "html.parser")
        movies = []

        for item in soup.select("div.ml-item")[:15]:  # Limit to top 15
            a_tag = item.select_one("a")
            img_tag = item.select_one("img")

            if a_tag and img_tag:
                href = a_tag.get("href")
                title = a_tag.get("title") or img_tag.get("alt")
                poster = img_tag.get("data-original") or img_tag.get("src")

                movies.append({
                    "title": title.strip(),
                    "poster": poster,
                    "source_url": href if href.startswith("http") else "https://yomovies.design" + href,
                    "label": "Bollywood"
                })

        return jsonify({"status": "done", "movies": movies})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})



# ------------------- ANIME -------------------

@app.route('/api/anime-search')
def anime_search():
    query = request.args.get('q')
    url = f"https://hianime.pe/search?keyword={query}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for item in soup.select(".flw-item"):
        title = item.select_one(".dynamic-name")['title']
        poster = item.select_one("img")["data-src"]
        link = item.select_one("a")["href"]

        results.append({
            "title": title,
            "poster": poster,
            "source_url": f"https://hianime.pe{link}"
        })

    return jsonify({"status": "done", "anime": results})


@app.route("/api/anime-episodes")
def anime_episodes():
    url = request.args.get("url")
    if not url:
        return jsonify({"status": "error", "message": "Missing URL"})

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        episodes = []

        for ep in soup.select("#episodes li a"):
            ep_title = ep.get("title") or ep.text.strip()
            ep_href = ep.get("href")
            if ep_href:
                full_url = "https://hianime.pe" + ep_href
                episodes.append({
                    "title": ep_title,
                    "embed_url": full_url
                })

        return jsonify({"status": "done", "episodes": episodes})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/anime-category")
def anime_category():
    genre = request.args.get("genre", "action")
    url = f"https://hianime.pe/genre/{genre}"
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    anime = []
    for item in soup.select("div.flw-item")[:15]:
        title_tag = item.select_one(".film-name a")
        poster = item.select_one("img")

        if title_tag and poster:
            anime.append({
                "title": title_tag.text.strip(),
                "embed_url": "https://hianime.pe" + title_tag["href"],
                "poster": poster.get("data-src") or poster.get("src")
            })

    return jsonify({"status": "done", "anime": anime})


@app.route('/proxy-redirect')
def proxy_redirect():
    target = request.args.get('url')
    return redirect(target, code=302)


# ------------------- START -------------------
if __name__ == "__main__":
    from os import getenv
    port = int(getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

