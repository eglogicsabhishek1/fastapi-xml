from xml.sax import make_parser
from xml.sax.handler import ContentHandler

def parse_xml(file_path: str, handler: ContentHandler):
    parser = make_parser()
    parser.setContentHandler(handler)
    with open(file_path, "r", encoding="utf-8") as f:
        parser.parse(f)
