import cx_Freeze

executables = [cx_Freeze.Executable("game.py")]

cx_Freeze.setup(
    name = "Ultra Racing Car Game",
    options = {"build_exe": {"packages": ["pygame"], "include_files": ["racecar.png", "ComicRelief-Bold.ttf","Crash.mp3","game_music.mp3", "truck.png", "sedan.png", "game_introbackground.png", "icon.png", "microphone.png"]}},
    executables = executables
)