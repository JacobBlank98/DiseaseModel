import uuid
import random
import pandas


class Disease(object):
    """
    Any disease object can infect, kill, and change the days_infected of a Person instance depending on
    percent/duration/death passed to the disease.
    """

    def __init__(self, percent=0.2, duration=14, death=0.01):
        assert percent >= 0, "Percent of people initially infected must be >= 0."
        assert duration > 0, "Disease must last for some duration > 0 days."
        assert death >= 0, "Death rate must be >= 0"

        self._percent = percent
        self._duration = duration
        self._death = death
        self._id = uuid.uuid4()

    @property
    def percent(self):
        return self._percent

    @property
    def duration(self):
        return self._duration

    @property
    def death(self):
        return self._death

    @property
    def id(self):
        return self._id

    def set_disease_id(self, Person):
        Person.set_disease_id(self.id)

    def infect(self, Person):
        if random.random() < self.percent and not Person.dead:
            Person.infect()
            Person.set_disease_id(self.id)

    def kill(self, Person):
        if random.random() < self.death and Person.infected:
            Person.kill()
            Person.disinfect()
            Person.set_disease_id(None)

    def pass_day(self, Person):
        if Person.days_infected == self.duration:
            Person.disinfect()
            Person.set_disease_id(None)
        elif Person.days_infected == 0:
            pass
        else:
            Person.add_day()


class Person(object):

    def __init__(self, infected=False, days_infected=0, dead=False):
        assert days_infected >= 0, "Days infected must be >= 0"

        self._infected = infected
        self._days_infected = days_infected
        self._dead = dead
        self._person_location = None
        self._id = uuid.uuid4()
        self._disease_id = list()

    # properties
    @property
    def infected(self):
        return self._infected

    @property
    def days_infected(self):
        return self._days_infected

    @property
    def dead(self):
        return self._dead

    @property
    def person_location(self):
        return self._person_location

    @property
    def id(self):
        return self._id

    @property
    def disease_id(self):
        return self._disease_id

    # infect/disinfect/kill/increase no. days sick
    def infect(self):
        self._infected = True
        self.add_day()

    def disinfect(self):
        self._infected = False
        self._days_infected = 0

    def kill(self):
        self._dead = True

    def add_day(self):
        self._days_infected += 1

    # setting disease id, and person location
    def set_disease_id(self, id):
        self._disease_id.append(id)

    def set_person_location(self, location):
        self._person_location = location


class Location(object):
    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, x):
        assert x >= 0, "x ({}) must be positive".format(x)
        self._x = x

    @y.setter
    def y(self, y):
        assert y >= 0, "y ({}) must be positive".format(y)
        self._y = y


class Map(object):
    __MIN_X = 10  # map must be greater than or equal to 10 x 10
    __MIN_Y = 10

    def __init__(self, max_x, max_y):
        assert max_x >= self.__MIN_X, "max_x must be >= " + str(self.__MIN_X)  # assert that passed max_x & max_y
        assert max_y >= self.__MIN_Y, "max_y must be >= " + str(self.__MIN_Y)  # are >= 10
        self._max_x = max_x
        self._max_y = max_y

        self._map = {}  # self._map = dictionary
        for x in range(self._max_x):  # x index & x number of dictionaries within self._map = dictionary
            self._map[x] = {}
            for y in range(self._max_y):  # y index & y number of dictionaries w/in dict() w/in dict()
                self._map[x][y] = dict()

    def _assert_good_location(self, location):  # asserts location is valid (e.g., less than max_x and max_y)
        assert location.x < self._max_x and location.y < self._max_y, \
            "coordinate ({}, {}) not in ({}, {})".format(location.x, location.y, self._max_x - 1, self._max_y - 1)

    def _space(self, location):
        self._assert_good_location(location)
        return self._map[location.x][location.y]  # returns smallest level dictionary in coordinates specified
        # in location.x and location.y from location class

    @property
    def max_x(self):
        return self._max_x

    @property
    def max_y(self):
        return self._max_y

    def get_people(self):
        """Return list of tuples (location, person) if a person exists in the map somewhere"""
        ret = list()
        for x in range(self._max_x):
            for y in range(self._max_y):
                for person in self._space(Location(x, y)):
                    ret.append((Location(x, y), person))
        return ret

    def set_person(self, location, person):
        assert person.id not in self._space(location), \
            "person {} already in space ({}, {})".format(person.id, location.x, location.y)
        self._space(location)[person.id] = person

    def remove_person(self, location, person):
        assert person.id in self._space(location), \
            "no person {} in space ({}, {})".format(person.id, location.x, location.y)
        del self._space(location)[person.id]

    def move_person(self, prev_location, person):
        self.remove_person(prev_location, person)
        self.set_person(randomize(prev_location), person)


# set disease, map, and population size
coronavirus = Disease(percent=0.99, death=0.1)
coronavirus_map = Map(10, 10)
POP_SIZE = 10

PEOPLE_NAMES = list()


