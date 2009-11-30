import unittest
from mmapi import *

print "-------------------------------------------------------------------------"
print "Beginning mmapi unittests"
print "-------------------------------------------------------------------------\n\n"

DEV_KEY = 'OA08061815799061525'
LAT = 53.36663
LON = -2.90809
DS_1 = 'mm.poi.global.general.atm'
DS_2 = 'mm.poi.global.general.wifi'
DS_BAD = 'mm.poi.global.herebedragons'
COUNT = 10
FIELDNAME = 'carpark'
OPERATOR = 'eq'
VALUE = 'large'
OPTIONS = ['one', 'two', 'three']
STREET = 'Fleet Street'
CITY = 'London'
COUNTRY_CODE = 'GB'
AREAS = ['London', 'England']
REGION = 'England'
POSTAL_CODE = 'ec1n'
DISPLAY_NAME = 'Multimap Office'
QS_UNIQUE = 'London'
GEOCODE_QUALITY = 1
GEOCODE_SCORE = 0.995
ZOOM_FACTOR = 4
ZIP = '90210'
STATE = 'Washington'

ADDRESS = {
    'street': STREET,
    'city': CITY,
    'areas': AREAS,
    'region': REGION,
    'state': STATE,
    'postal_code': POSTAL_CODE,
    'zip': ZIP,
    'display_name': DISPLAY_NAME,
    'country_code': COUNTRY_CODE,
    'qs': QS_UNIQUE
}

LATLON = {
    'lat': LAT,
    'lon': LON
}

LOCATION = {
    'geocode_quality': GEOCODE_QUALITY,
    'geocode_score': GEOCODE_SCORE,
    'address': ADDRESS,
    'zoom_factor': ZOOM_FACTOR,
    'point': LATLON
}

class testMMLatLon(unittest.TestCase):
    """Tests MMLatLon objects and methods"""
    
    def setUp(self):
        """Instantiate a MMLatLon object"""
        self.latlon = MMLatLon(LAT,LON)
    
    def test_structure(self):
        """MMLatLon.__init__() tests general struture of MMLatLon object."""
        self.assertTrue(type(self.latlon) is MMLatLon)
        self.assertEqual(self.latlon['lat'], LAT)
        self.assertEqual(self.latlon['lon'], LON)
    
    def test_to_api_query(self):
        """MMLatLon.to_api_query() should return query string for API request."""
        qs = { 'lat': str(LAT), 'lon': str(LON) }
        self.assertEqual(self.latlon.to_api_query(), qs)
        
    def test_to_api_query_with_postfix(self):
        """MMLatLon.to_api_query(3) should return query string for API request including arg_[COUNTER]."""
        qs = {'lon_3': str(LON), 'lat_3': str(LAT) }
        self.assertEqual(self.latlon.to_api_query(3), qs)
    
    def test_from_json(self):
        """MMLatLon.from_json() should create object with correct structure and values."""
        newlatlon = MMLatLon()
        newlatlon.from_json( { 'lat': LAT, 'lon': LON } )
        self.assertEqual(newlatlon['lat'], LAT)
        self.assertEqual(newlatlon['lon'], LON)


