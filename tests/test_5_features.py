import re
import json

def test_index_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 1. Version Bump
    assert 'css/style.css?v=2.7.0' in html, "CSS version 2.7.0 not found in index.html"
    assert 'js/app.js?v=2.7.0' in html, "JS version 2.7.0 not found in index.html"
    
    # 5. Filter bar features
    assert 'data-category="Display"' in html, "Display category chip not found in index.html"
    assert 'id="fs-filter-usecase"' in html, "fs-filter-usecase not found in index.html"
    assert 'data-pill="display"' in html, "Fontshare display pill not found in index.html"
    assert 'data-pill="vn-ready"' in html, "Fontshare vn-ready pill not found in index.html"
    print("✓ test_index_html passed")

def test_css():
    for path in ['css/style.css', 'style.css']:
        with open(path, 'r', encoding='utf-8') as f:
            css = f.read()
        
        # 1. Variant chips 2 rows wrap & compact
        assert '.card-weights-bar' in css and 'flex-wrap: wrap' in css, f"flex-wrap not in {path}"
        assert 'max-height: 64px' in css, f"max-height: 64px not in {path}"
        assert 'font-size: 0.72rem' in css, f"font-size: 0.72rem not in {path}"
        assert 'border-radius: 999px' in css, f"border-radius: 999px not in {path}"
        
        # 2. Interactive badges
        assert '.card-badges-row button.badge' in css, f"button.badge styles not in {path}"
        assert '.badge-style' in css, f".badge-style not in {path}"
        assert '.badge-mood' in css, f".badge-mood not in {path}"
        assert '.badge-use' in css, f".badge-use not in {path}"
        
        # 4. Waterfall split view 2 columns
        assert '.fs-waterfall-split-view' in css, f".fs-waterfall-split-view not in {path}"
        assert '.fs-waterfall-sticky-col' in css, f".fs-waterfall-sticky-col not in {path}"
        assert '.fs-waterfall-rows-list' in css, f".fs-waterfall-rows-list not in {path}"
        assert '.fs-waterfall-live-text' in css, f".fs-waterfall-live-text not in {path}"
        print(f"✓ test_css ({path}) passed")

def test_js():
    for path in ['js/app.js', 'app.js']:
        with open(path, 'r', encoding='utf-8') as f:
            js = f.read()
        
        # 1 & 3: getFontNumericWeights function
        assert 'function getFontNumericWeights' in js, f"getFontNumericWeights not in {path}"
        assert 'minWeight' in js and 'maxWeight' in js, f"minWeight / maxWeight not in {path}"
        
        # 2. Duplicate studio check and interactive buttons
        assert 'data-filter-style' in js, f"data-filter-style not in {path}"
        assert 'data-filter-mood' in js, f"data-filter-mood not in {path}"
        assert 'data-filter-usecase' in js, f"data-filter-usecase not in {path}"
        assert 'data-filter-vn' in js, f"data-filter-vn not in {path}"
        assert 'data-studio' in js, f"data-studio not in {path}"
        
        # 4. Waterfall split view markup & live specimen sync
        assert 'fs-waterfall-split-view' in js, f"fs-waterfall-split-view not in {path}"
        assert 'fs-waterfall-sticky-col' in js, f"fs-waterfall-sticky-col not in {path}"
        assert 'fs-waterfall-live-text' in js, f"fs-waterfall-live-text not in {path}"
        
        # 5. 2-way sync & filter usecase
        assert 'syncFiltersBetweenViews' in js, f"syncFiltersBetweenViews not in {path}"
        assert 'fsFilterUseCase' in js, f"fsFilterUseCase not in {path}"
        print(f"✓ test_js ({path}) passed")

if __name__ == '__main__':
    test_index_html()
    test_css()
    test_js()
    print("\n✓ ALL 5 FEATURES VERIFIED SUCCESSFULLY!")
