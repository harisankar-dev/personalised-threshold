"""Vercel adapter for the existing request handler."""
import sys
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from marketer_app import Handler
class handler(Handler):
    def route(self):
        value=parse_qs(urlsplit(self.path).query).get('route',[None])[0]
        if value in ('analyze','research','simulation','config'):self.path='/api/'+value
    def do_GET(self):
        self.route();super().do_GET()
    def do_POST(self):
        self.route();super().do_POST()
