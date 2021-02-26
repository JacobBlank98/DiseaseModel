import random
import pygame
import math
import xlsxwriter

POPULATION_SIZE = 200
WIDTH = 640  # game window width
HEIGHT = 480  # game window height
FPS = 30  # game's speeds
Person_Radius = 4
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # set the game window

RED = (255, 100, 100)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 128)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)


def circle_collide(p1, p2):
    collision_distance = 0.0 + p1.radius + p2.radius
    distance = math.hypot(p1.person_location.x - p2.person_location.x, p1.person_location.y - p2.person_location.y)
    if distance >= collision_distance:
        return False
    elif distance < collision_distance:
        return True


def move_now(person, movement_probability=0.2):
    """
    If given person instance, moves the person (according to probability of movement passed). Taken mostly from https://stackoverflow.com/questions/30015787/random-movement-pygame
    """
    Generator_Bias_Offset = random.random() - 0.1

    directions = {"S": ((-1, 2), (1, person.speed)), "SW": ((-person.speed, -1), (1, person.speed)),
                  "W": ((-person.speed, -1), (-1, 2)), "NW": ((-person.speed, -1), (-person.speed, -1)),
                  "N": ((-1, 2), (-person.speed, -1)), "NE": ((1, person.speed), (-person.speed, -1)),
                  "E": ((1, person.speed), (-1, 2)), "SE": ((1, person.speed), (1, person.speed))}

    directions_keys = ("S", "SW", "W", "NW", "N", "NE", "E", "SE")

    """
    Decides where person will move.
    """
    if random.random() < movement_probability:
        if person.direction is None:
            person.direction = random.choice(directions_keys)
        else:
            direction_index = directions_keys.index(person.direction)
            direction_index = random.randrange(direction_index - 1, direction_index + 2) # Don't want people going in opposite direction
            if direction_index > len(directions_keys) - 1:
                direction_index = 0
            person.direction = directions_keys[direction_index]

        person.move[0] = round(random.randrange(directions[person.direction][0][0],
                                                directions[person.direction][0][1]) + Generator_Bias_Offset)
        person.move[1] = round(random.randrange(directions[person.direction][1][0],
                                                directions[person.direction][1][1]) + Generator_Bias_Offset)

    """
    Prevents person from leaving map.
    """
    if person.person_location.x < 5 or person.person_location.x > WIDTH - 5 or person.person_location.y < 5 + HEIGHT // 5 or person.person_location.y > HEIGHT - 5:
        if person.person_location.x < 5:
            person.direction = "E"
        elif person.person_location.x > WIDTH - 5:
            person.direction = "W"
        elif person.person_location.y < 5 + HEIGHT // 5:
            person.direction = "S"
        elif person.person_location.y > HEIGHT - 5:
            person.direction = "N"

        person.move[0] = round(
            random.randrange(directions[person.direction][0][0], directions[person.direction][0][1]) + \
            Generator_Bias_Offset)
        person.move[1] = round(
            random.randrange(directions[person.direction][1][0], directions[person.direction][1][1]) + \
            Generator_Bias_Offset)
    """
    Moves person.
    """
    if person.move[0] is not None:
        person.person_location.x += person.move[0]
        person.person_location.y += person.move[1]


# Any disease object can infect, kill, and change the days_infected of a Person instance depending on
# percent/duration/death passed to the disease.
class Disease(object):

    def __init__(self, startRate=0.2, duration=14, death=0.01, transmission = 0.01):
        assert startRate >= 0, "Percent of people initially infected must be >= 0."
        assert duration > 0, "Disease must last for some duration > 0 days."
        assert death >= 0, "Death rate must be >= 0"

        self._startRate = startRate
        self._duration = 30 * duration
        self._death = death
        self._transmission = transmission
        

    @property
    def startRate(self):
        return self._startRate

    @property
    def duration(self):
        return self._duration

    @property
    def death(self):
        return self._death

    @property
    def transmission(self):
        return self._transmission

    def infect(self, Person, POPULATION_SIZE, i = 0, isInitial = False):
        if i <= self._startRate * POPULATION_SIZE and isInitial:
            Person.infect()
        elif random.random() < self._transmission and not Person.dead:
            Person.infect()

    def kill(self, Person):
        if random.random() < self.death and Person.infected and not Person.dead:
            Person.kill()

    def pass_day(self, Person):
        if Person.days_infected == self.duration:
            Person.disinfect()
            return True
        elif Person.days_infected != 0 and Person.days_infected != self.duration:
            Person.add_day()

