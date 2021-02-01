import xml.etree.ElementTree as ET

def main():
    print('hello world')
    tree = ET.parse('target.gpx')
    ET.register_namespace('', "http://www.topografix.com/GPX/1/0")
    ET.register_namespace('', "http://www.topografix.com/GPX/1/1")
    ET.register_namespace('gpxtpx', "http://www.garmin.com/xmlschemas/TrackPointExtension/v1")
    root = tree.getroot()
    trk = root[1]
    trkseg = trk[1]
    for point in trkseg:
        if point.tag == '{http://www.topografix.com/GPX/1/1}trkpt':
            ele = point[0]
            time = point[1]

            # fix the extension
            extensions = point[2]
            track_point_extension = extensions[0]
            for extension in track_point_extension:
                if extension.tag == '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}hr':
                    track_point_extension.remove(extension)

                if extension.tag == '{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}atemp':
                    track_point_extension.remove(extension)

    tree.write('result.gpx')

if __name__ == '__main__':
    main()
