import xml.etree.ElementTree as ET
from haversine import haversine
import datetime
import copy
import random
from time import sleep
from obfuscation import *

ET.register_namespace('', "http://www.topografix.com/GPX/1/0")
ET.register_namespace('', "http://www.topografix.com/GPX/1/1")
ET.register_namespace('gpxtpx', "http://www.garmin.com/xmlschemas/TrackPointExtension/v1")
ET.register_namespace('gte', "http://www.gpstrackeditor.com/xmlschemas/General/1")

SAMPLE_RATE = 1


################################################################################
# Aggregation method
###

# in meter
def distance_between(trkpt1, trkpt2):
    return haversine(
        (trkpt1.lat(), trkpt1.lon()),
        (trkpt2.lat(), trkpt2.lon())
    ) * 1000


# in meter
def distance_of(trkpts):
    total = 0

    for i in range(0, len(trkpts)-SAMPLE_RATE, SAMPLE_RATE):
        total += distance_between(trkpts[i], trkpts[i+SAMPLE_RATE])
    return total


# in meter
def elevation_diff(trkpt1, trkpt2):
    return trkpt2.ele() - trkpt1.ele()


# in meter
def elevation_of(trkpts):
    total = 0
    for i in range(0, len(trkpts)-SAMPLE_RATE, SAMPLE_RATE):
        diff = elevation_diff(trkpts[i], trkpts[i+SAMPLE_RATE])
        if diff > 0:
            total += diff
    return total

# in meter
def descent_of(trkpts):
    total = 0
    for i in range(0, len(trkpts)-SAMPLE_RATE, SAMPLE_RATE):
        diff = elevation_diff(trkpts[i], trkpts[i+SAMPLE_RATE])
        if diff < 0:
            total += abs(diff)
    return total


# in second
def time_spent_of(trkpts):
    return trkpts[-1].time().timestamp() - trkpts[0].time().timestamp()

def effort_points_of(trkpts):
    distance = distance_of(trkpts)
    elevation = elevation_of(trkpts)
    return (distance / 1000) + (elevation / 100)


def eph_of(trkpts):
    ep = effort_points_of(trkpts)
    time_spent = time_spent_of(trkpts)

    return ep / (time_spent / 60 / 60)


def speed_of(trkpts):
    distance = distance_of(trkpts)
    time_spent = time_spent_of(trkpts)
    return (distance / 1000) / (time_spent / 60 / 60)


def pace_of(trkpts):
    time_spent = time_spent_of(trkpts)
    distance = distance_of(trkpts)
    return (time_spent / (distance / 1000)/ 60)


def set_by_speed(gpx, speed, time_start, time_end=None):
    h, t = gpx.trkpts_between_idx(time_start, time_end)

    former_trkpts = gpx.trkpts[0:h]
    target_trkpts = gpx.trkpts[h:t+1]
    latter_trkpts = gpx.trkpts[t+1:]

    # generate new section
    new_target_trkpts = new_trkpts_by_speed(target_trkpts, speed)
    random_points_delete(new_target_trkpts)

    # calculate the time_diff
    time_diff_in_seconds = 0

    shift_trkpts_time(latter_trkpts, time_diff_in_seconds)

    gpx.remove_all()
    gpx.append_trkpts(former_trkpts)
    gpx.append_trkpts(new_target_trkpts)
    gpx.append_trkpts(latter_trkpts)


def find_mid_point(ax, ay, bx, by, percentile):
    x = ax + (bx - ax) * percentile
    y = ay + (by - ay) * percentile
    return (x, y)


def random_points_delete(trkpts):
    pt_to_remove = 0
    for trkpt in list(trkpts):
        if pt_to_remove > 0:
            trkpts.remove(trkpt)
            pt_to_remove -= 1
            continue

        lottery = random.randint(1, 1200)

        if lottery == 1:
            pt_to_remove += random.randint(6, 10)
        elif lottery <= 10:
            pt_to_remove += random.randint(2, 5)
        elif lottery <= 100:
            pt_to_remove += 1


