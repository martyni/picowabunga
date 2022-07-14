from browser import document as doc
from browser import timer
import random
canvas = doc["plotarea"]
ctx = canvas.getContext("2d")

def get_temp():
   temp = open('temp').read()
   print(temp)
   #document['temp'].value = temp
   temp = float(temp)/2
   graph(temp)

## After doing this I saw that this could be achieved using
## translate(0,canvas.height); scale(1,-1);
## https://developer.mozilla.org/en-US/docs/HTML/Canvas/Tutorial/Transformations
def change_ref_system(x, y):
    return (20 + x * 8, 420 - y * 20)

def draw_line(x1, y1, x2, y2, linethick = 3, color = "black"):
    ctx.beginPath()
    ctx.lineWidth = linethick
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.strokeStyle = color
    ctx.stroke()

def axis(color = "black", linethick = 3):
    #Draw of x axis
    draw_line(20, 420, 820, 420, linethick = linethick, color = color)
    #Draw of y axis
    draw_line(20, 100, 20, 420, linethick = linethick, color = color)

def axis_color(ev):
    axis(color = doc["axis_color"].value)

def figure_title():
    ctx.clearRect(410, 0, 400, 30)
    ctx.fillStyle = "gray"
    ctx.font = "bold 16px Arial"
    ctx.fillText(doc["titletext"].value, 410, 20)

def title_update(ev):
    figure_title()

dataset = []
def graph(data):
    data = str(data)[0:5]
    data = float(data)
    print('graph function')

    doc["console"] <= '%s, ' % str(data)[0:5]
    dataset.append(data)
    if len(dataset) == 1:
        x, y = change_ref_system(len(dataset), data)
        draw_line(x, y, x, y, linethick=3, color="blue")
    else:
        x1, y1 = change_ref_system(len(dataset)-1, dataset[-2])
        x2, y2 = change_ref_system(len(dataset), data)
        draw_line(x1, y1, x2, y2, linethick=3, color="blue")
    if len(dataset) >= 100:
        timer.clear_interval(work)


axis()
figure_title()
work = timer.set_interval(get_temp, 3000)

doc['btn-axis'].bind('click', axis_color)
doc['btn-title'].bind('click', title_update) 
   