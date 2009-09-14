try:
    import json
except:
    import simplejson as json


import urllib, math, string

API_PROTOCOL = 'http://'
API_HOSTNAME = 'developer.multimap.com'
API_VERSION = '1.2'
API_OUTPUT = 'json'

API_URL = string.Template(
    API_PROTOCOL + API_HOSTNAME + "/API/${action}/" + API_VERSION + "/${dev_key}?${query_string}&output=" + API_OUTPUT
)

class MMAPIException(Exception):
    pass


def do_api_request(url):
    """Simple request using urllib module. Might want to drop down to httplib for more advanced/granular usage later."""
    try:
        response = urllib.urlopen( url )
        parsed_response = json.load( response )
        return parsed_response
    except ValueError:
        raise MMAPIException, "The url (%s) returned a bad response. Copy and paste this url into a browser and check it out. It may be because of single quoted JSON with is invalid" % url
    except IOError:
        raise MMAPIException, "The url (%s) did not get a response from the server. Copy and paste this url into a browser and check it out." % url
        
        
def lat_lon_to_mercator(lat, lon, eccentricity=None):
    k0 = 1 # Scale factor at the natural origin. Unity in our case.
    lon0 = 0 # Longitude of the natural origin. Is the prime meridian in our case.
    
    # Convert from degrees to radians
    rlat = float(lat) * ( math.pi / 180 )
    rlon = float(lon) * ( math.pi / 180 )
    
    a = 6378137 # Radius of WGS84 ellipsoid.
    f = 298.257223563 # Reciprocal flattening of ellipsoid.
    e = 0.0818191908426215 # Eccentricity of the ellipsoid.
    
    if eccentricity:
        e = eccentricity
    
    b1 = ( math.pi / 4 ) + ( rlat / 2 )
    b1 = math.tan( b1 )
    
    if e:
        b2 = ( 1 - ( e * math.sin( rlat ) ) ) / ( 1 + ( e * math.sin( rlat ) ) )
        b2 = b2 ** ( e / 2 )
    else:
        b2 = 1
    b = b1 * b2
    
    # Only find log if number is greater than zero.
    if ( b > 0 ):
        ln = math.log(b)
    else:
        ln = 0
    
    y = a * k0 * ln
    x = a * k0 * ( rlon - lon0 )
    
    return { 'x': x, 'y': y }

def coord_to_tile(x, y, zoom):
    world_width = 40075016.0
    half_world_width = 20037508.0
    digits = zoom - 1
    tile_width = float( world_width / ( 2 ** digits ) )
    x = ( x + half_world_width ) / tile_width
    y = ( y + half_world_width ) / tile_width
    return { 'x': x, 'y': y }


class MMLatLon(dict):
    def __init__( self, lat=None, lon=None ):
        self['lat'] = lat
        self['lon'] = lon
        
    def forceNumbers(self):
        if type(self['lat']) is 'str':
            self['lat'] = float(self['lat'])
        if type(self['lon']) is 'str':
            self['lon'] = float(self['lon'])
            
    def copy(self):
        return MMLatLon( self['lat'], self['lon'] )
        
    
    def to_api_query( self, postfix=''):
        url = {}
        
        if postfix is not '':
            postfix = '_' + str(postfix)
        
        if self.has_key('lat'):
            url['lat' + postfix] = str(self['lat'])
        if self.has_key('lon'):
            url['lon' + postfix] = str(self['lon'])
            
        return url
        
    def to_string(self):
        return '(' + str(self['lat']) + ',' + str(self['lon']) + ')'
    
    def from_json(self,json):
        if json is not None:
            self['lat'] = json['lat']
            self['lon'] = json['lon']


