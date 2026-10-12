import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from src.check_images import check_urls, encode_url, is_alive, remove_dead_images


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/ok.png", "/rum%20ribs%20(2).jpg"):
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
        elif self.path == "/page":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
        else:
            self.send_response(404)
        self.end_headers()
        self.wfile.write(b"x")

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def base_url():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def test_only_real_images_are_alive(base_url):
    assert is_alive(f"{base_url}/ok.png")
    assert not is_alive(f"{base_url}/missing.png")
    assert not is_alive(f"{base_url}/page")
    assert not is_alive("http://127.0.0.1:1/unreachable.png")
    assert not is_alive("not a url")


def test_check_urls_reports_each_url(base_url):
    urls = [f"{base_url}/ok.png", f"{base_url}/missing.png"]
    assert check_urls(urls, workers=2) == {urls[0]: True, urls[1]: False}


def test_dead_links_are_removed_and_others_kept():
    recipes = [{"image": "http://a/ok.png"}, {"image": "http://a/dead.png"}, {"image": ""}, {}]
    removed = remove_dead_images(recipes, {"http://a/ok.png": True, "http://a/dead.png": False})
    assert removed == 1
    assert [r.get("image") for r in recipes] == ["http://a/ok.png", "", "", None]


def test_urls_with_spaces_are_encoded_and_checked(base_url):
    assert encode_url("https://x/a b (2).jpg") == "https://x/a%20b%20(2).jpg"
    assert encode_url("https://x/already%20ok.jpg") == "https://x/already%20ok.jpg"
    assert is_alive(f"{base_url}/rum ribs (2).jpg")


def test_a_malformed_url_never_stops_the_whole_check(base_url):
    urls = [f"{base_url}/ok.png", "https://x/bad\nline.jpg"]
    assert check_urls(urls, workers=2) == {urls[0]: True, urls[1]: False}
