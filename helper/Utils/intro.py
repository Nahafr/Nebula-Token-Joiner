import threading
import time
import sys

import keyboard

from helper.Utils.utils import Utils

utils = Utils()
red_gradient = [
    '\033[38;2;255;0;0m',
    '\033[38;2;200;0;0m',
    '\033[38;2;150;0;0m',
    '\033[38;2;100;0;0m',
    '\033[38;2;50;0;0m',
]

frames = [
    fr'''
    {red_gradient[0]}     
    {red_gradient[1]} 
    {red_gradient[2]}
    {red_gradient[3]}
    {red_gradient[4]}
    ''',
    fr'''
    {red_gradient[0]}     
    {red_gradient[1]} •
    {red_gradient[2]} ▐
    {red_gradient[3]} █
    {red_gradient[4]} ▀ 
    ''',
    fr'''
    {red_gradient[0]}  ▐    
    {red_gradient[1]} •█  
    {red_gradient[2]} ▐█ 
    {red_gradient[3]} ██ 
    {red_gradient[4]} ▀▀ 
    ''',
    fr'''
    {red_gradient[0]}  ▐    
    {red_gradient[1]} •█▌ 
    {red_gradient[2]} ▐█▐ 
    {red_gradient[3]} ██▐ 
    {red_gradient[4]} ▀▀  
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄    
    {red_gradient[1]} •█▌▐ 
    {red_gradient[2]} ▐█▐▐ 
    {red_gradient[3]} ██▐█
    {red_gradient[4]} ▀▀ █ 
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄    
    {red_gradient[1]} •█▌▐█  
    {red_gradient[2]} ▐█▐▐▌ 
    {red_gradient[3]} ██▐█▌ 
    {red_gradient[4]} ▀▀ █▪ 
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄   
    {red_gradient[1]} •█▌▐█ ▀
    {red_gradient[2]} ▐█▐▐▌ ▐
    {red_gradient[3]} ██▐█▌ ▐
    {red_gradient[4]} ▀▀ █▪ ▀  
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄    
    {red_gradient[1]} •█▌▐█ ▀▄
    {red_gradient[2]} ▐█▐▐▌ ▐▀
    {red_gradient[3]} ██▐█▌ ▐█ 
    {red_gradient[4]} ▀▀ █▪ ▀▀  
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄    
    {red_gradient[1]} •█▌▐█ ▀▄. 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀
    {red_gradient[3]} ██▐█▌ ▐█▄ 
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄    
    {red_gradient[1]} •█▌▐█ ▀▄.▀ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ 
    {red_gradient[3]} ██▐█▌ ▐█▄▄
    {red_gradient[4]} ▀▀ █▪ ▀▀▀ 
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄    
    {red_gradient[1]} •█▌▐█ ▀▄.▀· 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ 
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄  
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ █
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄  
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄ 
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄ 
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀ 
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·   
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ 
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ 
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀  
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• 
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• 
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪█
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ 
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ 
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ 
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌█
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ . 
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ █
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀  
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄▄
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ ██
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██▪
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█▌
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀  
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄▄▌  
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ ██• 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██▪  
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█▌▐  
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀▀▀  
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄▄▌   
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ ██•  
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██▪   
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█▌▐▌▐   
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀▀▀   
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄▄▌   
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ ██•  ▐
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██▪   ▄
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█▌▐▌▐█   
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀▀▀  ▀   
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄▄▌   ▄ 
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ ██•  ▐█ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██▪   ▄█
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█▌▐▌▐█    
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀▀▀  ▀   
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄▄▌   ▄▄
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ ██•  ▐█ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██▪   ▄█▀
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█▌▐▌▐█ ▪ 
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀▀▀  ▀    
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄▄▌   ▄▄▄
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ ██•  ▐█ ▀
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██▪   ▄█▀▀
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█▌▐▌▐█ ▪▐ 
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀▀▀  ▀  ▀ 
    ''',
    fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄▄▌   ▄▄▄· 
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ ██•  ▐█ ▀█ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██▪   ▄█▀▀█
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█▌▐▌▐█ ▪▐▌   
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀▀▀  ▀  ▀   
    ''',
]

continue_animation = True

def check_for_enter() -> None:
    global continue_animation
    while continue_animation:
        if keyboard.is_pressed('s'):
            continue_animation = False
        if continue_animation == False:
            break

def intro() -> None:
    global continue_animation
    enter_thread = threading.Thread(target=check_for_enter, daemon=True)
    enter_thread.start()
    for frame in frames:
        if not continue_animation:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.write(fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄▄▌   ▄▄▄· 
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ ██•  ▐█ ▀█ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██▪   ▄█▀▀█
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█▌▐▌▐█ ▪▐▌   
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀▀▀  ▀  ▀   
''')
            break
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.write(frame)
        sys.stdout.flush()
        time.sleep(0.016)
    continue_animation = False
    utils.clear()
    sys.stdout.write(fr'''
    {red_gradient[0]}  ▐ ▄  ▄▄▄  .▄▄▄▄·  ▄• ▄▌ ▄▄▌   ▄▄▄· 
    {red_gradient[1]} •█▌▐█ ▀▄.▀· ▐█ ▀█ ▪█▪██▌ ██•  ▐█ ▀█ 
    {red_gradient[2]} ▐█▐▐▌ ▐▀▀ ▄ ▐█▀▀█▄ █▌▐█▌██▪   ▄█▀▀█
    {red_gradient[3]} ██▐█▌ ▐█▄▄▌ ██▄▪▐█ ▐█▄█▌▐█▌▐▌▐█ ▪▐▌   
    {red_gradient[4]} ▀▀ █▪ ▀▀▀   ·▀▀▀▀   ▀▀▀ .▀▀▀  ▀  ▀   
''')
    print("")


# // I know this code is fucking ass So dont point it out. Im to lazy to change it yet, Maybe in next update? 