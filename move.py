import sys

def move_it(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start_idx = -1
    end_idx = -1
    footer_idx = -1
    
    for i, line in enumerate(lines):
        if '<!-- About & Founders Section -->' in line:
            start_idx = i
        if start_idx != -1 and end_idx == -1 and '</section>' in line:
            end_idx = i
        if '<footer' in line:
            footer_idx = i
            
    if start_idx != -1 and end_idx != -1 and footer_idx != -1:
        if footer_idx > end_idx:
            new_lines = lines[:start_idx] + lines[end_idx+1:footer_idx] + lines[start_idx:end_idx+1] + ['\n'] + lines[footer_idx:]
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print('Moved ' + filename)
    else:
        print('Failed ' + filename + f' {start_idx} {end_idx} {footer_idx}')

move_it('index.html')
move_it('templates/index.html')