# Person may be infected/disinfected/killed and moved.
class Person(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # Person's stats.
        self._infected = False  # starts False/Healthy
        self._dead = False  # starts False/Alive
        self._colour = WHITE  # starts Green/Healthy
        self._days_infected = 0  # starts not-infected
        self._radius = Person_Radius

        #Movement Location
        self._x = random.randrange(10, WIDTH - 10)                  # x position (10 to account for circle diameter)
        self._y = random.randrange(10 + HEIGHT // 5, HEIGHT - 10)   # y position (// 5 to start below graphs)
        self._person_location = Location(self._x, self._y)

      
        #Needed for moving person around with move_now()
        self._speed = random.randrange(2, 5)    # cell speed
        self.move = [None, None]                # relative x and y coordinates to move to
        self.direction = None                   # movement direction

    """
    Properties.
    """

    @property
    def infected(self):
        return self._infected

    @property
    def dead(self):
        return self._dead

    @property
    def colour(self):
        return self._colour

    @property
    def days_infected(self):
        return self._days_infected

    @property
    def person_location(self):
        return self._person_location

    @property
    def speed(self):
        return self._speed

    @property
    def radius(self):
        return self._radius

    """
    Change person's stats.
    """

    def add_day(self):
        self._days_infected += 1

    def infect(self):
        self._infected = True
        self.add_day()
        self._colour = RED

    def disinfect(self):
        self._infected = False
        self._days_infected = 0
        self._colour = GREY

    def update(self):
        move_now(self)

    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.person_location.x, self.person_location.y), self._radius)


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



class Collector(object):
    
    def __init__(self, populationSize = 0, startRate=0, duration=0, deathRate=0, transmissionRate = 0):
        self.populationSize = populationSize
        self.diseaseStartRate = startRate
        self.diseaseDuration = duration
        self.deathRate = deathRate
        self.dataColumns = self.DataColumns()

    
    class DataColumns(object):
        def __init__(self, day = [], dailyCases = [], dailyActiveCases = [], dailyDeaths= [], dailyRecoveries  = [], dailyClosedCases = []):
            
            self.day                    = day
            self.dailyCases             = dailyCases
            self.dailyActiveCases       = dailyActiveCases
            self.dailyDeaths            = dailyDeaths
            self.dailyRecoveries        = dailyRecoveries
            self.dailyClosedCases       = dailyClosedCases
            self.columns = 6
        

    #Record Data in Excel Spreadsheet
    def Record(self, columns):
        workbook = xlsxwriter.Workbook("DiseaseData.xlsx")
        worksheet = workbook.add_worksheet()    
        RowIndex = 3
        ColumnIndex = 0
        
        worksheet.write(2, 0, "Day")
        worksheet.write(2, 1, "Daily Cases")
        worksheet.write(2, 2, "Active Cases")
        worksheet.write(2, 3, "Daily Deaths")
        worksheet.write(2, 4, "Daily RecoveriesCases")

        RowIndex, ColumnIndex = self._WriteDataColumn(worksheet, columns.day, RowIndex, ColumnIndex)        
        RowIndex, ColumnIndex = self._WriteDataColumn(worksheet, columns.dailyCases, RowIndex, ColumnIndex)
        RowIndex, ColumnIndex = self._WriteDataColumn(worksheet, columns.dailyActiveCases, RowIndex, ColumnIndex)
        RowIndex, ColumnIndex = self._WriteDataColumn(worksheet, columns.dailyDeaths, RowIndex, ColumnIndex)
        RowIndex, ColumnIndex = self._WriteDataColumn(worksheet, columns.dailyRecoveries, RowIndex, ColumnIndex)
        #RowIndex, ColumnIndex = self._WriteDataColumn(worksheet, columns.dailyClosedCases, RowIndex, ColumnIndex)
        workbook.close()
        
    def _WriteDataColumn(self, worksheet, DataArray = [], StartRowIndex = 0, StartColumnIndex = 0):
    
        RowIndex = StartRowIndex
        ColumnIndex =  StartColumnIndex
        
        for Data in DataArray:
            worksheet.write(RowIndex, ColumnIndex, Data)
            RowIndex += 1
        
        NextRowIndex = StartRowIndex
        NextColumnIndex = StartColumnIndex+1
        
        
        return NextRowIndex, NextColumnIndex 

    