class testMMBounds(unittest.TestCase):
    """Test MMBounds objects and methods."""
    
    def setUp(self):
        pass
        
    def test_simple_constuctor(self):
        """MMBounds.__init__() test constructor and reset methods give correct values and structure."""
        bounds1 = MMBounds( MMLatLon( -10.0, -10.0 ), MMLatLon( 10.0, 10.0 ) )
        bounds2 = MMBounds( MMLatLon( -10.0, -10.0 ) )
        bounds3 = MMBounds( None, MMLatLon( 10.0, 10.0 ) )
        bounds4 = MMBounds( MMLocation( coords=MMLatLon( -10.0, -10.0 ) ), MMLocation( coords=MMLatLon( 10.0, 10.0 ) ) )
        bounds5 = MMBounds( MMLatLon( -10.0, 10.0 ), MMLatLon( 10.0, -10.0 ) )
        
        self.assertEqual('(-10.0,-10.0)', bounds1.getSouthWest().to_string(), "Basic assignment of SW broken.")
        self.assertEqual('(10.0,10.0)', bounds1.getNorthEast().to_string(), "Basic assignment of NE broken.")
        self.assertEqual(bounds2.getSouthWest().to_string(), bounds2.getNorthEast().to_string(),"Assignment with single argument broken.")
        self.assertEqual(bounds3.getSouthWest().to_string(), bounds3.getNorthEast().to_string(), "Assignment with undefined first argument broken.")
        self.assertEqual('(-10.0,-10.0)', bounds4.getSouthWest().to_string(), "Basic MMLocation assignment of SW broken.")
        self.assertEqual('(10.0,10.0)', bounds4.getNorthEast().to_string(), "Basic MMLocation assignment of NE broken.")
        self.assertEqual('(-10.0,10.0)', bounds5.getSouthWest().to_string(), "Basic assignment of IDL SW broken." )
        self.assertEqual('(10.0,-10.0)', bounds5.getNorthEast().to_string(), "Basic assignment of IDL NE broken.")
        
    def test_extending_normal(self):
        """MMBounds.extend() test for correct values and structure"""
        bounds = MMBounds( MMLatLon( -10.0, -10.0 ), MMLatLon( 10.0, 10.0 ) )
        bounds.extend( MMLatLon( 15.0, 15.0 ) )
        self.assertEqual('[ (-10.0,-10.0), (15.0,15.0) ]', bounds.to_string())
        bounds.extend( MMLatLon( 20.0, -15.0 ) )
        self.assertEqual('[ (-10.0,-15.0), (20.0,15.0) ]', bounds.to_string())
        bounds.extend( MMLatLon( -15.0, 7.0 ) )
        self.assertEqual('[ (-15.0,-15.0), (20.0,15.0) ]', bounds.to_string(), "Third extension didn't move S correctly." )

        bounds = MMBounds( MMLatLon( 53.36663, -2.90809 ), MMLatLon( 53.38286, -2.88785 ) )
        bounds.extend( MMLatLon( 53.382867, -2.90807 ) )
        self.assertEqual('[ (53.36663,-2.90809), (53.382867,-2.88785) ]', bounds.to_string(), "Known bad extension failed again.")
        
    def test_to_api_query(self):
        """MMBounds.to_api_query() should return query string for API request."""
        bounds = MMBounds( MMLatLon( -10.0, -10.0 ), MMLatLon( 10.0, 10.0 ) )
        qs = {'bb': '-10.0,-10.0;10.0,10.0' }
        self.assertEqual(bounds.to_api_query(), qs)
        
    def test_to_api_query_with_postfix(self):
         """MMBounds.to_api_query() should return query string for API request."""
         bounds = MMBounds( MMLatLon( -10.0, -10.0 ), MMLatLon( 10.0, 10.0 ) )
         qs = {'bb_3': '-10.0,-10.0;10.0,10.0' }
         self.assertEqual(bounds.to_api_query(3), qs)

class testMMAddress(unittest.TestCase):
    """Tests MMAddress objects and methods."""
    
    def setUp(self):
        self.address = MMAddress( street=STREET, city=CITY, areas=AREAS, region=REGION, state=STATE, postal_code=POSTAL_CODE,
                                  zip_code=ZIP, display_name=DISPLAY_NAME, country_code=COUNTRY_CODE, qs=QS_UNIQUE)
    
    def test_to_api_query(self):
        """MMAddress.to_api_query() should return query string for API request."""
        qs = {'postalCode': POSTAL_CODE, 'city': CITY, 'countryCode': COUNTRY_CODE, 'ZIP': ZIP, 'region': REGION, 'state': STATE, 'street': STREET, 'qs': QS_UNIQUE }
        self.assertEqual(self.address.to_api_query(), qs)
        
    def test_to_api_query_with_postfix(self):
        """MMAddress.to_api_query(3) should return query string for API request including arg_[COUNTER]."""
        qs = {'postalCode_3': POSTAL_CODE, 'city_3': CITY, 'ZIP_3': ZIP, 'region_3': REGION, 'countryCode_3': COUNTRY_CODE, 'state_3': STATE, 'street_3': STREET, 'qs_3': QS_UNIQUE }
        self.assertEqual(self.address.to_api_query(3), qs)


