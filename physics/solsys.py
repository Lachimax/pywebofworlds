import telnetlib as tn
import datetime as dt
# from matplotlib import axes
import matplotlib.pyplot as plt


# If JPL changes how their system works this entire thing is obsolete. That's coding for you!

# TODO: Functionalise, Allow selectable planets
# TODO: Plot planet orbits (by plotting a year's worth of data)
# TODO: General function for querying ephemeris
# TODO: Allow query to accept names, which it turns into the relevant numbers
# TODO: Generalise query to retrieve more properties
# TODO: Subtract Sun's coordinates to make heliocentric
# TODO: Function to show current distance from Earth to given body


def query(objects, date_start=None, date_end=None, resolution='1d'):
    if date_start is None:
        current = dt.datetime.now()
        date_start = current.strftime('%Y-%b-%d %H:%M')
    if date_end is None:
        end = dt.datetime.now()
        end = end.replace(year=end.year + 1)
        date_end = end.strftime('%Y-%b-%d %H:%M')

    date_start = bytes(date_start, 'utf8')
    date_end = bytes(date_end, 'utf8')

    connection = tn.Telnet(host='horizons.jpl.nasa.gov', port=6775, timeout=10)

    xxx = []
    yyy = []
    zzz = []

    print(connection.read_until(b'Horizons>'))
    connection.write(b'Sun\n')
    print(connection.read_until(b'<cr>: '))
    connection.write(b'E\n')
    # Observe, Elements, Vectors  [o,e,v,?] :
    print(connection.read_until(b'[o,e,v,?] : '))
    connection.write(b'v\n')
    print(connection.read_until(b' : '))
    connection.write(b'geo\n')
    print(connection.read_until(b' : '))
    connection.write(b'eclip\n')
    print(connection.read_until(b' : '))
    connection.write(date_start + b'\n')
    print(connection.read_until(b' : '))
    connection.write(date_end + b'\n')
    print(connection.read_until(b' : '))
    connection.write(b'1d\n')
    print(connection.read_until(b' : '))
    connection.write(b'\n')
    print(connection.read_until(b' X ='))

    xx = []
    yy = []
    zz = []

    for d in range(1, 365):
        x = connection.read_until(b' Y =')
        y = connection.read_until(b' Z =')
        z = connection.read_until(b'\r')

        x = x[:len(x) - 4]
        y = y[:len(y) - 4]
        z = z[:len(z) - 1]

        x = float(x)
        y = float(y)
        z = float(z)

        print(x)
        print(y)
        print(z)

        xx.append(x)
        yy.append(y)
        zz.append(z)

        connection.read_until(b' X =')

    xxx.append(xx)
    yyy.append(yy)
    zzz.append(zz)

    print(connection.read_until(b' ? : '))
    connection.write(b'N\n')

    for obj in objects:
        print(connection.read_until(b'Horizons>'))
        connection.write(obj)
        print(connection.read_until(b'<cr>: '))
        connection.write(b'E\n')
        # Observe, Elements, Vectors  [o,e,v,?] :
        print(connection.read_until(b'[o,e,v,?] : '))
        connection.write(b'v\n')
        # Use previous center  [ cr=(y), n, ? ] : '
        print(connection.read_until(b' : '))
        connection.write(b'\n')
        # Reference plane [eclip, frame, body ] :
        print(connection.read_until(b' : '))
        connection.write(b'eclip\n')
        # Starting TDB [>=   1599-Dec-03 00:00] :
        print(connection.read_until(b' : '))
        connection.write(date_start + b'\n')
        # Ending   TDB [<=   2600-Jan-01 00:00] :
        print(connection.read_until(b' : '))
        connection.write(date_end + b'\n')
        # Output interval [ex: 10m, 1h, 1d, ? ] :
        print(connection.read_until(b' : '))
        connection.write(b'1d\n')
        # Accept default output [ cr=(y), n, ?] :
        print(connection.read_until(b' : '))
        connection.write(b'\n')
        print(connection.read_until(b' X ='))

        xx = []
        yy = []
        zz = []

        for d in range(1, 365):
            x = connection.read_until(b' Y =')
            y = connection.read_until(b' Z =')
            z = connection.read_until(b'\r')

            x = x[:len(x) - 4]
            y = y[:len(y) - 4]
            z = z[:len(z) - 1]

            x = float(x)
            y = float(y)
            z = float(z)

            print(x)
            print(y)
            print(z)

            xx.append(x)
            yy.append(y)
            zz.append(z)

            connection.read_until(b' X =')

        xxx.append(xx)
        yyy.append(yy)
        zzz.append(zz)

        print(connection.read_until(b' ? : '))
        connection.write(b'N\n')

    connection.close()

    return xxx, yyy, zzz


def overhead():
    end = dt.datetime.now()
    end = end.replace(year=end.year + 1)
    start_date = dt.datetime.now().strftime('%Y-%b-%d %H:%M')
    end_date = end.strftime('%Y-%b-%d %H:%M')

    items = [b'199\n',  # Mercury
             b'299\n',  # Venus
             b'399\n',  # Earth
             b'499\n',  # Mars
             b'599\n',  # Jupiter
             b'699\n',  # Saturn
             b'799\n',  # Uranus
             b'899\n',  # Neptune
             ]

    names = ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
    colours = ['yellow', 'grey', 'brown', 'green', 'red', 'orange', 'purple', 'cyan', 'blue']

    xxx, yyy, zzz = query(objects=items, date_start=start_date, date_end=end_date)

    plotx = plt.figure()
    ax = plotx.add_subplot(111)

    for i, name in enumerate(names):
        ax.plot(x=xxx[i], y=yyy[i], c=colours[i])
        ax.scatter(x=xxx[i][1], y=yyy[i][1], label=name, c=colours[i])

    ax.legend()
    plt.show()

    return xxx, yyy, zzz
