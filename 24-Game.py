# ----------------------------------------------------------------
# CONFIGURATION AND INITIALISATION
# ----------------------------------------------------------------

import pygame as pg
import random
import itertools as it
from collections import deque

pg.init()
pg.display.set_caption('24 Game')

screen = pg.display.set_mode((1680, 1000))
ss = (screen.get_width(), screen.get_height())
center = pg.Vector2(ss[0] / 2, ss[1] / 2)
clock = pg.time.Clock()
tick = 0

tc = 4 # Total cards
cw = int((ss[0]*0.6)/tc) # Card width
cts = int(cw/4) # Card text size

num_symbols = ['0', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
allowed_characters = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "*", "/", "(", ")"]
suits = ["H", "D", "S", "C"]
suit_colours = ["#eb0505", "#eb0505", "#262626", "#262626"]
button_colours = {
    "idle": "#0282de",
    "hover": "#3293d9",
    "press": "#1b7bbf",
    "disabled": "#787b80",
}

running = True

cards, typed, display_text, error, evaluated, max_chars, cursor_pos, key_down, mouse_down, page = [], "", "", "", "?", 15, 0, False, False, "main_menu"

# ----------------------------------------------------------------
# FUNCTIONS
# ----------------------------------------------------------------

# generates_cards() -> returns 4 cards, e.g ["H3", "S5", "DA", "CK"]

def generate_cards():
    all_cards = []
    for i in range(1, 5):
        for j in range(1, 14):
            all_cards.append(f"{suits[i-1]}{num_symbols[j]}")
    c = []
    for i in range(tc):
        c.append(random.choice(all_cards))
        all_cards.remove(c[-1])
    return c

# rectangle(topleft_x, topleft_y, width, height, colour, round_corners) -> draws a rectangle

def rectangle(topleft_x, topleft_y, width, height, colour, round_corners):
    pg.draw.rect(screen, colour, pg.Rect(topleft_x, topleft_y, width, height), border_radius=round_corners)
    return 0

# button(topleft_x, topleft_y, width, height, round_corners, text, text_size, not_disabled)
# -> creates a button which is a rectangle with text, returns True if mouse is touching it AND down

def button(topleft_x, topleft_y, width, height, round_corners, text, text_size, not_disabled):
    mouse_pos = pg.mouse.get_pos()
    if not_disabled:
        button_press = False
        if (mouse_pos[0] > topleft_x and mouse_pos[0] < topleft_x+width and mouse_pos[1] > topleft_y and mouse_pos[1] < topleft_y+height):
            if mouse_down:
                rectangle(topleft_x, topleft_y, width, height, button_colours["press"], round_corners)
                button_press = True
            else:
                rectangle(topleft_x, topleft_y, width, height, button_colours["hover"], round_corners)
        else:
            rectangle(topleft_x, topleft_y, width, height, button_colours["idle"], round_corners)
        render_text(topleft_x+width/2, topleft_y+height*0.12, "#ffffff", text, text_size, "Verdana", "c")
    else:
        rectangle(topleft_x, topleft_y, width, height, button_colours["disabled"], round_corners)
        render_text(topleft_x+width/2, topleft_y+height*0.12, "#ebebeb", text, text_size, "Verdana", "c")
        button_press = False
    return button_press

# render_text(x, y, colour, text, size, font, align) -> creates text with "left", "center" or "right" align

def render_text(x, y, colour, text, size, font, align):
    t_size = pg.font.SysFont(font, int(size)).size(text)
    x_pos = x # left align
    if align == "c":
        x_pos -= t_size[0]/2
    elif align == "r":
        x_pos -= t_size[0]
    screen.blit(pg.font.SysFont(font, int(size)).render(text, True, colour), (x_pos, y))        
    return 0

# draw_suit(x, y, suit, colour, size) -> draws a HEART, DIAMOND, SPADE or CLUB at (x, y) with colour and size

