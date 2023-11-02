import os
import pygame
import time
import random
import RPi.GPIO as GPIO

# 파일 이름과 경로 설정
file_names = ["0001_t.wav", "0002_t.wav", "0003_t.wav", "0004_t.wav", "0005_t.wav", "0006_t.wav", "0007_t.wav"]
file_paths = [os.path.join("/Users/bae_sunguk/Desktop/iosTest/wav", name) for name in file_names]

# 초기화 및 사운드 객체 생성
pygame.init()
pygame.mixer.init()
sounds = [pygame.mixer.Sound(path) for path in file_paths]

# 사운드 재생 함수
def play_random_sound():
    sound = random.choice(sounds)
    sound.set_volume(0.5)
    sound.play()
    time.sleep(5)
    sound.stop()

# 랜덤하게 사운드 재생
play_random_sound()