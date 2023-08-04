import math
import pygame
import os
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip
import random
import pygame.mixer
from pydub import AudioSegment


def pan_audio(audio_path, pan_value):
    audio = AudioSegment.from_file(audio_path)
    
    # If audio is not stereo, convert it to stereo
    if audio.channels == 1:
        audio = audio.set_channels(2)

    # Define pan with left and right values
    pan_left = max(min(1 - pan_value, 1), 0)
    pan_right = max(min(1 + pan_value, 1), 0)

    # Apply pan
    audio = audio.pan(pan_value)

    # Create the panned audio by adjusting the volume of each channel
    left = audio.split_to_mono()[0].apply_gain(pan_left)
    right = audio.split_to_mono()[1].apply_gain(pan_right)

    # Combine the left and right channels to create a stereo track
    panned_audio = AudioSegment.from_mono_audiosegments(left, right)

    return panned_audio


# Pygame setup
# this line makes pygame not open a window
pygame.init()
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.display.init()

# Enable alpha for the screen
pygame.display.set_mode((0, 0), pygame.NOFRAME | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SRCALPHA)

# Define constants
WIDTH, HEIGHT = 1080, 1920
FPS = 60
DURATION = 58  # duration of the video in seconds
TOTAL_FRAMES = DURATION * FPS  # total frames in the video

BORDER_WIDTH = 5  # border width in pixels
BORDER_DIMENSION = 950  # dimension of the border (it's a square)

BORDER_X = (WIDTH - BORDER_DIMENSION) // 2
BORDER_Y = (HEIGHT - BORDER_DIMENSION) // 2

# Colors
RAINBOW_COLORS = [
    (255, 0, 0),      # red
    (255, 127, 0),    # orange
    (255, 255, 0),    # yellow
    (127, 255, 0),    # spring green
    (0, 255, 0),      # green
    (0, 255, 127),    # turquoise
    (0, 255, 255),    # cyan
    (0, 127, 255),    # ocean
    (0, 0, 255),      # blue
    (127, 0, 255),    # violet
    (255, 0, 255),    # magenta
    (255, 0, 127),    # rose
]

# Load the sound files
note_num = 12
NOTE_SOUNDS_PATHS = [f'C:\\Users\\lodos\\Desktop\\Project_Bounce\\audio\\chosen_music_box\\note{i % 7}.wav' for i in range(note_num)]
NOTE_SOUNDS = [pygame.mixer.Sound(path) for path in NOTE_SOUNDS_PATHS]
NOTE_AUDIOCLIPS = [AudioFileClip(path) for path in NOTE_SOUNDS_PATHS]


pygame.mixer.init(channels=note_num+1)

# Create channels for each note
CHANNELS = [pygame.mixer.find_channel() for _ in range(note_num)]
for channel in CHANNELS:
    if channel is None:
        print("Could not create a new channel.")

scheduled_sounds = []

# Create the Pygame screen
screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Define the squares
class Square:
    def __init__(self, x, y, vx, vy, color, alpha):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.alpha = alpha

squares = []
square_size = 100
direction_x = random.choice([-1, 1])
direction_y = random.choice([-1, 1])

# Create a circle of squares with rainbow colors
radius = 300
center_x = WIDTH // 2
center_y = HEIGHT // 2
angle_increment = 2 * math.pi / note_num  # divide the circle into 7 parts
for i in range(note_num):  # create 12 squares
    angle = i * angle_increment
    # adjust for square's size
    x = center_x + radius * math.cos(angle) - square_size // 2
    # adjust for square's size
    y = center_y + radius * math.sin(angle) - square_size // 2
    velocity_x = random.randint(1, 10)
    if velocity_x >= 5:
        velocity_y = random.randint(1, 10)
    else:
        velocity_y = random.randint(5, 10)

    vx = direction_x * velocity_x
    vy = direction_y * velocity_y
    color = RAINBOW_COLORS[i % 12]
    alpha = 0  # initial transparency
    squares.append(Square(x, y, vx, vy, color, alpha))

frames = []

