#!/usr/bin/env python

"""
doctest runner
"""

import doctest
import os
import shutil
import sys
from optparse import OptionParser
from paste.fixture import TestApp
from toolbox.dispatcher import Dispatcher

try:
    import json
except ImportError:
    import simplejson as json

# globals
directory = os.path.dirname(os.path.abspath(__file__))
json_dir = os.path.join(directory, 'test_json')

class ToolboxTestApp(TestApp):
    """WSGI app wrapper for testing JSON responses"""
    
    def __init__(self):
        app = Dispatcher(fields=('usage', 'author', 'type', 'language', 'dependencies'), directory=json_dir)
        TestApp.__init__(self, app)

    def get(self, url='/', **kwargs):
        kwargs.setdefault('params', {})['format'] = 'json'
        response = TestApp.get(self, url, **kwargs)
        return json.loads(response.body)

class MemoryCacheTestApp(ToolboxTestApp):
    """test the MemoryCache file-backed backend"""

def run_tests(raise_on_error=False, cleanup=True):
    tests =  [ test for test in os.listdir(directory)
               if test.endswith('.txt') ]
    results = {}
    for test in tests:
        shutil.rmtree(json_dir, ignore_errors=True)
        os.makedirs(json_dir)
        app = ToolboxTestApp()
        extraglobs = {'here': directory, 'app': app, 'json_dir': json_dir}
        try:
            results[test] = doctest.testfile(test, extraglobs=extraglobs, raise_on_error=raise_on_error,
                                             optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
        except doctest.UnexpectedException, failure:
            return {}
            import pdb
            raise failure.exc_info[0], failure.exc_info[1], failure.exc_info[2]
            pdb.set_trace()
        finally:
            if cleanup:
                shutil.rmtree(json_dir, ignore_errors=True)
    return results

def main(args=sys.argv[1:]):
    parser = OptionParser()
    parser.add_option('--cleanup', dest='cleanup',
                      default=False, action='store_true',
                      help="cleanup following the tests")
    parser.add_option('--raise', dest='raise_on_error',
                      default=False, action='store_true',
                      help="raise on first error")
    options, args = parser.parse_args(args)
    results = run_tests(raise_on_error=options.raise_on_error, cleanup=options.cleanup)
    if sum([i.failed for i in results.values()]):
        sys.exit(1) # error

if __name__ == '__main__':
    main()

