from gpx import *
import datetime

class TestGPX:
    def test_trk_points(self):
        gpx1 = GPX('fixtures/track1.gpx', lat_p=7, lon_p=7, ele_p=1)
        gpx2 = GPX('fixtures/track2.gpx', lat_p=6, lon_p=6, ele_p=2)

        assert len(gpx1.trkpts) == 39669
        assert len(gpx2.trkpts) == 19363

    ############################################################################
    # deep copy of trkpt
    ###
    def test_deep_copy_of_track_point(self):
        gpx1 = GPX('fixtures/track1.gpx', lat_p=7, lon_p=7, ele_p=1)

        old_trkpt = gpx1.trkpts[0]
        new_trkpt = old_trkpt.deep_copy()
        old_trkpt.set_lon(50)
        new_trkpt.set_lon(100)
        assert old_trkpt.lon() != new_trkpt.lon()


    ############################################################################
    # Getter and setter
    ###
    def test_get_and_set_lat_of(self):
        gpx1 = GPX('fixtures/track1.gpx', lat_p=7, lon_p=7, ele_p=1)
        gpx2 = GPX('fixtures/track2.gpx', lat_p=6, lon_p=6, ele_p=2)

        assert gpx1.trkpts[0].lat() == 22.3490950
        assert gpx2.trkpts[0].lat() == 22.397566

        gpx1.trkpts[0].set_lat(100.12345)
        assert gpx1.trkpts[0].lat() == 100.12345

    def test_get_and_set_lon_of(self):
        gpx1 = GPX('fixtures/track1.gpx', lat_p=7, lon_p=7, ele_p=1)
        gpx2 = GPX('fixtures/track2.gpx', lat_p=6, lon_p=6, ele_p=2)

        assert gpx1.trkpts[0].lon() == 114.194624
        assert gpx2.trkpts[0].lon() == 114.319292

        gpx1.trkpts[0].set_lon(100.12345)
        assert gpx1.trkpts[0].lon() == 100.12345

    def test_get_and_set_ele_of(self):
        gpx1 = GPX('fixtures/track1.gpx', lat_p=7, lon_p=7, ele_p=1)
        gpx2 = GPX('fixtures/track2.gpx', lat_p=6, lon_p=6, ele_p=2)

        assert gpx1.trkpts[0].ele() == 122.9
        assert gpx2.trkpts[0].ele() == 14.0

        gpx1.trkpts[0].set_ele(150)
        assert gpx1.trkpts[0].ele() == 150

    def test_get_and_set_time_of(self):
        gpx1 = GPX('fixtures/track1.gpx', lat_p=7, lon_p=7, ele_p=1)
        gpx2 = GPX('fixtures/track2.gpx', lat_p=6, lon_p=6, ele_p=2)
        gpx3 = GPX('fixtures/track3.gpx', lat_p=6, lon_p=6, ele_p=2, ms=True)

        assert gpx1.trkpts[0].time() == datetime.datetime(2021, 3, 29, 23, 6, 15)
        assert gpx2.trkpts[0].time() == datetime.datetime(2021, 1, 30, 0, 18, 5)
        assert gpx3.trkpts[0].time() == datetime.datetime(2021, 3, 7, 0, 29, 9)

        gpx1.trkpts[0].set_time(datetime.datetime(2021, 3, 29, 23, 6, 10))
        gpx3.trkpts[0].set_time(datetime.datetime(2021, 3, 29, 23, 6, 10))
        assert gpx1.trkpts[0].raw_time() == '2021-03-29T23:06:10Z'
        assert gpx3.trkpts[0].raw_time() == '2021-03-29T23:06:10.000Z'

    ############################################################################
    # Slicer
    ###
    def test_trkpts_between(self):
        gpx1 = GPX('fixtures/track1.gpx', lat_p=7, lon_p=7, ele_p=1)
        trkpts = gpx1.trkpts_between(
            datetime.datetime(2021, 3, 29, 23, 6, 25),
            datetime.datetime(2021, 3, 29, 23, 6, 30)
        )

        assert len(trkpts) == 6
        assert trkpts[0].ele() == 124.5
        assert trkpts[4].ele() == 124.9

    def test_trkpts_after(self):
        gpx1 = GPX('fixtures/track1.gpx', lat_p=7, lon_p=7, ele_p=1)
        trkpts = gpx1.trkpts_after(datetime.datetime(2021, 3, 30, 10, 32, 30))
        assert len(trkpts) == 14

    ############################################################################
    # Modifier
    ###
    def test_remove_trkpts(self):
        gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
        assert len(gpx.trkpts) == 13705

        trkpts = gpx.trkpts_between(
            datetime.datetime(2021, 3, 7, 0, 30, 00),
            datetime.datetime(2021, 3, 7, 1, 30, 00)
        )

        assert len(trkpts) == 1429

        gpx.remove_trkpts(trkpts)

        assert len(gpx.trkpts) == 13705 - 1429

    def test_insert_trkpts(self):
        gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
        new_trkpts = [gpx.trkpts[0].deep_copy(),  gpx.trkpts[0].deep_copy()]
        new_trkpts[0].shift_time(-10)
        new_trkpts[1].shift_time(-5)

        gpx.insert_trkpts(0, new_trkpts)

        assert len(gpx.trkpts) == 13707
        assert gpx.trkpts[0].time() == datetime.datetime(2021, 3, 7, 0, 28, 59)
        assert gpx.trkpts[1].time() == datetime.datetime(2021, 3, 7, 0, 29, 4)
        assert gpx.trkpts[2].time() == datetime.datetime(2021, 3, 7, 0, 29, 9)