def new_trkpts_by_speed(track, target_speed):
    def trkpt_factory(lat=0, lon=0, ele=0, time=datetime.datetime.now()):
        model = track[0].deep_copy()
        model.set_lat(lat)
        model.set_lon(lon)
        model.set_ele(ele)
        model.set_time(time)

        return model

    def get_point(a, b, current_distance, target_distance):
        ab = distance_between(a, b)
        ac = current_distance - target_distance
        percentile = (ac / ab)
        lon, lat = find_mid_point(a.lon(), a.lat(), b.lon(), b.lat(), percentile)
        return trkpt_factory(
            lat=lat,
            lon=lon,
            ele=a.ele()
        )

    def get_target_distances():
        actual_speed = speed_of(track)
        ratio = actual_speed / target_speed
        n = len(track) * ((actual_speed / target_speed) + 1.2)

        target_speeds = random_target_speeds(int(n), base=target_speed, height_scale=1.5)
        return list(map(lambda x: x / 3.6, target_speeds))

    target_distances = get_target_distances()

    new_trkpts = []
    new_trkpts.append(track[0].deep_copy())

    distance_idx = 0
    track_idx = 1
    points_to_cross = [new_trkpts[-1]]

    while(track_idx < len(track)):
        points_to_cross.append(track[track_idx])

        current_distance = distance_of(points_to_cross)

        if current_distance == target_distances[distance_idx]: # alright, just accept the next_pt
            new_trkpts.append(track[track_idx].deep_copy())
            track_idx += 1
            points_to_cross = [new_trkpts[-1]]

        elif current_distance < target_distances[distance_idx]:
            track_idx += 1

        elif current_distance > target_distances[distance_idx]:
            new_trkpt = get_point(
                points_to_cross[-1],
                points_to_cross[-2],
                current_distance,
                target_distances[distance_idx]
            )
            new_trkpt.set_time(new_trkpts[-1].time() + datetime.timedelta(seconds=1))
            new_trkpts.append(new_trkpt)
            points_to_cross = [new_trkpts[-1]]
            distance_idx += 1
        else:
            raise 'DISASTER!'

    return new_trkpts


def shift_trkpts_time(trkpts, time_in_second):
    for trkpt in trkpts:
        trkpt.shift_time(time_in_second)


class GPX:
    def __init__(
        self,
        file_name,
        lat_p=-1,
        lon_p=-1,
        ele_p=-1,
        ms=False
    ):
        self.tree = ET.parse(file_name)
        self.ms = ms
        self.root = self.tree.getroot()
        self.namespace = '{http://www.topografix.com/GPX/1/1}'
        self.trkseg = self.root.find(f'{self.namespace}trk').find(f'{self.namespace}trkseg')
        self.lat_p = lat_p
        self.lon_p = lon_p
        self.ele_p = ele_p
        self.trkpts = self.load_trkpts()


    def load_trkpts(self):
        return list(map(
            lambda p: TrackPoint(p, lat_p=self.lat_p, lon_p=self.lon_p, ms=self.ms),
            list(self.trkseg))
        )

    def write(self, file_path):
        self.load_trkpts()
        for trkpt in self.trkpts:
            trkpt.set_lat(format(round(trkpt.lat(), self.lat_p), '.7f'))
            trkpt.set_lon(format(round(trkpt.lon(), self.lon_p), '.7f'))
            trkpt.set_ele(format(round(trkpt.ele(), self.ele_p), '.1f'))

        self.load_trkpts()
        self.tree.write(file_path, encoding='utf-8', xml_declaration=True)

    # trkpts: List[Trackpoints]
    def remove_trkpts(self, trkpts):
        for trkpt in trkpts:
            self.trkseg.remove(trkpt.xml_element)

        self.trkpts = self.load_trkpts()

    def remove_all(self):
        for child in list(self.trkseg):
            self.trkseg.remove(child)

        self.trkpts = self.load_trkpts()

    # trkpts: List[Trackpoints]
    def insert_trkpts(self, idx, trkpts):
        next_idx = idx
        for trkpt in trkpts:
            self.trkseg.insert(next_idx, trkpt.xml_element)
            next_idx += 1

        self.trkpts = self.load_trkpts()

    def append_trkpts(self, trkpts):
        for trkpt in trkpts:
            self.trkseg.append(trkpt.xml_element)

        self.trkpts = self.load_trkpts()

    def randomize_lat_and_lon(self):
        self.trkpts = self.load_trkpts()
        for point in self.each_trk_point():
            point.attrib['lat'] = str(round(float(point.attrib['lat']) + GPX.location_offset(), self.lat_p))
            point.attrib['lon'] = str(round(float(point.attrib['lon']) + GPX.location_offset(), self.lon_p))

    def remove_extension(self):
        self.trkpts = self.load_trkpts()
        for point in self.each_trk_point():
            print('point 1: ' + point)
            extensions = point[2]
            track_point_extension = extensions[0]
            for extension in track_point_extension:
                if extension.tag == '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr':
                    track_point_extension.remove(extension)

                if extension.tag == '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}atemp':
                    track_point_extension.remove(extension)

    def trkpts_between(self, earliest_datetime, latest_datetime):
        earliest_idx, latest_idx = self.trkpts_between_idx(earliest_datetime, latest_datetime)
        return self.trkpts[earliest_idx:latest_idx+1]

    # NOW: sequecntial search
    # TODO: binary search to improve performance
    def trkpts_between_idx(self, earliest_datetime, latest_datetime):
        earliest_idx = None
        latest_idx = None

        for idx, trkpt in enumerate(self.trkpts):
            if earliest_idx is None:
                if trkpt.time() >= earliest_datetime:
                    earliest_idx = idx

            if latest_idx is None:
                if trkpt.time() >= latest_datetime:
                    latest_idx = idx

            if not (earliest_idx is None or latest_idx is None):
                break

        if latest_idx is None:
            latest_idx = len(self.trkpts) - 1

        return earliest_idx, latest_idx

    # inclusive
    # NOW: sequecntial search
    # TODO: binary search to improve performance
    def trkpts_after(self, earliest_datetime):
        for idx, trkpt in reversed(list(enumerate(self.trkpts))):
            if trkpt.time() >= earliest_datetime:
                continue

            return self.trkpts[idx:]


    @staticmethod
    def location_offset():
        return random.uniform(-0.000001, 0.000001)


