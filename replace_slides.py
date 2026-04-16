with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_line = -1
end_line = -1
depth = 0
for i, line in enumerate(lines):
    if '<div class="slides">' in line and start_line == -1:
        start_line = i
        depth = 1
        continue
    if start_line != -1:
        depth += line.count('<div')
        depth -= line.count('</div>')
        if depth <= 0:
            end_line = i
            break

print(f"Slides section: lines {start_line+1} to {end_line+1}")

new_slides = [
    '        <div class="slides">\n',
    '            <div class="slide active">\n',
    '                <img src="{{ url_for(\'static\', filename=\'images/banner/banner_1.jpg\') }}" alt="MCA Pune - Premium Interior">\n',
    '                <div class="slide-content">\n',
    '                    <h1>Luxury. Minimalism. Modern Aesthetics.</h1>\n',
    '                    <p>Elevating Spaces Beyond Imagination</p>\n',
    '                </div>\n',
    '            </div>\n',
    '            <div class="slide">\n',
    '                <img src="{{ url_for(\'static\', filename=\'images/banner/banner_2.jpg\') }}" alt="Premium Commercial Interior">\n',
    '                <div class="slide-content">\n',
    '                    <h1>Functionally Excellent. Cosmetically Superior.</h1>\n',
    '                    <p>Turning architectural vision into flawless reality.</p>\n',
    '                </div>\n',
    '            </div>\n',
    '            <div class="slide">\n',
    '                <img src="{{ url_for(\'static\', filename=\'images/banner/banner_3.jpg\') }}" alt="Executive Lounge Interior">\n',
    '                <div class="slide-content">\n',
    '                    <h1>Bespoke Commercial &amp; Residential Design</h1>\n',
    '                    <p>Master Craftsmanship Since 2000</p>\n',
    '                </div>\n',
    '            </div>\n',
    '            <div class="slide">\n',
    '                <img src="{{ url_for(\'static\', filename=\'images/banner/banner_4.jpg\') }}" alt="Modern Office Design">\n',
    '                <div class="slide-content">\n',
    '                    <h1>Where Precision Meets Elegance.</h1>\n',
    '                    <p>Every Detail Crafted With Purpose</p>\n',
    '                </div>\n',
    '            </div>\n',
    '            <div class="slide">\n',
    '                <img src="{{ url_for(\'static\', filename=\'images/banner/banner_5.jpg\') }}" alt="Luxury Corporate Space">\n',
    '                <div class="slide-content">\n',
    '                    <h1>Transforming Spaces. Inspiring Lives.</h1>\n',
    '                    <p>Premium Turnkey Interiors &mdash; Pune &amp; Beyond</p>\n',
    '                </div>\n',
    '            </div>\n',
    '        </div>\n',
]

new_lines = lines[:start_line] + new_slides + lines[end_line+1:]

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("SUCCESS: templates/index.html updated with 5 banner slides")