class testMMLocation(unittest.TestCase):
    """Tests MMlocation objects adn methods"""
    
    def setUp(self):
        self.location = MMLocation()
    
    def test_from_json(self):
        """MMLocation.from_json() should create object with correct structure and values."""
        self.location.from_json( LOCATION )
        self.assertTrue(type(self.location) is MMLocation )
        self.assertTrue(type(self.location['address']) is MMAddress )
        self.assertTrue(type(self.location['coords']) is MMLatLon )
        # Bounds not yet implemented
        #self.assertTrue(type(location['bounds']) is MMBounds )
        self.assertEqual(self.location['geocode_quality'], GEOCODE_QUALITY )
        self.assertEqual(self.location['geocode_score'], GEOCODE_SCORE )
        self.assertEqual(self.location['zoom_factor'], ZOOM_FACTOR )
        
    def test_to_api_query(self):
        """MMLocation.to_api_query() should return query string for API request."""
        qs = { 'street': STREET, 'city': CITY, 'region': REGION, 'state': STATE, 'postalCode': POSTAL_CODE, 'countryCode': COUNTRY_CODE, 'qs': QS_UNIQUE, 'ZIP': ZIP, 'lat': str(LAT), 'lon': str(LON) }
        self.location.from_json( LOCATION )
        self.assertEqual(self.location.to_api_query(), qs)
        
    def test_to_api_query_with_postfix(self):
        """MMLocation.to_api_query() should return query string for API request including arg_[COUNTER]."""
        qs = { 'street_3': STREET, 'city_3': CITY, 'region_3': REGION, 'state_3': STATE, 'postalCode_3': POSTAL_CODE, 'ZIP_3': ZIP, 'qs_3': QS_UNIQUE, 'countryCode_3': COUNTRY_CODE, 'lat_3': str(LAT), 'lon_3': str(LON) }
        self.location.from_json( LOCATION )
        self.assertEqual(self.location.to_api_query(3), qs)
        
    def test_lat_lon_constructor(self):
        """MMLocation.__init__(LAT, LON) should create object with correct structure, types and values"""
        location = MMLocation( lat=LAT, lon=LON )
        self.assertTrue(type(location['coords']) is MMLatLon )
        self.assertEqual(location['coords']['lat'], LAT)
        self.assertEqual(location['coords']['lon'], LON)
        
    def test_lat_lon_object_constructor(self):
        """MMLocation.__init__(MMLatLon) should create object with correct structure, types and values"""
        location = MMLocation( coords=MMLatLon(LAT, LON) )
        self.assertTrue(type(location['coords']) is MMLatLon )
        self.assertEqual(location['coords']['lat'], LAT)
        self.assertEqual(location['coords']['lon'], LON)
    
    def test_qs_constructor(self):
        """MMLocation.__init__(qs) should create object with correct structure, types and values"""
        location = MMLocation( qs='se22' )
        self.assertTrue(type(location['address']) is MMAddress )
        self.assertEqual(location['address']['qs'], 'se22')
        
    def test_address_constructor(self):
        """MMLocation.__init__(MMAddress) should create object with correct structure, types and values"""
        location = MMLocation( address=MMAddress(qs='se22', country_code='gb') )
        self.assertTrue(type(location['address']) is MMAddress )
        self.assertEqual(location['address']['qs'], 'se22')
        
    def test_search_constructor(self):
        """MMLocation.__init__(MMSearch) should create object with correct structure, types and values"""
        search = MMSearch()
        search['point'] = MMLatLon( LAT, LON )
        location = MMLocation( search=search )
        self.assertTrue(type(location['search']) is MMSearch )
        self.assertTrue(type(location['search']['point']) is MMLatLon )
        self.assertEqual(location['search']['point']['lat'], LAT )
        
    def test_route_constructor(self):
        """MMLocation.__init__(MMRoute) should create object with correct structure, types and values"""
        route = MMRoute( [] )
        route['mode'] = 'driving'
        location = MMLocation( route=route )
        self.assertTrue(type(location['route']) is MMRoute )
        self.assertEqual(location['route']['mode'], 'driving' )
        
    def test_multiple_object_constructor(self):
        """MMLocation.__init__(MMSearch, MMAddress) should create object with correct structure, types and values"""
        address = MMAddress(qs='se22', country_code='gb')
        search = MMSearch()
        search['point'] = MMLatLon( LAT, LON )
        location = MMLocation( search=search, address=address )
        self.assertTrue(type(location['address']) is MMAddress )
        self.assertEqual(location['address']['qs'], 'se22')
        self.assertTrue(type(location['search']) is MMSearch )
        self.assertTrue(type(location['search']['point']) is MMLatLon )
        self.assertEqual(location['search']['point']['lat'], LAT )
        