def test_distance_between():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    trkpts = gpx.trkpts_between(
        datetime.datetime(2021, 3, 7, 0, 30, 00),
        datetime.datetime(2021, 3, 7, 1, 30, 00)
    )
    assert distance_between(trkpts[0], trkpts[-1]) == 2657.1148850368686

    trkpts = gpx.trkpts
    assert distance_between(trkpts[0], trkpts[1]) == 0.9189787340305945
    assert distance_between(trkpts[1], trkpts[2]) == 12.033092108593971
    assert distance_between(trkpts[2], trkpts[3]) == 5.550641410522128
    assert distance_between(trkpts[3], trkpts[4]) == 4.87470435820659
    assert distance_between(trkpts[0], trkpts[-1]) == 21891.243987551534
    assert distance_between(trkpts[0], trkpts[0]) == 0


def test_distance_of():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    trkpts = gpx.trkpts_between(
        datetime.datetime(2021, 3, 7, 0, 30, 00),
        datetime.datetime(2021, 3, 7, 1, 30, 00)
    )
    assert distance_of(trkpts) == 7876.294257593097

    trkpts = gpx.trkpts
    assert distance_of(trkpts) == 58023.3122908493
    assert distance_of(trkpts[0:2]) == 0.9189787340305945


def test_elevation_of():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    trkpts = gpx.trkpts_between(
        datetime.datetime(2021, 3, 7, 0, 30, 00),
        datetime.datetime(2021, 3, 7, 1, 30, 00)
    )
    assert elevation_of(trkpts) == 490.00012588500977

    trkpts = gpx.trkpts
    assert elevation_of(trkpts) == 3896.200174331665
    assert elevation_of(trkpts[0:2]) == 0.40000152587890625
    assert elevation_of(trkpts[1:3]) == 0


def test_descent_of():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    trkpts = gpx.trkpts_between(
        datetime.datetime(2021, 3, 7, 0, 30, 00),
        datetime.datetime(2021, 3, 7, 1, 30, 00)
    )
    assert descent_of(trkpts) == 301.00013160705566

    trkpts = gpx.trkpts
    assert descent_of(trkpts) == 3408.8001613616943
    assert descent_of(trkpts[0:2]) == 0
    assert descent_of(trkpts[1:3]) == 0.6000003814697266


def test_time_spent_of():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    trkpts = gpx.trkpts_between(
        datetime.datetime(2021, 3, 7, 0, 30, 00),
        datetime.datetime(2021, 3, 7, 1, 30, 00)
    )

    assert time_spent_of(trkpts) == 3598.0

    trkpts = gpx.trkpts
    assert time_spent_of(trkpts) == 33652.0


def test_effort_points_of():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    trkpts = gpx.trkpts_between(
        datetime.datetime(2021, 3, 7, 0, 30, 00),
        datetime.datetime(2021, 3, 7, 1, 30, 00)
    )

    assert effort_points_of(trkpts) == 12.776295516443195

    trkpts = gpx.trkpts
    assert effort_points_of(trkpts) == 96.98531403416595
    assert effort_points_of(trkpts[0:2]) == 0.004918993992819656


