from src.extract.parser import parse_reviews_from_html


def test_parser_basic() -> None:
    html = '''
    <div class="_27M-vq">
      <div class="_3LWZlK">5</div>
      <p class="_2-N8zT">Excellent</p>
      <div class="t-ZTKy"><div>Amazing camera</div></div>
      <p class="_2sc7ZR _2V5EHH">Alice</p>
      <p class="_2sc7ZR">Certified Buyer, Mumbai</p>
      <p class="_2sc7ZR">14 days ago</p>
    </div>
    '''
    rows = parse_reviews_from_html(html, "https://www.flipkart.com/p/product-reviews/x?pid=ABC", 1)
    assert len(rows) == 1
    assert rows[0]["rating"] == 5