class testGeocoder(unittest.TestCase):
    """Tests geocoding results for various qs strings."""
        
    def setUp(self):
        self.geocoder = MMGeocoder( DEV_KEY )
    
    def test_london(self):
        """MMGeocoder.request() should return geocoder response object with unique location result, and correct structure, types and values"""
        address = MMAddress(qs='london', country_code='gb')
        result = self.geocoder.geocode( address )
        
        self.assertEqual(result['location_count'], 1)
        self.assertEqual(int(result['result_set'][0]['geocode_quality']), 3)
        self.assertTrue(type(result['result_set'][0]) is MMLocation )
        self.assertTrue(type(result['result_set'][0]['address']) is MMAddress )
        self.assertEqual(result['result_set'][0]['address']['display_name'], 'London, England, SW1P 3')
        self.assertEqual(result['result_set'][0]['address']['postal_code'], 'SW1P 3')
        self.assertEqual(result['result_set'][0]['address']['country_code'], 'GB')
        self.assertEqual(result['result_set'][0]['address']['areas'][0], 'London')
        self.assertEqual(result['result_set'][0]['address']['areas'][1], 'England')
        self.assertEqual(float(result['result_set'][0]['geocode_score']), 1.000)
        self.assertEqual(result['result_set'][0]['zoom_factor'], 14)
        self.assertTrue(type(result['result_set'][0]['coords']) is MMLatLon )
        self.assertTrue(result['result_set'][0]['coords']['lat'])
        self.assertTrue(result['result_set'][0]['coords']['lon'])
    
    def test_sutton(self):
        """MMGeocoder.request() should return geocoder response object with disambiguation result, and correct structure, types and values"""
        
        address = MMAddress(qs='sutton', country_code='gb')
        result = self.geocoder.geocode( address )
        
        self.assertEqual(result['error_code'], 'MM_GEOCODE_MULTIPLE_MATCHES')
        self.assertTrue(result['location_count'] > 10)
        self.assertEqual(int(result['result_set'][5]['geocode_quality']), 3)
        self.assertTrue(type(result['result_set'][5]) is MMLocation )
        self.assertTrue(type(result['result_set'][5]['address']) is MMAddress )
        self.assertTrue(result['result_set'][5]['address']['display_name'])
        self.assertTrue(result['result_set'][5]['address']['postal_code'])
        self.assertTrue(result['result_set'][5]['address']['country_code'])
        self.assertTrue(result['result_set'][5]['address']['areas'][0])
        self.assertTrue(result['result_set'][5]['address']['areas'][1])
        self.assertTrue(result['result_set'][0]['geocode_score'])
        self.assertEqual(result['result_set'][5]['zoom_factor'], 14)
        self.assertTrue(type(result['result_set'][5]['coords']) is MMLatLon )
        self.assertTrue(result['result_set'][5]['coords']['lat'])
        self.assertTrue(result['result_set'][5]['coords']['lon'])
    
    def test_not_found(self):
        """MMGeocoder.request() should return geocoder response object with no matches result, and correct structure, types and values"""
        
        address = MMAddress(qs='herebedragons', country_code='gb')
        result = self.geocoder.geocode( address )
        
        self.assertEqual(result['error_code'], 'MM_GEOCODE_NO_MATCHES')
        self.assertEqual(result['location_count'], int(0))
        
class testMMRoute(unittest.TestCase):
    """Tests MMRoute object and methods"""
    
    def setUp(self):
        location_1 = MMLocation( MMAddress(qs='w1', country_code='GB') )
        location_2 = MMLocation( MMAddress(qs='w2', country_code='GB') )
        self.route = MMRoute( [location_1, location_2 ])
        self.route['mode'] = 'walking'
        self.route['optimize_for'] = 'distance'
        self.route['optimize_intermediates'] = 'true'
        self.route['emissions'] = 'true'
        self.route['custom_emission'] = [
            { 'name': 'car', 'value': 23, 'unit': 'mpg_imp', 'type': 'gas' },
            { 'name': 'truck', 'value': 34, 'unit': 'mpg_imp', 'type': 'gas' },
            { 'name': 'van', 'value': 89, 'unit': 'mpg', 'type': 'diesel' },
        ]
        self.route['exclude'] = 'something'
        self.route['format'] = 'dunno'
        self.route['lang'] = 'fr'
        
    def test_to_api_query(self):
        """MMRoute.to_api_query() should return query string for API request."""
        qs = { 'qs_1': 'w1', 'countryCode_1': 'GB', 'qs_2': 'w2', 'countryCode_2': 'GB', 'mode': 'walking', 'optimizeFor': 'distance', 'optimizeIntermediates': 'true', 'emissions': 'true', 'custom_name_1': 'car', 'custom_value_1': '23', 'custom_unit_1': 'mpg_imp', 'custom_type_1': 'gas', 'custom_name_2': 'truck', 'custom_value_2': '34', 'custom_unit_2': 'mpg_imp', 'custom_type_2': 'gas', 'custom_name_3': 'van', 'custom_value_3': '89', 'custom_unit_3': 'mpg', 'custom_type_3': 'diesel', 'exclude': 'something', 'format': 'dunno', 'lang': 'fr' }
        self.assertEqual(self.route.to_api_query(), qs)
        