def draw_suit(x, y, suit, size):
    points = []
    if suit == "H":
        points = [[0, -1],  [0.25, -1.35], [0.45, -1.75], [0.9, -2.1], [1.5, -2.2], [1.9, -2.15], [2.5, -1.7], [2.8, -1.1], [2.8, -0.5], [2.7, 0], [2, 1], [1, 1.9], [0, 3]]
    elif suit == "D":
        points = [[0, 3], [1.1, 1.4], [2.35, 0], [1.1, -1.4], [0, -3]]
    elif suit == "S":
        points = [[1.8, 3], [1, 2.4], [0.45, 2], [0.26, 1], [0.25, 1.08], [0.45, 1.4], [0.9, 1.68], [1.5, 1.76], [1.9, 1.72], [2.5, 1.36], [2.8, 0.88], [2.8, 0.4], [2.7, 0], [2, -1], [1, -1.9], [0, -3], [0, 3]]
    elif suit == "C":
        points = [[1.8,3],[1,2.4],[0.45,2],[0.26,1],[0.26,1.08],[0.46,1.4],[0.9,1.68],[1.5,1.76],[1.9,1.72],[2.5,1.37],[2.8,0.88],[2.8,0.4],[2.7,0],[2.3,-0.3],[2,-0.5],[1.6,-0.6],[1.1,-0.5],[1.4,-1],[1.5,-1.5],[1.4,-2.2],[1.2,-2.55],[0.9,-2.8],[0.4,-3],[0,-3],[0,3]]
    for i in range(len(points)):
            points.append([0-points[i][0], points[i][1]])
    for i in range(len(points)):
            points[i] = [points[i][0]*cw*size+x, points[i][1]*cw*size+y]
    pg.draw.polygon(screen, ["#eb0505", "#eb0505", "#262626", "#262626"][suits.index(suit)], points)
    return 0

# solve(nums) -> returns all possible solutions for 4 given numbers

def solve(nums):
    solutions = []
    for i in list(set(it.permutations(nums))): # combinations for the numbers
        for j in list(it.product(['+', '-', '*', '/', '--', '//'], repeat=3)): # combinations for the operations
            ans = i[0]
            for x in range(3):
                if (j[x] == '+'):
                    ans += i[x+1]
                elif (j[x] == '-'):
                    ans -= i[x+1]
                elif (j[x] == '--'):
                    ans = i[x+1]-ans
                elif (j[x] == '*'):
                    ans *= i[x+1]
                elif (j[x] == '/'):
                    ans /= i[x+1]
                elif (ans != 0 and j[x] == '//'):
                    ans = i[x+1]/ans
            if ans > 23.99 and ans < 24.01:
                ret = deque([str(i[0])])
                prev = [False, False, False]
                for x in range(3):
                    if j[x] == '+' or j[x] == '-':
                        prev = [True, True, True]
                    elif j[x] == '--':
                        if prev[0]:
                            ret.append(')')
                            ret.appendleft('(')
                        prev = [True, True, True]
                    elif i[x+1] != 1 and (j[x] == '/' or j[x] == '*'):
                        if prev[0] or prev[1]:
                            ret.append(')')
                            ret.appendleft('(')
                        prev = [False, False, True]
                    elif j[x] == '//':
                        if prev[0] or prev[1] or prev[2]:
                            ret.append(')')
                            ret.appendleft('(')
                        prev = [False, False, True]
                    if j[x] == '--' or j[x] == '//':
                        ret.appendleft(j[x][0])
                        ret.appendleft(str(i[x+1]))
                    else:
                        ret.append(j[x])
                        ret.append(str(i[x+1]))
                solutions.append(''.join(ret))
    return list(set(solutions))

# new_game() -> initialises a new game

def new_game():
    global cards, typed, display_text, error, evaluated, max_chars, cursor_pos, page
    cards, typed, display_text, error, evaluated, max_chars, cursor_pos, page = generate_cards(), "", "", "", "?", 15, 0, "in_game"

# handle_events() -> handles events like QUIT, MOUSEUP/DOWN and KEYDOWN

def handle_events():

    global key_down, mouse_down, running, cursor_pos, typed

    for event in pg.event.get():
        key_down = False
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            mouse_down = True
        elif event.type == pg.MOUSEBUTTONUP:
            mouse_down = False
        elif page == "in_game" and event.type == pg.KEYDOWN:
            key_down = True
            if event.key == pg.K_BACKSPACE:
                typed = typed[:cursor_pos-1] + typed[cursor_pos:]
                cursor_pos -= 1
            elif event.key == pg.K_LEFT:
                cursor_pos -= 1
            elif event.key == pg.K_RIGHT:
                cursor_pos += 1
            elif event.unicode in allowed_characters and len(typed) < max_chars:
                typed = typed[:cursor_pos] + event.unicode + typed[cursor_pos:]
                cursor_pos += 1