class MMBounds(dict):
    def __init__(self,south_west=None, north_east=None):
        self.reset(south_west, north_east)
        
    def reset(self,south_west=None, north_east=None):
        self.south_west = None
        self.north_east = None
        
        if type(south_west) is list:
            for e in south_west:
                self.extend(e)
        
        elif south_west or north_east:
            sw = self.__getPoint( south_west )
            ne = self.__getPoint( north_east )
            if not sw:
                sw = ne
            if not ne:
                ne = sw
                
            self['south_west'] = sw
            self['north_east'] = ne 
        
    def extend(self,point):
        if type(point) is MMBounds:
            self.extend( point['south_west'] )
            self.extend( point['north_east'] )
            return

        point = self.__getPoint( point )
        if not self.has_key('south_west'):
            self['south_west'] = point.copy()
            self['north_east'] = point.copy()
        else:
            if point['lat'] < self['south_west']['lat']:
                self['south_west']['lat'] = point['lat']
            if point['lat'] > self['north_east']['lat']:
                self['north_east']['lat'] = point['lat']
          
        possibles = []
        contained = self.contains( point )
        if not contained:
            # Try using the lon of the new point as a replacement for
            # each of the SW and NE lons and get the new distance
            possibles.append( {
                'distance': self.__getDistance( self['south_west']['lon'], point['lon'] ), 
                'sw_lon': self['south_west']['lon'],
                'ne_lon': point['lon'] } )
            possibles.append( {
                'distance': self.__getDistance( point['lon'], self['north_east']['lon'] ), 
                'sw_lon': point['lon'],
                'ne_lon': self['north_east']['lon'] } )

            # The one with the shortest distance will be the one we want
            shortest_distance = None
            for p in possibles:
                if shortest_distance is None or p['distance'] < shortest_distance:
                    self['south_west']['lon'] = p['sw_lon']
                    self['north_east']['lon'] = p['ne_lon']
                    shortest_distance = p['distance']
        
    
    def from_json(self,json):
        if json is not None:
            self['south_west'] = MMLatLon(float(json['south_west']['lat']), float(json['south_west']['lon']))
            self['north_east'] = MMLatLon(float(json['north_east']['lat']), float(json['north_east']['lon']))
            
    def copy(self):
        cp = MMBounds()
        if self.has_key('south_west'):
            cp['south_west'] = self['south_west'].copy()
        if self.has_key('north_east'):
            cp['north_east'] = self['north_east'].copy()
        return cp
        
    def __getPoint(self, point):
        if point and type(point) is MMLocation:
            point = point['coords']
        if point:
            point.forceNumbers()
        return point    
        
    def contains(self, point):
        contained = False
        if type(self['south_west']) is MMLatLon:
            if self['south_west']['lon'] > self['north_east']['lon']:
                if (point['lon'] >= self['south_west']['lon'] or point['lon'] <= self['north_east']['lon']) and point['lat'] >= self['south_west']['lat'] and point['lat'] <= self['north_east']['lat']:
                    contained = True
            else:
                if point['lon'] >= self['south_west']['lon'] and point['lon'] <= self['north_east']['lon'] and point['lat'] >= self['south_west']['lat'] and point['lat'] <= self['north_east']['lat']:
                    contained = True
        
        return contained
            
    def __getDistance(self, sw_lon, ne_lon):
        if sw_lon > ne_lon:
            return (ne_lon + 360) - sw_lon
        else:
            return ne_lon - sw_lon
            
    def getSouthWest(self):
        if self.has_key('south_west'):
            return self['south_west'].copy()
            
    def getNorthEast(self):
        if self.has_key('north_east'):
             return self['north_east'].copy()
            
    def getSouthEast(self):
        return MMLatLon(self['south_west']['lat'], self['north_east']['lon'])
            
    def getNorthWest(self):
        return MMLatLon(self['north_east']['lat'], self['south_west']['lon'])
            
    def getCenter(self):
        sw = self.getSouthWest()
        ne = self.getNorthEast()
        sw.forceNumbers()
        ne.forceNumbers()
        center = nil
        
        if( type(sw) is MMLatLon ):
            if( sw.lon > ne.lon ):
                ne.lon += 360
            center = MMLatLon(sw.lat + ( (ne.lat - sw.lat ) / 2 ), sw.lon + ( (ne.lon - sw.lon ) / 2 ) )
            if( center.lon > 180 ):
                center.lon -= 360

        else:
            center = MMPoint.new(sw.x + ( ( ne.x - sw.x ) / 2 ), sw.y + ( ( ne.y - sw.y ) / 2 ) )
        return center
        
    def to_string(self):
        return '[ ' + ('undefined', self['south_west'].to_string())[self.has_key('south_west')] + ', ' + ('undefined', self['north_east'].to_string())[self.has_key('north_east')] + ' ]'
            
    def to_api_query(self, postfix=''):
        
        if postfix is not '':
            postfix = '_' + str(postfix)
        
        url = {}
        url['bb' + postfix] = str(self.getSouthWest()['lon']) + ',' + str(self.getSouthWest()['lat']) + ';' + str(self.getNorthEast()['lon']) + ',' + str(self.getNorthEast()['lat'])
        
        return url

