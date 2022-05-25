from modules.PlateDetector import PlateDetector
from modules.Constants import Constants
import tkinter as tk


# Function that returns simple format of api's response data
def get_str(JSON):
    # Return json formatted for showing (no json.dumps..)
    st = ''

    for key in JSON:
        st += f'{key}: {JSON[key]}\n'

    return st


# Open new window of car plate detecting
def new_window(var, image_path):
    image = image_path
    pd = PlateDetector(image)
    var.set(get_str(pd.get_car_info()))


# Main loop
def main():

    # Window screen
    ws = tk.Tk()
    ws.title("Car info system")

    # Main canvas
    canvas = tk.Canvas(ws, height=Constants.HEIGHT_INPUT, width=Constants.WIDTH_INPUT)
    canvas.pack()

    # Input field
    inp = tk.Text(ws, height=1)

    # Info display
    info_str = tk.StringVar()
    info = tk.Label(
        ws,
        textvariable=info_str
    )

    # Submit button
    button = tk.Button(
        ws,
        text="Submit path",
        bg='White',
        fg='Black',
        command=lambda: new_window(info_str, inp.get("1.0", 'end-1c')),
    )

    # Pack components and begin mainloop
    info.pack()
    inp.pack()
    button.pack()
    ws.mainloop()


if __name__ == '__main__':
    main()