# ----------------------------------------------------------------
# PAGES
# ----------------------------------------------------------------

# in_game_tick() -> runs everything that occurs while in game

def in_game_tick():

    global cards, typed, display_text, error, evaluated, max_chars, cursor_pos, page, tick

    error = ""
    if typed == "":
        evaluated = "0"
    else:
        try:
            evaluated = eval(typed)
            if evaluated <= 100000:
                evaluated = str("{:.2f}".format(evaluated))
            else:
                 error = "Result is too big"
                 evaluated = "?"
        except (RuntimeError, TypeError, NameError, SyntaxError, ZeroDivisionError):
            evaluated = "?"
    if len(typed) >= max_chars:
        error = "Character limit reached"
    if cursor_pos < 0:
        cursor_pos = 1
    elif cursor_pos > len(typed):
        cursor_pos = len(typed)
    
    display_text = typed.replace("*", "×").replace("/", "÷")
    tick += 1 # used for cursor flashing
    if (tick % 60 >= 43 or key_down) and len(typed) < max_chars:
        display_text = display_text[:cursor_pos] + "|" + display_text[cursor_pos:]
    else:
        display_text = display_text[:cursor_pos] + " " + display_text[cursor_pos:]

    nums = []
    for i in range(tc):

        cn = cards[i][1:] # Card Number
        csu = cards[i][0] # Card suit
        ccx = center.x-((cw+40)*(tc-1))/2+i*(cw+40) # Card center x
        ccy = ss[1]*0.38 # Card center y
        cco = ["#eb0505", "#eb0505", "#262626", "#262626"][suits.index(csu)] # Card colour
        nums.append(str(num_symbols.index(cn)))
        
        rectangle(ccx-cw*0.5, ccy-cw*0.7, cw, cw*1.4, "#ededed", int(cw/6))
        draw_suit(ccx, ccy, csu, 0.084)
        render_text(ccx-cw/2+cts/2, ccy-cw*0.7+cts/2, cco, cn, cts, "Monospace", "l")
        render_text(ccx+cw/2-cts*len(cn), ccy+cw*0.7-cts*1.25, cco, cn, cts, "Monospace", "l")

    rectangle(ss[0]*0.1, ss[1]*0.6, ss[0]*0.52, ss[1]*0.17, "#c4c4c4", 5)
    render_text(center.x, ss[1]*0.05, "#ffffff", "24 Game", ss[1]*0.075, "Verdana", "c")
    main_menu = button(ss[0]*0.02, ss[1]*0.03, ss[0]*0.14, ss[1]*0.1, 5, "Menu", ss[1]*0.055, True)
    if typed == "":
        render_text(ss[0]*0.115, ss[1]*0.615, "#ebebeb", "Type equation here" + display_text, ss[1]*0.055, "Verdana", "l")
    else:  
        render_text(ss[0]*0.115, ss[1]*0.615, "#ffffff", display_text, ss[1]*0.055, "Verdana", "l")    
    render_text(ss[0]*0.605, ss[1]*0.7, "#ebebeb", "= " + evaluated, ss[1]*0.045, "Verdana", "r")
    render_text(ss[0]*0.115, ss[1]*0.69, "#8a8a8a", error, ss[1]*0.025, "Verdana", "l")
    render_text(ss[0]*0.115, ss[1]*0.72, "#8a8a8a", f"{int(len(typed))}/{int(max_chars)} characters used", ss[1]*0.025, "Verdana", "l")
    
    all_nums_used = all(num_str in typed for num_str in nums) and len(set(typed).difference(set(" ".join(nums) + "+-*/()"))) == 0

    submit = button(ss[0]*0.65, ss[1]*0.6, ss[0]*0.25, ss[1]*0.1, 5, "Submit", ss[1]*0.055, (evaluated=="24.00" and all_nums_used))
    impossible = button(ss[0]*0.65, ss[1]*0.73, ss[0]*0.25, ss[1]*0.1, 5, "Impossible", ss[1]*0.055, True)
    give_up = button(ss[0]*0.65, ss[1]*0.86, ss[0]*0.25, ss[1]*0.1, 5, "Give up", ss[1]*0.055, True)

    if submit or impossible or give_up:
        page = "solutions"
    elif main_menu:
        page = "main_menu"