class MMAddress(dict):
    def __init__( self, addr=None ):
        if addr is not None:
            if addr.has_key('street'): self['street'] = addr['street']
            if addr.has_key('city'): self['city'] = addr['city']
            if addr.has_key('areas'): self['areas'] = addr['areas']
            if addr.has_key('region'): self['region'] = addr['region']
            if addr.has_key('state'): self['state'] = addr['state']
            if addr.has_key('postal_code'): self['postal_code'] = addr['postal_code']
            if addr.has_key('zip'): self['zip'] = addr['zip']
            if addr.has_key('display_name'): self['display_name'] = addr['display_name']
            if addr.has_key('country_code'): self['country_code'] = addr['country_code']
            if addr.has_key('qs'): self['qs'] = addr['qs']
    
    def to_api_query(self, postfix=''):
        url = {}
        
        if postfix is not '':
            postfix = '_' + str(postfix)
        
        if self.has_key('street'):
            url['street' + postfix] = self['street']
        if self.has_key('city'):
            url['city' + postfix] = self['city']
        #if self.has_key('areas'):
        #    url += '&areas' + postfix + '=' + self['areas']
        if self.has_key('region'):
            url['region' + postfix] = self['region']
        if self.has_key('state'):
            url['state' + postfix] = self['state']
        if self.has_key('postal_code'):
            url['postalCode' + postfix] = self['postal_code']
        if self.has_key('zip'):
            url['ZIP' + postfix] = self['zip']
        if self.has_key('qs'):
            url['qs' + postfix] = self['qs']
        if self.has_key('country_code'):
            url['countryCode' + postfix] = self['country_code']
        
        return url


class MMLocation(dict):
    def __init__(self,*args):
        
        if len(args) > 0:
            
            # If the first two arguments are type float, then they are lat/lon values.
            if len(args) > 1 and type(args[0]) is float and type(args[1]) is float:
                self['coords'] = MMLatLon( args[0], args[1] )
                
                # If a third argumnt is type int then it is a zoom_factor value.
                if len(args) > 2 and type(args[2]) is int:
                    self['zoom_factor'] = args[2]
            
            # If the first argument is type str then it is a qs value. Build a MMAddress object with it.
            if type(args[0]) is str:
                self['address'] = MMAddress( { 'qs': args[0] })
            
            # Otherwise go throuh all arguments and determine their type.
            else:
                for arg in args:
                    if type(arg) is int:
                        self['zoom_factor'] = arg
                    elif type(arg) is MMLatLon:
                        self['coords'] = arg
                    elif type(arg) is MMRoute:
                        self['route'] = arg
                    elif type(arg) is MMAddress:
                        self['address'] = arg
                    elif type(arg) is MMSearch:
                        self['search'] = arg
                    elif type(arg) is MMBounds:
                        self['bounds'] = arg
                        
        
    def to_api_query(self, postfix=''):
        url = {}
        
        if self.has_key('address'):
            url.update(self['address'].to_api_query(postfix))
        if self.has_key('search'):
            url.update(self['search'].to_api_query(postfix))
        if self.has_key('coords'):
            url.update(self['coords'].to_api_query(postfix))
        if self.has_key('bounds'):
            url.update(self['bounds'].to_api_query(postfix))
            
        return url
    
    def from_json(self,json):
        if json is not None:
            if json.has_key('geocode_quality'):
                self['geocode_quality'] = json['geocode_quality']
            if json.has_key('geocode_score'):
                self['geocode_score'] = json['geocode_score']
            if json.has_key('zoom_factor'):
                self['zoom_factor'] = json['zoom_factor']
            if json.has_key('address'):
                self['address'] = MMAddress(json['address'])
            if json.has_key('point'):
                self['coords'] = MMLatLon(json['point']['lat'], json['point']['lon'])
            if json.has_key('bounds'):
                self['bounds'] = MMBounds()
                self['bounds'].from_json(json['bounds'])


class MMGeocoder:
    def __init__( self, dev_key ):
        self.dev_key = dev_key
    
    def geocode( self, address ):
        url = API_URL.substitute(action='geocode', dev_key=self.dev_key, query_string=urllib.urlencode(address.to_api_query()))
        response = do_api_request( url )
        
        if response.has_key('result_set'):
            locations = []
            for result in response['result_set']:
                location = MMLocation()
                location.from_json( result )
                locations.append( location )
            response['result_set'] = locations
        
        return response
        
        