# Game loop
for frame_number in range(TOTAL_FRAMES):

    # Draw everything
    screen.fill((173, 216, 230, 255))  # fill the screen with light blue
    pygame.draw.rect(screen, (255, 255, 255, 255), pygame.Rect(BORDER_X + BORDER_WIDTH, BORDER_Y + BORDER_WIDTH,
                     BORDER_DIMENSION - 2 * BORDER_WIDTH, BORDER_DIMENSION - 2 * BORDER_WIDTH))  # fill the area inside the border with white

    for i, square in enumerate(squares):
        # Predict the next position of the square
        next_x = square.x + square.vx
        next_y = square.y + square.vy

        # Check if the square will hit the border in the next frame
        if next_x < BORDER_X or next_x + square_size > BORDER_X + BORDER_DIMENSION:
            square.vx *= -1
            square.alpha = 255
            # Calculate the panning based on the x position of the square
            pan = 2 * (square.x - BORDER_X) / BORDER_DIMENSION - 1

            panned_audio = pan_audio(NOTE_SOUNDS_PATHS[i], pan)


            scheduled_sounds.append((frame_number / FPS -0.5, panned_audio))

        if next_y < BORDER_Y or next_y + square_size > BORDER_Y + BORDER_DIMENSION:
            square.vy *= -1
            square.alpha = 255
            # Calculate the panning based on the x position of the square even for top and bottom collisions
            pan = 2 * (square.x - BORDER_X) / BORDER_DIMENSION - 1

            panned_audio = pan_audio(NOTE_SOUNDS_PATHS[i], pan)

            scheduled_sounds.append((frame_number / FPS -0.5, panned_audio))
        # Update the square's position
        square.x += square.vx
        square.y += square.vy
        # Define the border thickness
        border_thickness = 3

        # Decrease the square's alpha to make it fade away gradually
        square.alpha = max(100, square.alpha - 2)

        # Create a new surface for the square
        square_surf = pygame.Surface((square_size, square_size), pygame.SRCALPHA)

        # Draw the border of the square on the new surface
        pygame.draw.rect(square_surf, square.color + (square.alpha,), square_surf.get_rect())

        # Draw the inner part of the square on the new surface
        inner_rect = pygame.Rect(border_thickness, border_thickness, square_size - 2*border_thickness, square_size - 2*border_thickness)
        pygame.draw.rect(square_surf, square.color + (square.alpha,), inner_rect)

        # Blit the square surface onto the main screen
        screen.blit(square_surf, (square.x, square.y))

    border_color = (0, 255, 0, 255)
    pygame.draw.rect(screen, border_color, pygame.Rect(BORDER_X, BORDER_Y, BORDER_DIMENSION, BORDER_WIDTH))
    pygame.draw.rect(screen, border_color, pygame.Rect(BORDER_X, BORDER_Y + BORDER_DIMENSION - BORDER_WIDTH, BORDER_DIMENSION, BORDER_WIDTH))
    pygame.draw.rect(screen, border_color, pygame.Rect(BORDER_X, BORDER_Y, BORDER_WIDTH, BORDER_DIMENSION))
    pygame.draw.rect(screen, border_color, pygame.Rect(BORDER_X + BORDER_DIMENSION - BORDER_WIDTH, BORDER_Y, BORDER_WIDTH, BORDER_DIMENSION))

    pygame.image.save(screen, "frame{}.jpg".format(len(frames)))
    frames.append("frame{}.jpg".format(len(frames)))

# Make video from frames
clip = ImageSequenceClip(frames, fps=FPS)
# Create a list to hold the final audio clips
final_audio_clips = []


# Create a base sound
base_sound = AudioSegment.silent(duration=DURATION * 1000)  # duration in milliseconds

# Overlay each sound onto the base sound
for start_time, sound in scheduled_sounds:
    start_time_ms = int(start_time * 1000)  # convert to milliseconds
    base_sound = base_sound.overlay(sound, position=start_time_ms)

# Export the final sound to a WAV file
base_sound.export("final_audio.wav", format="wav")


# Create a composite audio clip from the final audio clips
final_audio = AudioFileClip("final_audio.wav")
final_audio = final_audio.subclip(0, DURATION)  # get the first 60 seconds of the audio
clip = clip.set_audio(final_audio)

# Write the video file
clip.set_duration(DURATION).write_videofile("output.mp4")

# Delete frames after making video
for frame in frames:
    os.remove(frame)
