#albums_allowable = ['City Folk','Original','New Leaf']
#albums_allowable = ['Original']
#albums_allowable = ['Pokemon RSE','FFCC','Original','City Folk']
#albums_allowable = ['Pokemon RSE', 'FFCC', 'Original', 'City Folk', 'New Leaf']
albums_allowable = ['Pokemon RSE']


flexible_defs = dict(
    # Specify which hours, 0 through 23, should belong to these time categories
    # The flexible albums will pull music based on these times
    Morning = [8, 9, 10, 11],
    Noon = [12, 13, 14, 15],
    Afternoon = [16, 17, 18, 19],
    Evening = [20, 21, 22, 23],
    Night = [0, 1, 2, 3, 4, 5, 6, 7],
)

location = "Jersey City, US"


    # Default volume level for the hours 0 through 23 from scale 0 (mute) through 10
    # [ 0 1 2 3 4 5
    #   6 7 8 9 10 11
    #   12 13 14 15 16 17
    #   18 19 20 21 22 23]
time_volume = [ 0, 0, 0, 0, 1, 2,
                3, 5, 6, 7, 8, 8,
                9, 9, 9, 9, 9, 9,
                8, 8, 7, 6, 5, 4] 


cts_preferences = dict(
    test = 'test',
)


hrly_preferences = dict(
    # If you want the bell to ring before the music plays, set as True
    ring_bell = True,
)