class MMRoute(dict):
    def __init__(self, locations):
        self.locations = locations
        
    def to_api_query(self):
        url = {}
        
        if self.has_key('key'):
            url['routeKey'] = self['key']
        else:
            index = 1
            for location in self.locations:
                url.update(location.to_api_query(index))
                index += 1
                
        if self.has_key('mode'):
            url['mode'] = self['mode']
        if self.has_key('optimize_for') and self['optimize_for'] is 'distance':
            url['optimizeFor'] = 'distance'
        if self.has_key('optimize_intermediates') and self['optimize_intermediates'] == 'true':
            url['optimizeIntermediates'] = 'true'
        if self.has_key('emissions') and self['emissions'] == 'true':
            url['emissions'] = 'true'
            if self.has_key('custom_emission'):
                i = 1
                for custom in self['custom_emission']:
                    if custom.has_key('name'):
                        url['custom_name_'  + str(i)]  = custom['name'];
                    if custom.has_key('value'):
                        url['custom_value_' + str(i)] = str(custom['value']);
                    if custom.has_key('unit'):
                        url['custom_unit_'  + str(i)] = custom['unit'];
                    if custom.has_key('type'):
                        url['custom_type_'  + str(i)] = custom['type'];
                    i += 1
        
        if self.has_key('exclude'):
            url['exclude'] = self['exclude']
        if self.has_key('format'):
            url['format'] = self['format']
        if self.has_key('lang'):
            url['lang'] = self['lang']

        return url
        
class MMRouteRequester:
    def __init__( self, dev_key ):
        self.dev_key = dev_key
        
    def request(self, route):
        url = API_URL.substitute(action='route', dev_key=self.dev_key, query_string=urllib.urlencode(route.to_api_query()))
        response = do_api_request( url )

        return self.parseStructure(response)
        
    def parseStructure(self, json ):
        
        if json.has_key('stages'):
        
            #json['bounds'] = MMBounds( json['bounds'] )
        
            for stage in json['stages']:
            
                # the start_point and end_point of each stage to be MMLatLon objects
                stage['start_point'] = MMLatLon(float(stage['start_point']['lat']), float(stage['start_point']['lon']));
                stage['end_point'] = MMLatLon(float(stage['end_point']['lat']), float(stage['end_point']['lon']));

                # the StartAddress and EndAddress of each stage to be MMAddress objects
                stage['start_address'] = MMAddress(stage['start_address']);
                stage['end_address'] = MMAddress(stage['end_address']);

                # the bounds of each Stage to be MMBounds objects
                #stage['bounds'] = MMBounds();
                #stage['bounds'].from_json(stage['bounds']);
            
                # the start_point and end_point of each step to be MMLatLon objects
                if stage['steps']:
                  step_index = 0
                  for step in stage['steps']:
                      step['start_point'] = MMLatLon(float(step['start_point']['lat']), float(step['start_point']['lon']));
                      step['end_point'] = MMLatLon(float(step['end_point']['lat']), float(step['end_point']['lon']));
                
        elif json.has_key('errors'):
            
            json['error_code'] = 'MM_ROUTE_GEOCODING_ERRORS'
            json['geocoding_errors'] = json['errors'];
            
            for error in json['geocoding_errors']:
                error['address'] = MMAddress( error['address'] )
                if error['results']:
                    locations = []
                    for result in error['results']:
                        location = MMLocation()
                        location.from_json(result)
                        locations.append( location )
                    error['results'] = locations
                        
        return json

