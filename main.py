# Musicplayer_controlled_by_hand_gesture
# Computer Vision final term project
# Last Modified : 2024.05.12
# Author : CheerUpBee


import pygame
import os
import sys
import cv2 as cv
import mediapipe as mp
import numpy as np
import time
import threading
#from mediapipe.tasks import python
from mediapipe.tasks.python import vision
#import pyautogui


TASK_FILE_PATH=''
MUSIC_FOLDER_PATH=''


gesture_count = {
    "Thumb_Up": 0, # Previous music
    "Thumb_Down": 0, # Next music
    "Open_Palm": 0, # Play or Pause
    "Closed_Fist": 0, # Exit
    "Victory": 0 # Stop
}

THRESHOLD = 40 # Minimum number of gesture repetitions

current_gesture="Dummy" # Dummy string for initialization

# Callback function for async recognizer
def print_result(result: mp.tasks.vision.GestureRecognizerResult,output_image: mp.Image, timestamp_ms: int):
    if result.gestures:
        g=result.gestures[-1][-1].category_name
        if g in gesture_count:
            gesture_count[g]+=1
            if(gesture_count[g]>THRESHOLD):
                for key in gesture_count:
                    gesture_count[key] = 0
                execute_command(g)
                print(f'Gesture: {g}') 

def execute_command(gesture):
    global current_gesture
    # Keyboard input(not used)
    '''
    if gesture == "Thumb_Up":
        pyautogui.keyDown('space')
        pyautogui.keyUp('space')
        #print(gesture+" Executed: Next Music")
    elif gesture == "Thumb_Down":
        pyautogui.keyDown('enter')
        pyautogui.keyUp('enter')
        #print(gesture+" Executed: Previous Music")
    elif gesture == "Open_Palm":
        pyautogui.keyDown('space')
        pyautogui.keyUp('space')  # space
        #print(gesture+" Executed: Pause or Play")
    elif gesture == "Victory":
        pyautogui.keyDown('s')
        pyautogui.keyUp('s')  # s
        #print(gesture+" Executed: Stop")        
    elif gesture == "Closed_Fist":
        pyautogui.keyDown('esc')
        pyautogui.keyUp('esc')
        print(gesture+" Executed: esc")
    '''
    update_gesture(gesture)


# Standard callback function from Mediapipe example(Not used)
# reference: https://developers.google.com/mediapipe/solutions/vision/gesture_recognizer/python
'''
def print_result(result: mp.tasks.vision.GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    print('gesture recognition result: {}'.format(result))
'''


# Recognizer generation by vision.GestureRecognizerOptions
# Model reference: https://developers.google.com/mediapipe/solutions/vision/gesture_recognizer#get_started
base_options = mp.tasks.BaseOptions(model_asset_path=TASK_FILE_PATH)
options = vision.GestureRecognizerOptions(
    base_options=base_options,
    running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
    result_callback=print_result
    )
recognizer = vision.GestureRecognizer.create_from_options(options)

# Recognizer for image(Not used, deprecated)
'''
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
'''
# mp_drawing = mp.solutions.drawing_utils

##############################################################
# Camera function
def camera():
    global current_gesture
    cap = cv.VideoCapture(0)
    while True:
        
        ret, frame = cap.read()
        if not ret:
            print("No frame from camera")
            continue
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        timestamp_ms = int(time.time() * 1000)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        cv.imshow('Camera',cv.resize(frame,(640,480)))
        recognizer.recognize_async(mp_image, timestamp_ms)
        if (cv.waitKey(1) & 0xFF == 27) or current_gesture=="Closed_Fist":
            break
    
    cap.release()
    cv.destroyAllWindows()

##############################################################

# Folder path
path=MUSIC_FOLDER_PATH

# Music player state(Stopped, Playing, Paused)
current_state="Stopped"

# Music
music_files = [m for m in os.listdir(path) if m.endswith('.mp3')]
current_track=0

##############################################################
# Funcionts for music player
def play_music():
    global current_state
    file_path = os.path.join(path, music_files[current_track])
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()

    current_state="Playing"

def stop_music():
    global current_state
    pygame.mixer.music.stop()
    current_state="Stopped"

def pause_music():
    global current_state
    pygame.mixer.music.pause()
    current_state="Paused"

def unpause_music():
    global current_state
    if(current_state=="Stopped"):
        play_music()
    else:
        pygame.mixer.music.unpause()
    current_state="Playing"

def next_track():
    global current_track
    global current_state
    current_track = (current_track + 1) % len(music_files)
    temp=current_state
    stop_music()
    if(temp=="Playing"):
        play_music()
    elif(temp=="Paused"):
        play_music()
        pause_music()
    print(current_track)


def previous_track():
    global current_track
    global current_state
    if current_track==0:
        current_track=len(music_files)-1
    else:
        current_track = (current_track - 1) % len(music_files)
    temp=current_state
    stop_music()
    if(temp=="Playing"):
        play_music()
    elif(temp=="Paused"):
        play_music()
        pause_music()
    print(current_track)

##########################################################

##########################################################
# Multi-thread handling
def update_gesture(new_gesture):
    global current_gesture
    with threading.Lock():
        current_gesture = new_gesture

def get_gesture():
    with threading.Lock():
        return current_gesture
##########################################################


##########################################################
# Print Music directory and playable list
print(f"Path:{path}")
print("Playable Music Tracks:")
for index, file in enumerate(music_files):
    print(f"{index + 1}: {file}")
##########################################################

##########################################################
# Pygame for Music Player
def player():
    pygame.init()
    pygame.mixer.init()
    size=[1000,600]
    screen=pygame.display.set_mode(size)
    title="Music player"
    clock=pygame.time.Clock()
    pygame.display.set_caption(title)
    font = pygame.font.SysFont("malgungothic", 36)
    pygame.display.flip()
    
    running=True
    play_music()
    pause_music()
    while running:
        screen.fill((0,0,0))
        text_track = font.render('Track'+str(current_track+1)+' : '+music_files[current_track], True, (255, 255, 255))
        text_state = font.render(current_state, True, (255, 255, 255))
        screen.blit(text_track, (50, 0))
        screen.blit(text_state, (50, 40))
        for index, track in enumerate(music_files):
            y_position = 100 + index * 40 
            track_text = font.render(f"{index + 1}: {track}", True, (255, 255, 0) if index == current_track else (255, 255, 255))
            screen.blit(track_text, (50, y_position))        
        pygame.display.flip()
        
        # Control by camera
        if get_gesture()=="Open_Palm":
            if pygame.mixer.music.get_busy():
                        pause_music()
                        update_gesture("Dummy")
            else:
                        unpause_music()
                        update_gesture("Dummy")
        elif get_gesture()=="Thumb_Down":
            next_track()
            update_gesture("Dummy")
        elif get_gesture()=="Thumb_Up":
            previous_track()
            update_gesture("Dummy")
        elif get_gesture()=="Victory":
            stop_music()
            update_gesture("Dummy")
        elif get_gesture()=="Closed_Fist":
            running=False
        
        # Control by keyboard
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if pygame.mixer.music.get_busy():
                        pause_music()
                    else:
                        unpause_music()
                elif event.key == pygame.K_UP:
                    next_track()
                elif event.key == pygame.K_DOWN:
                    previous_track()
                elif event.key == pygame.K_s:
                    stop_music()
                elif event.key == pygame.K_ESCAPE:
                    running=False
        clock.tick(60)
##########################################################

##########################################################
# Main
t1=threading.Thread(target=camera)
t2=threading.Thread(target=player)

t1.start()
t2.start()

t1.join()
t2.join()

pygame.quit()
sys.exit()