def initialize_simulation(disease, map, population_size):
    names = pandas.read_csv("person_names.csv")

    for i in range(population_size):
        # creating unique person instances w/ names from database
        globals()[names.loc[i]['name']] = Person()
        PEOPLE_NAMES.append(names.loc[i]['name'])

    for i in range(population_size):
        # infecting random subset of population
        disease.infect(globals()[PEOPLE_NAMES[i]])
        disease.kill(globals()[PEOPLE_NAMES[i]])

    for i in range(population_size):
        # random coordinates based on map size
        x = random.randint(0, map.max_x - 1)
        y = random.randint(0, map.max_y - 1)

        # building location instance
        location = Location(x, y)

        # setting person location in Person() instance
        globals()[PEOPLE_NAMES[i]].set_person_location(location)

        # setting person location in map
        map.set_person(location, globals()[PEOPLE_NAMES[i]])


initialize_simulation(disease=coronavirus, map=coronavirus_map, population_size=POP_SIZE)

def randomize(location):
    """
    Takes in class Location(), and returns a new Location() having added random movement.
    """
    val = random.randint(1, 4)
    if val == 1 and location.x != coronavirus_map.max_x - 1:
        location.x = location.x + 1
    elif val == 2 and location.x > 0:
        location.x = location.x - 1
    elif val == 3 and location.y != coronavirus_map.max_y - 1:
        location.y = location.y + 1
    elif val == 4 and location.y > 0:
        location.y = location.y - 1
    else:
        pass
    return location


def contact_coordinates():
    global PEOPLE_NAMES

    coordinates_list = []
    duplicate_coordinates = []

    for i in range(POP_SIZE):
        coordinates_list.append(
            (globals()[PEOPLE_NAMES[i]].person_location.x, globals()[PEOPLE_NAMES[i]].person_location.y))

    for coordinate in coordinates_list:
        if coordinates_list.count(coordinate) > 1:
            duplicate_coordinates.append(coordinate)

    final_coordinates = list(set(duplicate_coordinates))

    return final_coordinates


# returns list of contact pairs (of Person() objects)
def contact_people(final_coordinates):
    duo_temp = []
    contact_pairs = []

    for coordinate in final_coordinates:
        for individual in range(POP_SIZE):
            if (globals()[PEOPLE_NAMES[individual]].person_location.x,
                globals()[PEOPLE_NAMES[individual]].person_location.y) \
                    == (coordinate[0], coordinate[1]) and len(duo_temp) == 0:
                duo_temp.append(individual)
            elif (globals()[PEOPLE_NAMES[individual]].person_location.x,
                  globals()[PEOPLE_NAMES[individual]].person_location.y) \
                    == (coordinate[0], coordinate[1]) and len(duo_temp) != 0:
                duo_temp.append(individual)
                contact_pairs.append((duo_temp[0], duo_temp[1]))
                duo_temp.clear()
            else:
                pass
    return contact_pairs


# infects other person
def contact_infection(contact_pairs):
    for pair in contact_pairs:
        if any((globals()[PEOPLE_NAMES[pair[0]]].infected, globals()[PEOPLE_NAMES[pair[1]]].infected)):
            if globals()[PEOPLE_NAMES[pair[0]]].infected:
                coronavirus.set_disease_id(globals()[PEOPLE_NAMES[pair[1]]])
                globals()[PEOPLE_NAMES[pair[1]]].infect()
            else:
                coronavirus.set_disease_id(globals()[PEOPLE_NAMES[pair[0]]])
                globals()[PEOPLE_NAMES[pair[0]]].infect()
        else:
            pass


DAY = 1

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np

fig = plt.figure()
ax1 = fig.add_subplot(111)


def run_days():
    global POP_SIZE, PEOPLE_NAMES
    for i in range(POP_SIZE):
        coronavirus_map.move_person(globals()[PEOPLE_NAMES[i]].person_location, globals()[PEOPLE_NAMES[i]])
        coronavirus.pass_day(globals()[PEOPLE_NAMES[i]])

    final_coordinates = contact_coordinates()
    contact_pairs = contact_people(final_coordinates)
    contact_infection(contact_pairs)

    for i in range(POP_SIZE):
        coronavirus.kill(globals()[PEOPLE_NAMES[i]])


def give_Xs_and_Ys():
    x = list()
    y = list()
    sick = list()
    for i in range(POP_SIZE):
        x.append(globals()[PEOPLE_NAMES[i]].person_location.x)
        y.append(globals()[PEOPLE_NAMES[i]].person_location.y)
        sick.append(globals()[PEOPLE_NAMES[i]].infected)
    run_days()
    return x, y, sick


# where x = list of x coordinates from first to last
# where y = list of y coordinates form first to last
# sick = 0 or 1 based on whether person is sick or not
def plot_new_coordinate(i):
    x, y, sick = give_Xs_and_Ys()
    ax1.clear()
    plt.ylim(0, coronavirus_map.max_y)
    plt.xlim(0, coronavirus_map.max_x)
    ax1.scatter(x, y, c=sick)


ani = animation.FuncAnimation(fig, plot_new_coordinate, interval=1000)
plt.show()




