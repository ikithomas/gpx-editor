import xml.etree.ElementTree as ET
import copy


class TestXML:
    def test_access_by_hardcoding(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        assert root.tag == 'data'
        assert root.attrib == {}
        assert len(root) == 3

        # data
        assert root[0].tag == 'country'
        assert root[0].attrib == {'name': 'Liechtenstein'}
        assert root[1].tag == 'country'
        assert root[1].attrib == {'name': 'Singapore'}
        assert root[2].tag == 'country'
        assert root[2].attrib == {'name': 'Panama'}

        # country 1
        assert root[0][0].tag == 'rank'
        assert root[0][0].text == '1'


    def test_access_country_by_element_iter(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        countries = list(root.iter('country'))

        assert len(countries) == 3

    def test_access_neighbor_by_element_iter(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        neighbors = list(root.iter('neighbor'))

        assert len(neighbors) == 5

    def test_access_country_with_findall(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        countries = list(root.findall('country'))

        assert len(countries) == 3

    def test_access_nieghbor_with_findall(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        neighbors = list(root.findall('neighbor'))

        assert len(neighbors) == 0

    def test_access_rank_with_find(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        countries = list(root.findall('country'))
        assert countries[0].find('rank').text == '1'
        assert countries[1].find('rank').text == '4'
        assert countries[2].find('rank').text == '68'

    def test_access_neighbor_with_xpath(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        neighbors = list(root.findall('./country/neighbor'))

        assert len(neighbors) == 5

    def test_deep_clone_country(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        old_country = list(root.findall('country'))[0]
        new_country = copy.deepcopy(old_country)

        new_country.find('rank').text = '50'

        assert old_country.find('rank').text == '1'
        assert new_country.find('rank').text == '50'

    def test_insert_a_country(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        countries = list(root.findall('country'))

        assert len(countries) == 3

        new_country = copy.deepcopy(countries[0])
        new_country.find('rank').text = '50'
        root.insert(1, new_country)

        root = tree.getroot()
        countries = list(root.findall('country'))

        assert len(countries) == 4
        assert countries[0].find('rank').text == '1'
        assert countries[1].find('rank').text == '50'
        assert countries[2].find('rank').text == '4'
        assert countries[3].find('rank').text == '68'

    def test_append_a_country(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        countries = list(root.findall('country'))

        new_country = copy.deepcopy(countries[0])
        new_country.find('rank').text = '50'
        root.append(new_country)

        root = tree.getroot()
        countries = list(root.findall('country'))

        assert len(countries) == 4
        assert countries[0].find('rank').text == '1'
        assert countries[1].find('rank').text == '4'
        assert countries[2].find('rank').text == '68'
        assert countries[3].find('rank').text == '50'

    def test_remove_a_country(self):
        tree = ET.parse('fixtures/country_data.xml')
        root = tree.getroot()

        countries = list(root.findall('country'))
        assert len(countries) == 3
        root.remove(countries[1])

        root = tree.getroot()
        countries = list(root.findall('country'))

        assert len(countries) == 2
        assert countries[0].find('rank').text == '1'
        assert countries[1].find('rank').text == '68'
