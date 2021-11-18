# coding: utf-8
# license: GPLv3

import pygame as pg
from solar_vis import *
from solar_model import *
from solar_input import *
from solar_objects import *
from graphics import draw_garphic, graphic
import thorpy
import time
import numpy as np

timer = None

alive = True

perform_execution = False
"""Флаг цикличности выполнения расчёта"""

model_time = 0
"""Физическое время от начала расчёта.
Тип: float"""

time_scale = 1000.0
"""Шаг по времени при моделировании.
Тип: float"""

space_objects = []
"""Список космических объектов."""


def execution(delta):
    """Функция исполнения -- выполняется циклически, вызывая обработку всех небесных тел,
    а также обновляя их положение на экране.
    Цикличность выполнения зависит от значения глобальной переменной perform_execution.
    При perform_execution == True функция запрашивает вызов самой себя по таймеру через от 1 мс до 100 мс.
    """
    global model_time
    global displayed_time
    recalculate_space_objects_positions([dr.obj for dr in space_objects], delta)
    model_time += delta


def start_execution():
    """Обработчик события нажатия на кнопку Start.
    Запускает циклическое исполнение функции execution.
    """
    global perform_execution
    perform_execution = True

def pause_execution():
    global perform_execution
    perform_execution = False

def stop_execution():
    """Обработчик события нажатия на кнопку Start.
    Останавливает циклическое исполнение функции execution.
    """
    global alive
    alive = False


def open_file_solar_solar_system(in_filename="solar_system.txt"):
    """Открывает диалоговое окно выбора имени файла и вызывает
    функцию считывания параметров системы небесных тел из данного файла.
    Считанные объекты сохраняются в глобальный список space_objects
    """
    global space_objects
    global browser
    global model_time
    k = 0.5
    print(in_filename)
    model_time = 0.0
    space_objects = read_space_objects_data_from_file(in_filename)
    max_distance = max([max(abs(obj.obj.x), abs(obj.obj.y)) for obj in space_objects])
    calculate_scale_factor(k, max_distance)


def calculate_planet_v(space_objects):
    satellite_vx = None
    satellite_vy = None
    if len(space_objects) > 0:
        satellite_vx = space_objects[1].obj.Vx
        satellite_vy = space_objects[1].obj.Vy
        return (satellite_vx**2 + satellite_vy**2)**(1/2)


def calculate_planet_r(space_objects):
    global satellite_r
    satellite_r = None
    if len(space_objects) > 0:
        satellite_r = ((space_objects[1].obj.x - space_objects[0].obj.x)**2
        + (space_objects[1].obj.y - space_objects[0].obj.y)**2)**(1/2)
        return satellite_r
        



def open_file_double_star(in_filename = "double_star.txt"):
    """Открывает диалоговое окно выбора имени файла и вызывает
    функцию считывания параметров системы небесных тел из данного файла.
    Считанные объекты сохраняются в глобальный список space_objects
    """
    k = 0.05
    global space_objects
    global browser
    global model_time
    print(in_filename)
    model_time = 0.0
    space_objects = read_space_objects_data_from_file(in_filename)
    max_distance = max([max(abs(obj.obj.x), abs(obj.obj.y)) for obj in space_objects])
    calculate_scale_factor(k, max_distance)


def open_file_one_satellite(in_filename = "one_satellite.txt"):
    """Открывает диалоговое окно выбора имени файла и вызывает
    функцию считывания параметров системы небесных тел из данного файла.
    Считанные объекты сохраняются в глобальный список space_objects
    """
    k = 0.3
    global space_objects
    global browser
    global model_time
    print(in_filename)
    model_time = 0.0
    space_objects = read_space_objects_data_from_file(in_filename)
    max_distance = max([max(abs(obj.obj.x),abs(obj.obj.y)) for obj in space_objects])
    calculate_scale_factor(k, max_distance)

def handle_events(events, menu):
    global alive
    for event in events:
        menu.react(event)
        if event.type == pg.QUIT:
            alive = False

def slider_to_real(val):
    return np.exp(5 + val)

def slider_reaction(event):
    global time_scale
    time_scale = 2*slider_to_real(event.el.get_value())

def init_ui(screen):
    global browser
    slider = thorpy.SliderX(100, (-10, 10), "Simulation speed")
    slider.user_func = slider_reaction
    button_stop = thorpy.make_button("Quit", func=stop_execution)
    button_pause = thorpy.make_button("Pause", func=pause_execution)
    button_play = thorpy.make_button("Play", func=start_execution)
    timer = thorpy.OneLineText("Seconds passed")

    button_load_solar_system = thorpy.make_button(text="Load file 'solar_system'", func=open_file_solar_solar_system)

    button_load_double_star = thorpy.make_button(text="Load a file 'double_star'", func=open_file_double_star)

    button_load_one_satellite = thorpy.make_button(text="Load a file 'one_satellite'", func=open_file_one_satellite)

    box = thorpy.Box(elements=[
        slider,
        button_pause, 
        button_stop, 
        button_play, 
        button_load_solar_system,
        button_load_double_star,
        button_load_one_satellite,
        timer])
    reaction1 = thorpy.Reaction(reacts_to=thorpy.constants.THORPY_EVENT,
                                reac_func=slider_reaction,
                                event_args={"id":thorpy.constants.EVENT_SLIDE},
                                params={},
                                reac_name="slider reaction")
    box.add_reaction(reaction1)
    menu = thorpy.Menu(box)
    for element in menu.get_population():
        element.surface = screen

    box.set_topleft((0, 0))
    box.blit()
    box.update()
    return menu, box, timer

def main():
    """Главная функция главного модуля.
    Создаёт объекты графического дизайна библиотеки pygame: окно, холст, фрейм с кнопками, кнопки.
    """
    
    global physical_time
    global displayed_time
    global time_step
    global time_speed
    global space
    global start_button
    global perform_execution
    global timer
    global steps

    print('Modelling started!')
    physical_time = 0

    pg.init()

    width = 1000
    height = 800
    steps = 0
    screen = pg.display.set_mode((width, height))
    last_time = time.perf_counter()
    drawer = Drawer(screen)
    menu, box, timer = init_ui(screen)
    perform_execution = True

    while alive:
        handle_events(pg.event.get(), menu)
        cur_time = time.perf_counter()
        if perform_execution:
            execution((cur_time - last_time) * time_scale)
            text = "%d seconds passed" % (int(model_time))
            timer.set_text(text)
        last_time = cur_time
        drawer.update(space_objects, box)
        graphic(calculate_planet_v(space_objects), calculate_planet_r(space_objects), model_time)
    print('Modelling finished!')
    draw_garphic()

if __name__ == "__main__":
    main()