class testMMRouteRequester(unittest.TestCase):
    """Tests routing results for various qs strings."""
    
    def setUp(self):
        self.router = MMRouteRequester( DEV_KEY )
        
    def test_route(self):
        """MMRouteRequester.request() should return route response object with route result, and correct structure, types and values"""
        location_1 = MMLocation( MMAddress(qs='w1', country_code='GB') )
        location_2 = MMLocation( MMAddress(qs='w2', country_code='GB') )
        route = MMRoute( [location_1, location_2 ] )
        
        result = self.router.request(route)
        self.assertTrue(result['copyright'])
        self.assertTrue(result['disclaimer'])
        self.assertTrue(result['stages'])
        self.assertTrue(type(result['stages'][0]['start_point']) is MMLatLon)
        self.assertTrue(type(result['stages'][0]['end_point']) is MMLatLon)
        self.assertTrue(type(result['stages'][0]['steps'][0]['start_point']) is MMLatLon)
        self.assertTrue(type(result['stages'][0]['steps'][0]['end_point']) is MMLatLon)
        
        
    def test_disambiguation(self):
        """MMRouteRequester.request() should return route response object with disamgiguation result and not found result, and correct structure, types and values"""
        location_1 = MMLocation( MMAddress(qs='herebedragons', country_code='GB') )
        location_2 = MMLocation( MMAddress(qs='sutton', country_code='GB') )
        route = MMRoute( [location_1, location_2 ] )
        
        result = self.router.request(route)
        self.assertEquals(result['errors'][0]['action'], 'geocode')
        self.assertEquals(result['errors'][0]['error_code'], 'MM_GEOCODE_NO_MATCHES' )
        self.assertEquals(int(result['errors'][0]['input_id']), 1)
        self.assertEquals(len(result['errors'][0]['results']), 0)
        self.assertTrue(type(result['errors'][0]['address']) is MMAddress)
        self.assertEquals(result['errors'][1]['action'], 'geocode')
        self.assertEquals(result['errors'][1]['error_code'], 'MM_GEOCODE_MULTIPLE_MATCHES' )
        self.assertEquals(int(result['errors'][1]['input_id']), 2)
        self.assertTrue(len(result['errors'][1]['results']) > 0)
        self.assertTrue(type(result['errors'][1]['results'][0]) is MMLocation)

        

class testSearchRequester(unittest.TestCase):
    """Instantiate a MMSearchRequester object and a sample search object."""
    def setUp(self):
        self.searcher = MMSearchRequester( DEV_KEY )
        self.search = MMSearch()
        self.search['point'] = MMLatLon(LAT, LON)
        self.search['data_source'] = DS_1
        self.search['count'] = COUNT
    
    def test_search_success(self):
        """MMSearchRequester.search() should return a search response with record_set and correct structure"""
        result = self.searcher.search( self.search )
        self.assertTrue(result['record_sets'][DS_1]['records'])
        
    def test_search_no_results(self):
        """MMSearchRequester.search() should return total_record_count of 0"""
        self.search['point'] = MMLatLon('here', 'dragons')
        result = self.searcher.search( self.search )
        self.assertEqual(result['record_sets'][DS_1]['total_record_count'], 0)
        
    def test_search_bad_datasource(self):
        """MMSearchRequester.search() should return a MM_API_ERROR_DATA_SOURCE_NOT_PROVISIONED error"""
        self.search['data_source'] = DS_BAD
        result = self.searcher.search( self.search )
        self.assertEqual(result['record_sets'][DS_BAD]['error']['error_code'], 'MM_API_ERROR_DATA_SOURCE_NOT_PROVISIONED')
        
        