def test_eph_of():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    trkpts = gpx.trkpts_between(
        datetime.datetime(2021, 3, 7, 0, 30, 00),
        datetime.datetime(2021, 3, 7, 1, 30, 00)
    )

    assert eph_of(trkpts) == 12.7833974038898

    trkpts = gpx.trkpts
    assert eph_of(trkpts) == 10.375226747979243

    assert eph_of(trkpts[0:2]) == 17.70837837415076
    assert eph_of(trkpts[1:3]) == 8.66382631818766
    assert eph_of(trkpts[2:4]) == 3.9964618155759326
    assert eph_of(trkpts[3:5]) == 8.774467844771863
    assert eph_of(trkpts[4:6]) == 11.677338852348937
    assert eph_of(trkpts[2300:2302]) == 6.727606093642667
    assert eph_of(trkpts[2301:2303]) == 8.164731747067416
    assert eph_of(trkpts[2302:2304]) == 5.948076388539
    assert eph_of(trkpts[11859:11861]) == 12.196399801366054
    assert eph_of(trkpts[11860:11862]) == 23.88511330252638
    assert eph_of(trkpts[11861:11863]) == 19.148902154351877


def test_speed_of():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    trkpts = gpx.trkpts_between(
        datetime.datetime(2021, 3, 7, 0, 30, 00),
        datetime.datetime(2021, 3, 7, 1, 30, 00)
    )

    assert speed_of(trkpts) == 7.880672408931392

    trkpts = gpx.trkpts
    assert speed_of(trkpts) == 6.207177114199974


def test_pace_of():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    trkpts = gpx.trkpts_between(
        datetime.datetime(2021, 3, 7, 0, 30, 00),
        datetime.datetime(2021, 3, 7, 1, 30, 00)
    )

    assert pace_of(trkpts) == 7.613563524351078

    trkpts = gpx.trkpts
    assert pace_of(trkpts) == 9.666229736338568

##########################################################################
# Set time, given desired speed
##
def test_set_by_speed():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    start_time = datetime.datetime(2021, 3, 7, 9, 45, 00)
    end_time = datetime.datetime(2021, 3, 7, 9, 59, 00)
    trkpts = gpx.trkpts_between(start_time, end_time)

    assert speed_of(trkpts) == 6.185889586993364

    set_by_speed(gpx, 10, start_time, end_time)

    trkpts = gpx.trkpts_between(start_time, end_time)

    got = speed_of(trkpts)
    assert got >= 9 and got <= 11

def test_new_trkpts_by_speed():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    start_time = datetime.datetime(2021, 3, 7, 9, 40, 43)
    end_time = datetime.datetime(2021, 3, 7, 9, 50, 47)
    trkpts = gpx.trkpts_between(start_time, end_time)

    new_trkpts = new_trkpts_by_speed(gpx.trkpts, 10)

    got = speed_of(new_trkpts)
    assert got >= 9 and got <= 11


def test_shift_trkpts_time():
    gpx = GPX('fixtures/track3.gpx', lat_p=7, lon_p=7, ele_p=1, ms=True)
    trkpts = gpx.trkpts_between(
        datetime.datetime(2021, 3, 7, 0, 30, 00),
        datetime.datetime(2021, 3, 7, 1, 30, 00)
    )
    shift_trkpts_time(trkpts, 300)
    assert gpx.trkpts[50].time() == datetime.datetime(2021, 3, 7, 0, 36, 23)
    assert gpx.trkpts[100].time() == datetime.datetime(2021, 3, 7, 0, 39, 35)

def test_find_mid_point():
    assert (7, 0) ==  find_mid_point(10, 0, 0, 0, 0.3)
    assert (0, 4) == find_mid_point(0, 10, 0, 0, 0.6)
    assert (5, 5) == find_mid_point(1, 1, 9, 9, 0.5)
    assert (3.2, 3.2) == find_mid_point(3, 3, 5, 5, 0.1)
    assert (3.2, 0.5) == find_mid_point(3, 0, 5, 5, 0.1)
    assert (1.8, 1.8) == find_mid_point(1, 1, 9, 9, 0.1)
    assert (8.2, 8.2) == find_mid_point(1, 1, 9, 9, 0.9)
    assert (8.2, 8.2) == find_mid_point(9, 9, 1, 1, 0.1)
    assert (2.5, 2) == find_mid_point(-3, 5, 8, -1, 0.5)
    assert (2.5, 2) == find_mid_point(8, -1, -3, 5, 0.5)