class MMSearch(dict):
    def __init__( self ):
        pass

    def to_api_query( self, postfix_number = '' ):
        postfix = ''
        if postfix_number is not '':
            postfix = '_' + str(postfix_number)
    
        url = {}
    
        if self.has_key('data_source'):
            if ( type( self['data_source'] ) == list ):
                url['dataSource' + postfix] = (',').join( self['data_source'] )
            else:
                url['dataSource' + postfix] = self['data_source']
    
        if self.has_key('count'):
            url['count' + postfix] = str(self['count'])
    
        if self.has_key('format'):
            url['format' + postfix] = self['format']
    
        if self.has_key('start_index'):
            url['startIndex' + postfix] = str(self['start_index'])
    
        if self.has_key('bounding_box'):
            url.update( self['bounding_box'].to_api_query( postfix_number) )
    
        if self.has_key('point'):
            url.update( self['point'].to_api_query(postfix_number) )
    
        if self.has_key('address'):
            url.update( self['address'].to_api_query(postfix_number) )
    
        if self.has_key('max_distance'):
            url['maxDistance' + postfix] = self['max_distance']
    
        if self.has_key('distance_units'):
            url['distanceUnits' + postfix] = self['distance_units']
    
        if self.has_key('logic'):
            url['logic' + postfix] = self['logic']
    
        if self.has_key('min_distance'):
            url['minDistance' + postfix] = self['min_distance']
    
        if self.has_key('order_by_fields'):
            if ( type( self.order_by_fields ) == list ):
                url['orderByFields' + postfix] = (',').join( self['order_by_fields'] )
            else:
                url['orderByFields' + postfix] = self['order_by_fields']
    
        if self.has_key('order_by_order'):
            if ( type( self.order_by_order ) == list ):
                url['orderByOrder' + postfix] = (',').join( self['order_by_order'] )
            else:
                url['orderByOrder' + postfix] = self['order_by_order']
    
        if self.has_key('return_fields'):
            if ( type( self.return_fields ) == list ):
                url['returnFields' + postfix] = (',').join( self['return_fields'] )
            else:
                url['returnFields' + postfix] = self['return_field']
    
        if self.has_key('return_infobox'):
            url['returnInfobox'] = self['return_infobox']
    
        preflight_filters = 0
        if self.has_key('pre_search'):
            if self['pre_search'].has_key('data_source'):
                url['preSearchDataSource'] = self['pre_search']['data_source']
            if self['pre_search'].has_key('search_first_alt'):
                url['searchFirstAlt'] = self['pre_search']['search_first_alt']
            if self['pre_search'].has_key('filters'):
                # handle array of MMFieldFilter objects
                i = 0
                for filter in self['pre_search']['filters']:
                    url.update(filter.to_api_query( i + 1 ))
                    preflight_filters =+ 1
                    i =+ 1
        
            preflight_filters += 1
            url['preSearchFilters'] = str(preflight_filters)
    
        if self.has_key('compound_threshold'):
            url['compoundThreshold' + postfix] = self['compound_threshold']
    
        if self.has_key('result_set_size'):
            url['resultSetSize' + postfix] = self['result_set_size']
    
        if self.has_key('morton'):
            url['morton' + postfix] = self['morton']
    
        if self.has_key('compound_order'):
            url['compoundOrder' + postfix] = self['compound_order']
    
        if self.has_key('route_modes'):
            url['routeModes'] = self['route_modes']
    
        if self.has_key('route') and type(self['route']) is MMRoute:
           url.update(self['route'].to_api_query())
    
        if self.has_key('filters'):
            # handle array of MMFieldFilter objects
            i = 0
            for filter in self['filters']:
                # MMSearch objects with multiple field filters won't work for preflight routing
                if postfix_number:
                    postfix_number -= 1
                else:
                    postfix_number = 0
                    url.update(filter.to_api_query(i + 1 + preflight_filters + postfix_number))
                i += 1
                   
        return url





class MMSearchFilter:
    def __init__( self, field, operator, value, options=None ):
        self.field = field
        self.operator = operator
        self.value = value
        self.options = options
    
    def to_api_query( self, postfix=''):
        url = {}
        
        if postfix is not '':
            postfix = '_' + str(postfix)
        
        url['fieldname' + postfix] = self.field
        if self.operator:
            url['operator' + postfix] = self.operator
        
        url['value' + postfix] = self.value
        
        options_url = {}
        if self.options:
            if type( self.options ) is list:
                options_url['fieldFilterOptions' + postfix] = ','.join( self.options )
            else:
                options_url['fieldFilterOptions' + postfix] = self.options
        
        url.update(options_url)
        
        return url


class MMSearchRequester:
    def __init__( self, dev_key ):
        self.dev_key = dev_key
    
    def search( self, search ):
        url = API_URL.substitute(action='search', dev_key=self.dev_key, query_string=urllib.urlencode(search.to_api_query()))
        response = do_api_request( url )
        
        return response
        

class MMWhereAmI:
    def __init__( self, dev_key ):
        self.dev_key = dev_key
    
    def search( self, lat, lon, zoom = 16 ):
        merc = lat_lon_to_mercator( lat, lon )
        tile = coord_to_tile( merc['x'], merc['y'], zoom)
        
        query_string = '&zoom=' + str(zoom) + '&lat=' + str(lat) + '&lon=' + str(lon) + '&x=' + str(tile['x']) + '&y=' + str(tile['y']) 
        url = API_URL.substitute(action='WhereAmI', dev_key=self.dev_key, query_string=query_string)
        response = do_api_request( url )
        
        return response
