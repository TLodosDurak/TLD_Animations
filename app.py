import math
import pygame
import os
from moviepy.editor import ImageSequenceClip
import random
import pygame.mixer

# Pygame setup
# this line makes pygame not open a window
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()

# Initialize the Pygame mixer
pygame.mixer.init()


# Enable alpha for the screen so that we can use transparent colors
pygame.display.set_mode((0, 0), pygame.NOFRAME |
                        pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.SRCALPHA)

# Define constants
WIDTH, HEIGHT = 1080, 1920
FPS = 60
DURATION = 5  # duration of the video in seconds
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
NOTE_SOUNDS = [pygame.mixer.Sound(
    r'C:\Users\lodos\Desktop\Project Bounce\audio\chosen_notes\note{}.ogg'.format(i)) for i in range(12)]


# Create the Pygame screen
# use Surface instead of display, and enable alpha
screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Define the squares


class Square:
    def __init__(self, x, y, vx, vy, color, alpha):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.alpha = alpha  # add alpha attribute to represent transparency


squares = []
square_size = 100
direction_x = random.choice([-1, 1])
direction_y = random.choice([-1, 1])

# Create a circle of squares with rainbow colors
radius = 300
center_x = WIDTH // 2
center_y = HEIGHT // 2
angle_increment = 2 * math.pi / 12  # divide the circle into 12 parts
for i in range(12):  # create 12 squares
    angle = i * angle_increment
    # adjust for square's size
    x = center_x + radius * math.cos(angle) - square_size // 2
    # adjust for square's size
    y = center_y + radius * math.sin(angle) - square_size // 2
    vx = direction_x * random.randint(4, 6)
    vy = direction_y * random.randint(4, 6)
    color = RAINBOW_COLORS[i]
    alpha = 40  # initial transparency
    squares.append(Square(x, y, vx, vy, color, alpha))

frames = []  # List to store frames

# Game loop
for _ in range(TOTAL_FRAMES):

    # Draw everything
    screen.fill((173, 216, 230, 255))  # fill the screen with light blue
    pygame.draw.rect(screen, (255, 255, 255, 255), pygame.Rect(BORDER_X + BORDER_WIDTH, BORDER_Y + BORDER_WIDTH,
                     BORDER_DIMENSION - 2 * BORDER_WIDTH, BORDER_DIMENSION - 2 * BORDER_WIDTH))  # fill the area inside the border with white

    # use enumerate to get the index of the square
    for i, square in enumerate(squares):
        # Predict the next position of the square
        next_x = square.x + square.vx
        next_y = square.y + square.vy

        # Check if the square will hit the border in the next frame
        if next_x < BORDER_X or next_x + square_size > BORDER_X + BORDER_DIMENSION:
            square.vx *= -1
            square.alpha = 255  # make square fully visible
            NOTE_SOUNDS[i].play()  # Play the corresponding note sound

        if next_y < BORDER_Y or next_y + square_size > BORDER_Y + BORDER_DIMENSION:
            square.vy *= -1
            square.alpha = 255  # make square fully visible
            NOTE_SOUNDS[i].play()  # Play the corresponding note sound

        # Update the square's position
        square.x += square.vx
        square.y += square.vy

        # Decrease the square's alpha to make it fade away gradually
        square.alpha = max(178, square.alpha - 1)

        # Draw the square
        # create a new Surface for the square, with alpha enabled
        square_surf = pygame.Surface(
            (square_size, square_size), pygame.SRCALPHA)
        # fill it with the square's color and alpha
        square_surf.fill((*square.color, square.alpha))
        # blit the square's Surface onto the screen
        screen.blit(square_surf, (square.x, square.y))

    # Draw the border
    border_color = (0, 255, 0, 255)  # green with full opacity
    pygame.draw.rect(screen, border_color, pygame.Rect(
        BORDER_X, BORDER_Y, BORDER_DIMENSION, BORDER_WIDTH))  # top
    pygame.draw.rect(screen, border_color, pygame.Rect(BORDER_X, BORDER_Y +
                     BORDER_DIMENSION - BORDER_WIDTH, BORDER_DIMENSION, BORDER_WIDTH))  # bottom
    pygame.draw.rect(screen, border_color, pygame.Rect(
        BORDER_X, BORDER_Y, BORDER_WIDTH, BORDER_DIMENSION))  # left
    pygame.draw.rect(screen, border_color, pygame.Rect(
        BORDER_X + BORDER_DIMENSION - BORDER_WIDTH, BORDER_Y, BORDER_WIDTH, BORDER_DIMENSION))  # right

    # Save the current frame
    pygame.image.save(screen, "frame{}.jpg".format(len(frames)))
    frames.append("frame{}.jpg".format(len(frames)))

# Make video from frames
clip = ImageSequenceClip(frames, fps=FPS)
clip.write_videofile("output.mp4")

# Delete frames after making video
for frame in frames:
    os.remove(frame)