# main_menu_tick() -> displays main menu

def main_menu_tick():
    global page

    render_text(center.x, ss[1]*0.37, "#ffffff", "24 Game", ss[1]*0.09, "Verdana", "c")
    for i in range(4):
        draw_suit(ss[0]*((0.5-0.085*1.5)+i*0.085), ss[1]*0.25, suits[i], 0.084)
    start = button(ss[0]*0.35, ss[1]*0.52, ss[0]*0.3, ss[1]*0.1, 5, "Start", ss[1]*0.055, True)
    rules = button(ss[0]*0.35, ss[1]*0.65, ss[0]*0.3, ss[1]*0.1, 5, "How to Play", ss[1]*0.055, True)
    if start:
        new_game()
    elif rules:
        page = "rules"

# rules_tick() -> displays rules

def rules_tick():
    global page

    for i in range(4):
        draw_suit(ss[0]*((0.5-0.055*1.5)+i*0.055), ss[1]*0.12, suits[i], 0.04)
        
    render_text(center.x, ss[1]*0.172, "#ffffff", "24 Game", ss[1]*0.06, "Verdana", "c")
    render_text(center.x, ss[1]*0.25, "#ffffff", "How to Play", ss[1]*0.11, "Verdana", "c")

    instructions = ["1. You are given 4 cards with numbers ranging from 1-13",
                    "2. You must use all the numbers and some operations to make 24",
                    "3. You can only use add (+), subtract (-), multiply (*), divide (/) and parentheses ()",
                    "4. Press 'Give up' if you can't do it or 'Impossible' if you think it's impossible",
                    "5. Note: A = 1, J = 11, Q = 12, K = 13",
                    "",
                    "   Example: You are given 3, 2, 8 and 4",
                    "   Possible solution: 3 × 2 × (8 - 4)"]
    
    for i in range(len(instructions)):
        render_text(center.x, ss[1]*(0.42+0.06*i), "#ffffff", instructions[i], ss[1]*0.035, "Verdana", "c")
    
    main_menu = button(ss[0]*0.02, ss[1]*0.03, ss[0]*0.14, ss[1]*0.1, 5, "Menu", ss[1]*0.055, True)

    if main_menu:
        page = "main_menu"

# solutions_display() -> displays possible solutions

def solutions_display():

    start_new_game = button(ss[0]*0.35, ss[1]*0.85, ss[0]*0.3, ss[1]*0.1, 5, "New game", ss[1]*0.055, True)
    
    for i in range(4):
        draw_suit(ss[0]*((0.5-0.055*1.5)+i*0.055), ss[1]*0.08, suits[i], 0.04)
        
    render_text(center.x, ss[1]*0.132, "#ffffff", "24 Game", ss[1]*0.06, "Verdana", "c")
    render_text(center.x, ss[1]*0.215, "#ffffff", "Possible Solutions", ss[1]*0.07, "Verdana", "c")
    nums = []
    for card in cards:
        nums.append(int(num_symbols.index(card[1:])))
    solutions = solve(nums)
    if len(solutions) == 0:
        render_text(center.x, center.y, "#ffffff", "No solutions! This is impossible", ss[1]*0.06, "Verdana", "c")
    else:
        if len(solutions) > 9:
            render_text(center.x, ss[1]*0.78, "#ffffff", f"and {len(solutions)-9} more", ss[1]*0.04, "Verdana", "c")
            del solutions[9:]
        for i in range(len(solutions)):
            render_text(center.x, ss[1]*(0.33+0.05*i), "#ffffff", solutions[i].replace("*", "×").replace("/", "÷"), ss[1]*0.04, "Verdana", "c")
        
    if start_new_game:
        new_game()

# ----------------------------------------------------------------
# MAIN GAME LOOP
# ----------------------------------------------------------------

while running:
    handle_events() # handles mouse/keyboard events
            
    screen.fill("#4aa855") # green background
    
    if page == "main_menu":
        main_menu_tick() # main menu
    elif page == "in_game":
        in_game_tick() # in game
    elif page == "rules":
        rules_tick() # rules
    elif page == "solutions":
        solutions_display() # solutions
        
    pg.display.flip()
    clock.tick(60)
    
pg.quit() # quit when QUIT event
