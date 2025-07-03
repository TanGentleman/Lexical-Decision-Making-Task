import pandas as pd
from psychopy.gui import DlgFromDict
from psychopy.visual import Window, TextStim, ImageStim, ShapeStim, Circle
from psychopy.core import Clock, quit, wait
from psychopy.event import Mouse, getKeys, clearEvents


### DIALOG BOX ROUTINE ###
exp_info = {'participant_id': '', 'age': ''}
dlg = DlgFromDict(exp_info)

# If pressed Cancel, abort!
if not dlg.OK:
    print("Dialog cancelled, quitting...")
    quit()
else:
    print("Dialog OK, validating input...")
    # Quit when either the participant id or age is not filled in
    if not exp_info['participant_id'] or not exp_info['age']:
        print("Missing participant ID or age, quitting...")
        quit()
        
    # Also quit in case of invalid participant id or age
    if int(exp_info['participant_id']) > 99 or int(exp_info['age']) < 18:
        print("Invalid participant ID or age, quitting...")
        quit()
    else:  # let's start the experiment!
        print(f"Started experiment for participant {exp_info['participant_id']} "
                 f"with age {exp_info['age']}.")

# Initialize a fullscreen window with my monitor (HD format) size
# and my monitor specification called "samsung" from the monitor center
win = Window(size=(1920, 1080), fullscr=False, monitor='samsung')
print("Window created successfully!")

# Also initialize a mouse
mouse = Mouse(visible=True)

# Initialize a (global) clock
clock = Clock()

print("Clearing events...")
clearEvents()
print("Events cleared successfully!")

### START BODY OF EXPERIMENT ###

### WELCOME ROUTINE ###
# Create a welcome screen and show for 2 seconds
welcome_txt_stim = TextStim(win, text="Welcome to this experiment!", font='Calibri')
welcome_txt_stim.draw()
win.flip()
wait(2.0)

### INSTRUCTION ROUTINE ###
instruct_txt = """ 
In this experiment, you will see a string of letters. If the string forms a word, press LEFT.
If the string does not form a word, press RIGHT.
    
(Press ‘enter’ to start the experiment!)
 """

# Show instructions and wait until response (return)
instruct_txt = TextStim(win, instruct_txt, alignText='left', height=0.085)
instruct_txt.draw()
win.flip()

clearEvents()
while True:
    keys = getKeys()
    if 'return' in keys:
        print("Return key was pressed - starting experiment!")
        break

### TRIAL LOOP ROUTINE ###
print("Loading conditions file...")
cond_df = pd.read_excel('word_conditions.xlsx')
cond_df = cond_df.sample(frac=1)

# Create fixation target (a plus sign)
fix_target = TextStim(win, '+')
trial_clock = Clock()

# START exp clock
clock.reset()

# Show initial fixation
fix_target.draw()
win.flip()
wait(1)

correct_txt_stim = TextStim(win, text="correct", color=(0, 255, 0), font='Calibri')
incorrect_txt_stim = TextStim(win, text = "incorrect", color=(255,0,0), font='calibri')

for idx, row in cond_df.iterrows():
    # Extract current word and whether its a word

    curr_stim = row['stim']
    curr_word = row['word']

    # Create and draw text
    stim_txt = TextStim(win, curr_stim, pos=(0, 0.3))

    # Initially, onset is undefined
    cond_df.loc[idx, 'onset'] = -1

    trial_clock.reset()
    clearEvents()
    response_given = False

    while trial_clock.getTime() < 2 and not response_given:
        if trial_clock.getTime() < 0.5:
            stim_txt.draw()
        else:
            fix_target.draw()
            
        win.flip()
        if cond_df.loc[idx, 'onset'] == -1:
            cond_df.loc[idx, 'onset'] = clock.getTime()

        keys = getKeys(timeStamped=trial_clock)
        if keys:
            key_name, key_time = keys[0]
            print(f"Key {key_name} pressed at {key_time:.3f} seconds.")

            if key_name == 'q':
                print("Quit key pressed, exiting...")
                quit()

            cond_df.loc[idx, 'rt'] = key_time
            cond_df.loc[idx, 'resp'] = key_name
            response_given = True

            if key_name == 'left' and curr_word == 'yes':
                cond_df.loc[idx, 'correct'] = 1
                correct_txt_stim.draw()
                win.flip()
                wait(2)

            elif key_name == 'right' and curr_word == 'no':
                cond_df.loc[idx, 'correct'] = 1
                correct_txt_stim.draw()
                win.flip()
                wait(2)
                
            else:
                cond_df.loc[idx, 'correct'] = 0
                incorrect_txt_stim.draw()
                win.flip()
                wait(2)
        
effect = cond_df.groupby('word').mean(numeric_only=True)
rt_con = effect.loc['yes', 'rt']
rt_incon = effect.loc['no', 'rt']
acc = cond_df['correct'].mean()

cond_df['rt_word'] = rt_con #print means to the excel sheet

#3f means printing to 3 decimal places as a string (f)
txt = f""" 
Your reaction times are as follows:

    Real Words: {rt_con:.3f} 
    Fake words: {rt_incon:.3f}

Overall accuracy: {acc:.3f}
"""
result = TextStim(win, txt)
result.draw()
win.flip()
wait(2)

cond_df.to_csv(f"sub-{exp_info['participant_id']}_results.csv")


# Show instructions and wait
instruct1_txt = TextStim(win, text="thank you for participating", alignText='left', height=0.085)
instruct1_txt.draw()
win.flip()
wait(3.0)

instruct2_txt = TextStim(win, text="Click green if you enjoyed the experiment and red if you didn't!", alignText='left', pos=(0,0.5), height=0.085)

red_circle = Circle(win=win, units="pix", radius=50, fillColor=[1, 0, 0],
lineColor=[1, 0, 0],pos=(-50,0)) # Change radius and color as desired

green_circle = Circle(win=win, units="pix", radius=50, fillColor=[0, 1, 0],
lineColor=[0, 1, 0],pos=(100,0)) # Change radius and color as desired

instruct2_txt.draw()
green_circle.draw()
red_circle.draw()
win.flip()
wait(5)

while True:
    if mouse.isPressedIn(green_circle):
        instruct_yay_txt = TextStim(win, text=":)", height=0.085)
        instruct_yay_txt.draw()
        win.flip()
        wait(3.0)
        break
    if mouse.isPressedIn(red_circle):
        instruct_nay_txt = TextStim(win, text=":(", height=0.085)
        instruct_nay_txt.draw()
        win.flip()
        wait(3.0)
        break # This stops the routine from continuing


# Finish experiment by closing window and quitting
win.close()
quit()  