class testSearch(unittest.TestCase):
    """Test search objects and methods"""
    
    def setUp(self):
        """Instantiate a MMSearch object and set some properties on it. Create a filter for use in some filter tests."""
        self.search = MMSearch()
        self.search['point'] = MMLatLon(LAT,LON)
        self.search['data_source'] = DS_1
        self.search['count'] = COUNT
        self.filter = MMSearchFilter(FIELDNAME, OPERATOR, VALUE, OPTIONS)
    
    def test_to_api_query(self):
        """MMSearch.to_api_query() should return query string for API request."""
        qs = { 'dataSource': DS_1, 'count': str(COUNT), 'lat': str(LAT), 'lon': str(LON) }
        self.assertEqual(self.search.to_api_query(), qs)
        
    def test_to_api_query_with_postfix(self):
        """MMSearch.to_api_query() should return query string for API request including arg_[COUNTER]."""
        qs = { 'dataSource_3': DS_1, 'count_3': str(COUNT), 'lat_3': str(LAT), 'lon_3': str(LON) }
        self.assertEqual(self.search.to_api_query(3), qs)
        
    def test_to_api_query_with_filter(self):
        """MMSearch.to_api_query() should return query string for API request including filter."""
        self.search['filters'] = [self.filter]
        qs = { 'dataSource': DS_1, 'count': str(COUNT), 'lat': str(LAT), 'lon': str(LON), 'fieldname_1': FIELDNAME, 'operator_1': OPERATOR, 'value_1': VALUE, 'fieldFilterOptions_1': ','.join( OPTIONS ) }
        self.assertEqual(self.search.to_api_query(), qs)
        
    def test_to_api_query_with_multiple_filters(self):
        """MMSearch.to_api_query() should return query string for API request including multiple filters."""
        self.search['filters'] = [self.filter, self.filter]
        qs = { 'dataSource': DS_1, 'count': str(COUNT), 'lat': str(LAT), 'lon': str(LON), 'fieldname_1': FIELDNAME, 'operator_1': OPERATOR, 'value_1': VALUE, 'fieldFilterOptions_1': ','.join( OPTIONS ), 'fieldname_2': FIELDNAME, 'operator_2': OPERATOR, 'value_2': VALUE, 'fieldFilterOptions_2': ','.join( OPTIONS ) }
        self.assertEqual(self.search.to_api_query(), qs)
        
    def test_to_api_query_with_bounding_box(self):
        """MMSearch.to_api_query() should return query string for API request including bounding box."""
        self.search['bounding_box'] = MMBounds(MMLatLon( -10.0, -10.0 ), MMLatLon( 10.0, 10.0 ))
        qs = { 'dataSource': DS_1, 'count': str(COUNT), 'bb': '-10.0,-10.0;10.0,10.0', 'lat': str(LAT), 'lon': str(LON) }
        self.assertEqual(self.search.to_api_query(), qs)
        
    def test_to_api_query_with_route(self):
        """MMSearch.to_api_query() should return query string for API request including route."""
        location_1 = MMLocation( MMAddress(qs='w1', country_code='GB') )
        location_2 = MMLocation( MMAddress(qs='w2', country_code='GB') )
        self.search['route'] = MMRoute( [location_1, location_2 ])
        qs = {'dataSource': DS_1, 'count': str(COUNT), 'lat': str(LAT), 'lon': str(LON), 'qs_1': 'w1', 'countryCode_1': 'GB', 'qs_2': 'w2', 'countryCode_2': 'GB' }
        self.assertEqual(self.search.to_api_query(), qs)


class testSearchFilter(unittest.TestCase):
    """Tests search filter objects and methods."""
    
    def setUp(self):
        """Instantiate a MMSearchFilter object with some default args."""
        self.filter = MMSearchFilter(FIELDNAME, OPERATOR, VALUE, OPTIONS)
    
    def test_to_api_query(self):
        """MMSearchFilter.to_api_query() should return query string for API request."""
        qs = {'fieldname': FIELDNAME, 'operator': OPERATOR, 'value': VALUE, 'fieldFilterOptions': ','.join( OPTIONS ) }
        self.assertEqual(self.filter.to_api_query(), qs)
            
    def test_to_api_query_with_postfix(self):
        """MMSearchFilter.to_api_query(3) should return query string for API request including arg_[COUNTER]."""
        qs = {'fieldname_3': FIELDNAME, 'operator_3': OPERATOR, 'value_3': VALUE, 'fieldFilterOptions_3': ','.join( OPTIONS ) }
        self.assertEqual(self.filter.to_api_query(3), qs)
        

if __name__ == '__main__':
    
    unittest.main()
    
    #suiteFew = unittest.TestSuite()
    
    #suiteFew.addTest(testGeocoder("testLondon"))
    
    #unittest.TextTestRunner(verbosity=2).run(suiteFew)
    
    #unittest.TextTestRunner(verbosity=2).run(suite())