# Wrapper of the XML element trkpt
class TrackPoint:
    def __init__(self, trk_point, ms, lat_p, lon_p):
        self.xml_element = trk_point
        self.lat_p = lat_p
        self.lon_p = lon_p
        self.ms = ms
        self.namespace = '{http://www.topografix.com/GPX/1/1}'

    def lat(self):
        return float(self.xml_element.attrib['lat'])

    def set_lat(self, value):
        self.xml_element.attrib['lat'] = str(value)

    def lon(self):
        return float(self.xml_element.attrib['lon'])

    def set_lon(self, value):
        self.xml_element.attrib['lon'] = str(value)

    def ele(self):
        return float(self.xml_element.find(f'{self.namespace}ele').text)

    def set_ele(self, value):
        self.xml_element.find(f'{self.namespace}ele').text = str(value)

    # return datetime
    def time(self):
        rfc_3339_timestamp = self.raw_time()

        # print(self.ms)
        if self.ms:
          return datetime.datetime.strptime(rfc_3339_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ' )
        else:
          return datetime.datetime.strptime(rfc_3339_timestamp, '%Y-%m-%dT%H:%M:%SZ' )

    def raw_time(self):
        return self.xml_element.find(f'{self.namespace}time').text

    # set by datetime
    def set_time(self, value):
        if self.ms:
            rfc_3339_timestamp = value.strftime('%Y-%m-%dT%H:%M:%S.%fZ').replace('000000Z', '000Z')
        else:
            rfc_3339_timestamp = value.strftime('%Y-%m-%dT%H:%M:%SZ')
        self.xml_element.find(f'{self.namespace}time').text = rfc_3339_timestamp

    def shift_time(self, seconds):
        new_time = self.time() + datetime.timedelta(seconds=seconds)
        self.set_time(new_time)


    def deep_copy(self):
        new_trkpt = copy.deepcopy(self.xml_element)
        return TrackPoint(new_trkpt, self.ms, self.lat_p, self.lon_p)

    def __str__(self):
        return f'{round(self.lat(), 7)}, {round(self.lon(), 7)}, {self.time()}, {round(self.ele(), 2)}'
